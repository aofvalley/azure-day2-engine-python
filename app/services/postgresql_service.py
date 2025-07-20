import asyncio
import time
import os
import psycopg2
from typing import Dict, Any, List, Optional
import structlog
from app.core.azure_auth import azure_auth
from app.models.operations import OperationResult, OperationStatus
from app.core.config import settings

logger = structlog.get_logger(__name__)

class PostgreSQLService:
    def __init__(self):
        self.client = azure_auth.get_postgres_client()
    
    async def major_upgrade(self, resource_group: str, server_name: str, target_version: str) -> OperationResult:
        """Perform major upgrade on PostgreSQL Flexible Server"""
        start_time = time.time()
        try:
            logger.info(f"Starting major upgrade for PostgreSQL server: {server_name} to version {target_version}")
            
            # Get current server information
            server = self.client.servers.get(resource_group, server_name)
            current_version = server.version
            
            if current_version == target_version:
                return OperationResult(
                    status=OperationStatus.SUCCESS,
                    message=f"Server {server_name} is already on version {target_version}",
                    execution_time=time.time() - start_time
                )
            
            # Initiate major upgrade operation
            upgrade_operation = self.client.servers.begin_update(
                resource_group,
                server_name,
                {
                    "version": target_version
                }
            )
            
            # Wait for operation to complete
            result = upgrade_operation.result()
            
            execution_time = time.time() - start_time
            logger.info(f"PostgreSQL server {server_name} upgraded successfully from {current_version} to {target_version}")
            
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message=f"Server {server_name} upgraded successfully from {current_version} to {target_version}",
                details={
                    "previous_version": current_version,
                    "new_version": target_version,
                    "server_state": result.state if hasattr(result, 'state') else "Available"
                },
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