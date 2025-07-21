import asyncio
import time
import os
import psycopg2
import aiohttp
import json
from typing import Dict, Any, List, Optional
import structlog
from app.core.azure_auth import azure_auth
from app.models.operations import OperationResult, OperationStatus
from app.core.config import settings

logger = structlog.get_logger(__name__)

class PostgreSQLService:
    def __init__(self):
        if not azure_auth.get_credential() or not hasattr(azure_auth, 'get_postgres_client'):
            raise RuntimeError("No Azure credential disponible o método get_postgres_client no encontrado.")
        from app.core.config import settings
        if not settings.azure_subscription_id:
            raise ValueError("AZURE_SUBSCRIPTION_ID no está definido en el entorno.")
        self.client = azure_auth.get_postgres_client()
    
    async def major_upgrade(self, resource_group: str, server_name: str, target_version: str) -> OperationResult:
        """Perform major upgrade on PostgreSQL Flexible Server using Azure REST API"""
        start_time = time.time()
        try:
            logger.info(f"Starting major upgrade for PostgreSQL server: {server_name} to version {target_version}")
            
            # Get current server information first
            current_server_info = await self._get_server_via_rest_api(resource_group, server_name)
            if not current_server_info:
                return OperationResult(
                    status=OperationStatus.FAILED,
                    message=f"Failed to retrieve current server information for {server_name}",
                    execution_time=time.time() - start_time
                )
            
            current_version = current_server_info.get("properties", {}).get("version")
            
            if current_version == target_version:
                return OperationResult(
                    status=OperationStatus.SUCCESS,
                    message=f"Server {server_name} is already on version {target_version}",
                    execution_time=time.time() - start_time
                )
            
            # Perform major upgrade using REST API
            upgrade_result = await self._perform_upgrade_via_rest_api(
                resource_group, server_name, target_version
            )
            
            execution_time = time.time() - start_time
            
            if upgrade_result["success"]:
                logger.info(f"PostgreSQL server {server_name} upgraded successfully from {current_version} to {target_version}")
                
                return OperationResult(
                    status=OperationStatus.SUCCESS,
                    message=f"Server {server_name} upgraded successfully from {current_version} to {target_version}",
                    details={
                        "previous_version": current_version,
                        "new_version": target_version,
                        "server_state": upgrade_result.get("server_state", "Updating"),
                        "operation_id": upgrade_result.get("operation_id")
                    },
                    execution_time=execution_time
                )
            else:
                return OperationResult(
                    status=OperationStatus.FAILED,
                    message=f"Failed to upgrade server {server_name}: {upgrade_result.get('error', 'Unknown error')}",
                    details=upgrade_result,
                    execution_time=execution_time
                )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Failed to upgrade PostgreSQL server {server_name}", error=str(e))
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Failed to upgrade server {server_name}: {str(e)}",
                execution_time=execution_time
            )
    
    async def get_server_status(self, resource_group: str, server_name: str) -> OperationResult:
        """Get PostgreSQL Flexible Server status"""
        start_time = time.time()
        try:
            logger.info(f"Getting status for PostgreSQL server: {server_name} in {resource_group}")
            
            server = self.client.servers.get(resource_group, server_name)
            
            server_details = {
                "name": server.name,
                "location": server.location,
                "state": server.state,
                "version": server.version,
                "sku": {
                    "name": server.sku.name,
                    "tier": server.sku.tier
                } if server.sku else None,
                "storage": {
                    "storage_size_gb": server.storage.storage_size_gb if server.storage else None
                },
                "backup": {
                    "backup_retention_days": server.backup.backup_retention_days if server.backup else None,
                    "earliest_restore_date": str(server.backup.earliest_restore_date) if server.backup and server.backup.earliest_restore_date else None
                },
                "fully_qualified_domain_name": server.fully_qualified_domain_name
            }
            
            execution_time = time.time() - start_time
            logger.info(f"Retrieved status for PostgreSQL server {server_name}")
            
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message=f"Successfully retrieved status for server {server_name}",
                details=server_details,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Failed to get status for PostgreSQL server {server_name}", error=str(e))
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Failed to get status for server {server_name}: {str(e)}",
                execution_time=execution_time
            )
    
    async def execute_custom_script(
        self, 
        server_name: str, 
        database_name: str, 
        username: str, 
        password: str, 
        script_name: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        """Execute custom SQL script on PostgreSQL Flexible Server"""
        start_time = time.time()
        try:
            logger.info(f"Executing script {script_name} on database {database_name}")
            
            # Read script from scripts/sql directory
            script_path = f"app/scripts/sql/{script_name}"
            if not os.path.exists(script_path):
                return OperationResult(
                    status=OperationStatus.FAILED,
                    message=f"Script file {script_name} not found in scripts/sql directory",
                    execution_time=time.time() - start_time
                )
            
            with open(script_path, 'r', encoding='utf-8') as file:
                sql_script = file.read()
            
            # Replace parameters in script if provided
            if parameters:
                for key, value in parameters.items():
                    sql_script = sql_script.replace(f"${{{key}}}", str(value))
            
            # Connect to PostgreSQL database
            connection_string = f"host={server_name}.postgres.database.azure.com port={settings.postgres_default_port} dbname={database_name} user={username} password={password} sslmode={settings.postgres_ssl_mode}"
            
            conn = psycopg2.connect(connection_string)
            cursor = conn.cursor()
            
            # Execute script
            cursor.execute(sql_script)
            
            # Fetch results if it's a SELECT query
            query_results = None
            if sql_script.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                query_results = [dict(zip(columns, row)) for row in rows]
            
            conn.commit()
            cursor.close()
            conn.close()
            
            execution_time = time.time() - start_time
            logger.info(f"Script {script_name} executed successfully on {database_name}")
            
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message=f"Script {script_name} executed successfully",
                details={
                    "script_name": script_name,
                    "database": database_name,
                    "server": server_name,
                    "rows_affected": cursor.rowcount if not query_results else len(query_results),
                    "query_results": query_results
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Failed to execute script {script_name}", error=str(e))
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Failed to execute script {script_name}: {str(e)}",
                execution_time=execution_time
            )
    
    async def execute_cli_command(self, command: str) -> OperationResult:
        """Execute Azure CLI command for PostgreSQL operations"""
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
    
    async def _get_server_via_rest_api(self, resource_group: str, server_name: str) -> Optional[Dict[str, Any]]:
        """Get server information using Azure REST API"""
        try:
            credential = azure_auth.get_credential()
            token = credential.get_token("https://management.azure.com/.default")
            
            url = f"https://management.azure.com/subscriptions/{settings.azure_subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.DBforPostgreSQL/flexibleServers/{server_name}"
            
            headers = {
                "Authorization": f"Bearer {token.token}",
                "Content-Type": "application/json"
            }
            
            params = {
                "api-version": "2024-08-01"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Failed to get server info: {response.status} - {await response.text()}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting server via REST API: {str(e)}")
            return None
    
    async def _perform_upgrade_via_rest_api(self, resource_group: str, server_name: str, target_version: str) -> Dict[str, Any]:
        """Perform upgrade using Azure REST API"""
        try:
            credential = azure_auth.get_credential()
            token = credential.get_token("https://management.azure.com/.default")
            
            url = f"https://management.azure.com/subscriptions/{settings.azure_subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.DBforPostgreSQL/flexibleServers/{server_name}"
            
            headers = {
                "Authorization": f"Bearer {token.token}",
                "Content-Type": "application/json"
            }
            
            params = {
                "api-version": "2024-08-01"
            }
            
            request_body = {
                "properties": {
                    "createMode": "Update",
                    "version": target_version
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.patch(url, headers=headers, params=params, json=request_body) as response:
                    response_text = await response.text()
                    
                    if response.status in [200, 202]:
                        # 200 = synchronous success, 202 = async operation started
                        if response.status == 202:
                            # Extract operation location for tracking
                            operation_location = response.headers.get("Location") or response.headers.get("Azure-AsyncOperation")
                            return {
                                "success": True,
                                "status_code": response.status,
                                "operation_id": operation_location,
                                "server_state": "Updating",
                                "message": "Upgrade operation initiated successfully"
                            }
                        else:
                            # Synchronous completion
                            result_data = json.loads(response_text) if response_text else {}
                            return {
                                "success": True,
                                "status_code": response.status,
                                "server_state": result_data.get("properties", {}).get("state", "Available"),
                                "message": "Upgrade completed successfully"
                            }
                    else:
                        logger.error(f"Upgrade API call failed: {response.status} - {response_text}")
                        return {
                            "success": False,
                            "status_code": response.status,
                            "error": f"API call failed with status {response.status}: {response_text}"
                        }
                        
        except Exception as e:
            logger.error(f"Error performing upgrade via REST API: {str(e)}")
            return {
                "success": False,
                "error": f"Exception during REST API call: {str(e)}"
            }