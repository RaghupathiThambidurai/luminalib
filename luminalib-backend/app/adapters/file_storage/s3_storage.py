"""AWS S3 file storage adapter"""
import logging
from typing import Optional
from datetime import datetime
from app.ports.file_storage_port import FileStoragePort

logger = logging.getLogger(__name__)


class S3FileStorageAdapter(FileStoragePort):
    """
    Store files on AWS S3.
    
    Perfect for production deployments with automatic scaling.
    Files are stored in an S3 bucket and accessed via CloudFront or S3 URLs.
    
    Configuration:
        STORAGE_TYPE=s3
        AWS_ACCESS_KEY_ID=your_access_key
        AWS_SECRET_ACCESS_KEY=your_secret_key
        AWS_S3_BUCKET=luminallib-books
        AWS_S3_REGION=us-east-1
        STORAGE_BASE_URL=https://cdn.luminallib.com
    
    Example:
        >>> storage = S3FileStorageAdapter("luminallib-books", "us-east-1", "https://cdn.luminallib.com")
        >>> await storage.upload_file("books/123/cover.pdf", pdf_bytes, "application/pdf")
        'https://cdn.luminallib.com/books/123/cover.pdf'
    
    Requirements:
        pip install boto3
    """
    
    def __init__(self, bucket: str, region: str, base_url: str):
        """
        Initialize S3 file storage.
        
        Args:
            bucket: S3 bucket name
            region: AWS region (e.g., us-east-1)
            base_url: Base URL for CloudFront or S3 (e.g., https://cdn.example.com)
        """
        try:
            import boto3
        except ImportError:
            raise ImportError(
                "boto3 is required for S3 storage. "
                "Install with: pip install boto3"
            )
        
        self.bucket = bucket
        self.region = region
        self.base_url = base_url.rstrip('/')
        
        # Initialize S3 client
        self.s3_client = boto3.client('s3', region_name=region)
        
        logger.info(f"✓ S3 file storage initialized: s3://{bucket}/")
    
    async def upload_file(
        self,
        file_path: str,
        file_content: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[dict] = None
    ) -> str:
        """Upload file to S3"""
        try:
            extra_args = {
                'ContentType': content_type,
                'ACL': 'public-read'  # Make file publicly readable
            }
            
            if metadata:
                # S3 metadata must be strings
                extra_args['Metadata'] = {
                    k: str(v) for k, v in metadata.items()
                }
            
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=file_path,
                Body=file_content,
                **extra_args
            )
            
            logger.debug(f"✓ Uploaded to S3: {file_path} ({len(file_content)} bytes)")
            return await self.get_file_url(file_path)
        
        except Exception as e:
            logger.error(f"❌ S3 upload failed: {str(e)}")
            raise
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from S3"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=file_path)
            content = response['Body'].read()
            logger.debug(f"✓ Downloaded from S3: {file_path} ({len(content)} bytes)")
            return content
        
        except self.s3_client.exceptions.NoSuchKey:
            raise FileNotFoundError(f"File not found in S3: {file_path}")
        except Exception as e:
            logger.error(f"❌ S3 download failed: {str(e)}")
            raise
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from S3"""
        try:
            # Check if exists first
            if not await self.file_exists(file_path):
                logger.warning(f"File not found in S3 for deletion: {file_path}")
                return False
            
            self.s3_client.delete_object(Bucket=self.bucket, Key=file_path)
            logger.debug(f"✓ Deleted from S3: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"❌ S3 delete failed: {str(e)}")
            raise
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in S3"""
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=file_path)
            return True
        except self.s3_client.exceptions.NoSuchKey:
            return False
        except Exception as e:
            logger.error(f"❌ S3 head_object failed: {str(e)}")
            raise
    
    async def get_file_url(self, file_path: str) -> str:
        """Get public URL for file"""
        # Use CloudFront URL if configured
        return f"{self.base_url}/{file_path}"
    
    async def list_files(self, prefix: str = "") -> list[str]:
        """List files in S3 with optional prefix"""
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket, Prefix=prefix)
            
            files = []
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        if not obj['Key'].endswith('/'):  # Exclude "folders"
                            files.append(obj['Key'])
            
            return sorted(files)
        
        except Exception as e:
            logger.error(f"❌ S3 list failed: {str(e)}")
            raise
    
    async def get_file_metadata(self, file_path: str) -> dict:
        """Get file metadata from S3"""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket, Key=file_path)
            
            return {
                'size': response.get('ContentLength', 0),
                'modified': response.get('LastModified'),
                'content_type': response.get('ContentType', 'application/octet-stream'),
                'etag': response.get('ETag', '').strip('"')
            }
        
        except self.s3_client.exceptions.NoSuchKey:
            raise FileNotFoundError(f"File not found in S3: {file_path}")
        except Exception as e:
            logger.error(f"❌ S3 metadata fetch failed: {str(e)}")
            raise
