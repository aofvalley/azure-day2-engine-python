# Azure Day 2 Engine - Development Environment Guide

## Quick Start

To run the complete Azure Day 2 Engine development environment, simply execute:

```bash
./run_dev.sh
```

This single command will:

1. **Environment Setup**
   - Create Python virtual environment if it doesn't exist
   - Install all backend dependencies from `requirements.txt`
   - Install all frontend dependencies from `frontend/requirements.txt`
   - Create `.env` file from template if it doesn't exist

2. **Service Startup**
   - Start FastAPI backend server on `http://localhost:8000`
   - Start Streamlit frontend dashboard on `http://localhost:8501`
   - Automatically open browser windows (on macOS)

3. **Process Management**
   - Monitor both services for unexpected failures
   - Clean shutdown with Ctrl+C
   - Automatic port cleanup if ports are already in use

## Available Services

Once running, you can access:

- **🔗 API Backend**: http://localhost:8000
- **📖 API Documentation**: http://localhost:8000/docs
- **🎨 Frontend Dashboard**: http://localhost:8501
- **❤️ Health Check**: http://localhost:8000/health

## Development Features

- **Hot Reload**: Both services support automatic reloading when code changes
- **Error Handling**: Robust process management with automatic cleanup
- **Port Management**: Automatic detection and cleanup of busy ports
- **Cross-Platform**: Works on macOS, Linux, and Windows (with WSL)

## Stopping the Services

Press `Ctrl+C` to gracefully stop both services. The script will:
- Terminate backend and frontend processes
- Clean up any remaining child processes
- Show confirmation of successful shutdown

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - The script automatically detects and frees busy ports
   - If issues persist, manually check: `lsof -i:8000` and `lsof -i:8501`

2. **Missing Dependencies**
   - The script automatically installs missing packages
   - For manual installation: `pip install -r requirements.txt`

3. **Virtual Environment Issues**
   - Delete `venv` folder and run the script again
   - Ensure Python 3.8+ is installed

4. **Azure Credentials**
   - Edit `.env` file with your Azure credentials
   - Basic functionality works without Azure credentials

### Environment Variables

Edit `.env` file to configure:
- Azure credentials (AZURE_TENANT_ID, AZURE_CLIENT_ID, etc.)
- Debug settings
- PostgreSQL configuration

## Script Features

The `run_dev.sh` script includes:

✅ **Automatic Environment Setup**
✅ **Dependency Management**
✅ **Process Monitoring**
✅ **Graceful Shutdown**
✅ **Port Conflict Resolution**
✅ **Error Recovery**
✅ **Cross-Platform Compatibility**
✅ **Browser Auto-Open (macOS)**

## Manual Alternative

If you prefer to run services separately:

```bash
# Terminal 1 - Backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
source venv/bin/activate
cd frontend
streamlit run app.py --server.port 8501
```

## Development Tips

- Use the API documentation at `/docs` for testing endpoints
- The frontend provides a user-friendly interface for Azure operations
- Both services support hot-reload for rapid development
- Check the terminal output for detailed startup information and any errors
