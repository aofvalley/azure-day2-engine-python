from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
import structlog
from app.services.postgresql_service import PostgreSQLService
from app.models.operations import (
    PostgreSQLServerRequest,
    PostgreSQLMajorUpgradeRequest,
    PostgreSQLCustomScriptRequest,
    PostgreSQLListServersRequest,
    PostgreSQLResponse,
    PostgreSQLServerListResponse,
    ScriptExecutionResponse,
    CLICommandRequest,
    CLICommandResponse,
    OperationStatus
)
from app.core.auth import get_current_user

logger = structlog.get_logger(__name__)
router = APIRouter()

def get_postgresql_service():
    """Get PostgreSQL service instance with lazy loading"""
    return PostgreSQLService()

@router.post("/upgrade", response_model=PostgreSQLResponse)
async def major_upgrade(request: PostgreSQLMajorUpgradeRequest):
    """Perform major upgrade on PostgreSQL Flexible Server"""
    try:
        logger.info(f"Received request to upgrade PostgreSQL server: {request.server_name} to version {request.target_version}")
        
        postgresql_service = get_postgresql_service()
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
        
        postgresql_service = get_postgresql_service()
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
        
        postgresql_service = get_postgresql_service()
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

@router.post("/cli", response_model=CLICommandResponse)
async def execute_cli_command(request: CLICommandRequest):
    """Execute Azure CLI command for PostgreSQL operations"""
    try:
        logger.info(f"Received request to execute Azure CLI command: {request.command}")
        
        postgresql_service = get_postgresql_service()
        result = await postgresql_service.execute_cli_command(request.command)
        
        response = CLICommandResponse(
            operation="cli_command",
            command=request.command,
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
        logger.error(f"Error executing Azure CLI command", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/servers/list", response_model=PostgreSQLServerListResponse)
async def list_servers(request: PostgreSQLListServersRequest):
    """List PostgreSQL Flexible Servers in subscription or resource group"""
    try:
        logger.info(f"Received request to list PostgreSQL servers in {'resource group ' + request.resource_group if request.resource_group else 'subscription'}")
        
        postgresql_service = get_postgresql_service()
        result = await postgresql_service.list_servers(resource_group=request.resource_group)
        
        response = PostgreSQLServerListResponse(
            operation="list_servers",
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
        logger.error(f"Error listing PostgreSQL servers", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/servers/start", response_model=PostgreSQLResponse)
async def start_server(request: PostgreSQLServerRequest):
    """Start PostgreSQL Flexible Server"""
    try:
        logger.info(f"Received request to start PostgreSQL server: {request.server_name}")
        
        postgresql_service = get_postgresql_service()
        result = await postgresql_service.start_server(
            resource_group=request.resource_group,
            server_name=request.server_name
        )
        
        response = PostgreSQLResponse(
            operation="start_server",
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
        logger.error(f"Error starting PostgreSQL server {request.server_name}", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/servers/stop", response_model=PostgreSQLResponse)
async def stop_server(request: PostgreSQLServerRequest):
    """Stop PostgreSQL Flexible Server"""
    try:
        logger.info(f"Received request to stop PostgreSQL server: {request.server_name}")
        
        postgresql_service = get_postgresql_service()
        result = await postgresql_service.stop_server(
            resource_group=request.resource_group,
            server_name=request.server_name
        )
        
        response = PostgreSQLResponse(
            operation="stop_server",
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
        logger.error(f"Error stopping PostgreSQL server {request.server_name}", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/")
async def list_postgresql_operations():
    """List available PostgreSQL operations"""
    return {
        "service": "PostgreSQL Operations",
        "version": "v1",
        "available_operations": [
            {
                "endpoint": "/servers/list",
                "method": "POST",
                "description": "List PostgreSQL Flexible Servers",
                "parameters": ["resource_group (optional)"]
            },
            {
                "endpoint": "/servers/start",
                "method": "POST",
                "description": "Start PostgreSQL Flexible Server",
                "parameters": ["resource_group", "server_name"]
            },
            {
                "endpoint": "/servers/stop",
                "method": "POST",
                "description": "Stop PostgreSQL Flexible Server",
                "parameters": ["resource_group", "server_name"]
            },
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