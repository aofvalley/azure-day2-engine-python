#!/bin/bash

# Azure Day 2 Engine - Development Startup Script

echo "🚀 Starting Azure Day 2 Engine Development Environment"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your Azure credentials before running the application"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if Azure CLI is available
if ! command -v az &> /dev/null; then
    echo "⚠️  Azure CLI not found. Please install Azure CLI or use the devcontainer."
    echo "   Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
fi

echo "✅ Environment ready!"
echo "🌐 Starting FastAPI development server..."
echo "📖 API Documentation will be available at: http://localhost:8000/docs"
echo "❤️  Health Check will be available at: http://localhost:8000/health"
echo ""

# Start the development server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload