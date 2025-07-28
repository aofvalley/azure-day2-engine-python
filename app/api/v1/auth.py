"""
Authentication API endpoints
===========================

API endpoints for user authentication and token management.
"""

from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
import structlog

from app.core.auth import authenticate_user, create_access_token, get_current_user, get_auth_info
from app.core.auth import ACCESS_TOKEN_EXPIRE_MINUTES

logger = structlog.get_logger(__name__)

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_info: dict

class UserResponse(BaseModel):
    username: str
    role: str
    permissions: list

@router.post("/login", response_model=LoginResponse, summary="User Login")
async def login(credentials: LoginRequest):
    """
    Authenticate user and return access token
    
    - **username**: User's username
    - **password**: User's password
    
    Returns JWT access token for API authentication.
    """
    user = authenticate_user(credentials.username, credentials.password)
    if not user:
        logger.warning("Login attempt failed", username=credentials.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    logger.info("User login successful", username=user["username"], role=user["role"])
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        user_info={
            "username": user["username"],
            "role": user["role"],
            "permissions": user["permissions"]
        }
    )

@router.get("/me", response_model=UserResponse, summary="Get Current User")
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current user information
    
    Requires valid JWT token in Authorization header.
    """
    return UserResponse(
        username=current_user["username"],
        role=current_user["role"],
        permissions=current_user["permissions"]
    )

@router.post("/logout", summary="User Logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout user (token blacklisting not implemented in this simple version)
    
    In a production system, you would blacklist the token.
    For now, client should simply discard the token.
    """
    logger.info("User logout", username=current_user["username"])
    return {"message": "Logged out successfully", "note": "Please discard your token"}

@router.get("/info", summary="Authentication Info")
async def auth_info():
    """
    Get authentication configuration information (for debugging)
    """
    return get_auth_info()