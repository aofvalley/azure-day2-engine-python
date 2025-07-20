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

### Local Development
```bash
cd azure-day2-engine-python
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Container Build and Run
```bash
docker build -t azure-day2-engine:latest .
docker run -p 8000:8000 azure-day2-engine:latest
```

### Kubernetes Deployment
```bash
kubectl apply -f kubernetes/deployment.yaml
```

### Dependencies
- Python 3.11
- FastAPI and Uvicorn
- Azure SDK libraries (azure-identity, azure-mgmt-*)
- Azure CLI
- PostgreSQL client (psycopg2)

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