"""Mock recommendation adapter for development and testing"""
from typing import List
from app.domain.entities import Book
from app.ports.recommendation_port import RecommendationPort
from app.ports.storage_port import StoragePort


class MockRecommendationAdapter(RecommendationPort):
    """Mock recommendation adapter"""
    
    def __init__(self, storage: StoragePort):
        self.storage = storage
    
    async def get_recommendations(self, user_id: str, limit: int = 10) -> List[Book]:
        """Get mock recommendations - just return first N books"""
        books = await self.storage.list_books(skip=0, limit=limit)
        return books
    
    async def get_similar_books(self, book_id: str, limit: int = 10) -> List[Book]:
        """Get mock similar books - return books in same genre"""
        book = await self.storage.get_book(book_id)
        if not book:
            return []
        
        # For mock, just return books with same genre
        all_books = await self.storage.list_books(skip=0, limit=100)
        similar = [
            b for b in all_books 
            if b.id != book_id and b.genre == book.genre
        ]
        return similar[:limit]
    
    async def rank_books(self, book_ids: List[str], user_id: str) -> List[str]:
        """Rank books - mock just returns in same order"""
        return book_ids
    
    async def update_user_preferences(self, user_id: str, book_id: str, rating: int) -> None:
        """Update user preferences - mock does nothing"""
        pass
