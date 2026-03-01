"""Factory for creating file storage adapters based on configuration"""
import logging
from typing import Optional
from app.ports.file_storage_port import FileStoragePort
from app.adapters.file_storage.local_storage import LocalFileStorageAdapter

logger = logging.getLogger(__name__)


class FileStorageAdapterFactory:
    """
    Factory for creating file storage adapters.
    
    Supports switching between different storage backends with a single config change.
    
    Configuration (via .env or environment variables):
        STORAGE_TYPE=local|s3
        
    Provider-specific configs:
        # Local Disk Storage
        STORAGE_LOCAL_BASE_PATH=./files
        STORAGE_BASE_URL=http://localhost:8000/files
        
        # AWS S3 Storage
        AWS_ACCESS_KEY_ID=AKIA...
        AWS_SECRET_ACCESS_KEY=...
        AWS_S3_BUCKET=luminallib-books
        AWS_S3_REGION=us-east-1
        STORAGE_BASE_URL=https://cdn.luminallib.com
    
    Example Usage:
        >>> from app.core.config import settings
        >>> storage = FileStorageAdapterFactory.create(settings)
        >>> url = await storage.upload_file("books/123/cover.pdf", pdf_bytes)
    
    Swapping Providers (just change config!):
        # Development
        STORAGE_TYPE=local
        STORAGE_LOCAL_BASE_PATH=./files
        STORAGE_BASE_URL=http://localhost:8000/files
        
        # Production
        STORAGE_TYPE=s3
        AWS_S3_BUCKET=luminallib-books
        STORAGE_BASE_URL=https://cdn.luminallib.com
    """
    
    @staticmethod
    def create(settings) -> FileStoragePort:
        """
        Create a file storage adapter based on settings.
        
        Args:
            settings: Settings object with storage configuration
            
        Returns:
            FileStoragePort implementation (LocalFileStorageAdapter or S3FileStorageAdapter)
            
        Raises:
            ValueError: If provider is unknown or required config is missing
            ImportError: If required dependencies are not installed
        """
        storage_type = getattr(settings, 'storage_type', 'local').lower()
        
        if storage_type == "local":
            logger.info("🔧 Using Local File Storage adapter")
            try:
                base_path = getattr(settings, 'storage_local_base_path', './files')
                base_url = getattr(settings, 'storage_base_url', 'http://localhost:8000/files')
                
                return LocalFileStorageAdapter(base_path=base_path, base_url=base_url)
            except Exception as e:
                logger.error(f"Failed to initialize local file storage: {str(e)}")
                raise
        
        elif storage_type == "s3":
            logger.info("🔧 Using AWS S3 File Storage adapter")
            try:
                from app.adapters.file_storage.s3_storage import S3FileStorageAdapter
                
                bucket = getattr(settings, 'aws_s3_bucket', None)
                region = getattr(settings, 'aws_s3_region', 'us-east-1')
                base_url = getattr(settings, 'storage_base_url', None)
                
                if not bucket:
                    raise ValueError("AWS_S3_BUCKET is required for S3 storage")
                if not base_url:
                    raise ValueError("STORAGE_BASE_URL is required for S3 storage")
                
                return S3FileStorageAdapter(
                    bucket=bucket,
                    region=region,
                    base_url=base_url
                )
            except ImportError as e:
                logger.error(f"boto3 not installed: {str(e)}")
                raise ImportError(
                    "boto3 is required for S3 storage. "
                    "Install with: pip install boto3"
                )
            except Exception as e:
                logger.error(f"Failed to initialize S3 file storage: {str(e)}")
                raise
        
        else:
            raise ValueError(
                f"Unknown storage type: {storage_type}. "
                f"Supported: local, s3"
            )
