"""In-memory storage adapter for development and testing"""
from typing import Optional, List
from app.domain.entities import User, Book, Review, BorrowRecord
from app.ports.storage_port import StoragePort
import uuid
from datetime import datetime


class InMemoryStorageAdapter(StoragePort):
    """In-memory storage adapter"""
    
    def __init__(self):
        self.users: dict[str, User] = {}
        self.books: dict[str, Book] = {}
        self.reviews: dict[str, Review] = {}
        self.borrow_records: dict[str, BorrowRecord] = {}
    
    # User operations
    async def create_user(self, user: User) -> User:
        user.id = str(uuid.uuid4())
        user.created_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        self.users[user.id] = user
        return user
    
    async def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    async def update_user(self, user_id: str, user: User) -> User:
        user.updated_at = datetime.utcnow()
        self.users[user_id] = user
        return user
    
    async def delete_user(self, user_id: str) -> bool:
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False
    
    async def list_users(self, skip: int = 0, limit: int = 10) -> List[User]:
        users_list = list(self.users.values())
        return users_list[skip:skip + limit]
    
    # Book operations
    async def create_book(self, book: Book) -> Book:
        book.id = str(uuid.uuid4())
        book.created_at = datetime.utcnow()
        book.updated_at = datetime.utcnow()
        self.books[book.id] = book
        return book
    
    async def get_book(self, book_id: str) -> Optional[Book]:
        return self.books.get(book_id)
    
    async def update_book(self, book_id: str, book: Book) -> Book:
        book.updated_at = datetime.utcnow()
        self.books[book_id] = book
        return book
    
    async def delete_book(self, book_id: str) -> bool:
        if book_id in self.books:
            del self.books[book_id]
            return True
        return False
    
    async def list_books(self, skip: int = 0, limit: int = 10) -> List[Book]:
        books_list = list(self.books.values())
        return books_list[skip:skip + limit]
    
    async def search_books(self, query: str, skip: int = 0, limit: int = 10) -> List[Book]:
        query_lower = query.lower()
        results = [
            book for book in self.books.values()
            if query_lower in book.title.lower() or query_lower in book.author.lower()
        ]
        return results[skip:skip + limit]
    
    # Review operations
    async def create_review(self, review: Review) -> Review:
        review.id = str(uuid.uuid4())
        review.created_at = datetime.utcnow()
        review.updated_at = datetime.utcnow()
        self.reviews[review.id] = review
        return review
    
    async def get_review(self, review_id: str) -> Optional[Review]:
        return self.reviews.get(review_id)
    
    async def get_reviews_by_book(self, book_id: str, skip: int = 0, limit: int = 10) -> List[Review]:
        reviews = [r for r in self.reviews.values() if r.book_id == book_id]
        return reviews[skip:skip + limit]
    
    async def get_reviews_by_user(self, user_id: str, skip: int = 0, limit: int = 10) -> List[Review]:
        reviews = [r for r in self.reviews.values() if r.user_id == user_id]
        return reviews[skip:skip + limit]
    
    async def update_review(self, review_id: str, review: Review) -> Review:
        review.updated_at = datetime.utcnow()
        self.reviews[review_id] = review
        return review
    
    async def delete_review(self, review_id: str) -> bool:
        if review_id in self.reviews:
            del self.reviews[review_id]
            return True
        return False
    
    # Borrow record operations
    async def create_borrow_record(self, record: BorrowRecord) -> BorrowRecord:
        record.id = str(uuid.uuid4())
        self.borrow_records[record.id] = record
        return record
    
    async def get_borrow_record(self, record_id: str) -> Optional[BorrowRecord]:
        return self.borrow_records.get(record_id)
    
    async def get_active_borrow(self, user_id: str, book_id: str) -> Optional[BorrowRecord]:
        """Get active (non-returned) borrow record for user and book"""
        for record in self.borrow_records.values():
            if record.user_id == user_id and record.book_id == book_id and record.status == "active":
                return record
        return None
    
    async def get_user_borrow_records(self, user_id: str) -> List[BorrowRecord]:
        """Get all borrow records for a user"""
        return [r for r in self.borrow_records.values() if r.user_id == user_id]
    
    async def get_book_borrow_records(self, book_id: str) -> List[BorrowRecord]:
        """Get all borrow records for a book"""
        return [r for r in self.borrow_records.values() if r.book_id == book_id]
    
    async def update_borrow_record(self, record_id: str, record: BorrowRecord) -> BorrowRecord:
        self.borrow_records[record_id] = record
        return record
    
    async def delete_borrow_record(self, record_id: str) -> bool:
        if record_id in self.borrow_records:
            del self.borrow_records[record_id]
            return True
        return False