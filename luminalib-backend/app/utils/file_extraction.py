"""Utility for extracting text from various file formats"""
import io
import logging
import re
from typing import Optional

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import ebooklib
    from ebooklib import epub
except ImportError:
    ebooklib = None
    epub = None

logger = logging.getLogger(__name__)


async def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract text content from PDF file.
    
    Args:
        file_content: Binary PDF file content
        
    Returns:
        Extracted text from all pages
        
    Raises:
        ValueError: If PDF extraction fails
    """
    if PyPDF2 is None:
        raise ValueError("PyPDF2 library not installed. Run: pip install PyPDF2")
    
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        
        total_pages = len(pdf_reader.pages)
        logger.debug(f"Extracting text from {total_pages} pages")
        
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            except Exception as e:
                logger.warning(f"Failed to extract text from page {page_num}: {e}")
                continue
        
        logger.debug(f"✓ Extracted {len(text)} characters from PDF ({total_pages} pages)")
        return text
        
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        raise ValueError(f"PDF extraction failed: {str(e)}")


async def extract_text_from_epub(file_content: bytes) -> str:
    """
    Extract text content from EPUB file.
    
    Args:
        file_content: Binary EPUB file content
        
    Returns:
        Extracted text from all chapters
        
    Raises:
        ValueError: If EPUB extraction fails
    """
    if epub is None:
        raise ValueError("ebooklib library not installed. Run: pip install ebooklib")
    
    try:
        book = epub.read_epub(io.BytesIO(file_content))
        text = ""
        
        logger.debug("Extracting text from EPUB")
        
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                try:
                    content = item.get_content().decode('utf-8', errors='ignore')
                    # Remove HTML tags (basic cleanup)
                    content = re.sub('<[^<]+?>', '', content)
                    # Remove extra whitespace
                    content = re.sub(r'\s+', ' ', content)
                    if content.strip():
                        text += content + "\n"
                except Exception as e:
                    logger.warning(f"Failed to extract item: {e}")
                    continue
        
        logger.debug(f"✓ Extracted {len(text)} characters from EPUB")
        return text
        
    except Exception as e:
        logger.error(f"Failed to extract text from EPUB: {e}")
        raise ValueError(f"EPUB extraction failed: {str(e)}")


async def extract_text_from_txt(file_content: bytes) -> str:
    """
    Extract text from plain text file.
    
    Args:
        file_content: Binary text file content
        
    Returns:
        Extracted text
        
    Raises:
        ValueError: If text extraction fails
    """
    try:
        # Try UTF-8 first, then fall back to latin-1
        try:
            text = file_content.decode('utf-8')
        except UnicodeDecodeError:
            text = file_content.decode('latin-1', errors='ignore')
        
        logger.debug(f"✓ Extracted {len(text)} characters from TXT")
        return text
    except Exception as e:
        logger.error(f"Failed to extract text from TXT: {e}")
        raise ValueError(f"Text extraction failed: {str(e)}")


async def extract_text_from_file(file_name: str, file_content: bytes) -> str:
    """
    Extract text from any supported file format.
    
    Supports: PDF, EPUB, MOBI (as text), TXT, MD
    
    Args:
        file_name: Name of the file (used to detect format)
        file_content: Binary file content
        
    Returns:
        Extracted text
        
    Raises:
        ValueError: If file format is not supported or extraction fails
    """
    file_name_lower = file_name.lower()
    
    logger.info(f"Extracting text from: {file_name}")
    
    if file_name_lower.endswith('.pdf'):
        return await extract_text_from_pdf(file_content)
    elif file_name_lower.endswith('.epub'):
        return await extract_text_from_epub(file_content)
    elif file_name_lower.endswith(('.txt', '.md', '.mobi')):
        return await extract_text_from_txt(file_content)
    else:
        raise ValueError(f"Unsupported file format: {file_name}")


def truncate_text(text: str, max_chars: int = 10000) -> str:
    """
    Truncate text to maximum character count.
    
    Tries to cut at word boundary if possible.
    
    Args:
        text: Text to truncate
        max_chars: Maximum characters
        
    Returns:
        Truncated text
    """
    if len(text) <= max_chars:
        return text
    
    # Try to cut at word boundary
    truncated = text[:max_chars]
    last_space = truncated.rfind(' ')
    
    # Only if space is close to end (within 10%)
    if last_space > max_chars * 0.9:
        truncated = truncated[:last_space]
    
    truncated += "..."
    return truncated
