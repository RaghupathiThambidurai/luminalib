"""Authentication API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from app.core.security import (
    hash_password,
    verify_password,
    verify_token,
    create_tokens,
    TokenData,
)
from app.domain.entities import UserCreate, UserResponse, TokenResponse, LoginRequest, User
from app.ports.storage_port import StoragePort
from app.core.di import DIContainer


class Credentials(BaseModel):
    """Credentials model for manual extraction"""
    credentials: str

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

security = HTTPBearer()


async def get_storage() -> StoragePort:
    """Dependency to get storage adapter"""
    container = DIContainer()
    return container.get("storage")


async def get_current_user(
    authorization: HTTPBearer = Depends(security),
    storage: StoragePort = Depends(get_storage)
) -> UserResponse:
    """
    Dependency to verify JWT token and get current user
    
    Args:
        authorization: HTTPAuthorizationCredentials with JWT token
        storage: Storage adapter for user lookup
    
    Returns:
        UserResponse if token is valid
        
    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    # Extract token from HTTPAuthorizationCredentials
    # token = authorization.credentials if hasattr(authorization, 'credentials') else str(authorization)
    
    # token_data = verify_token(token)
    
    # if not token_data:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid authentication credentials",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    
    # # For simplicity, we search by username
    # # In production, store user_id in token for better performance
    # username = token_data.sub
    # from datetime import datetime
    token = authorization.credentials
    token_data = verify_token(token)

    if not token_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

    username = token_data.sub
    user = await storage.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    
    # Get user from storage (this is a placeholder - actual implementation depends on StoragePort)
    # For now, we return a minimal response
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=getattr(user, "full_name", None),
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    storage: StoragePort = Depends(get_storage)
) -> dict:
    """
    Register a new user and return access/refresh tokens
    
    Args:
        user_data: User registration data
        storage: Storage adapter
    
    Returns:
        TokenResponse with access and refresh tokens
        
    Raises:
        HTTPException: 400 if user already exists
    """
    try:
        # Check if user already exists by username
        existing_user = await storage.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{user_data.username}' already registered"
            )
        
        # Create user with hashed password
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            password_hash=hash_password(user_data.password)
        )
        
        # Save user to storage
        created_user = await storage.create_user(user)
        
        # Generate tokens
        tokens = create_tokens(created_user.username)
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest = None,
    username: str = Query(None),
    password: str = Query(None),
    storage: StoragePort = Depends(get_storage)
) -> dict:
    """
    Login with username and password, return access/refresh tokens
    
    Supports both JSON body and query parameters:
    - JSON: POST /api/auth/login with {"username":"...", "password":"..."}
    - Query: POST /api/auth/login?username=...&password=...
    
    Args:
        credentials: Login credentials (username and password) from JSON body
        username: Username from query parameter
        password: Password from query parameter
        storage: Storage adapter
    
    Returns:
        TokenResponse with access and refresh tokens
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    try:
        # Use query parameters if JSON body not provided
        if credentials is None:
            if not username or not password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username and password required"
                )
            credentials = LoginRequest(username=username, password=password)
        
        # Get user by username
        user = await storage.get_user_by_username(credentials.username)
        
        if not user or not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Generate tokens
        tokens = create_tokens(user.username)
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    authorization: HTTPBearer = Depends(security),
    storage: StoragePort = Depends(get_storage)
) -> dict:
    """
    Refresh expired access token using refresh token
    
    Args:
        authorization: HTTPAuthorizationCredentials containing refresh token
        storage: Storage adapter
    
    Returns:
        TokenResponse with new access and refresh tokens
        
    Raises:
        HTTPException: 401 if refresh token is invalid
    """
    # Extract token from HTTPAuthorizationCredentials
    token = authorization.credentials if hasattr(authorization, 'credentials') else str(authorization)
    
    token_data = verify_token(token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify user still exists and is active
    user = await storage.get_user_by_username(token_data.sub)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate new tokens
    tokens = create_tokens(user.username)
    
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Get current authenticated user information
    
    Args:
        current_user: Current authenticated user (from dependency)
    
    Returns:
        UserResponse with user information
    """
    return current_user


@router.post("/logout")
async def logout(
    authorization: HTTPBearer = Depends(security)
) -> dict:
    """
    Logout user by blacklisting their token
    
    Args:
        authorization: HTTPAuthorizationCredentials with JWT token
    
    Returns:
        Success message
        
    Raises:
        HTTPException: 401 if token is invalid
    """
    from app.core.security import token_blacklist
    
    # Extract token from HTTPAuthorizationCredentials
    token = authorization.credentials if hasattr(authorization, 'credentials') else str(authorization)
    
    try:
        # Verify token is valid before blacklisting
        token_data = verify_token(token)
        
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Add token to blacklist
        token_blacklist.add_token(token)
        
        return {
            "message": f"User '{token_data.sub}' logged out successfully",
            "status": "success"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )
