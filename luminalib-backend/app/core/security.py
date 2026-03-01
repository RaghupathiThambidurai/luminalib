"""Security utilities for JWT authentication and password hashing"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import hashlib
import os
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class TokenData(BaseModel):
    """Token payload data"""
    sub: str  # subject (username)
    exp: Optional[int] = None
    iat: Optional[int] = None
    scopes: list = []


class SecuritySettings(BaseSettings):
    """Security configuration"""
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env file


security_settings = SecuritySettings()


# Token blacklist for logout functionality
# In production, use Redis or database for persistence
class TokenBlacklist:
    """In-memory token blacklist for logout"""
    _blacklist: set = set()
    
    @classmethod
    def add_token(cls, token: str) -> None:
        """Add token to blacklist"""
        cls._blacklist.add(token)
    
    @classmethod
    def is_blacklisted(cls, token: str) -> bool:
        """Check if token is blacklisted"""
        return token in cls._blacklist
    
    @classmethod
    def clear_expired(cls) -> None:
        """Clear expired tokens (called periodically)"""
        # This is simplified - in production, decode token to check expiration
        pass


token_blacklist = TokenBlacklist()


# Password hashing using SHA256 (simple and compatible with Python 3.14)
def hash_password(password: str) -> str:
    """Hash a password using SHA256 with salt"""
    salt = os.urandom(32).hex()
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${hashed}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        salt, hashed = hashed_password.split("$")
        return hashlib.sha256((plain_password + salt).encode()).hexdigest() == hashed
    except (ValueError, AttributeError):
        return False


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    is_refresh: bool = False
) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Token payload data (must include 'sub' for username)
        expires_delta: Optional custom expiration time
        is_refresh: If True, create refresh token with longer expiration
    
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if is_refresh:
        # Refresh token expires in days
        expire = datetime.now(timezone.utc) + timedelta(
            days=security_settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    else:
        # Access token expires in minutes
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=security_settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
    
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    
    encoded_jwt = jwt.encode(
        to_encode,
        security_settings.SECRET_KEY,
        algorithm=security_settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token to verify
    
    Returns:
        TokenData if valid, None if invalid or blacklisted
    """
    # Check if token is blacklisted
    if token_blacklist.is_blacklisted(token):
        return None
    
    try:
        payload = jwt.decode(
            token,
            security_settings.SECRET_KEY,
            algorithms=[security_settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, sub=username)
        return token_data
    except JWTError:
        return None


def create_tokens(username: str) -> dict:
    """
    Create both access and refresh tokens for a user
    
    Args:
        username: Username for the token subject
    
    Returns:
        Dictionary with access_token and refresh_token
    """
    access_token = create_access_token(
        data={"sub": username},
        is_refresh=False
    )
    refresh_token = create_access_token(
        data={"sub": username},
        is_refresh=True
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": security_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
    }


# HTTPBearer scheme for FastAPI dependency injection
class HTTPBearer(BaseModel):
    """HTTP Bearer token credentials"""
    credentials: Optional[str] = None
    scheme: str = "bearer"
    
    def __init__(self, credentials: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.credentials = credentials


async def security(authorization: Optional[str] = None) -> Optional[HTTPBearer]:
    """
    FastAPI dependency for extracting Bearer token from Authorization header
    
    Args:
        authorization: Authorization header value (automatically injected by FastAPI)
    
    Returns:
        HTTPBearer with extracted credentials if valid, None otherwise
    """
    if not authorization:
        return None
    
    try:
        scheme, credentials = authorization.split()
        if scheme.lower() != "bearer":
            return None
        
        # Verify the token
        token_data = verify_token(credentials)
        if token_data is None:
            return None
        
        return HTTPBearer(credentials=credentials)
    except (ValueError, AttributeError):
        return None
