#!/bin/bash

# Azure Day 2 Engine - Full Development Environment Launcher
# =========================================================

echo "🚀 Starting Azure Day 2 Engine Full Development Environment"
echo "   This script will start both the API backend and the frontend dashboard"
echo "   Press Ctrl+C at any time to stop both services"
echo ""

# Change to script directory to ensure relative paths work
cd "$(dirname "$0")"

# Verify we're in the correct directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Not in the correct project directory. Expected to find app/main.py"
    echo "   Current directory: $(pwd)"
    exit 1
fi

echo "📂 Working directory: $(pwd)"

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down development environment..."
    
    # Kill background processes and their children
    if [ ! -z "$API_PID" ]; then
        # Kill the process group to ensure all child processes are terminated
        pkill -P $API_PID 2>/dev/null
        kill $API_PID 2>/dev/null
        # Give it a moment to terminate gracefully
        sleep 1
        # Force kill if still running
        kill -9 $API_PID 2>/dev/null
        echo "   ✅ API server stopped"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        # Kill the process group to ensure all child processes are terminated
        pkill -P $FRONTEND_PID 2>/dev/null
        kill $FRONTEND_PID 2>/dev/null
        # Give it a moment to terminate gracefully
        sleep 1
        # Force kill if still running
        kill -9 $FRONTEND_PID 2>/dev/null
        echo "   ✅ Frontend server stopped"
    fi
    
    # Also kill any remaining uvicorn or streamlit processes
    pkill -f "uvicorn.*app.main:app" 2>/dev/null
    pkill -f "streamlit.*app.py" 2>/dev/null
    
    echo "🏁 Development environment shut down complete"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📋 Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "⚠️  Please edit .env file with your Azure credentials before running the application"
        echo "   You can continue without Azure credentials for basic functionality"
    else
        echo "⚠️  No .env.example found. Creating basic .env file..."
        cat > .env << 'EOF'
# Azure Configuration (edit with your values)
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here
AZURE_CLIENT_SECRET=your-client-secret-here
AZURE_SUBSCRIPTION_ID=your-subscription-id-here

# Application Configuration
DEBUG=true
LOG_LEVEL=INFO

# PostgreSQL Configuration (defaults)
POSTGRES_DEFAULT_PORT=5432
POSTGRES_SSL_MODE=require
EOF
        echo "   ✅ Created basic .env file - edit with your Azure credentials"
    fi
    echo ""
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8 or later."
    exit 1
fi

# Get Python version for compatibility check
PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
echo "🐍 Using Python $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Verify activation
if [ "$VIRTUAL_ENV" = "" ]; then
    echo "❌ Error: Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated: $VIRTUAL_ENV"

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip install --upgrade pip --quiet
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
else
    echo "⚠️  No requirements.txt found in root directory"
fi

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
if [ -d "frontend" ]; then
    cd frontend
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt --quiet
    else
        echo "⚠️  No requirements.txt found in frontend directory"
        # Install minimal requirements for streamlit frontend
        pip install streamlit requests pandas plotly --quiet
    fi
    cd ..
else
    echo "⚠️  Frontend directory not found"
fi

# Verify critical installations
echo "🔍 Verifying installations..."
python -c "import fastapi, uvicorn; print('✅ FastAPI and Uvicorn installed')" 2>/dev/null || {
    echo "⚠️ Installing FastAPI and Uvicorn..."
    pip install fastapi uvicorn[standard] --quiet
}

python -c "import streamlit; print('✅ Streamlit installed')" 2>/dev/null || {
    echo "⚠️ Installing Streamlit..."
    pip install streamlit --quiet
}

# Check if Azure CLI is available
if ! command -v az &> /dev/null; then
    echo "⚠️  Azure CLI not found. Please install Azure CLI or use the devcontainer."
    echo "   Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    echo ""
fi

echo "✅ Environment setup complete!"
echo ""

# Start API Backend
echo "🌐 Starting FastAPI backend server..."
echo "   📖 API Documentation: http://localhost:8000/docs"
echo "   ❤️  Health Check: http://localhost:8000/health"
echo "   📚 ReDoc: http://localhost:8000/redoc"

# Check if port 8000 is already in use
if lsof -i:8000 &> /dev/null; then
    echo "⚠️  Port 8000 is already in use. Attempting to free it..."
    pkill -f "uvicorn.*app.main:app" 2>/dev/null
    sleep 2
fi

# Start the API with proper error handling
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level warning &
API_PID=$!

# Verify the API process started
sleep 1
if ! kill -0 $API_PID 2>/dev/null; then
    echo "❌ Failed to start API backend"
    exit 1
fi

# Wait for API to be ready
echo "⏳ Waiting for API to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ API failed to start within 30 seconds"
        cleanup
        exit 1
    fi
    sleep 1
done

echo ""

# Start Frontend Dashboard
echo "🎨 Starting Streamlit frontend dashboard..."
echo "   🌐 Frontend Dashboard: http://localhost:8501"

# Check if port 8501 is already in use
if lsof -i:8501 &> /dev/null; then
    echo "⚠️  Port 8501 is already in use. Attempting to free it..."
    pkill -f "streamlit.*app.py" 2>/dev/null
    sleep 2
fi

# Start the frontend
if [ -f "frontend/app.py" ]; then
    cd frontend
    streamlit run app.py --server.port 8501 --server.address localhost --logger.level error --server.headless true &
    FRONTEND_PID=$!
    cd ..
    
    # Verify the frontend process started
    sleep 1
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Failed to start frontend dashboard"
        cleanup
        exit 1
    fi
else
    echo "⚠️  Frontend app.py not found. Skipping frontend startup."
fi

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to start..."
for i in {1..20}; do
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        echo "✅ Frontend dashboard is ready!"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "⚠️  Frontend may take a moment to start..."
        break
    fi
    sleep 1
done

echo ""
echo "🎉 Azure Day 2 Engine development environment is running!"
echo ""
echo "📋 Available Services:"
echo "   🔗 API Backend:           http://localhost:8000"
echo "   📖 API Documentation:     http://localhost:8000/docs"
if [ ! -z "$FRONTEND_PID" ]; then
    echo "   🎨 Frontend Dashboard:    http://localhost:8501"
fi
echo "   ❤️  Health Check:         http://localhost:8000/health"
echo ""
echo "🛠️  Development Tips:"
echo "   • The API supports hot-reload for code changes"
echo "   • The frontend auto-refreshes when you modify app.py"
echo "   • Use Ctrl+C to stop both services"
echo "   • Check logs above for any startup issues"
echo ""

# Open browser automatically on macOS (optional)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🌐 Opening browser windows..."
    sleep 2
    open http://localhost:8000/docs > /dev/null 2>&1 &
    if [ ! -z "$FRONTEND_PID" ]; then
        sleep 1
        open http://localhost:8501 > /dev/null 2>&1 &
    fi
fi

echo "🔄 Monitoring both services... (Press Ctrl+C to stop)"

# Wait for user interrupt
while true; do
    # Check if API process is still running
    if ! kill -0 $API_PID 2>/dev/null; then
        echo "❌ API process has died unexpectedly"
        cleanup
        exit 1
    fi
    
    # Check if Frontend process is still running (only if it was started)
    if [ ! -z "$FRONTEND_PID" ] && ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend process has died unexpectedly"
        cleanup
        exit 1
    fi
    
    sleep 5
done