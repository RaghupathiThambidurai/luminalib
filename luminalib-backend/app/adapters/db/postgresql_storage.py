"""PostgreSQL storage adapter using SQLAlchemy"""
from typing import Optional, List
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from app.domain.entities import User, Book, Review, BorrowRecord
from app.ports.storage_port import StoragePort
from app.adapters.db.models import UserModel, BookModel, ReviewModel, BorrowRecordModel, Base
from datetime import datetime
import uuid


class PostgreSQLAdapter(StoragePort):
    """PostgreSQL storage adapter using SQLAlchemy ORM"""

    def __init__(self, database_url: str):
        """Initialize PostgreSQL adapter"""
        # First, ensure the database exists
        self._ensure_database_exists(database_url)
        
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=self.engine)

    def _ensure_database_exists(self, database_url: str):
        """Ensure the target database exists, creating it if necessary"""
        try:
            # Parse the database URL to get the database name
            from urllib.parse import urlparse
            parsed = urlparse(database_url)
            db_name = parsed.path.lstrip('/')
            
            # Create a connection to the default postgres database
            default_url = database_url.replace(f'/{db_name}', '/postgres')
            
            engine = create_engine(default_url, echo=False, isolation_level="AUTOCOMMIT")
            
            with engine.connect() as conn:
                # Check if database exists
                result = conn.execute(
                    text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
                )
                if not result.fetchone():
                    # Database doesn't exist, create it
                    conn.execute(text(f"CREATE DATABASE {db_name}"))
                    print(f"✅ Database '{db_name}' created successfully")
            
            engine.dispose()
        except Exception as e:
            print(f"⚠️  Database pre-check failed: {e}")
            # Continue anyway, the database might already exist

    def _get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()

    def _model_to_entity(self, model_obj) -> dict:
        """Convert SQLAlchemy model to dictionary"""
        if model_obj is None:
            return None
        return {
            'id': model_obj.id,
            'created_at': model_obj.created_at,
            'updated_at': model_obj.updated_at
        }

    # User operations
    async def create_user(self, user: User) -> User:
        """Create a new user"""
        session = self._get_session()
        try:
            user_id = str(uuid.uuid4())
            db_user = UserModel(
                id=user_id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                password_hash=user.password_hash,
                is_active=user.is_active,
                preferences=user.preferences or {}
            )
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            user.id = db_user.id
            user.created_at = db_user.created_at
            user.updated_at = db_user.updated_at
            return user
        finally:
            session.close()

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        session = self._get_session()
        try:
            db_user = session.query(UserModel).filter(UserModel.id == user_id).first()
            if not db_user:
                return None
            return User(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                full_name=db_user.full_name,
                password_hash=db_user.password_hash,
                is_active=db_user.is_active,
                preferences=db_user.preferences or {},
                created_at=db_user.created_at,
                updated_at=db_user.updated_at
            )
        finally:
            session.close()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        session = self._get_session()
        try:
            db_user = session.query(UserModel).filter(UserModel.email == email).first()
            if not db_user:
                return None
            return User(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                full_name=db_user.full_name,
                password_hash=db_user.password_hash,
                is_active=db_user.is_active,
                preferences=db_user.preferences or {},
                created_at=db_user.created_at,
                updated_at=db_user.updated_at
            )
        finally:
            session.close()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        session = self._get_session()
        try:
            db_user = session.query(UserModel).filter(UserModel.username == username).first()
            if not db_user:
                return None
            return User(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                full_name=db_user.full_name,
                password_hash=db_user.password_hash,
                is_active=db_user.is_active,
                preferences=db_user.preferences or {},
                created_at=db_user.created_at,
                updated_at=db_user.updated_at
            )
        finally:
            session.close()

    async def update_user(self, user_id: str, user: User) -> User:
        """Update user"""
        session = self._get_session()
        try:
            db_user = session.query(UserModel).filter(UserModel.id == user_id).first()
            if db_user:
                db_user.full_name = user.full_name
                db_user.is_active = user.is_active
                db_user.preferences = user.preferences or {}
                db_user.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(db_user)
                user.updated_at = db_user.updated_at
            return user
        finally:
            session.close()

    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        session = self._get_session()
        try:
            db_user = session.query(UserModel).filter(UserModel.id == user_id).first()
            if db_user:
                session.delete(db_user)
                session.commit()
                return True
            return False
        finally:
            session.close()

    async def list_users(self, skip: int = 0, limit: int = 10) -> List[User]:
        """List users"""
        session = self._get_session()
        try:
            db_users = session.query(UserModel).offset(skip).limit(limit).all()
            return [
                User(
                    id=db_user.id,
                    username=db_user.username,
                    email=db_user.email,
                    full_name=db_user.full_name,
                    password_hash=db_user.password_hash,
                    is_active=db_user.is_active,
                    preferences=db_user.preferences or {},
                    created_at=db_user.created_at,
                    updated_at=db_user.updated_at
                )
                for db_user in db_users
            ]
        finally:
            session.close()

    # Book operations
    async def create_book(self, book: Book) -> Book:
        """Create a new book"""
        session = self._get_session()
        try:
            # Use provided book ID if available, otherwise generate one
            book_id = book.id or str(uuid.uuid4())
            db_book = BookModel(
                id=book_id,
                title=book.title,
                author=book.author,
                isbn=book.isbn,
                description=book.description,
                genre=book.genre,
                published_date=book.published_date,
                cover_url=book.cover_url,
                file_url=book.file_url,
                file_size=book.file_size,
                book_metadata=book.metadata or {}
            )
            session.add(db_book)
            session.commit()
            session.refresh(db_book)
            book.id = db_book.id
            book.created_at = db_book.created_at
            book.updated_at = db_book.updated_at
            book.file_url = db_book.file_url
            book.file_size = db_book.file_size
            return book
        finally:
            session.close()

    async def get_book(self, book_id: str) -> Optional[Book]:
        """Get book by ID"""
        session = self._get_session()
        try:
            db_book = session.query(BookModel).filter(BookModel.id == book_id).first()
            if not db_book:
                return None
            return Book(
                id=db_book.id,
                title=db_book.title,
                author=db_book.author,
                isbn=db_book.isbn,
                description=db_book.description,
                genre=db_book.genre,
                published_date=db_book.published_date,
                cover_url=db_book.cover_url,
                file_url=db_book.file_url,
                file_size=db_book.file_size,
                metadata=db_book.book_metadata or {},
                created_at=db_book.created_at,
                updated_at=db_book.updated_at
            )
        finally:
            session.close()

    async def update_book(self, book_id: str, book: Book) -> Book:
        """Update book"""
        session = self._get_session()
        try:
            db_book = session.query(BookModel).filter(BookModel.id == book_id).first()
            if db_book:
                db_book.title = book.title
                db_book.author = book.author
                db_book.isbn = book.isbn
                db_book.description = book.description
                db_book.genre = book.genre
                db_book.cover_url = book.cover_url
                db_book.file_url = book.file_url
                db_book.file_size = book.file_size
                db_book.book_metadata = book.metadata or {}
                db_book.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(db_book)
                book.updated_at = db_book.updated_at
            return book
        finally:
            session.close()

    async def delete_book(self, book_id: str) -> bool:
        """Delete book"""
        session = self._get_session()
        try:
            db_book = session.query(BookModel).filter(BookModel.id == book_id).first()
            if db_book:
                session.delete(db_book)
                session.commit()
                return True
            return False
        finally:
            session.close()

    async def list_books(self, skip: int = 0, limit: int = 10) -> List[Book]:
        """List books"""
        session = self._get_session()
        try:
            db_books = session.query(BookModel).offset(skip).limit(limit).all()
            return [
                Book(
                    id=db_book.id,
                    title=db_book.title,
                    author=db_book.author,
                    isbn=db_book.isbn,
                    description=db_book.description,
                    genre=db_book.genre,
                    published_date=db_book.published_date,
                    cover_url=db_book.cover_url,
                    file_url=db_book.file_url,
                    file_size=db_book.file_size,
                    metadata=db_book.book_metadata or {},
                    created_at=db_book.created_at,
                    updated_at=db_book.updated_at
                )
                for db_book in db_books
            ]
        finally:
            session.close()

    async def search_books(self, query: str, skip: int = 0, limit: int = 10) -> List[Book]:
        """Search books by title or author"""
        session = self._get_session()
        try:
            query_lower = f"%{query.lower()}%"
            db_books = session.query(BookModel).filter(
                (BookModel.title.ilike(query_lower)) |
                (BookModel.author.ilike(query_lower))
            ).offset(skip).limit(limit).all()
            return [
                Book(
                    id=db_book.id,
                    title=db_book.title,
                    author=db_book.author,
                    isbn=db_book.isbn,
                    description=db_book.description,
                    genre=db_book.genre,
                    published_date=db_book.published_date,
                    cover_url=db_book.cover_url,
                    file_url=db_book.file_url,
                    file_size=db_book.file_size,
                    metadata=db_book.book_metadata or {},
                    created_at=db_book.created_at,
                    updated_at=db_book.updated_at
                )
                for db_book in db_books
            ]
        finally:
            session.close()

    # Review operations
    async def create_review(self, review: Review) -> Review:
        """Create a new review"""
        session = self._get_session()
        try:
            review_id = str(uuid.uuid4())
            db_review = ReviewModel(
                id=review_id,
                user_id=review.user_id,
                book_id=review.book_id,
                rating=review.rating,
                content=review.content,
                is_helpful=review.is_helpful,
                helpful_count=review.helpful_count
            )
            session.add(db_review)
            session.commit()
            session.refresh(db_review)
            review.id = db_review.id
            review.created_at = db_review.created_at
            review.updated_at = db_review.updated_at
            return review
        finally:
            session.close()

    async def get_review(self, review_id: str) -> Optional[Review]:
        """Get review by ID"""
        session = self._get_session()
        try:
            db_review = session.query(ReviewModel).filter(ReviewModel.id == review_id).first()
            if not db_review:
                return None
            return Review(
                id=db_review.id,
                user_id=db_review.user_id,
                book_id=db_review.book_id,
                rating=db_review.rating,
                content=db_review.content,
                is_helpful=db_review.is_helpful,
                helpful_count=db_review.helpful_count,
                created_at=db_review.created_at,
                updated_at=db_review.updated_at
            )
        finally:
            session.close()

    async def get_reviews_by_book(self, book_id: str, skip: int = 0, limit: int = 10) -> List[Review]:
        """Get reviews for a book"""
        session = self._get_session()
        try:
            db_reviews = session.query(ReviewModel).filter(
                ReviewModel.book_id == book_id
            ).offset(skip).limit(limit).all()
            return [
                Review(
                    id=db_review.id,
                    user_id=db_review.user_id,
                    book_id=db_review.book_id,
                    rating=db_review.rating,
                    content=db_review.content,
                    sentiment_score=db_review.sentiment_score,
                    is_helpful=db_review.is_helpful,
                    helpful_count=db_review.helpful_count,
                    created_at=db_review.created_at,
                    updated_at=db_review.updated_at
                )
                for db_review in db_reviews
            ]
        finally:
            session.close()

    async def get_reviews_by_user(self, user_id: str, skip: int = 0, limit: int = 10) -> List[Review]:
        """Get reviews by a user"""
        session = self._get_session()
        try:
            db_reviews = session.query(ReviewModel).filter(
                ReviewModel.user_id == user_id
            ).offset(skip).limit(limit).all()
            return [
                Review(
                    id=db_review.id,
                    user_id=db_review.user_id,
                    book_id=db_review.book_id,
                    rating=db_review.rating,
                    content=db_review.content,
                    sentiment_score=db_review.sentiment_score,
                    is_helpful=db_review.is_helpful,
                    helpful_count=db_review.helpful_count,
                    created_at=db_review.created_at,
                    updated_at=db_review.updated_at
                )
                for db_review in db_reviews
            ]
        finally:
            session.close()

    async def update_review(self, review_id: str, review: Review) -> Review:
        """Update review"""
        session = self._get_session()
        try:
            db_review = session.query(ReviewModel).filter(ReviewModel.id == review_id).first()
            if db_review:
                db_review.rating = review.rating
                db_review.content = review.content
                db_review.sentiment_score = review.sentiment_score
                db_review.is_helpful = review.is_helpful
                db_review.helpful_count = review.helpful_count
                db_review.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(db_review)
                review.updated_at = db_review.updated_at
            return review
        finally:
            session.close()

    async def delete_review(self, review_id: str) -> bool:
        """Delete review"""
        session = self._get_session()
        try:
            db_review = session.query(ReviewModel).filter(ReviewModel.id == review_id).first()
            if db_review:
                session.delete(db_review)
                session.commit()
                return True
            return False
        finally:
            session.close()

    # Borrow record operations
    async def create_borrow_record(self, record: BorrowRecord) -> BorrowRecord:
        """Create a new borrow record"""
        session = self._get_session()
        try:
            record_id = str(uuid.uuid4())
            db_record = BorrowRecordModel(
                id=record_id,
                user_id=record.user_id,
                book_id=record.book_id,
                borrowed_at=record.borrowed_at,
                due_date=record.due_date,
                returned_at=record.returned_at,
                status=record.status
            )
            session.add(db_record)
            session.commit()
            session.refresh(db_record)
            record.id = db_record.id
            return record
        finally:
            session.close()

    async def get_borrow_record(self, record_id: str) -> Optional[BorrowRecord]:
        """Get borrow record by ID"""
        session = self._get_session()
        try:
            db_record = session.query(BorrowRecordModel).filter(BorrowRecordModel.id == record_id).first()
            if not db_record:
                return None
            return BorrowRecord(
                id=db_record.id,
                user_id=db_record.user_id,
                book_id=db_record.book_id,
                borrowed_at=db_record.borrowed_at,
                due_date=db_record.due_date,
                returned_at=db_record.returned_at,
                status=db_record.status
            )
        finally:
            session.close()

    async def get_active_borrow(self, user_id: str, book_id: str) -> Optional[BorrowRecord]:
        """Get active (non-returned) borrow record for user and book"""
        session = self._get_session()
        try:
            db_record = session.query(BorrowRecordModel).filter(
                BorrowRecordModel.user_id == user_id,
                BorrowRecordModel.book_id == book_id,
                BorrowRecordModel.status == "active"
            ).first()
            if not db_record:
                return None
            return BorrowRecord(
                id=db_record.id,
                user_id=db_record.user_id,
                book_id=db_record.book_id,
                borrowed_at=db_record.borrowed_at,
                due_date=db_record.due_date,
                returned_at=db_record.returned_at,
                status=db_record.status
            )
        finally:
            session.close()

    async def get_user_borrow_records(self, user_id: str) -> List[BorrowRecord]:
        """Get all borrow records for a user"""
        session = self._get_session()
        try:
            db_records = session.query(BorrowRecordModel).filter(
                BorrowRecordModel.user_id == user_id
            ).all()
            return [
                BorrowRecord(
                    id=r.id,
                    user_id=r.user_id,
                    book_id=r.book_id,
                    borrowed_at=r.borrowed_at,
                    due_date=r.due_date,
                    returned_at=r.returned_at,
                    status=r.status
                )
                for r in db_records
            ]
        finally:
            session.close()

    async def get_book_borrow_records(self, book_id: str) -> List[BorrowRecord]:
        """Get all borrow records for a book"""
        session = self._get_session()
        try:
            db_records = session.query(BorrowRecordModel).filter(
                BorrowRecordModel.book_id == book_id
            ).all()
            return [
                BorrowRecord(
                    id=r.id,
                    user_id=r.user_id,
                    book_id=r.book_id,
                    borrowed_at=r.borrowed_at,
                    due_date=r.due_date,
                    returned_at=r.returned_at,
                    status=r.status
                )
                for r in db_records
            ]
        finally:
            session.close()

    async def update_borrow_record(self, record_id: str, record: BorrowRecord) -> BorrowRecord:
        """Update borrow record"""
        session = self._get_session()
        try:
            db_record = session.query(BorrowRecordModel).filter(BorrowRecordModel.id == record_id).first()
            if db_record:
                db_record.returned_at = record.returned_at
                db_record.status = record.status
                session.commit()
                session.refresh(db_record)
            return record
        finally:
            session.close()

    async def delete_borrow_record(self, record_id: str) -> bool:
        """Delete borrow record"""
        session = self._get_session()
        try:
            db_record = session.query(BorrowRecordModel).filter(BorrowRecordModel.id == record_id).first()
            if db_record:
                session.delete(db_record)
                session.commit()
                return True
            return False
        finally:
            session.close()