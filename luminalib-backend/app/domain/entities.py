"""Domain entities for the application"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    """User entity"""
    id: Optional[str] = None
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    full_name: Optional[str] = None
    password_hash: Optional[str] = None
    is_active: bool = True
    preferences: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "is_active": True
            }
        }


class UserCreate(BaseModel):
    """User creation request schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    """User response schema (without password)"""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # in seconds


class Book(BaseModel):
    """Book entity"""
    id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=200)
    isbn: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    published_date: Optional[datetime] = None
    cover_url: Optional[str] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "isbn": "978-0743273565",
                "genre": "Fiction",
                "description": "A classic novel"
            }
        }


class BookCreate(BaseModel):
    """Book creation request schema"""
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=200)
    isbn: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    published_date: Optional[datetime] = None
    cover_url: Optional[str] = None


class BookUpdate(BaseModel):
    """Book update request schema"""
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    isbn: Optional[str] = None
    cover_url: Optional[str] = None


class Review(BaseModel):
    """Review entity"""
    id: Optional[str] = None
    user_id: str
    book_id: str
    rating: int = Field(..., ge=1, le=5)
    content: Optional[str] = None
    sentiment_score: Optional[float] = None  # -1 to 1, from sentiment analysis
    is_helpful: bool = False
    helpful_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "book_id": "book_456",
                "rating": 5,
                "content": "Amazing book!",
                "sentiment_score": 0.95,
                "is_helpful": True
            }
        }


class ReviewCreate(BaseModel):
    """Review creation request schema"""
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    content: str = Field(..., min_length=10, max_length=5000, description="Review content (minimum 10 characters)")


class BorrowRecord(BaseModel):
    """Book borrow record entity"""
    id: Optional[str] = None
    user_id: str
    book_id: str
    borrowed_at: datetime = Field(default_factory=datetime.utcnow)
    due_date: datetime
    returned_at: Optional[datetime] = None
    status: str = Field(default="active")  # active, returned, overdue

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "book_id": "book_456",
                "borrowed_at": "2026-02-25T10:00:00",
                "due_date": "2026-03-11T10:00:00",
                "status": "active"
            }
        }


class Recommendation(BaseModel):
    """Book recommendation entity"""
    id: Optional[str] = None
    user_id: str
    book_id: str
    score: float = Field(..., ge=0, le=1)  # Recommendation confidence score
    reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime  # Recommendations expire and need refresh

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "book_id": "book_456",
                "score": 0.87,
                "reason": "Based on your borrowing history and reviews"
            }
        }


class ReviewAnalysis(BaseModel):
    """Analysis of reviews for a book"""
    book_id: str
    total_reviews: int
    average_rating: float
    average_sentiment: float  # Average sentiment score of all reviews
    summary: str  # LLM-generated summary
    generated_at: datetime = Field(default_factory=datetime.utcnow)
