from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import configuration
from app.core.config import settings
from app.core.di import DIContainer

# Import adapter factories
from app.adapters.llm.llm_factory import LLMAdapterFactory
from app.adapters.file_storage.file_storage_factory import FileStorageAdapterFactory
from app.adapters.db.postgresql_storage import PostgreSQLAdapter
from app.adapters.db.in_memory_storage import InMemoryStorageAdapter
from app.adapters.recommendation.mock_recommendation import MockRecommendationAdapter

# Import services
from app.services.user_service import UserService
from app.services.book_service import BookService
from app.services.review_service import ReviewService

# Import routers
from app.api import users, books, reviews, auth


def _initialize_test_data(storage_adapter: InMemoryStorageAdapter):
    """Initialize test data for in-memory storage"""
    import asyncio
    
    async def init():
        from app.domain.entities import User, Book
        
        # Create test user
        test_user = User(
            id="user_123",
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            full_name="Test User"
        )
        await storage_adapter.create_user(test_user)
        logger.info(f"✅ Created test user: {test_user.username}")
        
        # Create test books
        test_books = [
            {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "genre": "Fiction",
                "description": "A classic American novel",
                "isbn": "978-0-7432-7356-5"
            },
            {
                "title": "To Kill a Mockingbird",
                "author": "Harper Lee",
                "genre": "Fiction",
                "description": "A gripping tale of racial injustice",
                "isbn": "978-0-06-112008-4"
            },
            {
                "title": "1984",
                "author": "George Orwell",
                "genre": "Dystopian",
                "description": "A dystopian social science fiction novel",
                "isbn": "978-0-451-52494-2"
            }
        ]
        
        for book_data in test_books:
            book = Book(**book_data)
            await storage_adapter.create_book(book)
            logger.info(f"✅ Created test book: {book.title}")
    
    try:
        asyncio.run(init())
    except Exception as e:
        logger.error(f"Failed to initialize test data: {e}")


def setup_di_container():
    """
    Setup Dependency Injection Container
    
    This is where all adapters and services are configured.
    Changing configuration here enables switching between:
    - LLM providers (mock → openai → huggingface)
    - Storage backends (local disk → AWS S3)
    
    All done through .env configuration!
    """
    logger.info("🔧 Configuring Dependency Injection Container...")
    
    # ========== DATABASE ADAPTER ==========
    try:
        logger.info(f"📚 Database: {settings.database_url[:50]}...")
        storage_adapter = PostgreSQLAdapter(settings.database_url)
        DIContainer.register_singleton("storage", storage_adapter)
        logger.info("✅ Using PostgreSQL adapter")
    except Exception as db_error:
        logger.warning(f"⚠️  PostgreSQL connection failed: {db_error}")
        logger.info("📚 Falling back to In-Memory Storage for development")
        storage_adapter = InMemoryStorageAdapter()
        DIContainer.register_singleton("storage", storage_adapter)
        logger.info("✅ Using In-Memory Storage adapter")
        # Initialize test data for in-memory storage
        _initialize_test_data(storage_adapter)
    
    # ========== LLM ADAPTER (Config-Driven) ==========
    logger.info(f"🧠 LLM Provider: {settings.llm_provider}")
    llm_adapter = LLMAdapterFactory.create(settings)
    DIContainer.register_singleton("llm", llm_adapter)
    
    # ========== FILE STORAGE ADAPTER (Config-Driven) ==========
    logger.info(f"💾 Storage Type: {settings.storage_type}")
    file_storage_adapter = FileStorageAdapterFactory.create(settings)
    DIContainer.register_singleton("file_storage", file_storage_adapter)
    
    # ========== RECOMMENDATION ADAPTER ==========
    recommendation_adapter = MockRecommendationAdapter(storage_adapter)
    DIContainer.register_singleton("recommendation", recommendation_adapter)
    
    # ========== BUSINESS SERVICES ==========
    # Register services as factories (singletons with dependencies)
    def create_user_service():
        return UserService(storage_adapter)
    
    def create_book_service():
        return BookService(storage_adapter, file_storage_adapter)
    
    def create_review_service():
        return ReviewService(storage_adapter, llm_adapter)
    
    DIContainer.register_factory("user_service", create_user_service)
    DIContainer.register_factory("book_service", create_book_service)
    DIContainer.register_factory("review_service", create_review_service)
    
    logger.info("✅ Dependency Injection Container initialized")
    logger.info(f"📋 Registered dependencies: {len(DIContainer.get_all_registered())}")


# Create lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: startup and shutdown"""
    try:
        # Startup
        logger.info("=" * 60)
        logger.info("🚀 Starting LuminalLib Backend")
        logger.info("=" * 60)
        logger.info(f"Environment: {settings.environment}")
        logger.info(f"Debug: {settings.debug}")
        
        setup_di_container()
        
        logger.info("=" * 60)
        logger.info("✅ LuminalLib Backend Ready!")
        logger.info("=" * 60)
        
        yield
    
    finally:
        # Shutdown
        logger.info("=" * 60)
        logger.info("🛑 Shutting down LuminalLib Backend...")
        logger.info("=" * 60)
        DIContainer.clear()


# Initialize FastAPI app
app = FastAPI(
    title="LuminalLib Backend API",
    description="Hexagonal Architecture with Clean Dependencies & Full Extensibility",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== API ENDPOINTS ==========

@app.get("/")
async def root():
    """Root endpoint - Welcome message"""
    return {
        "message": "Welcome to LuminalLib Backend API",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "luminallib-backend",
        "version": settings.app_version,
        "environment": settings.environment,
        "llm_provider": settings.llm_provider,
        "storage_type": settings.storage_type
    }


@app.get("/config")
async def get_config():
    """Get current configuration (useful for debugging)"""
    return {
        "app": {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment
        },
        "llm": {
            "provider": settings.llm_provider,
            "openai_model": settings.openai_model if settings.llm_provider == "openai" else None,
            "huggingface_model": settings.huggingface_model if settings.llm_provider == "huggingface" else None
        },
        "storage": {
            "type": settings.storage_type,
            "base_url": settings.storage_base_url,
            "local_path": settings.storage_local_base_path if settings.storage_type == "local" else None
        }
    }


# Include API routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(books.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
