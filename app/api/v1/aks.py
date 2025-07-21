from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import structlog
from app.services.aks_service import AKSService
from app.models.operations import (
    AKSClusterRequest, 
    AKSClusterResponse,
    CLICommandRequest,
    CLICommandResponse,
    OperationResult,
    OperationStatus
)

logger = structlog.get_logger(__name__)
router = APIRouter()

def get_aks_service():
    """Get AKS service instance with lazy loading"""
    return AKSService()

@router.post("/start", response_model=AKSClusterResponse)
async def start_cluster(request: AKSClusterRequest):
    """Start an AKS cluster"""
    try:
        logger.info(f"Received request to start AKS cluster: {request.cluster_name}")
        
        aks_service = get_aks_service()
        result = await aks_service.start_cluster(
            resource_group=request.resource_group,
            cluster_name=request.cluster_name
        )
        
        response = AKSClusterResponse(
            operation="start",
            cluster_name=request.cluster_name,
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
        logger.error(f"Error starting AKS cluster {request.cluster_name}", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/stop", response_model=AKSClusterResponse)
async def stop_cluster(request: AKSClusterRequest):
    """Stop an AKS cluster"""
    try:
        logger.info(f"Received request to stop AKS cluster: {request.cluster_name}")
        
        aks_service = get_aks_service()
        result = await aks_service.stop_cluster(
            resource_group=request.resource_group,
            cluster_name=request.cluster_name
        )
        
        response = AKSClusterResponse(
            operation="stop",
            cluster_name=request.cluster_name,
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
        logger.error(f"Error stopping AKS cluster {request.cluster_name}", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/status/{resource_group}/{cluster_name}", response_model=AKSClusterResponse)
async def get_cluster_status(resource_group: str, cluster_name: str):
    """Get AKS cluster status"""
    try:
        logger.info(f"Received request to get status for AKS cluster: {cluster_name}")
        
        aks_service = get_aks_service()
        result = await aks_service.get_cluster_status(
            resource_group=resource_group,
            cluster_name=cluster_name
        )
        
        response = AKSClusterResponse(
            operation="status",
            cluster_name=cluster_name,
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
        logger.error(f"Error getting status for AKS cluster {cluster_name}", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/cli", response_model=CLICommandResponse)
async def execute_cli_command(request: CLICommandRequest):
    """Execute Azure CLI command for AKS operations"""
    try:
        logger.info(f"Received request to execute Azure CLI command: {request.command}")
        
        aks_service = get_aks_service()
        result = await aks_service.execute_cli_command(request.command)
        
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

@router.get("/")
async def list_aks_operations():
    """List available AKS operations"""
    return {
        "service": "AKS Operations",
        "version": "v1",
        "available_operations": [
            {
                "endpoint": "/start",
                "method": "POST",
                "description": "Start an AKS cluster",
                "parameters": ["resource_group", "cluster_name"]
            },
            {
                "endpoint": "/stop",
                "method": "POST",
                "description": "Stop an AKS cluster",
                "parameters": ["resource_group", "cluster_name"]
            },
            {
                "endpoint": "/status/{resource_group}/{cluster_name}",
                "method": "GET",
                "description": "Get AKS cluster status"
            },
            {
                "endpoint": "/cli",
                "method": "POST",
                "description": "Execute Azure CLI command",
                "parameters": ["command"]
            }
        ]
    }