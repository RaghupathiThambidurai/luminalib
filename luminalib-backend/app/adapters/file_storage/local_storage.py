"""Local file system storage adapter"""
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from app.ports.file_storage_port import FileStoragePort

logger = logging.getLogger(__name__)


class LocalFileStorageAdapter(FileStoragePort):
    """
    Store files on local disk.
    
    Perfect for development and small deployments.
    Files are stored in a configured directory and served via HTTP.
    
    Configuration:
        STORAGE_TYPE=local
        STORAGE_LOCAL_BASE_PATH=./files  # Relative to project root
        STORAGE_BASE_URL=http://localhost:8000/files
    
    Example:
        >>> storage = LocalFileStorageAdapter("./files", "http://localhost:8000/files")
        >>> await storage.upload_file("books/123/cover.pdf", pdf_bytes, "application/pdf")
        'http://localhost:8000/files/books/123/cover.pdf'
    """
    
    def __init__(self, base_path: str, base_url: str):
        """
        Initialize local file storage.
        
        Args:
            base_path: Base directory where files are stored
            base_url: Base URL for accessing files (e.g., http://localhost:8000/files)
        """
        self.base_path = Path(base_path)
        self.base_url = base_url.rstrip('/')
        
        # Create base directory if it doesn't exist
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Local file storage initialized at {self.base_path}")
    
    async def upload_file(
        self,
        file_path: str,
        file_content: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[dict] = None
    ) -> str:
        """Upload file to local disk"""
        full_path = self.base_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'wb') as f:
            f.write(file_content)
        
        logger.debug(f"✓ Uploaded file: {file_path} ({len(file_content)} bytes)")
        return await self.get_file_url(file_path)
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from local disk"""
        full_path = self.base_path / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(full_path, 'rb') as f:
            content = f.read()
        
        logger.debug(f"✓ Downloaded file: {file_path} ({len(content)} bytes)")
        return content
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from local disk"""
        full_path = self.base_path / file_path
        
        if not full_path.exists():
            logger.warning(f"File not found for deletion: {file_path}")
            return False
        
        full_path.unlink()
        logger.debug(f"✓ Deleted file: {file_path}")
        return True
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        full_path = self.base_path / file_path
        return full_path.exists()
    
    async def get_file_url(self, file_path: str) -> str:
        """Get public URL for file"""
        return f"{self.base_url}/{file_path}"
    
    async def list_files(self, prefix: str = "") -> list[str]:
        """List files with optional prefix"""
        search_path = self.base_path / prefix
        
        if not search_path.exists():
            return []
        
        files = []
        if search_path.is_dir():
            for item in search_path.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(self.base_path)
                    files.append(str(relative_path))
        
        return sorted(files)
    
    async def get_file_metadata(self, file_path: str) -> dict:
        """Get file metadata"""
        full_path = self.base_path / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat = full_path.stat()
        
        return {
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'content_type': 'application/octet-stream',
            'etag': f"{stat.st_ino}-{stat.st_mtime_ns}"
        }
