"""User service - business logic for user operations"""
from typing import Optional, List
from app.domain.entities import User
from app.ports.storage_port import StoragePort
from app.core.exceptions import NotFoundError, ValidationError
import hashlib


class UserService:
    """Service for user management"""
    
    def __init__(self, storage: StoragePort):
        self.storage = storage
    
    async def create_user(self, username: str, email: str, password: str, full_name: Optional[str] = None) -> User:
        """Create a new user with hashed password"""
        # Check if user already exists
        existing = await self.storage.get_user_by_email(email)
        if existing:
            raise ValidationError(f"User with email {email} already exists")
        
        # Hash password
        password_hash = self._hash_password(password)
        
        # Create user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            password_hash=password_hash
        )
        return await self.storage.create_user(user)
    
    async def get_user(self, user_id: str) -> User:
        """Get user by ID"""
        user = await self.storage.get_user(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        return user
    
    async def update_user(self, user_id: str, **kwargs) -> User:
        """Update user information"""
        user = await self.get_user(user_id)
        
        # Update allowed fields
        allowed_fields = ['full_name', 'preferences', 'is_active']
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(user, key, value)
        
        return await self.storage.update_user(user_id, user)
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        user = await self.get_user(user_id)  # Verify exists
        return await self.storage.delete_user(user_id)
    
    async def list_users(self, skip: int = 0, limit: int = 10) -> List[User]:
        """List users"""
        return await self.storage.list_users(skip, limit)
    
    async def verify_password(self, user_id: str, password: str) -> bool:
        """Verify user password"""
        user = await self.get_user(user_id)
        return self._verify_password(password, user.password_hash)
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        """Verify password"""
        return hashlib.sha256(password.encode()).hexdigest() == password_hash
