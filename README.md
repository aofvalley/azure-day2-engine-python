
# 🧾 Azure Day 2 Engine - Python Edition

## 🎯 Purpose

Create a modular, extensible platform to perform governed Azure operations (e.g. starting/stopping clusters, upgrade/backup databases, etc...) using **FastAPI** and **Python**, deployed as a microservice in Azure Kubernetes Service (AKS). The system enables rich, role-aware service automation with Azure Managed Identity integration and seamless integration with IDPs, Generative AI agents and third party components.

---

## 🧠 Solution Architecture

| Layer | Components |
|-------|------------|
| **API Runtime** | FastAPI with Python 3.11 |
| **Operations** | Service-based operations for AKS and PostgreSQL |
| **Authentication** | Azure Managed Identity + Service Principal |
| **Container Runtime** | Docker container deployed in AKS |
| **Database Integration** | Direct PostgreSQL connection + SQL script execution |
| **Azure Integration** | Azure SDK + Azure CLI command execution |

---

## 🔌 Key Capabilities

- ✅ **FastAPI-based REST API** with automatic OpenAPI documentation
- 🐳 **Containerized deployment** ready for AKS with health checks
- 🔐 **Azure Managed Identity** authentication for secure resource access
- 🔄 **AKS Operations**: Start/stop clusters, status monitoring
- 🐘 **PostgreSQL Operations**: Major upgrades, custom SQL script execution
- 🖥️ **Azure CLI Integration** for advanced operations
- 📊 **Structured Logging** with audit trails and monitoring
- 🔧 **Dynamic Configuration** for multiple environments

---

## 🧠 Why This Matters

- 🛡️ **Secure by Design**: Uses Azure Managed Identity, no hardcoded credentials
- 🐍 **Python Ecosystem**: Leverages rich Python libraries and Azure SDK
- 🚀 **Cloud Native**: Designed for Kubernetes with proper health checks
- 🔌 **Extensible**: Easy to add new Azure services and operations
- 🧠 **AI Ready**: RESTful APIs perfect for AI agent integration

---

## 📜 Project Structure

```bash
azure-day2-engine-python/
├── app/
│   ├── api/v1/                 # API routes
│   │   ├── aks.py             # AKS operations (/AKS/v1/*)
│   │   └── pssql.py           # PostgreSQL operations (/PSSQL/v1/*)
│   ├── core/                   # Core functionality
│   │   ├── config.py          # Configuration management
│   │   └── azure_auth.py      # Azure authentication
│   ├── services/               # Business logic
│   │   ├── aks_service.py     # AKS operations service
│   │   └── postgresql_service.py # PostgreSQL operations service
│   ├── models/                 # Pydantic models
│   │   └── operations.py      # Request/response models
│   ├── scripts/sql/            # SQL scripts for execution
│   └── main.py                # FastAPI application
├── kubernetes/                 # Kubernetes manifests
│   └── deployment.yaml        # Complete AKS deployment config
├── tests/                     # Test files
├── Dockerfile                 # Container configuration
├── requirements.txt           # Python dependencies
└── README.md                  # Detailed documentation
```

---

## 🚀 Quick Start

### Local Development
```bash
cd azure-day2-engine-python
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Kubernetes Deployment
```bash
docker build -t azure-day2-engine:latest .
kubectl apply -f kubernetes/deployment.yaml
```

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health