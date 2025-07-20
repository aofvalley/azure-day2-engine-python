
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
azure-day2-engine/
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
├── .devcontainer/              # VS Code devcontainer config
│   ├── devcontainer.json      # Devcontainer configuration
│   └── Dockerfile             # Development container
├── .vscode/                    # VS Code settings
│   ├── launch.json            # Debug configurations
│   └── settings.json          # Editor settings
├── kubernetes/                 # Kubernetes manifests
│   └── deployment.yaml        # Complete AKS deployment config
├── tests/                     # Test files
├── Dockerfile                 # Production container configuration
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # Project documentation
```

---

## 🚀 Quick Start

### 🐳 VS Code Devcontainer (Recommended)

The fastest way to get started is using the pre-configured devcontainer:

1. **Prerequisites**:
   - Install [VS Code](https://code.visualstudio.com/)
   - Install [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
   - Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)

2. **Open in devcontainer**:
   ```bash
   git clone <your-repo>
   cd azure-day2-engine
   code .
   ```
   - Click "Reopen in Container" when prompted
   - Wait for container to build (includes Python, Azure CLI, and all extensions)

3. **Configure Azure credentials**:
   ```bash
   cp .env.example .env
   # Edit .env with your Azure credentials
   ```

4. **Start the application**:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access the application**:
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

### 🖥️ Local Development (Alternative)

If you prefer local development without containers:

1. **Quick start script**:
   ```bash
   ./run_dev.sh
   ```

2. **Manual setup**:
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Configure environment
   cp .env.example .env
   # Edit .env with your Azure credentials
   
   # Run application
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### 🐋 Container Development

Build and run in a container:

```bash
# Build the image
docker build -t azure-day2-engine:latest .

# Run with environment file
docker run -p 8000:8000 --env-file .env azure-day2-engine:latest
```

### ☸️ Kubernetes Deployment

Deploy to Azure Kubernetes Service:

```bash
# Build and tag for your registry
docker build -t your-registry/azure-day2-engine:latest .
docker push your-registry/azure-day2-engine:latest

# Configure Azure credentials
export AZURE_CLIENT_ID="your-client-id"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_SUBSCRIPTION_ID="your-subscription-id"

# Create base64 encoded secrets
export AZURE_CLIENT_ID_B64=$(echo -n $AZURE_CLIENT_ID | base64)
export AZURE_TENANT_ID_B64=$(echo -n $AZURE_TENANT_ID | base64)
export AZURE_SUBSCRIPTION_ID_B64=$(echo -n $AZURE_SUBSCRIPTION_ID | base64)

# Deploy to Kubernetes
envsubst < kubernetes/deployment.yaml | kubectl apply -f -
```

## 🔧 Development Tools

### VS Code Features (in devcontainer)
- **Python IntelliSense** with type checking
- **Auto-formatting** with Black
- **Import sorting** with isort
- **Linting** with Pylint and Flake8
- **Debugging** with pre-configured launch configurations
- **Azure CLI** integration
- **Kubernetes** tools and YAML support

### Available Scripts
- `./run_dev.sh` - Quick development environment setup
- **Debug configurations** in VS Code for FastAPI debugging
- **Integrated terminal** with all tools pre-installed

## 🌐 API Access

Once running, access these endpoints:

- **📚 API Documentation (Swagger)**: http://localhost:8000/docs
- **🔍 Alternative API Docs (ReDoc)**: http://localhost:8000/redoc
- **❤️ Health Check**: http://localhost:8000/health
- **📊 OpenAPI Schema**: http://localhost:8000/openapi.json