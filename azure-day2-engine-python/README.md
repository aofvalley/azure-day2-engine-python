# Azure Day 2 Engine - Python Edition

A modular, extensible platform for performing governed Azure operations using FastAPI, designed to run as a microservice in Azure Kubernetes Service (AKS).

## Features

- **FastAPI-based REST API** with automatic OpenAPI documentation
- **Azure Managed Identity authentication** for secure Azure resource access
- **AKS Operations**: Start/stop clusters, status monitoring
- **PostgreSQL Operations**: Major upgrades, custom SQL script execution
- **Azure CLI integration** for advanced operations
- **Kubernetes-ready** with proper health checks and monitoring

## Architecture

```
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
├── tests/                     # Test files
├── Dockerfile                 # Container configuration
└── requirements.txt           # Python dependencies
```

## API Endpoints

### AKS Operations (`/AKS/v1/`)

- `POST /AKS/v1/start` - Start an AKS cluster
- `POST /AKS/v1/stop` - Stop an AKS cluster
- `GET /AKS/v1/status/{resource_group}/{cluster_name}` - Get cluster status
- `POST /AKS/v1/cli` - Execute Azure CLI commands

### PostgreSQL Operations (`/PSSQL/v1/`)

- `POST /PSSQL/v1/upgrade` - Perform major version upgrade
- `GET /PSSQL/v1/status/{resource_group}/{server_name}` - Get server status
- `POST /PSSQL/v1/execute-script` - Execute custom SQL scripts
- `POST /PSSQL/v1/cli` - Execute Azure CLI commands

## Quick Start

### Local Development

1. **Clone and setup**:
   ```bash
   cd azure-day2-engine-python
   cp .env.example .env
   # Edit .env with your Azure credentials
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Kubernetes Deployment

1. **Build and push container**:
   ```bash
   docker build -t your-registry/azure-day2-engine:latest .
   docker push your-registry/azure-day2-engine:latest
   ```

2. **Configure Azure credentials**:
   ```bash
   # Update kubernetes/deployment.yaml with your values
   export AZURE_CLIENT_ID="your-client-id"
   export AZURE_TENANT_ID="your-tenant-id"
   export AZURE_SUBSCRIPTION_ID="your-subscription-id"
   
   # Create base64 encoded secrets
   export AZURE_CLIENT_ID_B64=$(echo -n $AZURE_CLIENT_ID | base64)
   export AZURE_TENANT_ID_B64=$(echo -n $AZURE_TENANT_ID | base64)
   export AZURE_SUBSCRIPTION_ID_B64=$(echo -n $AZURE_SUBSCRIPTION_ID | base64)
   ```

3. **Deploy to AKS**:
   ```bash
   envsubst < kubernetes/deployment.yaml | kubectl apply -f -
   ```

## Authentication

The application uses Azure Managed Identity for authentication:

- **In AKS**: Automatically uses the pod's managed identity
- **Local Development**: Falls back to Azure CLI credentials or environment variables

Required Azure permissions:
- `Contributor` or specific roles for target resource groups
- `Azure Kubernetes Service Cluster Admin Role` for AKS operations
- `PostgreSQL Server Contributor` for PostgreSQL operations

## SQL Scripts

Place custom SQL scripts in `app/scripts/sql/` directory. Scripts support parameter substitution using `${parameter_name}` syntax.

Example scripts included:
- `sample_health_check.sql` - Database health verification
- `sample_backup_check.sql` - Backup status and WAL information

## Usage Examples

### Start AKS Cluster
```bash
curl -X POST "http://localhost:8000/AKS/v1/start" \
  -H "Content-Type: application/json" \
  -d '{
    "resource_group": "my-rg",
    "cluster_name": "my-aks-cluster"
  }'
```

### PostgreSQL Major Upgrade
```bash
curl -X POST "http://localhost:8000/PSSQL/v1/upgrade" \
  -H "Content-Type: application/json" \
  -d '{
    "resource_group": "my-rg",
    "server_name": "my-postgres-server",
    "target_version": "15"
  }'
```

### Execute Custom SQL Script
```bash
curl -X POST "http://localhost:8000/PSSQL/v1/execute-script" \
  -H "Content-Type: application/json" \
  -d '{
    "resource_group": "my-rg",
    "server_name": "my-postgres-server",
    "database_name": "mydb",
    "username": "dbuser",
    "password": "dbpass",
    "script_name": "sample_health_check.sql"
  }'
```

## Security Considerations

- Uses Azure Managed Identity for secure authentication
- Sensitive data (passwords) should be passed securely
- Network policies should restrict access to authorized sources
- Consider using Azure Key Vault for credential management

## Monitoring and Logging

- Structured logging with `structlog`
- Health check endpoint at `/health`
- Kubernetes readiness and liveness probes configured
- Request/response logging for audit trails

## Contributing

1. Follow the existing code structure and patterns
2. Add appropriate error handling and logging
3. Update documentation for new features
4. Ensure proper type hints and Pydantic models