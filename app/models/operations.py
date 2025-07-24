from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum

class OperationStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"

class OperationResult(BaseModel):
    status: OperationStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None

# AKS Models
class AKSClusterRequest(BaseModel):
    resource_group: str = Field(..., description="Azure resource group name")
    cluster_name: str = Field(..., description="AKS cluster name")

class AKSClusterResponse(BaseModel):
    operation: str
    cluster_name: str
    resource_group: str
    result: OperationResult

# PostgreSQL Models
class PostgreSQLServerRequest(BaseModel):
    resource_group: str = Field(..., description="Azure resource group name")
    server_name: str = Field(..., description="PostgreSQL server name")

class PostgreSQLMajorUpgradeRequest(PostgreSQLServerRequest):
    target_version: str = Field(..., description="Target PostgreSQL version (e.g., '14', '15')")

class PostgreSQLCustomScriptRequest(PostgreSQLServerRequest):
    database_name: str = Field(..., description="Database name")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    script_name: str = Field(..., description="SQL script filename")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Script parameters")

class PostgreSQLListServersRequest(BaseModel):
    resource_group: Optional[str] = Field(default=None, description="Azure resource group name (optional - if not provided, lists all servers in subscription)")

class PostgreSQLServerListResponse(BaseModel):
    operation: str
    resource_group: Optional[str]
    result: OperationResult

class PostgreSQLResponse(BaseModel):
    operation: str
    server_name: str
    resource_group: str
    result: OperationResult

class ScriptExecutionResponse(BaseModel):
    operation: str
    server_name: str
    database_name: str
    script_name: str
    result: OperationResult
    query_results: Optional[List[Dict[str, Any]]] = None

class CLICommandRequest(BaseModel):
    command: str = Field(..., description="Azure CLI command to execute", example="az postgres flexible-server list -g myresourcegroup")

class CLICommandResponse(BaseModel):
    operation: str
    command: str
    result: OperationResult