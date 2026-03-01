"""Mock LLM adapter for development and testing"""
from app.ports.llm_port import LLMPort


class MockLLMAdapter(LLMPort):
    """Mock LLM adapter - returns dummy responses"""
    
    async def generate_summary(self, text: str, max_length: int = 200) -> str:
        """Generate a mock summary"""
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text
    
    async def generate_recommendation_reason(self, book_title: str, user_preferences: dict) -> str:
        """Generate a mock recommendation reason"""
        return f"This book matches your interest in {user_preferences.get('genre', 'literature')}."
    
    async def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment of text - mock implementation"""
        # Simple mock: count positive/negative words
        positive_words = ['great', 'amazing', 'excellent', 'love', 'best', 'awesome', 'wonderful']
        negative_words = ['bad', 'terrible', 'hate', 'worst', 'awful', 'horrible']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            sentiment = "positive"
            score = 0.85  # Strong positive
        elif neg_count > pos_count:
            sentiment = "negative"
            score = 0.15  # Strong negative
        else:
            sentiment = "neutral"
            score = 0.50  # Neutral
        
        return {
            "sentiment": sentiment,
            "score": score,
            "positive_count": pos_count,
            "negative_count": neg_count
        }
    
    async def extract_keywords(self, text: str, max_keywords: int = 5) -> list[str]:
        """Extract keywords from text - mock implementation"""
        # Simple mock: split by spaces and take longest words
        words = text.split()
        sorted_words = sorted(set(words), key=len, reverse=True)
        return sorted_words[:max_keywords]
