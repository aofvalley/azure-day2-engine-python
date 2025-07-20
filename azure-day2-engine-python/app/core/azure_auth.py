from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.rdbms.postgresql_flexibleservers import PostgreSQLManagementClient
from azure.cli.core import get_default_cli
import structlog
from typing import Optional
from app.core.config import settings

logger = structlog.get_logger(__name__)

class AzureAuthManager:
    def __init__(self):
        self._credential: Optional[DefaultAzureCredential] = None
        self._aks_client: Optional[ContainerServiceClient] = None
        self._postgres_client: Optional[PostgreSQLManagementClient] = None
        
    def get_credential(self) -> DefaultAzureCredential:
        """Get Azure credential using Managed Identity or default credential chain"""
        if self._credential is None:
            try:
                # Try Managed Identity first (for AKS pod deployment)
                self._credential = ManagedIdentityCredential()
                logger.info("Using Managed Identity for Azure authentication")
            except Exception:
                # Fallback to default credential chain (for local development)
                self._credential = DefaultAzureCredential()
                logger.info("Using Default Azure Credential chain")
        return self._credential
    
    def get_aks_client(self) -> ContainerServiceClient:
        """Get AKS management client"""
        if self._aks_client is None:
            credential = self.get_credential()
            self._aks_client = ContainerServiceClient(
                credential=credential,
                subscription_id=settings.azure_subscription_id
            )
            logger.info("Initialized AKS client")
        return self._aks_client
    
    def get_postgres_client(self) -> PostgreSQLManagementClient:
        """Get PostgreSQL Flexible Server management client"""
        if self._postgres_client is None:
            credential = self.get_credential()
            self._postgres_client = PostgreSQLManagementClient(
                credential=credential,
                subscription_id=settings.azure_subscription_id
            )
            logger.info("Initialized PostgreSQL client")
        return self._postgres_client
    
    async def execute_azure_cli(self, command: str) -> dict:
        """Execute Azure CLI command and return result"""
        try:
            cli = get_default_cli()
            result = cli.invoke(command.split())
            logger.info(f"Azure CLI command executed: {command}")
            return {
                "success": True,
                "exit_code": result,
                "command": command
            }
        except Exception as e:
            logger.error(f"Azure CLI command failed: {command}", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "command": command
            }

# Global instance
azure_auth = AzureAuthManager()