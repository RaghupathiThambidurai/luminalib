"""SQLAlchemy ORM models for PostgreSQL"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class UserModel(Base):
    """User database model"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    preferences = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reviews = relationship("ReviewModel", back_populates="user", cascade="all, delete-orphan")
    borrow_records = relationship("BorrowRecordModel", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UserModel(id={self.id}, username={self.username})>"


class BookModel(Base):
    """Book database model"""
    __tablename__ = "books"

    id = Column(String(36), primary_key=True)
    title = Column(String(200), nullable=False, index=True)
    author = Column(String(200), nullable=False, index=True)
    isbn = Column(String(20), unique=True, nullable=True, index=True)
    description = Column(Text, nullable=True)
    genre = Column(String(100), nullable=True, index=True)
    published_date = Column(DateTime, nullable=True)
    cover_url = Column(String(500), nullable=True)
    file_url = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    book_metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reviews = relationship("ReviewModel", back_populates="book", cascade="all, delete-orphan")
    borrow_records = relationship("BorrowRecordModel", back_populates="book", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<BookModel(id={self.id}, title={self.title})>"


class ReviewModel(Base):
    """Review database model"""
    __tablename__ = "reviews"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    book_id = Column(String(36), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    content = Column(Text, nullable=True)
    sentiment_score = Column(Integer, nullable=True)  # -1 to 1, stored as integer percentage
    is_helpful = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserModel", back_populates="reviews")
    book = relationship("BookModel", back_populates="reviews")

    def __repr__(self):
        return f"<ReviewModel(id={self.id}, rating={self.rating})>"


class BorrowRecordModel(Base):
    """Book borrow record database model"""
    __tablename__ = "borrow_records"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    book_id = Column(String(36), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    borrowed_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    returned_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="active", index=True)  # active, returned, overdue

    # Relationships
    user = relationship("UserModel", back_populates="borrow_records")
    book = relationship("BookModel", back_populates="borrow_records")

    def __repr__(self):
        return f"<BorrowRecordModel(id={self.id}, status={self.status})>"