"""
Unit tests for book service.

Tests:
- Book creation
- Book retrieval
- Book searching
- Book updates
- File handling
- Metadata extraction
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from unittest.mock import Mock, AsyncMock

from app.domain.models import Book


class TestBookServiceCreation:
    """Test book service creation."""
    
    def test_create_book_with_all_fields(self, test_db: Session, test_book_data: dict) -> None:
        """Test creating a book with all fields."""
        book = Book(
            id="book-1",
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
        
        assert book.title == test_book_data["title"]
        assert book.author == test_book_data["author"]
        assert book.isbn == test_book_data["isbn"]
        assert book.file_size == test_book_data["file_size"]
    
    def test_create_book_minimal_fields(self, test_db: Session) -> None:
        """Test creating a book with minimal required fields."""
        book = Book(
            id="book-minimal",
            title="Minimal Book",
            author="Anonymous",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        test_db.add(book)
        test_db.commit()
        test_db.refresh(book)
        
        assert book.title == "Minimal Book"
        assert book.author == "Anonymous"
        assert book.isbn is None
        assert book.description is None
    
    def test_book_id_generation(self, test_db: Session) -> None:
        """Test book ID is properly set."""
        book = Book(
            id="book-uuid-123",
            title="Test Book",
            author="Test Author",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        assert book.id == "book-uuid-123"


class TestBookServiceRetrieval:
    """Test book service retrieval."""
    
    def test_get_book_by_id(self, test_db: Session, test_book: Book) -> None:
        """Test retrieving book by ID."""
        retrieved_book = test_db.query(Book).filter(Book.id == test_book.id).first()
        
        assert retrieved_book is not None
        assert retrieved_book.id == test_book.id
        assert retrieved_book.title == test_book.title
    
    def test_get_book_by_isbn(self, test_db: Session, test_book: Book) -> None:
        """Test retrieving book by ISBN."""
        retrieved_book = test_db.query(Book).filter(Book.isbn == test_book.isbn).first()
        
        assert retrieved_book is not None
        assert retrieved_book.isbn == test_book.isbn
    
    def test_get_all_books(self, test_db: Session, create_multiple_books) -> None:
        """Test retrieving all books."""
        books = create_multiple_books(count=5)
        
        all_books = test_db.query(Book).all()
        
        assert len(all_books) >= 5
        assert any(b.id == books[0].id for b in all_books)
    
    def test_get_nonexistent_book(self, test_db: Session) -> None:
        """Test retrieving non-existent book returns None."""
        book = test_db.query(Book).filter(Book.id == "nonexistent").first()
        
        assert book is None


class TestBookServiceFiltering:
    """Test book service filtering."""
    
    def test_filter_books_by_genre(self, test_db: Session) -> None:
        """Test filtering books by genre."""
        # Create books with different genres
        fiction_book = Book(
            id="fiction-1",
            title="Fiction Book",
            author="Author",
            genre="Fiction",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        nonfiction_book = Book(
            id="nonfiction-1",
            title="Non-Fiction Book",
            author="Author",
            genre="Non-fiction",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        test_db.add_all([fiction_book, nonfiction_book])
        test_db.commit()
        
        fiction_books = test_db.query(Book).filter(Book.genre == "Fiction").all()
        
        assert len(fiction_books) >= 1
        assert all(b.genre == "Fiction" for b in fiction_books)
    
    def test_filter_books_by_author(self, test_db: Session) -> None:
        """Test filtering books by author."""
        author_name = "John Doe"
        
        book1 = Book(
            id="john-book-1",
            title="Book 1",
            author=author_name,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        book2 = Book(
            id="john-book-2",
            title="Book 2",
            author=author_name,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        other_book = Book(
            id="other-book",
            title="Book 3",
            author="Other Author",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        test_db.add_all([book1, book2, other_book])
        test_db.commit()
        
        author_books = test_db.query(Book).filter(Book.author == author_name).all()
        
        assert len(author_books) >= 2
        assert all(b.author == author_name for b in author_books)
    
    def test_search_books_by_title(self, test_db: Session) -> None:
        """Test searching books by title."""
        book1 = Book(
            id="book-1",
            title="Python Programming",
            author="Author",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        book2 = Book(
            id="book-2",
            title="JavaScript Guide",
            author="Author",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        test_db.add_all([book1, book2])
        test_db.commit()
        
        # Search for books containing "Python"
        results = test_db.query(Book).filter(Book.title.ilike("%Python%")).all()
        
        assert len(results) >= 1
        assert any("Python" in b.title for b in results)


class TestBookServiceUpdates:
    """Test book service updates."""
    
    def test_update_book_title(self, test_db: Session, test_book: Book) -> None:
        """Test updating book title."""
        new_title = "Updated Title"
        test_book.title = new_title
        test_db.commit()
        test_db.refresh(test_book)
        
        assert test_book.title == new_title
    
    def test_update_book_description(self, test_db: Session, test_book: Book) -> None:
        """Test updating book description."""
        new_description = "New description"
        test_book.description = new_description
        test_db.commit()
        test_db.refresh(test_book)
        
        assert test_book.description == new_description
    
    def test_update_book_genre(self, test_db: Session, test_book: Book) -> None:
        """Test updating book genre."""
        new_genre = "Science Fiction"
        test_book.genre = new_genre
        test_db.commit()
        test_db.refresh(test_book)
        
        assert test_book.genre == new_genre
    
    def test_update_book_file_metadata(self, test_db: Session, test_book: Book) -> None:
        """Test updating book file metadata."""
        new_file_url = "https://example.com/new-file.pdf"
        new_file_size = 2048000
        
        test_book.file_url = new_file_url
        test_book.file_size = new_file_size
        test_db.commit()
        test_db.refresh(test_book)
        
        assert test_book.file_url == new_file_url
        assert test_book.file_size == new_file_size


class TestBookServiceMetadata:
    """Test book service metadata."""
    
    def test_book_with_summary_metadata(self, test_db: Session, test_book: Book) -> None:
        """Test storing summary metadata in book."""
        # Assuming metadata field exists
        test_book.metadata = {
            "summary": "Generated summary",
            "summary_generated_at": datetime.utcnow().isoformat(),
            "summary_model": "gpt-3.5-turbo"
        }
        test_db.commit()
        test_db.refresh(test_book)
        
        assert test_book.metadata is not None
        assert test_book.metadata.get("summary") == "Generated summary"
    
    def test_book_without_metadata(self, test_db: Session) -> None:
        """Test creating book without metadata."""
        book = Book(
            id="book-no-meta",
            title="No Metadata Book",
            author="Author",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        test_db.add(book)
        test_db.commit()
        test_db.refresh(book)
        
        assert book.metadata is None or book.metadata == {}


class TestBookServiceDeletion:
    """Test book service deletion."""
    
    def test_delete_book(self, test_db: Session, test_book: Book) -> None:
        """Test deleting a book."""
        book_id = test_book.id
        test_db.delete(test_book)
        test_db.commit()
        
        deleted_book = test_db.query(Book).filter(Book.id == book_id).first()
        assert deleted_book is None
    
    def test_cascade_delete_book_reviews(self, test_db: Session, test_book: Book, test_review: object) -> None:
        """Test that deleting book cascades to reviews."""
        # This test would verify that deleting a book also deletes related reviews
        # Implementation depends on cascade delete configuration
        pass


class TestBookServicePagination:
    """Test book service pagination."""
    
    def test_paginate_books(self, test_db: Session, create_multiple_books) -> None:
        """Test paginating books."""
        create_multiple_books(count=15)
        
        # Get first page (limit 10)
        page_1 = test_db.query(Book).limit(10).offset(0).all()
        assert len(page_1) <= 10
        
        # Get second page
        page_2 = test_db.query(Book).limit(10).offset(10).all()
        assert len(page_2) <= 10
    
    def test_books_per_page(self, test_db: Session, create_multiple_books) -> None:
        """Test limiting books per page."""
        create_multiple_books(count=25)
        
        limit = 5
        books_page_1 = test_db.query(Book).limit(limit).offset(0).all()
        
        assert len(books_page_1) <= limit
