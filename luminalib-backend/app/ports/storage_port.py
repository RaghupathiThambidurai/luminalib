"""Storage port interface"""
from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities import User, Book, Review, BorrowRecord


class StoragePort(ABC):
    """Abstract interface for data storage"""
    
    # User operations
    @abstractmethod
    async def create_user(self, user: User) -> User:
        """Create a new user"""
        pass
    
    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass
    
    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        pass
    
    @abstractmethod
    async def update_user(self, user_id: str, user: User) -> User:
        """Update user"""
        pass
    
    @abstractmethod
    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        pass
    
    @abstractmethod
    async def list_users(self, skip: int = 0, limit: int = 10) -> List[User]:
        """List users with pagination"""
        pass
    
    # Book operations
    @abstractmethod
    async def create_book(self, book: Book) -> Book:
        """Create a new book"""
        pass
    
    @abstractmethod
    async def get_book(self, book_id: str) -> Optional[Book]:
        """Get book by ID"""
        pass
    
    @abstractmethod
    async def update_book(self, book_id: str, book: Book) -> Book:
        """Update book"""
        pass
    
    @abstractmethod
    async def delete_book(self, book_id: str) -> bool:
        """Delete book"""
        pass
    
    @abstractmethod
    async def list_books(self, skip: int = 0, limit: int = 10) -> List[Book]:
        """List books with pagination"""
        pass
    
    @abstractmethod
    async def search_books(self, query: str, skip: int = 0, limit: int = 10) -> List[Book]:
        """Search books by title or author"""
        pass
    
    # Review operations
    @abstractmethod
    async def create_review(self, review: Review) -> Review:
        """Create a new review"""
        pass
    
    @abstractmethod
    async def get_review(self, review_id: str) -> Optional[Review]:
        """Get review by ID"""
        pass
    
    @abstractmethod
    async def get_reviews_by_book(self, book_id: str, skip: int = 0, limit: int = 10) -> List[Review]:
        """Get reviews for a book"""
        pass
    
    @abstractmethod
    async def get_reviews_by_user(self, user_id: str, skip: int = 0, limit: int = 10) -> List[Review]:
        """Get reviews by a user"""
        pass
    
    @abstractmethod
    async def update_review(self, review_id: str, review: Review) -> Review:
        """Update review"""
        pass
    
    @abstractmethod
    async def delete_review(self, review_id: str) -> bool:
        """Delete review"""
        pass
    
    # Borrow record operations
    @abstractmethod
    async def create_borrow_record(self, record: BorrowRecord) -> BorrowRecord:
        """Create a new borrow record"""
        pass
    
    @abstractmethod
    async def get_borrow_record(self, record_id: str) -> Optional[BorrowRecord]:
        """Get borrow record by ID"""
        pass
    
    @abstractmethod
    async def get_active_borrow(self, user_id: str, book_id: str) -> Optional[BorrowRecord]:
        """Get active (non-returned) borrow record for user and book"""
        pass
    
    @abstractmethod
    async def get_user_borrow_records(self, user_id: str) -> List[BorrowRecord]:
        """Get all borrow records for a user"""
        pass
    
    @abstractmethod
    async def get_book_borrow_records(self, book_id: str) -> List[BorrowRecord]:
        """Get all borrow records for a book"""
        pass
    
    @abstractmethod
    async def update_borrow_record(self, record_id: str, record: BorrowRecord) -> BorrowRecord:
        """Update borrow record"""
        pass
    
    @abstractmethod
    async def delete_borrow_record(self, record_id: str) -> bool:
        """Delete borrow record"""
        pass