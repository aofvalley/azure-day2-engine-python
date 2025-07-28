"""
Authentication system for Azure Day 2 Engine
===========================================

Simple but secure authentication for protecting the API and frontend.
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import structlog

logger = structlog.get_logger(__name__)

# Configuration
SECRET_KEY = os.getenv("AUTH_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

# Simple user store (in production, use database or Azure AD)
VALID_USERS = {
    os.getenv("ADMIN_USERNAME", "admin"): {
        "password_hash": hashlib.sha256(os.getenv("ADMIN_PASSWORD", "azure-day2-admin").encode()).hexdigest(),
        "role": "admin",
        "permissions": ["read", "write", "admin"]
    }
}

security = HTTPBearer()

class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

def hash_password(password: str) -> str:
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    logger.info("Access token created", username=data.get("sub"), expires_at=expire.isoformat())
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise AuthenticationError("Invalid token: no username")
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.JWTError:
        raise AuthenticationError("Invalid token")

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user with username and password"""
    user = VALID_USERS.get(username)
    if not user:
        logger.warning("Authentication failed - user not found", username=username)
        return None
    
    if not verify_password(password, user["password_hash"]):
        logger.warning("Authentication failed - invalid password", username=username)
        return None
    
    logger.info("User authenticated successfully", username=username, role=user["role"])
    return {"username": username, **user}

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get the current authenticated user from the JWT token"""
    try:
        payload = verify_token(credentials.credentials)
        username = payload.get("sub")
        user = VALID_USERS.get(username)
        
        if user is None:
            raise AuthenticationError("User not found")
        
        return {"username": username, **user}
    except Exception as e:
        logger.error("Token verification failed", error=str(e))
        raise AuthenticationError("Invalid authentication credentials")

async def require_admin(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Require admin role for the endpoint"""
    if "admin" not in current_user.get("permissions", []):
        logger.warning("Admin access denied", username=current_user.get("username"))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

def get_auth_info() -> Dict[str, Any]:
    """Get authentication configuration info (for debugging)"""
    return {
        "algorithm": ALGORITHM,
        "token_expires_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
        "users_configured": len(VALID_USERS),
        "secret_key_configured": bool(SECRET_KEY),
    }