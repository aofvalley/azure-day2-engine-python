# ⚡ Azure Day 2 Engine

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF6B6B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Azure](https://img.shields.io/badge/Azure-Ready-0078D4?logo=microsoft-azure&logoColor=white)](https://azure.microsoft.com)

## 🎯 Overview

A production-ready platform for governed Azure operations (AKS cluster management, PostgreSQL operations, etc.) built with **FastAPI** and **Python**. Features a professional web dashboard for interactive demonstrations and automated operations.

**🎨 Professional frontend dashboard with real-time operations and structured data visualization**

---

## 🏗️ Architecture

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Streamlit | Interactive dashboard with real-time operations |
| **API** | FastAPI | REST endpoints with OpenAPI documentation |
| **Services** | Python | Lazy-loaded Azure operations with error handling |
| **Authentication** | Azure SDK | Managed Identity + Service Principal |
| **Database** | PostgreSQL | Direct connections with multi-query execution |
| **Deployment** | Docker/K8s | Container-ready for AKS deployment |

---

## ✨ Features

### 🎨 **Frontend Dashboard**
- Interactive web interface with professional design
- Real-time operations with visual feedback and execution timing
- Structured result display with success/error indicators
- Multi-query SQL visualization with tabular data presentation
- Predefined and custom Azure CLI command execution

### 🚀 **Backend Engine**
- FastAPI REST API with comprehensive validation and OpenAPI docs
- **AKS Operations**: Start/stop clusters, status monitoring, CLI integration
- **PostgreSQL Operations**: Server management, multi-query SQL execution, JSON serialization
- Azure CLI integration with subprocess execution and auto-authentication
- Lazy-loaded services preventing startup failures
- Structured logging with audit trails and execution tracking

---

## 📁 Project Structure

```
azure-day2-engine-python/
├── frontend/                    # Streamlit Dashboard
│   ├── app.py                  # Main dashboard
│   ├── requirements.txt        # Frontend dependencies
│   └── run_frontend.sh         # Quick start script
├── app/                        # FastAPI Application
│   ├── api/v1/                 # API routes
│   │   ├── aks.py             # AKS operations
│   │   └── pssql.py           # PostgreSQL operations
│   ├── core/                  # Core functionality
│   │   ├── config.py          # Configuration
│   │   └── azure_auth.py      # Azure authentication
│   ├── services/              # Business logic
│   ├── models/                # Request/response models
│   ├── scripts/sql/           # SQL scripts
│   └── main.py               # App entry point
├── test/                      # Authentication tests
├── kubernetes/                # K8s deployment
├── requirements.txt           # Dependencies
└── Dockerfile                # Container config
```

---

## 🚀 Quick Start

### 🎨 **Frontend Dashboard** (Recommended)

```bash
# 1. Start backend API
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 2. Start frontend (new terminal)
cd frontend && ./run_frontend.sh
```

**Access:**
- 🎨 **Dashboard**: http://localhost:8501
- 📚 **API Docs**: http://localhost:8000/docs
- ❤️ **Health**: http://localhost:8000/health

### 🐳 **VS Code DevContainer**

1. Open in VS Code → "Reopen in Container"
2. Configure `.env` with Azure credentials
3. Start backend and frontend as above

### 🖥️ **Local Setup**

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Configure Azure credentials
python -m uvicorn app.main:app --reload
```

---

## 🎛️ Dashboard Features

### 🚀 **AKS Operations**
- Cluster start/stop/status with real-time feedback
- Predefined and custom Azure CLI commands
- Structured output with execution timing

### 🐘 **PostgreSQL Operations**
- Server status and configuration display
- Multi-query SQL script execution with tabular results
- Health checks and backup monitoring scripts

### 🎯 **Interface**
- Color-coded success/error indicators
- Progress spinners for long operations
- Expandable JSON response viewers
- Real-time API health monitoring

---

## 🔧 Development

### **Authentication Testing**
```bash
# Validate Azure credentials
export PYTHONPATH=$(pwd)
python test/aks/test_auth.py
python test/postgresql/test_auth.py
```

### **API Testing**
- 🎨 **Dashboard**: Interactive testing with visual results
- 📚 **Swagger**: http://localhost:8000/docs
- 🔍 **ReDoc**: http://localhost:8000/redoc

---

## 🐳 Deployment

### **Docker**
```bash
# Build and run
docker build -t azure-day2-engine .
docker run -p 8000:8000 --env-file .env azure-day2-engine
```

### **Kubernetes**
```bash
# Set environment variables and deploy
export AZURE_CLIENT_ID="your-client-id"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
envsubst < kubernetes/deployment.yaml | kubectl apply -f -
```

---

## 🔐 Configuration

### **Required Environment Variables**
```bash
AZURE_CLIENT_ID=your-app-registration-client-id
AZURE_TENANT_ID=your-azure-tenant-id  
AZURE_CLIENT_SECRET=your-client-secret
AZURE_SUBSCRIPTION_ID=your-subscription-id
```

### **Authentication**
- DefaultAzureCredential chain (Managed Identity → Service Principal → Azure CLI)
- Automatic service principal login for CLI operations
- Secure credential isolation and validation

---

## 🆘 Troubleshooting

### **Quick Diagnostic**
```bash
# Run interactive troubleshooting tool
./scripts/troubleshoot-deployment.sh

# Check pod status
kubectl get pods -o wide

# View logs
kubectl logs -f -l component=backend
```

### **Common Issues**

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **ImagePullBackOff** | Pods can't pull images | Images built for wrong architecture → Use troubleshoot script option 5 |
| **CrashLoopBackOff** | Missing dependencies | Fixed in latest requirements.txt → Rebuild images |
| **Authentication** | Azure CLI errors | Clear cache: `rm -rf ~/.azure/msal_*` → `az login` |
| **Health Checks** | Pods not ready | Check `/health` endpoint → Review logs |

### **Architecture Notes**
- 🍎 **Mac Users**: Images auto-built for AMD64 (AKS compatibility)
- 🐳 **Docker**: Use `--platform linux/amd64` for AKS deployment
- ☁️ **AKS**: Nodes run AMD64, ensure image compatibility

**📋 Full troubleshooting guide**: See `TROUBLESHOOTING.md`

---

## 📚 Resources

- **API Documentation**: `/docs` endpoint with Swagger UI
- **Authentication Tests**: `test/` directory with validation scripts
- **Development Guide**: Comprehensive setup and configuration documentation

---

**Built for Azure automation and operational excellence** 🚀