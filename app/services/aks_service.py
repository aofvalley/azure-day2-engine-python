import asyncio
import time
from typing import Dict, Any
import structlog
from azure.mgmt.containerservice.models import ManagedCluster
from app.core.azure_auth import azure_auth
from app.models.operations import OperationResult, OperationStatus

logger = structlog.get_logger(__name__)

class AKSService:
    def __init__(self):
        if not azure_auth.get_credential() or not hasattr(azure_auth, 'get_aks_client'):
            raise RuntimeError("No Azure credential disponible o método get_aks_client no encontrado.")
        if not hasattr(azure_auth, 'get_aks_client'):
            raise RuntimeError("Método get_aks_client no disponible en AzureAuthManager.")
        if not hasattr(azure_auth, 'get_credential'):
            raise RuntimeError("Método get_credential no disponible en AzureAuthManager.")
        if not hasattr(azure_auth, 'get_aks_client'):
            raise RuntimeError("Método get_aks_client no disponible en AzureAuthManager.")
        from app.core.config import settings
        if not settings.azure_subscription_id:
            raise ValueError("AZURE_SUBSCRIPTION_ID no está definido en el entorno.")
        self.client = azure_auth.get_aks_client()
    
    async def start_cluster(self, resource_group: str, cluster_name: str) -> OperationResult:
        """Start an AKS cluster using Azure CLI"""
        start_time = time.time()
        try:
            logger.info(f"Starting AKS cluster: {cluster_name} in {resource_group}")
            
            # Use Azure CLI to start the cluster
            from app.core.azure_auth import azure_auth
            cli_command = f"az aks start --name {cluster_name} --resource-group {resource_group}"
            
            logger.info(f"Executing CLI command: {cli_command}")
            cli_result = await azure_auth.execute_azure_cli(cli_command)
            
            execution_time = time.time() - start_time
            
            if cli_result["success"]:
                logger.info(f"AKS cluster {cluster_name} started successfully")
                
                # Get cluster status after starting
                try:
                    cluster = self.client.managed_clusters.get(resource_group, cluster_name) 
                    power_state = getattr(cluster, 'power_state', None)
                    power_state_code = getattr(power_state, 'code', 'Unknown') if power_state else 'Unknown'
                    
                    return OperationResult(
                        status=OperationStatus.SUCCESS,
                        message=f"Cluster {cluster_name} started successfully. Power state: {power_state_code}",
                        details={
                            "provisioning_state": getattr(cluster, 'provisioning_state', 'Unknown'),
                            "power_state": power_state_code,
                            "cli_output": cli_result.get("output", ""),
                            "raw_output": cli_result.get("raw_output", "")
                        },
                        execution_time=execution_time
                    )
                except Exception as status_error:
                    logger.warning(f"Could not get cluster status after start: {status_error}")
                    return OperationResult(
                        status=OperationStatus.SUCCESS,
                        message=f"Cluster {cluster_name} start command executed successfully",
                        details={
                            "cli_output": cli_result.get("output", ""),
                            "raw_output": cli_result.get("raw_output", "")
                        },
                        execution_time=execution_time
                    )
            else:
                logger.error(f"Failed to start AKS cluster {cluster_name}: {cli_result.get('error', 'Unknown error')}")
                return OperationResult(
                    status=OperationStatus.FAILED,
                    message=f"Failed to start cluster {cluster_name}: {cli_result.get('error', 'Unknown error')}",
                    details={
                        "cli_error": cli_result.get("error", ""), 
                        "cli_output": cli_result.get("output", ""),
                        "raw_output": cli_result.get("raw_output", "")
                    },
                    execution_time=execution_time
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Failed to start AKS cluster {cluster_name}", error=str(e))
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Failed to start cluster {cluster_name}: {str(e)}",
                execution_time=execution_time
            )
    
    async def stop_cluster(self, resource_group: str, cluster_name: str) -> OperationResult:
        """Stop an AKS cluster using Azure CLI"""
        start_time = time.time()
        try:
            logger.info(f"Stopping AKS cluster: {cluster_name} in {resource_group}")
            
            # Use Azure CLI to stop the cluster
            from app.core.azure_auth import azure_auth
            cli_command = f"az aks stop --name {cluster_name} --resource-group {resource_group}"
            
            logger.info(f"Executing CLI command: {cli_command}")
            cli_result = await azure_auth.execute_azure_cli(cli_command)
            
            execution_time = time.time() - start_time
            
            if cli_result["success"]:
                logger.info(f"AKS cluster {cluster_name} stopped successfully")
                
                # Get cluster status after stopping
                try:
                    cluster = self.client.managed_clusters.get(resource_group, cluster_name) 
                    power_state = getattr(cluster, 'power_state', None)
                    power_state_code = getattr(power_state, 'code', 'Unknown') if power_state else 'Unknown'
                    
                    return OperationResult(
                        status=OperationStatus.SUCCESS,
                        message=f"Cluster {cluster_name} stopped successfully. Power state: {power_state_code}",
                        details={
                            "provisioning_state": getattr(cluster, 'provisioning_state', 'Unknown'),
                            "power_state": power_state_code,
                            "cli_output": cli_result.get("output", ""),
                            "raw_output": cli_result.get("raw_output", "")
                        },
                        execution_time=execution_time
                    )
                except Exception as status_error:
                    logger.warning(f"Could not get cluster status after stop: {status_error}")
                    return OperationResult(
                        status=OperationStatus.SUCCESS,
                        message=f"Cluster {cluster_name} stop command executed successfully",
                        details={
                            "cli_output": cli_result.get("output", ""),
                            "raw_output": cli_result.get("raw_output", "")
                        },
                        execution_time=execution_time
                    )
            else:
                logger.error(f"Failed to stop AKS cluster {cluster_name}: {cli_result.get('error', 'Unknown error')}")
                return OperationResult(
                    status=OperationStatus.FAILED,
                    message=f"Failed to stop cluster {cluster_name}: {cli_result.get('error', 'Unknown error')}",
                    details={
                        "cli_error": cli_result.get("error", ""), 
                        "cli_output": cli_result.get("output", ""),
                        "raw_output": cli_result.get("raw_output", "")
                    },
                    execution_time=execution_time
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Failed to stop AKS cluster {cluster_name}", error=str(e))
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Failed to stop cluster {cluster_name}: {str(e)}",
                execution_time=execution_time
            )
    
    async def get_cluster_status(self, resource_group: str, cluster_name: str) -> OperationResult:
        """Get AKS cluster status"""
        start_time = time.time()
        try:
            logger.info(f"Getting status for AKS cluster: {cluster_name} in {resource_group}")
            cluster = self.client.managed_clusters.get(resource_group, cluster_name)
            cluster_details = {
                "name": getattr(cluster, 'name', None),
                "location": getattr(cluster, 'location', None),
                "provisioning_state": getattr(cluster, 'provisioning_state', None),
                "kubernetes_version": getattr(cluster, 'kubernetes_version', None),
                "node_resource_group": getattr(cluster, 'node_resource_group', None),
                "fqdn": getattr(cluster, 'fqdn', None)
            }
            execution_time = time.time() - start_time
            logger.info(f"Retrieved status for AKS cluster {cluster_name}")
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message=f"Successfully retrieved status for cluster {cluster_name}",
                details=cluster_details,
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Failed to get status for AKS cluster {cluster_name}", error=str(e))
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Failed to get status for cluster {cluster_name}: {str(e)}",
                execution_time=execution_time
            )
    
    async def execute_cli_command(self, command: str) -> OperationResult:
        """Execute Azure CLI command for AKS operations"""
        start_time = time.time()
        try:
            logger.info(f"Executing Azure CLI command: {command}")
            
            result = await azure_auth.execute_azure_cli(command)
            execution_time = time.time() - start_time
            
            if result["success"]:
                return OperationResult(
                    status=OperationStatus.SUCCESS,
                    message=f"Azure CLI command executed successfully",
                    details=result,
                    execution_time=execution_time
                )
            else:
                return OperationResult(
                    status=OperationStatus.FAILED,
                    message=f"Azure CLI command failed: {result.get('error', 'Unknown error')}",
                    details=result,
                    execution_time=execution_time
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Failed to execute Azure CLI command", error=str(e))
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Failed to execute Azure CLI command: {str(e)}",
                execution_time=execution_time
            )