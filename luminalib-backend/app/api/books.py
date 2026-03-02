"""Book routes - Book ingestion, management, and borrowing"""
import asyncio
import logging
from fastapi import APIRouter, HTTPException, Depends, Query, File, UploadFile, Form, status, BackgroundTasks
from typing import List, Optional
from datetime import datetime
from app.domain.entities import Book, BookCreate, BookUpdate, BorrowRecord
from app.services.book_service import BookService
from app.workers.background_tasks import BackgroundWorker
from app.core.exceptions import NotFoundError, ValidationError
from app.core.security import HTTPBearer, security
from app.api.auth import get_current_user
from app.domain.entities import UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/books",
    tags=["books"],
    responses={404: {"description": "Not found"}},
)


# Dependency to get BookService
async def get_book_service() -> BookService:
    """Get book service instance"""
    from app.core.di import DIContainer
    return DIContainer.get("book_service")


@router.post("/", response_model=Book, status_code=201)
async def create_book(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    author: str = Form(...),
    file: Optional[UploadFile] = File(None),
    isbn: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    genre: Optional[str] = Form(None),
    published_date: Optional[str] = Form(None),
    cover_url: Optional[str] = Form(None),
    authorization: Optional[HTTPBearer] = Depends(security),
    service: BookService = Depends(get_book_service)
):
    """
    Create a new book with optional file upload.
    
    **Book Ingestion Process:**
    - Accepts multipart form data with book metadata
    - Optional file upload (PDF, EPUB, MOBI - max 100MB)
    - Files are stored via FileStoragePort (local or S3)
    - Book metadata and file reference stored in database
    - Triggers async summary generation (if file provided)
    
    **Request:**
    - title (required): Book title
    - author (required): Author name
    - file (optional): Book file (PDF, EPUB, MOBI)
    - isbn, description, genre, published_date, cover_url (optional)
    
    **Response:**
    - Complete Book entity with file_url and file_size
    """
    try:
        logger.info(f"📚 Creating book: {title} by {author}")
        
        # Parse published_date if provided
        parsed_date = None
        if published_date:
            try:
                parsed_date = datetime.fromisoformat(published_date)
            except ValueError:
                raise ValidationError(f"Invalid date format: {published_date}")
        
        # Prepare file content if uploaded
        file_content = None
        file_name = None
        file_size = None
        
        if file:
            logger.info(f"📤 Processing file upload: {file.filename}")
            
            # Validate file type
            allowed_types = {"application/pdf", "application/epub+zip", "application/x-mobipocket-ebook", "text/plain"}
            if file.content_type not in allowed_types:
                raise ValidationError(
                    f"❌ Unsupported file type: {file.content_type}. "
                    f"Allowed: PDF, EPUB, MOBI, TXT"
                )
            
            # Read and validate file size
            file_content = await file.read()
            file_size = len(file_content)
            max_size_mb = 100
            
            if file_size > max_size_mb * 1024 * 1024:
                raise ValidationError(
                    f"❌ File too large. Maximum size is {max_size_mb}MB, "
                    f"got {file_size / (1024*1024):.2f}MB"
                )
            
            file_name = file.filename
            logger.info(f"✅ File validation passed: {file_size / 1024:.2f}KB")
        
        # Create book (handles file upload via FileStoragePort)
        book = await service.create_book(
            title=title,
            author=author,
            isbn=isbn,
            description=description,
            genre=genre,
            published_date=parsed_date,
            cover_url=cover_url,
            file_content=file_content,
            file_name=file_name,
            file_size=file_size,
            metadata={"summary_task_id": None, "ingestion_date": datetime.utcnow().isoformat()}
        )
        
        logger.info(f"✅ Book created successfully: {book.id}")
        
        # ============ TRIGGER ASYNC SUMMARY GENERATION ============
        # If a file was uploaded, queue summary generation as background task
        if book.file_url:
            logger.info(f"📝 Queuing summary generation for book {book.id}")
            # Add background task that will run after response is sent
            background_tasks.add_task(BackgroundWorker.generate_summary, book.id)
            logger.debug(f"   Summary generation queued (will run in background)")
        
        return book
        
    except ValidationError as e:
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Server error creating book: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=dict)
async def list_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    genre: Optional[str] = Query(None),
    sort: Optional[str] = Query("created_at"),
    order: Optional[str] = Query("desc"),
    service: BookService = Depends(get_book_service)
):
    """List all books with pagination"""
    try:
        books = await service.list_books(skip, limit)
        # TODO: Get actual count from database
        total = len(books) + skip
        
        return {
            "books": books,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/my-borrows", response_model=dict)
async def get_my_borrowed_books(
    include_returned: bool = Query(False, description="Include returned books in response"),
    authorization: HTTPBearer = Depends(security),
    current_user: UserResponse = Depends(get_current_user),
    service: BookService = Depends(get_book_service)
):
    """
    Get list of books currently borrowed by authenticated user.
    
    **Fields:**
    - borrowed_books: Array of books with borrow details
    - active_count: Number of currently borrowed books
    - overdue_count: Number of overdue books
    - total_count: Total number of borrows (including returned)
    
    **Optional:**
    - include_returned: Set to true to include returned books
    """
    try:
        logger.info(f"📚 Getting borrowed books for user")
        
        # Extract user_id from authorization token
        # TODO: Extract from actual JWT token
        # user_id = authorization.credentials if authorization else "user_anonymous"
        # current_user: UserResponse = Depends(get_current_user)
        user_id = current_user.id
        
        borrowed = await service.get_user_borrowed_books(user_id, include_returned)
        active = [b for b in borrowed if b.get("status") == "active"]
        overdue = [b for b in borrowed if b.get("is_overdue")]
        
        return {
            "borrowed_books": borrowed,
            "active_count": len(active),
            "overdue_count": len(overdue),
            "total_count": len(borrowed),
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"❌ Error fetching borrowed books: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: str, service: BookService = Depends(get_book_service)):
    """Get detailed information about a specific book"""
    try:
        book = await service.get_book(book_id)
        if not book:
            raise HTTPException(status_code=404, detail=f"Book {book_id} not found")
        return book
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{book_id}", response_model=Book)
async def update_book(
    book_id: str,
    title: str = None,
    author: str = None,
    description: str = None,
    genre: str = None,
    isbn: str = None,
    cover_url: str = None,
    authorization: HTTPBearer = Depends(security),
    service: BookService = Depends(get_book_service)
):
    """Update book metadata"""
    try:
        updates = {}
        if title is not None:
            updates['title'] = title
        if author is not None:
            updates['author'] = author
        if description is not None:
            updates['description'] = description
        if genre is not None:
            updates['genre'] = genre
        if isbn is not None:
            updates['isbn'] = isbn
        if cover_url is not None:
            updates['cover_url'] = cover_url
        
        book = await service.update_book(book_id, **updates)
        return book
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{book_id}", status_code=204)
async def delete_book(
    book_id: str,
    authorization: HTTPBearer = Depends(security),
    service: BookService = Depends(get_book_service)
):
    """Delete book and associated files"""
    try:
        await service.delete_book(book_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/search/{query}", response_model=dict)
async def search_books(
    query: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: BookService = Depends(get_book_service)
):
    """Search books by title, author, or description"""
    try:
        books = await service.search_books(query, skip, limit)
        
        return {
            "books": books,
            "total": len(books),
            "query": query,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < len(books)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Book Borrowing Endpoints

@router.post("/{book_id}/borrow", response_model=dict, status_code=201)
async def borrow_book(
    book_id: str,
    due_date_days: int = Query(14, ge=1, le=60, description="Number of days to borrow (max 60)"),
    authorization: HTTPBearer = Depends(security),
    current_user: UserResponse = Depends(get_current_user),
    service: BookService = Depends(get_book_service)
):
    """
    Borrow a book for the authenticated user.
    
    **Constraints:**
    - User cannot borrow if they already have an active borrow of this book
    - Due date defaults to 14 days from now
    - User must return a book before borrowing another copy
    
    **Response:**
    - Borrow record with due_date and status
    
    **Note:** Users can only review books they have borrowed.
    """
    try:
        logger.info(f"📚 Borrow request: book_id={book_id}, days={due_date_days}")
        
        # Extract user_id from authorization token
        # TODO: Extract from actual JWT token
        # user_id = authorization.credentials if authorization else "user_anonymous"
        # current_user: UserResponse = Depends(get_current_user)
        user_id = current_user.id
        
        borrow_record = await service.borrow_book(book_id, user_id, due_date_days)
        
        return {
            "borrow_id": borrow_record.id,
            "user_id": borrow_record.user_id,
            "book_id": borrow_record.book_id,
            "borrowed_at": borrow_record.borrowed_at.isoformat(),
            "due_date": borrow_record.due_date.isoformat(),
            "status": borrow_record.status,
            "message": f"✅ Book borrowed successfully. Due date: {borrow_record.due_date.date()}"
        }
    except ValidationError as e:
        logger.warning(f"⚠️ Borrow validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except NotFoundError as e:
        logger.warning(f"⚠️ Book not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Borrow error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{book_id}/return", status_code=200)
async def return_book(
    book_id: str,
    authorization: HTTPBearer = Depends(security),
    current_user: UserResponse = Depends(get_current_user),
    service: BookService = Depends(get_book_service)
):
    """
    Return a borrowed book.
    
    **Behavior:**
    - Updates the borrow record with return_date and marks status as "returned"
    - User can now borrow another copy or write a review
    
    **Response:**
    - Updated borrow record with return confirmation
    """
    try:
        logger.info(f"📚 Return request: book_id={book_id}")
        
        # Extract user_id from authorization token
        # TODO: Extract from actual JWT token
        # user_id = authorization.credentials if authorization else "user_anonymous"
        # current_user: UserResponse = Depends(get_current_user)
        user_id = current_user.id
        
        borrow_record = await service.return_book(book_id, user_id)
        
        return {
            "borrow_id": borrow_record.id,
            "user_id": borrow_record.user_id,
            "book_id": borrow_record.book_id,
            "borrowed_at": borrow_record.borrowed_at.isoformat(),
            "returned_at": borrow_record.returned_at.isoformat() if borrow_record.returned_at else None,
            "status": borrow_record.status,
            "message": "✅ Book returned successfully"
        }
    except ValidationError as e:
        logger.warning(f"⚠️ Return validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except NotFoundError as e:
        logger.warning(f"⚠️ Borrow record not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Return error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
