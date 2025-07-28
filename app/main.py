from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import structlog
from app.api.v1.aks import router as aks_router
from app.api.v1.pssql import router as pssql_router
from app.api.v1.auth import router as auth_router
from app.core.config import settings

logger = structlog.get_logger(__name__)

app = FastAPI(
    title="Azure Day 2 Engine",
    description="Modular platform for performing governed Azure operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(aks_router, prefix="/AKS/v1", tags=["AKS Operations"])
app.include_router(pssql_router, prefix="/PSSQL/v1", tags=["PostgreSQL Operations"])

@app.get("/")
async def root():
    return {"message": "Azure Day 2 Engine - Python Edition", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "azure-day2-engine"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)