"""Recommendation port interface"""
from abc import ABC, abstractmethod
from typing import List
from app.domain.entities import Book


class RecommendationPort(ABC):
    """Abstract interface for recommendation engine"""
    
    @abstractmethod
    async def get_recommendations(self, user_id: str, limit: int = 10) -> List[Book]:
        """Get book recommendations for a user"""
        pass
    
    @abstractmethod
    async def get_similar_books(self, book_id: str, limit: int = 10) -> List[Book]:
        """Get books similar to a given book"""
        pass
    
    @abstractmethod
    async def rank_books(self, book_ids: List[str], user_id: str) -> List[str]:
        """Rank books based on user preferences"""
        pass
    
    @abstractmethod
    async def update_user_preferences(self, user_id: str, book_id: str, rating: int) -> None:
        """Update user preferences based on interaction"""
        pass
