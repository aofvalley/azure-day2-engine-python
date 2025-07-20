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
        self.client = azure_auth.get_aks_client()
    
    async def start_cluster(self, resource_group: str, cluster_name: str) -> OperationResult:
        """Start an AKS cluster"""
        start_time = time.time()
        try:
            logger.info(f"Starting AKS cluster: {cluster_name} in {resource_group}")
            
            # Get current cluster state
            cluster = self.client.managed_clusters.get(resource_group, cluster_name)
            
            if cluster.power_state and cluster.power_state.code == "Running":
                return OperationResult(
                    status=OperationStatus.SUCCESS,
                    message=f"Cluster {cluster_name} is already running",
                    execution_time=time.time() - start_time
                )
            
            # Start the cluster using Azure REST API
            operation = self.client.managed_clusters.begin_start(resource_group, cluster_name)
            result = operation.result()
            
            execution_time = time.time() - start_time
            logger.info(f"AKS cluster {cluster_name} started successfully")
            
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message=f"Cluster {cluster_name} started successfully",
                details={"cluster_state": "Running"},
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
        """Stop an AKS cluster"""
        start_time = time.time()
        try:
            logger.info(f"Stopping AKS cluster: {cluster_name} in {resource_group}")
            
            # Get current cluster state
            cluster = self.client.managed_clusters.get(resource_group, cluster_name)
            
            if cluster.power_state and cluster.power_state.code == "Stopped":
                return OperationResult(
                    status=OperationStatus.SUCCESS,
                    message=f"Cluster {cluster_name} is already stopped",
                    execution_time=time.time() - start_time
                )
            
            # Stop the cluster using Azure REST API
            operation = self.client.managed_clusters.begin_stop(resource_group, cluster_name)
            result = operation.result()
            
            execution_time = time.time() - start_time
            logger.info(f"AKS cluster {cluster_name} stopped successfully")
            
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message=f"Cluster {cluster_name} stopped successfully",
                details={"cluster_state": "Stopped"},
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
                "name": cluster.name,
                "location": cluster.location,
                "provisioning_state": cluster.provisioning_state,
                "power_state": cluster.power_state.code if cluster.power_state else "Unknown",
                "kubernetes_version": cluster.kubernetes_version,
                "node_resource_group": cluster.node_resource_group,
                "fqdn": cluster.fqdn
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