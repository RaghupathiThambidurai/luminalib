"""
Pytest configuration and shared fixtures for all tests.

This module contains:
- Database fixtures
- API client fixtures
- Authentication fixtures
- Mock data factories
"""

import os
import pytest
from typing import Generator, Any
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, MagicMock

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Import from app
from app.main import app, get_db
from app.core.config import Settings
from app.core.jwt_handler import JWTHandler
from app.domain.models import Base, User, Book, Review, BorrowRecord
from app.core.dependencies import container


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    Create a fresh in-memory SQLite database for each test.
    
    Yields:
        Session: SQLAlchemy session connected to test database
    """
    # Use in-memory SQLite for tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    
    db = TestingSessionLocal()
    
    # Override the get_db dependency
    def override_get_db() -> Generator[Session, None, None]:
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield db
    
    # Cleanup
    db.close()
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(test_db: Session) -> TestClient:
    """
    Create a FastAPI test client with test database.
    
    Args:
        test_db: Test database session
        
    Returns:
        TestClient: FastAPI test client
    """
    return TestClient(app)


# ============================================================================
# AUTHENTICATION FIXTURES
# ============================================================================

@pytest.fixture
def jwt_handler() -> JWTHandler:
    """
    Create a JWT handler for testing.
    
    Returns:
        JWTHandler: JWT handler with test secret
    """
    return JWTHandler(secret_key="test-secret-key-for-testing")


@pytest.fixture
def valid_token(jwt_handler: JWTHandler) -> str:
    """
    Create a valid JWT token for testing.
    
    Args:
        jwt_handler: JWT handler
        
    Returns:
        str: Valid JWT token
    """
    return jwt_handler.create_access_token(
        data={"sub": "test-user-id"},
        expires_delta=3600
    )


@pytest.fixture
def auth_headers(valid_token: str) -> dict[str, str]:
    """
    Create authorization headers with valid token.
    
    Args:
        valid_token: Valid JWT token
        
    Returns:
        dict: Authorization headers
    """
    return {"Authorization": f"Bearer {valid_token}"}


@pytest.fixture
def expired_token(jwt_handler: JWTHandler) -> str:
    """
    Create an expired JWT token for testing.
    
    Args:
        jwt_handler: JWT handler
        
    Returns:
        str: Expired JWT token
    """
    return jwt_handler.create_access_token(
        data={"sub": "test-user-id"},
        expires_delta=-3600  # Negative means already expired
    )


# ============================================================================
# USER FIXTURES
# ============================================================================

@pytest.fixture
def test_user_data() -> dict[str, str]:
    """
    Create test user data.
    
    Returns:
        dict: User data for testing
    """
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "full_name": "Test User",
        "password": "SecurePassword123!"
    }


@pytest.fixture
def test_user(test_db: Session, test_user_data: dict[str, str]) -> User:
    """
    Create a test user in the database.
    
    Args:
        test_db: Test database session
        test_user_data: User data
        
    Returns:
        User: Created user
    """
    user = User(
        id="test-user-id",
        username=test_user_data["username"],
        email=test_user_data["email"],
        full_name=test_user_data["full_name"],
        hashed_password="$2b$12$test_hash_for_testing",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


# ============================================================================
# BOOK FIXTURES
# ============================================================================

@pytest.fixture
def test_book_data() -> dict[str, Any]:
    """
    Create test book data.
    
    Returns:
        dict: Book data for testing
    """
    return {
        "title": "Test Book Title",
        "author": "Test Author",
        "isbn": "978-1-234567-89-0",
        "description": "A test book description",
        "genre": "Fiction",
        "published_date": "2023-01-15",
        "cover_url": "https://example.com/cover.jpg",
        "file_url": "https://example.com/file.pdf",
        "file_size": 1024000
    }


@pytest.fixture
def test_book(test_db: Session, test_book_data: dict[str, Any]) -> Book:
    """
    Create a test book in the database.
    
    Args:
        test_db: Test database session
        test_book_data: Book data
        
    Returns:
        Book: Created book
    """
    book = Book(
        id="test-book-id",
        title=test_book_data["title"],
        author=test_book_data["author"],
        isbn=test_book_data["isbn"],
        description=test_book_data["description"],
        genre=test_book_data["genre"],
        published_date=test_book_data["published_date"],
        cover_url=test_book_data["cover_url"],
        file_url=test_book_data["file_url"],
        file_size=test_book_data["file_size"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    test_db.add(book)
    test_db.commit()
    test_db.refresh(book)
    return book


# ============================================================================
# REVIEW FIXTURES
# ============================================================================

@pytest.fixture
def test_review_data() -> dict[str, Any]:
    """
    Create test review data.
    
    Returns:
        dict: Review data for testing
    """
    return {
        "rating": 4,
        "comment": "Great book! Highly recommend.",
        "title": "Excellent read"
    }


@pytest.fixture
def test_review(
    test_db: Session,
    test_user: User,
    test_book: Book,
    test_review_data: dict[str, Any]
) -> Review:
    """
    Create a test review in the database.
    
    Args:
        test_db: Test database session
        test_user: Test user
        test_book: Test book
        test_review_data: Review data
        
    Returns:
        Review: Created review
    """
    review = Review(
        id="test-review-id",
        user_id=test_user.id,
        book_id=test_book.id,
        rating=test_review_data["rating"],
        comment=test_review_data["comment"],
        title=test_review_data["title"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    test_db.add(review)
    test_db.commit()
    test_db.refresh(review)
    return review


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_storage() -> Mock:
    """
    Create a mock storage adapter.
    
    Returns:
        Mock: Mock storage object
    """
    return Mock()


@pytest.fixture
def mock_llm_service() -> AsyncMock:
    """
    Create a mock LLM service.
    
    Returns:
        AsyncMock: Mock LLM service
    """
    mock = AsyncMock()
    mock.generate_summary = AsyncMock(return_value="Generated summary text")
    return mock


@pytest.fixture
def mock_file_service() -> Mock:
    """
    Create a mock file service.
    
    Returns:
        Mock: Mock file service
    """
    mock = Mock()
    mock.upload_file = Mock(return_value="https://example.com/file.pdf")
    mock.download_file = Mock(return_value=b"file contents")
    mock.delete_file = Mock(return_value=True)
    return mock


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@pytest.fixture
def create_multiple_books(test_db: Session) -> callable:
    """
    Factory fixture to create multiple test books.
    
    Args:
        test_db: Test database session
        
    Returns:
        callable: Function to create books
    """
    def _create_books(count: int = 5) -> list[Book]:
        books = []
        for i in range(count):
            book = Book(
                id=f"book-{i}",
                title=f"Test Book {i}",
                author=f"Author {i}",
                isbn=f"978-1-{i:06d}-0",
                description=f"Description for book {i}",
                genre=["Fiction", "Non-fiction", "Science"][i % 3],
                published_date="2023-01-01",
                cover_url=f"https://example.com/cover-{i}.jpg",
                file_url=f"https://example.com/file-{i}.pdf",
                file_size=1024000 * (i + 1),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            test_db.add(book)
            books.append(book)
        test_db.commit()
        return books
    
    return _create_books


@pytest.fixture
def create_multiple_users(test_db: Session) -> callable:
    """
    Factory fixture to create multiple test users.
    
    Args:
        test_db: Test database session
        
    Returns:
        callable: Function to create users
    """
    def _create_users(count: int = 5) -> list[User]:
        users = []
        for i in range(count):
            user = User(
                id=f"user-{i}",
                username=f"user{i}",
                email=f"user{i}@example.com",
                full_name=f"Test User {i}",
                hashed_password="$2b$12$test_hash",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            test_db.add(user)
            users.append(user)
        test_db.commit()
        return users
    
    return _create_users
