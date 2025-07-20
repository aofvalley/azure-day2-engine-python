from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import structlog
from app.services.postgresql_service import PostgreSQLService
from app.models.operations import (
    PostgreSQLServerRequest,
    PostgreSQLMajorUpgradeRequest,
    PostgreSQLCustomScriptRequest,
    PostgreSQLResponse,
    ScriptExecutionResponse,
    OperationStatus
)

logger = structlog.get_logger(__name__)
router = APIRouter()
postgresql_service = PostgreSQLService()

@router.post("/upgrade", response_model=PostgreSQLResponse)
async def major_upgrade(request: PostgreSQLMajorUpgradeRequest):
    """Perform major upgrade on PostgreSQL Flexible Server"""
    try:
        logger.info(f"Received request to upgrade PostgreSQL server: {request.server_name} to version {request.target_version}")
        
        result = await postgresql_service.major_upgrade(
            resource_group=request.resource_group,
            server_name=request.server_name,
            target_version=request.target_version
        )
        
        response = PostgreSQLResponse(
            operation="major_upgrade",
            server_name=request.server_name,
            resource_group=request.resource_group,
            result=result
        )
        
        if result.status == OperationStatus.SUCCESS:
            return JSONResponse(
                status_code=200,
                content=response.dict()
            )
        else:
            return JSONResponse(
                status_code=500,
                content=response.dict()
            )
            
    except Exception as e:
        logger.error(f"Error upgrading PostgreSQL server {request.server_name}", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/status/{resource_group}/{server_name}", response_model=PostgreSQLResponse)
async def get_server_status(resource_group: str, server_name: str):
    """Get PostgreSQL Flexible Server status"""
    try:
        logger.info(f"Received request to get status for PostgreSQL server: {server_name}")
        
        result = await postgresql_service.get_server_status(
            resource_group=resource_group,
            server_name=server_name
        )
        
        response = PostgreSQLResponse(
            operation="status",
            server_name=server_name,
            resource_group=resource_group,
            result=result
        )
        
        if result.status == OperationStatus.SUCCESS:
            return JSONResponse(
                status_code=200,
                content=response.dict()
            )
        else:
            return JSONResponse(
                status_code=404,
                content=response.dict()
            )
            
    except Exception as e:
        logger.error(f"Error getting status for PostgreSQL server {server_name}", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/execute-script", response_model=ScriptExecutionResponse)
async def execute_custom_script(request: PostgreSQLCustomScriptRequest):
    """Execute custom SQL script on PostgreSQL Flexible Server"""
    try:
        logger.info(f"Received request to execute script {request.script_name} on database {request.database_name}")
        
        result = await postgresql_service.execute_custom_script(
            server_name=request.server_name,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
            script_name=request.script_name,
            parameters=request.parameters
        )
        
        response = ScriptExecutionResponse(
            operation="execute_script",
            server_name=request.server_name,
            database_name=request.database_name,
            script_name=request.script_name,
            result=result,
            query_results=result.details.get("query_results") if result.details else None
        )
        
        if result.status == OperationStatus.SUCCESS:
            return JSONResponse(
                status_code=200,
                content=response.dict()
            )
        else:
            return JSONResponse(
                status_code=500,
                content=response.dict()
            )
            
    except Exception as e:
        logger.error(f"Error executing script {request.script_name}", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/cli")
async def execute_cli_command(command: dict):
    """Execute Azure CLI command for PostgreSQL operations"""
    try:
        cmd = command.get("command", "")
        if not cmd:
            raise HTTPException(status_code=400, detail="Command is required")
        
        logger.info(f"Received request to execute Azure CLI command: {cmd}")
        
        result = await postgresql_service.execute_cli_command(cmd)
        
        if result.status == OperationStatus.SUCCESS:
            return JSONResponse(
                status_code=200,
                content={
                    "operation": "cli_command",
                    "command": cmd,
                    "result": result.dict()
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "operation": "cli_command",
                    "command": cmd,
                    "result": result.dict()
                }
            )
            
    except Exception as e:
        logger.error(f"Error executing Azure CLI command", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/")
async def list_postgresql_operations():
    """List available PostgreSQL operations"""
    return {
        "service": "PostgreSQL Operations",
        "version": "v1",
        "available_operations": [
            {
                "endpoint": "/upgrade",
                "method": "POST",
                "description": "Perform major upgrade on PostgreSQL Flexible Server",
                "parameters": ["resource_group", "server_name", "target_version"]
            },
            {
                "endpoint": "/status/{resource_group}/{server_name}",
                "method": "GET",
                "description": "Get PostgreSQL Flexible Server status"
            },
            {
                "endpoint": "/execute-script",
                "method": "POST",
                "description": "Execute custom SQL script",
                "parameters": ["server_name", "database_name", "username", "password", "script_name", "parameters (optional)"]
            },
            {
                "endpoint": "/cli",
                "method": "POST",
                "description": "Execute Azure CLI command",
                "parameters": ["command"]
            }
        ]
    }