import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Azure Configuration
    azure_tenant_id: Optional[str] = os.getenv("AZURE_TENANT_ID")
    azure_client_id: Optional[str] = os.getenv("AZURE_CLIENT_ID")
    azure_subscription_id: Optional[str] = os.getenv("AZURE_SUBSCRIPTION_ID")
    azure_client_secret: Optional[str] = os.getenv("AZURE_CLIENT_SECRET")
    
    # PostgreSQL Configuration
    postgres_default_port: int = 5432
    postgres_ssl_mode: str = "require"
    
    # Logging
    log_level: str = "INFO"
    
    # Application
    app_name: str = "Azure Day 2 Engine"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()