# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Azure Day 2 Engine is a modular, extensible **Python FastAPI** platform for performing governed Azure operations (starting/stopping clusters, database upgrades/backups, etc.) deployed as a microservice in Azure Kubernetes Service (AKS). The system enables role-aware service automation with Azure Managed Identity integration and seamless integration with IDPs, AI agents, and third-party components.

## Architecture

The system follows a service-based FastAPI architecture:

- **API Runtime**: FastAPI with Python 3.11 running in Docker container
- **Authentication**: Azure Managed Identity + Service Principal for secure access
- **Operations**: Service-based operations for AKS and PostgreSQL resources
- **Container Deployment**: Kubernetes deployment with health checks and monitoring
- **Database Integration**: Direct PostgreSQL connections with custom SQL script execution
- **Azure Integration**: Azure SDK + Azure CLI command execution capabilities

## Core Components

### FastAPI Application (app/main.py)
Main application entry point with:
- Route registration for AKS and PostgreSQL operations
- CORS middleware configuration
- Health check endpoints
- API documentation generation

### Services Layer
- **AKSService** (`app/services/aks_service.py`): AKS cluster operations
- **PostgreSQLService** (`app/services/postgresql_service.py`): PostgreSQL server operations

### API Routes
- **AKS Routes** (`app/api/v1/aks.py`): `/AKS/v1/*` endpoints
- **PostgreSQL Routes** (`app/api/v1/pssql.py`): `/PSSQL/v1/*` endpoints

### Azure Authentication (app/core/azure_auth.py)
- Managed Identity credential management
- Azure SDK client initialization
- Azure CLI command execution wrapper

## Development Commands

### VS Code Devcontainer Development (Recommended)

The project includes a complete devcontainer setup for optimal development experience:

**Quick Start:**
```bash
# Open in VS Code and select "Reopen in Container"
# All dependencies and tools are automatically configured

# Start the application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Features included in devcontainer:**
- Python 3.11 with FastAPI development stack
- Azure CLI pre-installed and configured
- VS Code extensions: Python, Azure, Kubernetes, YAML
- Debugging configurations for FastAPI
- Auto-formatting with Black and import sorting with isort
- Linting with Pylint and Flake8
- Docker-in-docker support for container operations

### Local Development (Alternative)

**Using the development script:**
```bash
./run_dev.sh
```

**Manual setup:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Copy environment template
cp .env.example .env
# Edit .env with your Azure credentials

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Container Build and Run
```bash
# Development container
docker build -f .devcontainer/Dockerfile -t azure-day2-engine:dev .

# Production container
docker build -t azure-day2-engine:latest .
docker run -p 8000:8000 --env-file .env azure-day2-engine:latest
```

### Kubernetes Deployment
```bash
# Configure Azure credentials as environment variables
export AZURE_CLIENT_ID="your-client-id"
export AZURE_TENANT_ID="your-tenant-id" 
export AZURE_SUBSCRIPTION_ID="your-subscription-id"

# Deploy with environment substitution
envsubst < kubernetes/deployment.yaml | kubectl apply -f -
```

### Dependencies
- Python 3.11
- FastAPI and Uvicorn
- Azure SDK libraries (azure-identity, azure-mgmt-*)
- Azure CLI
- PostgreSQL client (psycopg2)

### Development Tools
- **VS Code Devcontainer**: Complete development environment with pre-configured tools
- **run_dev.sh**: Quick setup script for local development
- **Debug Configurations**: Pre-configured launch.json for FastAPI debugging
- **Code Quality Tools**: Black, isort, Pylint, Flake8 for code formatting and linting
- **Azure Integration**: Azure CLI and Azure extensions for VS Code

## API Endpoints

### AKS Operations (`/AKS/v1/`)
- `POST /AKS/v1/start` - Start AKS cluster
- `POST /AKS/v1/stop` - Stop AKS cluster  
- `GET /AKS/v1/status/{resource_group}/{cluster_name}` - Get cluster status
- `POST /AKS/v1/cli` - Execute Azure CLI commands

### PostgreSQL Operations (`/PSSQL/v1/`)
- `POST /PSSQL/v1/upgrade` - Perform major version upgrade
- `GET /PSSQL/v1/status/{resource_group}/{server_name}` - Get server status
- `POST /PSSQL/v1/execute-script` - Execute custom SQL scripts
- `POST /PSSQL/v1/cli` - Execute Azure CLI commands

## Adding New Operations

1. Create new service class in `app/services/` following existing patterns
2. Add new API routes in `app/api/v1/` with appropriate request/response models  
3. Register new router in `app/main.py`
4. Update Pydantic models in `app/models/operations.py` if needed
5. Add appropriate error handling and logging
6. Test using the VS Code debugging configurations or development server

## Testing and Debugging

### Using VS Code Devcontainer
- **FastAPI Debug**: Use the pre-configured debug launch configuration
- **Breakpoint Debugging**: Set breakpoints in VS Code and debug interactively
- **Hot Reload**: Development server automatically reloads on code changes
- **Integrated Testing**: Run tests directly in the integrated terminal

### API Testing
- **Swagger UI**: http://localhost:8000/docs - Interactive API documentation  
- **Health Check**: http://localhost:8000/health - Application health status
- **ReDoc**: http://localhost:8000/redoc - Alternative API documentation

### Development Workflow
1. Open project in VS Code devcontainer
2. Configure `.env` file with Azure credentials
3. Start application with debug configuration or terminal
4. Use Swagger UI for interactive API testing
5. Set breakpoints and debug as needed

## Security Model

- **Azure Managed Identity**: Automatic authentication when deployed in AKS
- **Service Principal**: Fallback authentication for local development
- **Environment Variables**: Secure configuration via Kubernetes secrets
- **Database Authentication**: Username/password for PostgreSQL connections
- **Network Security**: Kubernetes network policies and service mesh integration

## SQL Scripts

Custom SQL scripts are stored in `app/scripts/sql/` and can be executed via the PostgreSQL API:
- Scripts support parameter substitution using `${parameter_name}` syntax
- Results are returned as JSON for SELECT queries
- Execution details and row counts are provided in response