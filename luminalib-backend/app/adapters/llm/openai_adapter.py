"""OpenAI LLM adapter"""
import logging
import os
from app.ports.llm_port import LLMPort

logger = logging.getLogger(__name__)


class OpenAIAdapter(LLMPort):
    """
    OpenAI LLM adapter for GPT-4, GPT-3.5, etc.
    
    Configuration:
        LLM_PROVIDER=openai
        OPENAI_API_KEY=sk-...
        OPENAI_MODEL=gpt-4-turbo-preview  # or gpt-3.5-turbo for cost savings
    
    Example:
        >>> llm = OpenAIAdapter(api_key="sk-...", model="gpt-4-turbo-preview")
        >>> summary = await llm.generate_summary("Long book text...")
        'The book discusses...'
    
    Requirements:
        pip install openai
    
    Cost Analysis:
        - GPT-4: $0.03/1K input tokens, $0.06/1K output tokens
        - GPT-3.5-turbo: $0.0005/1K input, $0.0015/1K output (cheaper)
        - Recommendations: Use GPT-3.5-turbo for cost savings, GPT-4 for quality
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize OpenAI adapter.
        
        Args:
            api_key: OpenAI API key (or use OPENAI_API_KEY env var)
            model: Model to use (gpt-4, gpt-3.5-turbo, etc)
        """
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError(
                "openai is required for OpenAI adapter. "
                "Install with: pip install openai"
            )
        
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key not found. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        logger.info(f"✓ OpenAI adapter initialized with model: {model}")
    
    async def generate_summary(self, text: str, max_length: int = 200) -> str:
        """Generate book summary using OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a literary expert. Summarize the following text in approximately {max_length} words."
                    },
                    {"role": "user", "content": text}
                ],
                temperature=0.7,
                max_tokens=int(max_length * 1.5)  # Add buffer for token count
            )
            
            summary = response.choices[0].message.content.strip()
            logger.debug(f"✓ Generated summary via OpenAI ({len(summary)} chars)")
            return summary
        
        except Exception as e:
            logger.error(f"❌ OpenAI summary generation failed: {str(e)}")
            raise
    
    async def generate_recommendation_reason(self, book_title: str, user_preferences: dict) -> str:
        """Generate recommendation reason using OpenAI"""
        try:
            prefs_str = ", ".join(
                f"{k}: {v}" for k, v in user_preferences.items()
            )
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a book recommendation expert. Generate a brief, engaging reason why a book is recommended."
                    },
                    {
                        "role": "user",
                        "content": f"Book: '{book_title}'. User preferences: {prefs_str}. Reason:"
                    }
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            reason = response.choices[0].message.content.strip()
            logger.debug(f"✓ Generated recommendation reason via OpenAI")
            return reason
        
        except Exception as e:
            logger.error(f"❌ OpenAI recommendation generation failed: {str(e)}")
            raise
    
    async def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment using OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze the sentiment of the following text. Return JSON: {\"sentiment\": \"positive|negative|neutral\", \"score\": 0-1, \"confidence\": 0-1}"
                    },
                    {"role": "user", "content": text}
                ],
                temperature=0,  # Deterministic for analysis
                max_tokens=100
            )
            
            import json
            response_text = response.choices[0].message.content.strip()
            result = json.loads(response_text)
            logger.debug(f"✓ Analyzed sentiment via OpenAI")
            return result
        
        except Exception as e:
            logger.error(f"❌ OpenAI sentiment analysis failed: {str(e)}")
            raise
    
    async def extract_keywords(self, text: str, max_keywords: int = 5) -> list[str]:
        """Extract keywords using OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"Extract {max_keywords} most important keywords from the text. Return as comma-separated list."
                    },
                    {"role": "user", "content": text}
                ],
                temperature=0,
                max_tokens=100
            )
            
            keywords_str = response.choices[0].message.content.strip()
            keywords = [k.strip() for k in keywords_str.split(",")]
            logger.debug(f"✓ Extracted keywords via OpenAI")
            return keywords[:max_keywords]
        
        except Exception as e:
            logger.error(f"❌ OpenAI keyword extraction failed: {str(e)}")
            raise
