from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.rdbms.postgresql_flexibleservers import PostgreSQLManagementClient
import subprocess
import json
import asyncio
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
        """Get Azure credential using default credential chain (local/dev)"""
        if self._credential is None:
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
            logger.info(f"Executing Azure CLI command: {command}")
            
            # Set environment variables for Azure CLI authentication
            import os
            env = os.environ.copy()
            
            # Ensure Azure CLI uses service principal authentication
            if settings.azure_client_id and settings.azure_client_secret and settings.azure_tenant_id:
                env['AZURE_CLIENT_ID'] = settings.azure_client_id
                env['AZURE_CLIENT_SECRET'] = settings.azure_client_secret
                env['AZURE_TENANT_ID'] = settings.azure_tenant_id
                env['AZURE_SUBSCRIPTION_ID'] = settings.azure_subscription_id or ""
                
                # Use a clean config directory to avoid cached credentials
                env['AZURE_CONFIG_DIR'] = '/tmp/az_config_service_principal'
                
                # First, ensure Azure CLI is logged in with service principal
                login_result = await self._ensure_cli_login(env)
                if not login_result["success"]:
                    return login_result
            
            # Prepare command for subprocess
            cmd_parts = command.split()
            
            # Run the command asynchronously
            process = await asyncio.create_subprocess_exec(
                *cmd_parts,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await process.communicate()
            
            # Decode output
            stdout_str = stdout.decode('utf-8') if stdout else ""
            stderr_str = stderr.decode('utf-8') if stderr else ""
            
            if process.returncode == 0:
                # Try to parse JSON output if possible
                output_data = None
                if stdout_str.strip():
                    try:
                        output_data = json.loads(stdout_str)
                    except json.JSONDecodeError:
                        # If not JSON, keep as string
                        output_data = stdout_str.strip()
                
                logger.info(f"Azure CLI command executed successfully: {command}")
                return {
                    "success": True,
                    "exit_code": process.returncode,
                    "command": command,
                    "output": output_data,
                    "raw_output": stdout_str.strip()
                }
            else:
                logger.error(f"Azure CLI command failed: {command}", error=stderr_str)
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "command": command,
                    "error": stderr_str.strip(),
                    "output": stdout_str.strip() if stdout_str.strip() else None
                }
                
        except Exception as e:
            logger.error(f"Azure CLI command execution error: {command}", error=str(e))
            return {
                "success": False,
                "error": f"Execution error: {str(e)}",
                "command": command
            }
    
    async def _ensure_cli_login(self, env: dict) -> dict:
        """Ensure Azure CLI is logged in with service principal"""
        try:
            # Try to get account info to see if already logged in
            check_process = await asyncio.create_subprocess_exec(
                'az', 'account', 'show',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await check_process.communicate()
            
            # If already logged in and account info is valid, return success
            if check_process.returncode == 0:
                logger.info("Azure CLI already authenticated")
                return {"success": True}
            
            # Not logged in, perform service principal login
            logger.info("Performing Azure CLI service principal login")
            login_process = await asyncio.create_subprocess_exec(
                'az', 'login', '--service-principal',
                '--username', settings.azure_client_id,
                '--password', settings.azure_client_secret,
                '--tenant', settings.azure_tenant_id,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            login_stdout, login_stderr = await login_process.communicate()
            
            if login_process.returncode == 0:
                logger.info("Azure CLI service principal login successful")
                return {"success": True}
            else:
                error_msg = login_stderr.decode('utf-8') if login_stderr else "Unknown login error"
                logger.error("Azure CLI service principal login failed", error=error_msg)
                return {
                    "success": False,
                    "error": f"Azure CLI login failed: {error_msg}",
                    "command": "az login"
                }
                
        except Exception as e:
            logger.error("Error during Azure CLI login check/attempt", error=str(e))
            return {
                "success": False,
                "error": f"Login check error: {str(e)}",
                "command": "az login"
            }

# Global instance
azure_auth = AzureAuthManager()