# ⚡ Azure Day 2 Engine - Python Edition

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF6B6B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Azure](https://img.shields.io/badge/Azure-Ready-0078D4?logo=microsoft-azure&logoColor=white)](https://azure.microsoft.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)

## 🎯 Purpose

A modular, extensible platform to perform governed Azure operations (starting/stopping clusters, database upgrades/backups, etc.) using **FastAPI** and **Python**, deployed as a microservice in Azure Kubernetes Service (AKS). The system enables rich, role-aware service automation with Azure Managed Identity integration and seamless integration with IDPs, AI agents, and third-party components.

**✨ Now featuring a professional Streamlit frontend for interactive demonstrations and client presentations!**

---

## 🧠 Solution Architecture

| Layer | Components |
|-------|------------|
| **Frontend Dashboard** | Streamlit web interface for interactive operations |
| **API Runtime** | FastAPI with Python 3.11 and automatic OpenAPI documentation |
| **Operations** | Service-based operations with lazy loading and enhanced error handling |
| **Authentication** | Azure Managed Identity + Service Principal with automatic CLI login |
| **Container Runtime** | Docker container ready for AKS deployment |
| **Database Integration** | Direct PostgreSQL connections with multi-query SQL execution |
| **Azure Integration** | Azure SDK + subprocess-based Azure CLI with JSON parsing |

---

## 🔌 Key Capabilities

### 🎨 **Frontend Dashboard**
- ✅ **Interactive Web Interface** with professional Azure-themed design
- 🎯 **Real-time Operations** with visual feedback and progress indicators
- 📊 **Structured Result Display** with success/error indicators and execution times
- 🔍 **Multi-query SQL Visualization** with pandas DataFrames and metadata
- 🔧 **Predefined CLI Commands** with custom command support

### 🚀 **Backend API Engine**
- ✅ **FastAPI-based REST API** with lazy-loaded services and comprehensive validation
- 🐳 **Containerized deployment** ready for AKS with health checks
- 🔐 **Enhanced Azure Authentication** with automatic service principal login
- 🔄 **AKS Operations**: Start/stop clusters, status monitoring, CLI integration
- 🐘 **Advanced PostgreSQL Operations**: Major upgrades, multi-query SQL execution, JSON serialization
- 🖥️ **Robust Azure CLI Integration** with subprocess execution and auto-authentication
- 📊 **Structured Logging** with audit trails and execution time tracking
- 🔧 **Production-Ready Error Handling** with comprehensive troubleshooting

---

## 🧠 Why This Matters

- 🛡️ **Secure by Design**: Azure Managed Identity, service principal authentication, no credential caching
- 🐍 **Python Ecosystem**: Rich Azure SDK integration with modern async/await patterns
- 🚀 **Cloud Native**: Kubernetes-ready with proper health checks and resource management
- 🔌 **Extensible Architecture**: Lazy loading, service-based design, easy to add new operations
- 🧠 **AI Ready**: RESTful APIs with structured responses perfect for AI agent integration
- 🎨 **Client Ready**: Professional frontend for demonstrations and stakeholder presentations

---

## 📜 Project Structure

```bash
azure-day2-engine-python/
├── 🎨 frontend/                    # Interactive Streamlit Dashboard
│   ├── app.py                     # Main dashboard application
│   ├── requirements.txt           # Frontend dependencies
│   ├── run_frontend.sh           # Quick start script
│   ├── README.md                 # Frontend documentation
│   └── .streamlit/
│       └── config.toml           # Streamlit configuration
├── 🚀 app/                        # Backend FastAPI Application
│   ├── api/v1/                   # API routes with lazy loading
│   │   ├── aks.py               # AKS operations (/AKS/v1/*)
│   │   └── pssql.py             # PostgreSQL operations (/PSSQL/v1/*)
│   ├── core/                     # Core functionality
│   │   ├── config.py            # Configuration management
│   │   └── azure_auth.py        # Enhanced Azure authentication
│   ├── services/                 # Business logic services
│   │   ├── aks_service.py       # AKS operations with error handling
│   │   └── postgresql_service.py # PostgreSQL with JSON serialization
│   ├── models/                   # Pydantic models
│   │   └── operations.py        # Request/response models + CLI models
│   ├── scripts/sql/              # SQL scripts for execution
│   │   ├── sample_health_check.sql   # Multi-query health monitoring
│   │   └── sample_backup_check.sql   # Backup verification queries
│   └── main.py                   # FastAPI application entry point
├── 🧪 test/                       # Authentication testing
│   ├── README.md                 # Testing documentation (Spanish)
│   ├── aks/test_auth.py         # AKS authentication validation
│   └── postgresql/test_auth.py  # PostgreSQL authentication validation
├── 🐳 .devcontainer/              # VS Code development environment
│   ├── devcontainer.json        # Complete dev environment
│   └── Dockerfile               # Development container
├── ☸️ kubernetes/                 # Kubernetes deployment
│   └── deployment.yaml          # Production AKS deployment
├── 📋 CLAUDE.md                   # Comprehensive development guide
├── 📦 requirements.txt            # Python dependencies
├── 🔧 run_dev.sh                 # Quick development setup
└── 🐋 Dockerfile                 # Production container
```

---

## 🚀 Quick Start Guide

### 🎨 **Option 1: Frontend Dashboard (Recommended for Demos)**

Perfect for client presentations and interactive testing:

```bash
# Clone and setup
git clone <your-repo>
cd azure-day2-engine-python

# Start backend API
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Start frontend dashboard (new terminal)
cd frontend
./run_frontend.sh
```

**Access Points:**
- 🎨 **Frontend Dashboard**: http://localhost:8501
- 📚 **API Documentation**: http://localhost:8000/docs
- ❤️ **Health Check**: http://localhost:8000/health

### 🐳 **Option 2: VS Code Devcontainer (Best for Development)**

Complete development environment with all tools:

1. **Prerequisites**: VS Code + Dev Containers extension + Docker Desktop

2. **Open in devcontainer**:
   ```bash
   git clone <your-repo>
   cd azure-day2-engine-python
   code .
   # Click "Reopen in Container"
   ```

3. **Configure Azure credentials**:
   ```bash
   cp .env.example .env
   # Edit .env with your Azure service principal credentials
   ```

4. **Start applications**:
   ```bash
   # Backend (terminal 1)
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   
   # Frontend (terminal 2)
   cd frontend && streamlit run app.py --server.port 8501
   ```

### 🖥️ **Option 3: Local Development**

Traditional local setup:

```bash
# Quick start
./run_dev.sh

# Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with credentials
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🎨 Frontend Dashboard Features

### **🚀 AKS Operations Tab**
- **Cluster Management**: Visual start/stop/status operations with real-time feedback
- **Predefined CLI Commands**: Common AKS operations with one-click execution
- **Custom Commands**: Execute any Azure CLI command with structured output
- **Execution Tracking**: View operation times and detailed results

### **🐘 PostgreSQL Operations Tab**
- **Server Management**: Comprehensive status display with configuration details
- **SQL Script Execution**: Multi-query scripts with tabular result visualization
  - `sample_health_check.sql`: Database version, size, connections, table counts
  - `sample_backup_check.sql`: Backup monitoring and verification
- **Result Visualization**: Pandas DataFrames with query metadata and row counts
- **Flexible Server Names**: Auto-handles both short names and FQDNs

### **🎯 Visual Features**
- **Success/Error Indicators**: Color-coded responses with detailed information
- **Loading Feedback**: Progress spinners for long-running operations
- **Raw Response Viewer**: Expandable JSON viewers for debugging
- **API Health Monitor**: Real-time backend connectivity status
- **Professional Styling**: Azure-themed design perfect for client presentations

---

## 🔧 Development & Testing

### **Authentication Testing**
Validate your Azure credentials before deployment:

```bash
# Test AKS authentication
export PYTHONPATH=$(pwd)
python test/aks/test_auth.py

# Test PostgreSQL authentication  
python test/postgresql/test_auth.py
```

### **VS Code Development Features**
- 🐍 **Python IntelliSense** with full type checking
- ⚡ **Auto-formatting** with Black and import sorting
- 🔍 **Linting** with Pylint and Flake8
- 🐛 **Debugging** with pre-configured FastAPI launch configs
- ☁️ **Azure CLI** integration and Kubernetes tools

### **API Testing Options**
- 🎨 **Frontend Dashboard**: Interactive testing with visual results
- 📚 **Swagger UI**: http://localhost:8000/docs - Complete API documentation
- 🔍 **ReDoc**: http://localhost:8000/redoc - Alternative API documentation
- 🧪 **Direct curl**: Command-line testing with structured JSON responses

---

## ☸️ Production Deployment

### **Container Build**
```bash
# Development container
docker build -f .devcontainer/Dockerfile -t azure-day2-engine:dev .

# Production container
docker build -t azure-day2-engine:latest .
docker run -p 8000:8000 --env-file .env azure-day2-engine:latest
```

### **Kubernetes Deployment**
```bash
# Configure Azure credentials
export AZURE_CLIENT_ID="your-client-id"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_SUBSCRIPTION_ID="your-subscription-id"

# Deploy to AKS
envsubst < kubernetes/deployment.yaml | kubectl apply -f -
```

---

## 🛠️ Advanced Features

### **Enhanced SQL Execution**
- **Multi-Statement Support**: Executes multiple queries and captures all results
- **JSON Serialization**: Automatic conversion of PostgreSQL types (datetime, decimal)
- **Parameter Substitution**: Dynamic script parameters with `${parameter_name}` syntax
- **Structured Metadata**: Query numbers, execution times, row counts

### **Robust Azure CLI Integration**
- **Subprocess-Based**: Reliable command execution independent of Python CLI integration
- **Auto-Authentication**: Automatic service principal login for CLI commands
- **JSON Parsing**: Intelligent parsing of command outputs with fallback to raw text
- **Clean Config Management**: Isolated credential directories prevent token conflicts

### **Production-Ready Error Handling**
- **Lazy Loading**: Services instantiated only when needed to prevent startup failures
- **Comprehensive Logging**: Structured logging with correlation IDs and execution tracking
- **Graceful Degradation**: Clear error messages and troubleshooting guidance
- **Type Safety**: Full Pydantic validation for all API endpoints

---

## 📋 Demo Flow for Client Presentations

### **Professional Demonstration Sequence**

1. **🔍 System Health Check**
   - Show API connectivity in frontend sidebar
   - Demonstrate real-time status monitoring

2. **🚀 AKS Operations Demo**
   - Execute cluster status retrieval with timing
   - Run Azure CLI commands showing structured output
   - Highlight error handling and logging

3. **🐘 PostgreSQL Operations Demo**  
   - Display server configuration and status
   - Execute health check script showing multi-query results
   - Demonstrate backup listing with CLI integration

4. **🎯 Key Feature Highlights**
   - Real-time execution times and performance metrics
   - Structured data visualization and error handling
   - Professional UI suitable for stakeholder presentations
   - Comprehensive logging and audit trails

---

## 🔐 Security & Configuration

### **Azure Authentication**
- **DefaultAzureCredential**: Automatic credential chain (Managed Identity → Service Principal → Azure CLI)
- **Service Principal**: Production authentication with client secret
- **Environment Variables**: Secure configuration via Kubernetes secrets

### **Required Environment Variables**
```bash
AZURE_CLIENT_ID=your-app-registration-client-id
AZURE_TENANT_ID=your-azure-tenant-id  
AZURE_CLIENT_SECRET=your-client-secret
AZURE_SUBSCRIPTION_ID=your-subscription-id
```

### **Security Best Practices**
- 🔒 **No Credential Caching**: Clean config directories prevent stale tokens
- 🛡️ **Input Validation**: Full Pydantic model validation for all inputs
- 🔐 **SQL Injection Prevention**: Parameterized queries and safe substitution
- 📊 **Audit Logging**: Comprehensive operation logging with structured data

---

## 🆘 Troubleshooting

### **Common Issues & Solutions**

| Issue | Cause | Solution |
|-------|--------|----------|
| "TypeError: Load failed" | Missing Azure credentials | Set environment variables, restart server |
| "Object not JSON serializable" | PostgreSQL datetime types | Automatic handling via `serialize_value()` |  
| "Refresh token expired" | Azure CLI cached credentials | Automatic service principal login |
| "Host name could not be translated" | Server name format | Auto-handles both short and FQDN formats |
| "API not reachable" | Backend not running | Start FastAPI server on port 8000 |

### **Debug Resources**
- 📋 **Authentication Tests**: Validate credentials before deployment
- 🔍 **Structured Logging**: Detailed error information with correlation IDs
- 🎨 **Frontend Raw Responses**: JSON viewers for API debugging
- 📚 **Comprehensive Documentation**: Step-by-step troubleshooting in CLAUDE.md

---

## 📚 Documentation

- 📋 **[CLAUDE.md](CLAUDE.md)**: Comprehensive development guide with architecture details
- 🎨 **[Frontend README](frontend/README.md)**: Complete frontend documentation and usage guide
- 🧪 **[Test Documentation](test/README.md)**: Authentication testing guide (Spanish)
- 📚 **API Documentation**: Auto-generated Swagger UI at `/docs`

---

## 🤝 Contributing

1. **Development Setup**: Use VS Code devcontainer for consistent environment
2. **Code Quality**: Black formatting, isort imports, Pylint linting enforced
3. **Testing**: Run authentication tests before deployment
4. **Documentation**: Update CLAUDE.md with new features and capabilities

---

## 📈 What's New

### **Recent Enhancements**
- ✨ **Professional Frontend Dashboard** with Streamlit
- 🔧 **Lazy Loading Services** preventing startup failures  
- 📊 **Multi-Query SQL Execution** with structured results
- 🔐 **Enhanced Azure CLI Integration** with auto-authentication
- 🎨 **JSON Serialization** for PostgreSQL complex types
- 📱 **Responsive Design** suitable for client presentations
- 🛡️ **Production-Ready Error Handling** with comprehensive logging

The Azure Day 2 Engine is now a complete, production-ready platform with both powerful backend capabilities and an intuitive frontend interface perfect for demonstrations, development, and client presentations!

---

**Built with ❤️ for Azure automation and operational excellence**