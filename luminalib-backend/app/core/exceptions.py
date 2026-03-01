"""Exception definitions for the application"""


class LuminallibException(Exception):
    """Base exception for the application"""
    pass


class NotFoundError(LuminallibException):
    """Resource not found"""
    pass


class ValidationError(LuminallibException):
    """Validation error"""
    pass


class AuthenticationError(LuminallibException):
    """Authentication error"""
    pass


class StorageError(LuminallibException):
    """Storage/Database error"""
    pass


class LLMError(LuminallibException):
    """LLM provider error"""
    pass


class RecommendationError(LuminallibException):
    """Recommendation service error"""
    pass
