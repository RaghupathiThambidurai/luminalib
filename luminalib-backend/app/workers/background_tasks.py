"""Async tasks and background workers"""
import asyncio
import logging
from typing import Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class TaskQueue:
    """Simple async task queue for background jobs"""
    
    def __init__(self):
        self.tasks: list[Callable] = []
    
    def enqueue(self, task: Callable):
        """Add a task to the queue"""
        self.tasks.append(task)
    
    async def process(self):
        """Process all tasks in the queue"""
        while self.tasks:
            task = self.tasks.pop(0)
            if asyncio.iscoroutinefunction(task):
                await task()
            else:
                task()


class BackgroundWorker:
    """Background worker for async tasks"""
    
    @staticmethod
    async def update_recommendations(user_id: str, book_id: str, rating: int):
        """Update user recommendations based on new review"""
        # This would be called asynchronously when a user rates a book
        logger.info(f"📊 Updating recommendations for user {user_id} - rated book {book_id} with {rating} stars")
        # TODO: Implement recommendation update logic
        await asyncio.sleep(1)  # Simulate async work
    
    @staticmethod
    async def generate_summary(book_id: str):
        """
        Generate summary for a book using LLM.
        
        This runs asynchronously after book creation.
        
        Process:
        1. Retrieve book from database
        2. Download file from storage
        3. Extract text from file
        4. Generate summary using LLM
        5. Save summary back to database
        
        Args:
            book_id: ID of the book to summarize
        """
        from app.core.di import DIContainer
        from app.utils.file_extraction import extract_text_from_file, truncate_text
        
        try:
            logger.info(f"📝 Starting summary generation for book {book_id}")
            
            # Get services from DI container
            book_service = DIContainer.get("book_service")
            file_storage = DIContainer.get("file_storage")
            llm_adapter = DIContainer.get("llm")
            
            logger.info(f"   Services retrieved: book_service={book_service}, llm={llm_adapter.__class__.__name__}")
            
            # ============ STEP 1: Get book ============
            book = await book_service.get_book(book_id)
            
            if not book:
                logger.error(f"❌ Book not found: {book_id}")
                return
            
            logger.info(f"   📖 Book: {book.title} by {book.author}")
            logger.info(f"   📋 Book ID: {book.id}")
            logger.info(f"   📋 Book.file_url: {repr(book.file_url)}")
            logger.info(f"   📋 Book.file_url is None: {book.file_url is None}")
            logger.info(f"   📋 Book.file_url bool: {bool(book.file_url)}")
            
            if not book.file_url:
                logger.warning(f"⚠️  Book {book_id} has no file (file_url={repr(book.file_url)}), skipping summary")
                return
            
            # ============ STEP 2: Download file ============
            logger.debug(f"   Downloading file: {book.file_url}")
            try:
                # Extract file path from URL (e.g., "http://localhost:8000/files/books/123/file.txt" -> "books/123/file.txt")
                file_path = book.file_url.split('/files/')[-1]
                logger.debug(f"   Extracted file path: {file_path}")
                
                file_content = await file_storage.download_file(file_path)
                logger.debug(f"   Downloaded {len(file_content)} bytes")
            except Exception as e:
                logger.error(f"   ❌ Failed to download file: {e}")
                return
            
            # ============ STEP 3: Extract text ============
            logger.debug(f"   Extracting text from {book.file_url}")
            try:
                # Get file name from URL (last part after /)
                file_name = book.file_url.split('/')[-1]
                extracted_text = await extract_text_from_file(file_name, file_content)
                logger.debug(f"   ✓ Extracted {len(extracted_text)} characters")
            except Exception as e:
                logger.error(f"   ❌ Failed to extract text: {e}")
                return
            
            if not extracted_text or len(extracted_text.strip()) < 100:
                logger.warning(f"   ⚠️  Not enough text extracted ({len(extracted_text)} chars)")
                return
            
            # ============ STEP 4: Generate summary ============
            # Truncate to prevent overwhelming the LLM
            # Most LLMs work better with 5000-10000 character inputs
            text_for_summary = truncate_text(extracted_text, max_chars=10000)
            
            logger.debug(f"   Generating summary from {len(text_for_summary)} characters...")
            try:
                summary = await llm_adapter.generate_summary(
                    text_for_summary,
                    max_length=300  # Target ~300 words
                )
                logger.debug(f"   ✓ Generated summary: {len(summary)} characters")
            except Exception as e:
                logger.error(f"   ❌ Failed to generate summary: {e}")
                return
            
            # ============ STEP 5: Save to database ============
            logger.debug(f"   Saving summary to database...")
            try:
                # Initialize metadata if needed
                if book.metadata is None:
                    book.metadata = {}
                
                # Update with summary
                book.metadata['summary'] = summary
                book.metadata['summary_generated_at'] = datetime.utcnow().isoformat()
                book.metadata['summary_model'] = llm_adapter.__class__.__name__
                
                # Save back to database
                await book_service.update_book(book_id, metadata=book.metadata)
                
            except Exception as e:
                logger.error(f"   ❌ Failed to save summary: {e}")
                return
            
            # ============ SUCCESS ============
            logger.info(f"✅ Summary generated successfully for book {book_id}")
            logger.info(f"   Title: {book.title}")
            logger.info(f"   Summary preview: {summary[:100]}...")
            
        except Exception as e:
            logger.error(f"❌ Unexpected error in generate_summary: {e}", exc_info=True)
    
    @staticmethod
    async def send_notification(user_id: str, message: str):
        """Send notification to user"""
        logger.info(f"🔔 Sending notification to user {user_id}: {message}")
        # TODO: Implement notification sending
        await asyncio.sleep(1)  # Simulate async work
