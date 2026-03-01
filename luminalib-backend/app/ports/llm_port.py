"""LLM port interface"""
from abc import ABC, abstractmethod
from typing import Optional


class LLMPort(ABC):
    """Abstract interface for LLM operations"""
    
    @abstractmethod
    async def generate_summary(self, text: str, max_length: int = 200) -> str:
        """Generate a summary of text"""
        pass
    
    @abstractmethod
    async def generate_recommendation_reason(self, book_title: str, user_preferences: dict) -> str:
        """Generate a reason why a book is recommended"""
        pass
    
    @abstractmethod
    async def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment of text"""
        pass
    
    @abstractmethod
    async def extract_keywords(self, text: str, max_keywords: int = 5) -> list[str]:
        """Extract keywords from text"""
        pass
