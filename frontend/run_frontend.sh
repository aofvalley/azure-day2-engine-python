#!/bin/bash

# Azure Day 2 Engine - Frontend Launcher
# =====================================

echo "🚀 Starting Azure Day 2 Engine Frontend Dashboard..."
echo

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv ../venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source ../venv/bin/activate

# Verify activation
if [ "$VIRTUAL_ENV" = "" ]; then
    echo "❌ Error: Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated: $VIRTUAL_ENV"

# Install frontend dependencies
echo "📥 Installing frontend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Verify plotly installation
echo "🔍 Verifying plotly installation..."
python -c "import plotly; print(f'✅ Plotly {plotly.__version__} installed successfully')" || {
    echo "⚠️ Installing plotly..."
    pip install plotly>=5.15.0
}

# Check if backend is running
echo "🔍 Checking if backend API is running..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend API is running"
else
    echo "⚠️  Backend API not detected. Make sure to start it with:"
    echo "   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    echo
fi

# Start Streamlit frontend
echo "🎨 Starting Streamlit frontend..."
echo "🌐 Frontend will be available at: http://localhost:8501"
echo

streamlit run app.py --server.port 8501 --server.address localhost