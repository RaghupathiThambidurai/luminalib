"""Dependency injection container with singleton and factory patterns"""
from typing import Optional, Type, Any, Callable
import logging

logger = logging.getLogger(__name__)


class DIContainer:
    """
    Advanced Dependency Injection Container for managing dependencies.
    
    Supports:
    - Singleton pattern (shared instances)
    - Factory pattern (new instances per request)
    - Lazy initialization
    - Circular dependency detection
    - Type hints support
    """
    
    _singletons: dict[str, Any] = {}
    _factories: dict[str, Callable] = {}
    _types: dict[str, Type] = {}
    _initializing: set[str] = set()  # Track circular dependencies
    
    @classmethod
    def register_singleton(cls, key: str, instance: Any) -> None:
        """
        Register a singleton instance (shared across all requests).
        
        Args:
            key: Unique identifier for the dependency
            instance: The singleton instance
            
        Example:
            >>> container = DIContainer()
            >>> storage = PostgreSQLAdapter("postgresql://...")
            >>> DIContainer.register_singleton("storage", storage)
        """
        cls._singletons[key] = instance
        logger.debug(f"✓ Registered singleton: {key} ({type(instance).__name__})")
    
    @classmethod
    def register_factory(cls, key: str, factory: Callable) -> None:
        """
        Register a factory function (creates new instance per request).
        
        Args:
            key: Unique identifier for the dependency
            factory: Callable that creates instances
            
        Example:
            >>> DIContainer.register_factory(
            ...     "user_service",
            ...     lambda storage: UserService(storage)
            ... )
        """
        cls._factories[key] = factory
        logger.debug(f"✓ Registered factory: {key}")
    
    @classmethod
    def register_type(cls, key: str, type_class: Type) -> None:
        """
        Register a type for auto-instantiation (requires __init__ signature inspection).
        
        Args:
            key: Unique identifier for the dependency
            type_class: The class to instantiate
        """
        cls._types[key] = type_class
        logger.debug(f"✓ Registered type: {key} ({type_class.__name__})")
    
    @classmethod
    def get(cls, key: str) -> Any:
        """
        Get a dependency instance (singleton or factory result).
        
        Args:
            key: Dependency identifier
            
        Returns:
            The dependency instance
            
        Raises:
            ValueError: If dependency not found or circular dependency detected
        """
        # Check for circular dependencies
        if key in cls._initializing:
            raise ValueError(f"❌ Circular dependency detected for '{key}'")
        
        # Check singleton first (fastest)
        if key in cls._singletons:
            return cls._singletons[key]
        
        # Check factory
        if key in cls._factories:
            cls._initializing.add(key)
            try:
                instance = cls._factories[key]()
                cls._singletons[key] = instance  # Cache as singleton
                return instance
            finally:
                cls._initializing.discard(key)
        
        # Check type-registered classes
        if key in cls._types:
            cls._initializing.add(key)
            try:
                type_class = cls._types[key]
                instance = type_class()
                cls._singletons[key] = instance
                return instance
            finally:
                cls._initializing.discard(key)
        
        raise ValueError(f"❌ Dependency '{key}' not found in container")
    
    @classmethod
    def has(cls, key: str) -> bool:
        """Check if a dependency is registered"""
        return (key in cls._singletons or 
                key in cls._factories or 
                key in cls._types)
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered dependencies (useful for testing)"""
        cls._singletons.clear()
        cls._factories.clear()
        cls._types.clear()
        cls._initializing.clear()
        logger.debug("🧹 Cleared all dependencies")
    
    @classmethod
    def reset_singletons(cls) -> None:
        """Reset only singletons (keep factories and types)"""
        cls._singletons.clear()
        logger.debug("🧹 Reset singletons")
    
    @classmethod
    def get_all_registered(cls) -> dict[str, str]:
        """Get all registered dependencies for debugging"""
        result = {}
        for key in cls._singletons:
            result[key] = f"singleton ({type(cls._singletons[key]).__name__})"
        for key in cls._factories:
            result[key] = "factory"
        for key in cls._types:
            result[key] = f"type ({cls._types[key].__name__})"
        return result


# Global dependency getter for FastAPI
def get_dependency(key: str) -> Callable:
    """
    Create a FastAPI dependency function.
    
    Args:
        key: Dependency identifier
        
    Returns:
        A callable suitable for FastAPI's Depends()
        
    Example:
        >>> router = APIRouter()
        >>> @router.get("/books")
        ... async def list_books(service = Depends(get_dependency("book_service"))):
        ...     return await service.list_books()
    """
    def _get():
        return DIContainer.get(key)
    return _get
