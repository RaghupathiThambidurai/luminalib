"""File storage port interface - abstracts local disk vs S3 vs other storage"""
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime


class FileStoragePort(ABC):
    """
    Abstract interface for file storage operations.
    
    Implementations:
    - LocalFileStorageAdapter: Store files on local disk
    - S3FileStorageAdapter: Store files on AWS S3
    - GCSFileStorageAdapter: Store files on Google Cloud Storage
    
    This allows swapping storage backends with a single config change.
    """
    
    @abstractmethod
    async def upload_file(
        self,
        file_path: str,
        file_content: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[dict] = None
    ) -> str:
        """
        Upload a file to storage.
        
        Args:
            file_path: Relative path where file should be stored
            file_content: Binary content of the file
            content_type: MIME type of the file
            metadata: Optional metadata (e.g., {'user_id': '123'})
            
        Returns:
            Public URL or identifier for accessing the file
            
        Example:
            >>> await storage.upload_file(
            ...     "books/abc123/cover.pdf",
            ...     pdf_bytes,
            ...     "application/pdf"
            ... )
            'https://s3.amazonaws.com/bucket/books/abc123/cover.pdf'
        """
        pass
    
    @abstractmethod
    async def download_file(self, file_path: str) -> bytes:
        """
        Download a file from storage.
        
        Args:
            file_path: Path/identifier of the file to download
            
        Returns:
            Binary content of the file
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_path: Path/identifier of the file to delete
            
        Returns:
            True if successful, False if file not found
        """
        pass
    
    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            file_path: Path/identifier of the file
            
        Returns:
            True if file exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_file_url(self, file_path: str) -> str:
        """
        Get a public URL for a file.
        
        Args:
            file_path: Path/identifier of the file
            
        Returns:
            Public URL for accessing the file
        """
        pass
    
    @abstractmethod
    async def list_files(self, prefix: str = "") -> list[str]:
        """
        List files in storage with optional prefix filter.
        
        Args:
            prefix: Optional prefix to filter files
            
        Returns:
            List of file paths matching the prefix
            
        Example:
            >>> await storage.list_files("books/abc123/")
            ["books/abc123/cover.pdf", "books/abc123/preview.txt"]
        """
        pass
    
    @abstractmethod
    async def get_file_metadata(self, file_path: str) -> dict:
        """
        Get metadata for a file (size, modified time, etc).
        
        Args:
            file_path: Path/identifier of the file
            
        Returns:
            Dictionary with metadata:
            {
                'size': int (bytes),
                'modified': datetime,
                'content_type': str,
                'etag': str (optional)
            }
        """
        pass
