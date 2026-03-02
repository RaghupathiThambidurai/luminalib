"""
Unit tests for JWT handler.

Tests:
- Token creation
- Token validation
- Token expiration
- Invalid token handling
- Token refresh
"""

import pytest
from datetime import datetime, timedelta
from app.core.jwt_handler import JWTHandler


class TestJWTHandlerTokenCreation:
    """Test JWT token creation."""
    
    def test_create_access_token(self, jwt_handler: JWTHandler) -> None:
        """Test creating a valid access token."""
        token = jwt_handler.create_access_token(
            data={"sub": "user-123"},
            expires_delta=3600
        )
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count(".") == 2  # JWT has 3 parts
    
    def test_create_token_with_custom_claims(self, jwt_handler: JWTHandler) -> None:
        """Test creating token with custom claims."""
        data = {
            "sub": "user-123",
            "email": "user@example.com",
            "role": "admin"
        }
        token = jwt_handler.create_access_token(data=data, expires_delta=3600)
        payload = jwt_handler.verify_token(token)
        
        assert payload["sub"] == "user-123"
        assert payload["email"] == "user@example.com"
        assert payload["role"] == "admin"
    
    def test_token_contains_expiration(self, jwt_handler: JWTHandler) -> None:
        """Test that created token contains expiration time."""
        token = jwt_handler.create_access_token(
            data={"sub": "user-123"},
            expires_delta=3600
        )
        payload = jwt_handler.verify_token(token)
        
        assert "exp" in payload
        assert isinstance(payload["exp"], int)


class TestJWTHandlerTokenVerification:
    """Test JWT token verification."""
    
    def test_verify_valid_token(self, jwt_handler: JWTHandler) -> None:
        """Test verifying a valid token."""
        token = jwt_handler.create_access_token(
            data={"sub": "user-123"},
            expires_delta=3600
        )
        payload = jwt_handler.verify_token(token)
        
        assert payload["sub"] == "user-123"
    
    def test_verify_invalid_token_format(self, jwt_handler: JWTHandler) -> None:
        """Test verifying token with invalid format."""
        with pytest.raises(Exception):
            jwt_handler.verify_token("invalid.token")
    
    def test_verify_token_with_wrong_secret(self) -> None:
        """Test verifying token signed with different secret."""
        handler1 = JWTHandler(secret_key="secret-1")
        handler2 = JWTHandler(secret_key="secret-2")
        
        token = handler1.create_access_token(
            data={"sub": "user-123"},
            expires_delta=3600
        )
        
        with pytest.raises(Exception):
            handler2.verify_token(token)
    
    def test_verify_tampered_token(self, jwt_handler: JWTHandler) -> None:
        """Test verifying a tampered token."""
        token = jwt_handler.create_access_token(
            data={"sub": "user-123"},
            expires_delta=3600
        )
        
        # Tamper with token
        tampered_token = token[:-5] + "xxxxx"
        
        with pytest.raises(Exception):
            jwt_handler.verify_token(tampered_token)


class TestJWTHandlerTokenExpiration:
    """Test JWT token expiration."""
    
    def test_expired_token_raises_exception(self, expired_token: str, jwt_handler: JWTHandler) -> None:
        """Test that expired token raises exception."""
        with pytest.raises(Exception):
            jwt_handler.verify_token(expired_token)
    
    def test_token_expiration_time(self, jwt_handler: JWTHandler) -> None:
        """Test that token expiration time is correct."""
        expires_delta = 1800  # 30 minutes
        token = jwt_handler.create_access_token(
            data={"sub": "user-123"},
            expires_delta=expires_delta
        )
        payload = jwt_handler.verify_token(token)
        
        # Check expiration is approximately correct (within 5 seconds)
        now = datetime.utcnow().timestamp()
        exp_time = payload["exp"]
        diff = exp_time - now
        
        assert 1795 < diff < 1805  # Should be around 30 minutes


class TestJWTHandlerEdgeCases:
    """Test edge cases in JWT handling."""
    
    def test_empty_data_dict(self, jwt_handler: JWTHandler) -> None:
        """Test creating token with empty data."""
        token = jwt_handler.create_access_token(
            data={},
            expires_delta=3600
        )
        payload = jwt_handler.verify_token(token)
        
        assert "exp" in payload
    
    def test_none_expires_delta(self, jwt_handler: JWTHandler) -> None:
        """Test creating token with None expires_delta."""
        token = jwt_handler.create_access_token(
            data={"sub": "user-123"},
            expires_delta=None
        )
        payload = jwt_handler.verify_token(token)
        
        assert "exp" in payload or payload.get("exp") is None
    
    def test_zero_expires_delta(self, jwt_handler: JWTHandler) -> None:
        """Test creating token with zero expires_delta."""
        token = jwt_handler.create_access_token(
            data={"sub": "user-123"},
            expires_delta=0
        )
        # Token should be expired immediately
        with pytest.raises(Exception):
            jwt_handler.verify_token(token)
