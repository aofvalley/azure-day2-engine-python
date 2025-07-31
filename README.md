# 🔐 Azure Day 2 Engine

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF6B6B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Azure](https://img.shields.io/badge/Azure-Ready-0078D4?logo=microsoft-azure&logoColor=white)](https://azure.microsoft.com)
[![Security](https://img.shields.io/badge/Security-JWT+Auth-red?logo=shield&logoColor=white)](https://jwt.io)

## 🎯 Overview

**Enterprise-grade secure platform** for governed Azure operations with **JWT authentication**, **protected API endpoints**, and **production-ready deployment**. Built with FastAPI and Python, featuring a secure web dashboard for interactive operations.

**🔐 Security-first design with login protection and authenticated API access**

---

## 🏗️ Architecture

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Streamlit + Auth | **Secure dashboard** with login protection |
| **API** | FastAPI + JWT | **Protected REST endpoints** with OpenAPI docs |
| **Security** | JWT + SHA256 | **Authentication middleware** for all operations |
| **Services** | Python | Lazy-loaded Azure operations with error handling |
| **Azure Auth** | Azure SDK | Managed Identity + Service Principal |
| **Database** | PostgreSQL | Direct connections with multi-query execution |
| **Deployment** | Helm/AKS | **Production-ready** with LoadBalancer services |

---

## ✨ Features

### 🔐 **Security Features**
- **🛡️ Protected Frontend**: Login screen prevents unauthorized access
- **🔑 JWT Authentication**: Secure API access with token-based auth
- **🚫 Protected Endpoints**: All operations require authentication (except `/health`, `/docs`)
- **⚙️ Configurable Credentials**: Environment-based auth configuration
- **🔒 Session Management**: Secure logout and token expiration

### 🎨 **Frontend Dashboard**
- **🔐 Secure access** with login protection and session management
- Interactive web interface with professional design
- Real-time operations with visual feedback and execution timing
- Structured result display with success/error indicators
- Multi-query SQL visualization with tabular data presentation

### 🚀 **Backend Engine**
- **🔐 JWT-protected** REST API with comprehensive validation
- **AKS Operations**: Start/stop clusters, status monitoring, CLI integration
- **PostgreSQL Operations**: Server management, multi-query SQL execution, JSON serialization
- Azure CLI integration with subprocess execution and auto-authentication
- Lazy-loaded services preventing startup failures
- Structured logging with audit trails and execution tracking

---

## 📁 Project Structure

```
azure-day2-engine-python/
├── frontend/                    # Secure Streamlit Dashboard
│   ├── app.py                  # Main dashboard with auth
│   ├── auth.py                 # Authentication module
│   ├── requirements.txt        # Frontend dependencies
│   └── run_frontend.sh         # Quick start script
├── app/                        # JWT-Protected FastAPI
│   ├── api/v1/                 # API routes
│   │   ├── aks.py             # AKS operations (protected)
│   │   ├── pssql.py           # PostgreSQL operations (protected)
│   │   └── auth.py            # Authentication endpoints
│   ├── core/                  # Core functionality
│   │   ├── auth.py            # JWT authentication middleware
│   │   ├── config.py          # Configuration
│   │   └── azure_auth.py      # Azure authentication
│   ├── services/              # Business logic
│   ├── models/                # Request/response models
│   ├── scripts/sql/           # SQL scripts
│   └── main.py               # App entry point
├── helm-chart/                # Production Helm deployment
│   ├── templates/             # Kubernetes manifests
│   └── values.yaml           # Configuration values
├── scripts/                   # Deployment & testing
│   ├── deploy-with-security.sh  # Complete deployment
│   └── test-security.sh       # Security validation
├── test/                      # Authentication tests
├── requirements.txt           # Dependencies
└── Dockerfile                # Container config
```

---

## 🚀 Production Deployment Guide

### **Prerequisites**
- Azure CLI configured (`az login`)
- AKS cluster access (`kubectl cluster-info`)
- Docker with buildx support
- Helm v3 installed

### **Step 1: Environment Setup**
```bash
# Interactive setup (recommended)
./scripts/setup-env.sh

# Or manually configure .env
cp .env.example .env
# Edit .env with your Azure credentials
```

### **Step 2: Deploy with Security**
```bash
# Complete secure deployment to AKS
./scripts/deploy-with-security.sh
```

**This script will:**
- ✅ Build and push multi-architecture Docker images to ACR
- ✅ Generate secure JWT secrets and authentication credentials
- ✅ Deploy backend and frontend as LoadBalancer services
- ✅ Configure authentication and protect all API endpoints
- ✅ Validate security implementation and provide access URLs

### **Step 3: Access Your Deployment**

After successful deployment, you'll get:

**🎨 Frontend Dashboard**: `http://<FRONTEND-IP>`
- **Login Required**: Username: `admin`, Password: `azure-day2-engine-2025`
- Secure dashboard with authentication protection

**📚 Backend API**: `http://<BACKEND-IP>`
- **Public**: `/health`, `/docs`, `/redoc` (documentation)
- **Protected**: All AKS and PostgreSQL operations (require JWT token)

### **Step 4: Verify Security**
```bash
# Test authentication and security features
./scripts/test-security.sh
```

---

## 🔧 Local Development

### **Quick Local Setup**
```bash
# 1. Setup environment
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Configure Azure credentials

# 2. Start backend API
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Start frontend (new terminal)
cd frontend && ./run_frontend.sh
```

**Local Access:**
- 🔐 **Dashboard**: http://localhost:8501 (login required)
- 📚 **API Docs**: http://localhost:8000/docs
- ❤️ **Health**: http://localhost:8000/health

### **VS Code DevContainer**
1. Open in VS Code → "Reopen in Container"
2. All dependencies and tools pre-configured
3. Start services as above

---

## 🎛️ Security Features

### **🔐 Authentication**
- **Frontend**: Login screen protects all dashboard access
- **Backend**: JWT tokens required for all operations
- **Credentials**: Configurable via environment variables
- **Session**: Secure logout and token expiration (24h default)

### **🛡️ Protected Endpoints**
```bash
# Public endpoints (no auth required)
GET /health              # Health check
GET /docs               # API documentation  
GET /redoc              # Alternative API docs

# Authentication endpoints
POST /auth/login        # Get JWT token
GET /auth/me           # Current user info
POST /auth/logout      # Logout user

# Protected endpoints (JWT required)
POST /AKS/v1/*         # All AKS operations
POST /PSSQL/v1/*       # All PostgreSQL operations
```

---

## 🔐 Configuration

### **Required Environment Variables**
```bash
# Azure Credentials
AZURE_CLIENT_ID=your-app-registration-client-id
AZURE_TENANT_ID=your-azure-tenant-id  
AZURE_CLIENT_SECRET=your-client-secret
AZURE_SUBSCRIPTION_ID=your-subscription-id

# Authentication (optional, auto-generated if not set)
AUTH_USERNAME=admin
AUTH_PASSWORD=azure-day2-engine-2025
AUTH_SECRET_KEY=auto-generated-jwt-secret

# Deployment Configuration
ACR_NAME=your-container-registry
AKS_CLUSTER=your-aks-cluster-name
AKS_RESOURCE_GROUP=your-resource-group
```

### **Security Configuration**
- **JWT Authentication**: Tokens expire in 24 hours (configurable)
- **Password Hashing**: SHA-256 for credential storage
- **DefaultAzureCredential**: Managed Identity → Service Principal → Azure CLI
- **Environment Isolation**: Separate credentials per environment

---

## 🆘 Troubleshooting

### **Quick Diagnostic**
```bash
# Test security and deployment
./scripts/test-security.sh

# Interactive troubleshooting tool
./scripts/troubleshoot-deployment.sh

# Check deployment status
kubectl get pods,svc -l app=azure-day2-engine

# View logs
kubectl logs -f -l component=backend
kubectl logs -f -l component=frontend
```

### **Common Issues**

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Login Failed** | Cannot access frontend | Check auth credentials in Kubernetes secret |
| **API 401 Errors** | Authentication failed | Verify JWT token and login again |
| **ImagePullBackOff** | Pods can't pull images | Use `./scripts/build-and-push.sh` with correct architecture |
| **LoadBalancer Pending** | No external IP | Check AKS LoadBalancer service limits |
| **Health Check Failed** | Pods not ready | Verify `/health` endpoint and check logs |

### **Security Troubleshooting**
```bash
# Check authentication secrets
kubectl get secret auth-credentials -o yaml

# Test API authentication
curl -X POST http://<BACKEND-IP>/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"azure-day2-engine-2025"}'

# Verify protected endpoints
curl -H "Authorization: Bearer <TOKEN>" \
  http://<BACKEND-IP>/auth/me
```

---

## 📚 Resources

### **Documentation**
- **API Documentation**: `http://<BACKEND-IP>/docs` - Interactive Swagger UI
- **Alternative Docs**: `http://<BACKEND-IP>/redoc` - ReDoc interface
- **Health Check**: `http://<BACKEND-IP>/health` - Service status

### **Testing & Validation**
- **Security Tests**: `./scripts/test-security.sh` - Comprehensive security validation
- **Auth Tests**: `test/` directory - Azure credential validation scripts
- **Troubleshooting**: `./scripts/troubleshoot-deployment.sh` - Interactive diagnostic tool

### **Deployment Scripts**
- **Complete Deployment**: `./scripts/deploy-with-security.sh` - Full production deployment
- **Environment Setup**: `./scripts/setup-env.sh` - Interactive configuration
- **Build & Push**: `./scripts/build-and-push.sh` - Multi-architecture container builds

---

## 🏆 Production Ready Features

✅ **Enterprise Security** - JWT authentication, protected endpoints, secure sessions  
✅ **Production Deployment** - Helm charts, LoadBalancer services, automatic scaling  
✅ **Comprehensive Testing** - Security validation, health checks, authentication tests  
✅ **Operational Excellence** - Structured logging, health monitoring, error handling  
✅ **Azure Integration** - Managed Identity, Service Principal, CLI automation  
✅ **Professional UI** - Secure dashboard, real-time operations, interactive testing  

---

**🔐 Built for secure Azure automation and operational excellence** 🚀
