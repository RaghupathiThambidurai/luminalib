"""Book service - business logic for book operations"""
import logging
from typing import Optional, List
from datetime import datetime, timedelta
from app.domain.entities import Book, BorrowRecord
from app.ports.storage_port import StoragePort
from app.ports.file_storage_port import FileStoragePort
from app.core.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class BookService:
    """Service for book management and borrowing"""
    
    def __init__(self, storage: StoragePort, file_storage: FileStoragePort):
        self.storage = storage
        self.file_storage = file_storage
    
    async def create_book(self, title: str, author: str, **kwargs) -> Book:
        """Create a new book with optional file upload"""
        import uuid
        
        # Handle file upload if provided
        file_content = kwargs.pop('file_content', None)
        file_name = kwargs.pop('file_name', None)
        
        # Generate book ID upfront so we can use it in the file path
        book_id = str(uuid.uuid4())
        
        book = Book(
            id=book_id,
            title=title,
            author=author,
            **kwargs
        )
        
        # Upload file to storage if provided
        if file_content and file_name:
            try:
                logger.info(f"📤 Uploading file for book: {title}")
                file_path = f"books/{book.id}/{file_name}"
                file_url = await self.file_storage.upload_file(
                    file_path=file_path,
                    file_content=file_content,
                    metadata={
                        "book_title": title,
                        "book_author": author,
                        "upload_date": datetime.utcnow().isoformat()
                    }
                )
                book.file_url = file_url
                logger.info(f"✅ File uploaded successfully: {file_url}")
            except Exception as e:
                logger.error(f"❌ File upload failed: {e}")
                raise ValidationError(f"Failed to upload file: {str(e)}")
        
        # Store book in database
        saved_book = await self.storage.create_book(book)
        logger.info(f"📚 Book saved to database with file_url: {saved_book.file_url}")
        return saved_book
    
    async def get_book(self, book_id: str) -> Book:
        """Get book by ID"""
        book = await self.storage.get_book(book_id)
        if not book:
            raise NotFoundError(f"Book {book_id} not found")
        return book
    
    async def update_book(self, book_id: str, **kwargs) -> Book:
        """Update book information"""
        book = await self.get_book(book_id)
        
        # Update allowed fields (exclude file operations)
        allowed_fields = ['title', 'author', 'description', 'genre', 'isbn', 'cover_url', 'metadata']
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(book, key, value)
        
        return await self.storage.update_book(book_id, book)
    
    async def delete_book(self, book_id: str) -> bool:
        """Delete book and associated files"""
        book = await self.get_book(book_id)
        
        # Delete file from storage if exists
        if book.file_url:
            try:
                file_path = f"books/{book_id}/"
                await self.file_storage.delete_file(file_path)
                logger.info(f"✅ Deleted book file: {book.file_url}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to delete book file: {e}")
        
        return await self.storage.delete_book(book_id)
    
    async def list_books(self, skip: int = 0, limit: int = 10) -> List[Book]:
        """List books"""
        return await self.storage.list_books(skip, limit)
    
    async def search_books(self, query: str, skip: int = 0, limit: int = 10) -> List[Book]:
        """Search books by title or author"""
        return await self.storage.search_books(query, skip, limit)
    
    # Borrow/Return functionality
    
    async def borrow_book(self, book_id: str, user_id: str, due_date_days: int = 14) -> BorrowRecord:
        """
        Borrow a book for a user.
        
        Constraints:
        - User can only borrow if they don't already have an active borrow of this book
        - Due date defaults to 14 days from now
        """
        # Verify book exists
        book = await self.get_book(book_id)
        logger.info(f"📚 User {user_id} borrowing book: {book.title}")
        
        # Check if user already has an active borrow of this book
        existing_borrow = await self.storage.get_active_borrow(user_id, book_id)
        if existing_borrow:
            raise ValidationError(
                f"User already has an active borrow of '{book.title}'. "
                f"Please return the book first."
            )
        
        # Create borrow record
        due_date = datetime.utcnow() + timedelta(days=due_date_days)
        borrow_record = BorrowRecord(
            user_id=user_id,
            book_id=book_id,
            borrowed_at=datetime.utcnow(),
            due_date=due_date,
            status="active"
        )
        
        return await self.storage.create_borrow_record(borrow_record)
    
    async def return_book(self, book_id: str, user_id: str) -> BorrowRecord:
        """
        Return a borrowed book.
        
        Updates the borrow record with return date and status.
        """
        # Verify book exists
        book = await self.get_book(book_id)
        
        # Get active borrow record
        borrow_record = await self.storage.get_active_borrow(user_id, book_id)
        if not borrow_record:
            raise NotFoundError(
                f"No active borrow record found for user {user_id} and book {book.title}"
            )
        
        # Update borrow record
        borrow_record.returned_at = datetime.utcnow()
        borrow_record.status = "returned"
        
        logger.info(f"✅ Book returned: {book.title} by user {user_id}")
        return await self.storage.update_borrow_record(borrow_record.id, borrow_record)
    
    async def get_user_borrowed_books(self, user_id: str, include_returned: bool = False) -> List[dict]:
        """Get all books borrowed by a user"""
        borrow_records = await self.storage.get_user_borrow_records(user_id)
        
        if not include_returned:
            borrow_records = [b for b in borrow_records if b.status != "returned"]
        
        # Enrich with book details
        result = []
        for record in borrow_records:
            book = await self.storage.get_book(record.book_id)
            is_overdue = record.status == "active" and datetime.utcnow() > record.due_date
            
            result.append({
                "borrow_id": record.id,
                "book": book,
                "borrowed_at": record.borrowed_at,
                "due_date": record.due_date,
                "returned_at": record.returned_at,
                "status": record.status,
                "is_overdue": is_overdue,
                "days_remaining": max(0, (record.due_date - datetime.utcnow()).days) if record.status == "active" else 0
            })
        
        return result
    
    async def has_user_borrowed_book(self, user_id: str, book_id: str) -> bool:
        """Check if user has ever borrowed this book (completed borrow)"""
        borrow_records = await self.storage.get_user_borrow_records(user_id)
        for record in borrow_records:
            if record.book_id == book_id and record.status == "returned":
                return True
        return False
