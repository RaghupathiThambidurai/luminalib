"""Application configuration with full extensibility"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application Settings - Centralized Configuration
    
    All settings can be overridden via:
    1. Environment variables
    2. .env file
    3. Constructor parameters
    
    Key Features:
    - Adapter swapping via single config change
    - Environment-specific configs (dev, staging, prod)
    - Type-safe settings with validation
    - Documented defaults
    
    Usage:
        from app.core.config import settings
        print(settings.llm_provider)  # Access settings
    """
    
    # ========== APPLICATION SETTINGS ==========
    app_name: str = "LuminalLib"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"  # development, staging, production
    
    # ========== SERVER SETTINGS ==========
    host: str = "0.0.0.0"
    port: int = 8000
    
    # ========== DATABASE SETTINGS ==========
    database_url: str = "sqlite:///./luminallib.db"
    # Use postgresql://user:password@localhost/luminallib for PostgreSQL
    
    # ========== CORS SETTINGS ==========
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # ========== SECURITY SETTINGS ==========
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    jwt_algorithm: str = "HS256"
    refresh_token_expire_days: int = 7
    
    # ========== LLM PROVIDER SETTINGS ==========
    # Swap LLM provider with a single change: mock -> openai -> huggingface
    llm_provider: str = "huggingface"  # Options: mock, openai, huggingface
    
    # OpenAI Configuration (used when llm_provider=openai)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    # Cost savings: gpt-3.5-turbo ($0.0005/1K input, $0.0015/1K output)
    # Quality: gpt-4-turbo-preview ($0.03/1K input, $0.06/1K output)
    
    # HuggingFace Configuration (used when llm_provider=huggingface)
    huggingface_model: str = "meta-llama/Llama-2-7b-chat"
    # Popular models:
    # - meta-llama/Llama-2-7b-chat (7B, fast)
    # - meta-llama/Llama-2-70b-chat (70B, high quality)
    # - mistralai/Mistral-7B-Instruct-v0.1 (7B, fast)
    # - TheBloke/Llama-2-13B-chat-GGUF (13B, balanced)
    
    huggingface_token: Optional[str] = None
    huggingface_device: str = "cuda"  # cuda for GPU, cpu for CPU
    huggingface_quantize: bool = False  # Use 4-bit quantization to save memory
    
    # ========== FILE STORAGE SETTINGS ==========
    # Swap file storage with a single change: local -> s3
    storage_type: str = "local"  # Options: local, s3
    
    # Local Storage Configuration (used when storage_type=local)
    storage_local_base_path: str = "./files"
    # Where files are stored on local disk
    
    storage_base_url: str = "http://localhost:8000/files"
    # Base URL for accessing files
    # Development: http://localhost:8000/files
    # Production with S3: https://cdn.luminallib.com
    
    # AWS S3 Configuration (used when storage_type=s3)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_s3_bucket: str = "luminallib-books"
    # S3 bucket name
    
    aws_s3_region: str = "us-east-1"
    # AWS region (us-east-1, us-west-2, eu-west-1, etc)
    
    # ========== CACHING SETTINGS ==========
    redis_url: Optional[str] = None  # redis://localhost:6379
    cache_enabled: bool = False
    
    # Cache TTLs (Time To Live)
    cache_ttl_book_summary: int = 7 * 24 * 60 * 60  # 7 days
    cache_ttl_review_analysis: int = 3 * 24 * 60 * 60  # 3 days
    cache_ttl_recommendations: int = 24 * 60 * 60  # 24 hours
    
    # ========== ASYNC WORKER SETTINGS ==========
    celery_broker_url: Optional[str] = None  # redis://localhost:6379
    celery_result_backend: Optional[str] = None  # redis://localhost:6379
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        # Load from .env file with prefix support
        # E.g., DB_URL=... → database_url


# Create global settings instance
settings = Settings()
