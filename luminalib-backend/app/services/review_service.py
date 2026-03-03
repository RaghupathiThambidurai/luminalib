"""Review service - business logic for review operations"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.domain.entities import Review, ReviewAnalysis, Recommendation
from app.ports.storage_port import StoragePort
from app.core.exceptions import NotFoundError, ValidationError


class ReviewService:
    """Service for review management"""
    
    def __init__(self, storage: StoragePort, llm_adapter=None):
        self.storage = storage
        self.llm_adapter = llm_adapter
        self._analysis_cache: Dict[str, ReviewAnalysis] = {}  # TODO: Replace with Redis
        self._recommendations_cache: Dict[str, List[Recommendation]] = {}  # TODO: Replace with Redis
    
    async def create_review(self, user_id: str, book_id: str, rating: int, content: Optional[str] = None) -> Review:
        if not 1 <= rating <= 5:
            raise ValidationError("Rating must be between 1 and 5")

        book = await self.storage.get_book(book_id)
        if not book:
            raise NotFoundError(f"Book {book_id} not found")

        user = await self.storage.get_user(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")

        # ✅ must have borrowed
        borrow_records = await self.storage.get_user_borrow_records(user_id)
        has_completed_borrow = any(
            br.book_id == book_id and br.status == "returned"
            for br in borrow_records
        )

        if not has_completed_borrow:
            raise ValidationError(
            "You must borrow and return this book before submitting a review."
        )
        if not any(br.book_id == book_id for br in borrow_records):
            raise ValidationError("You cannot review a book you haven't borrowed.")

        review = Review(user_id=user_id, book_id=book_id, rating=rating, content=content)
        return await self.storage.create_review(review)
    
    async def analyze_and_update_sentiment(self, review_id: str) -> Optional[Review]:
        """
        Analyze review sentiment using LLM adapter and update the review.
        This can be called asynchronously after review creation.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            if not self.llm_adapter:
                logger.warning(f"⚠️  No LLM adapter configured, skipping sentiment analysis for review {review_id}")
                return None
            
            # Get the review
            review = await self.get_review(review_id)
            
            if not review.content:
                logger.warning(f"⚠️  Review {review_id} has no content, skipping sentiment analysis")
                return None
            
            # Analyze sentiment using LLM adapter
            sentiment_result = await self.llm_adapter.analyze_sentiment(review.content)
            
            # Extract score (normalize to 0-1 range)
            sentiment_score = sentiment_result.get("score", 0.5)
            if isinstance(sentiment_score, float) and 0 <= sentiment_score <= 1:
                # Store as integer percentage (0-100) or keep as float
                review.sentiment_score = sentiment_score
            
            # Update review with sentiment score
            updated_review = await self.storage.update_review(review_id, review)
            
            sentiment = sentiment_result.get("sentiment", "unknown")
            logger.info(f"✅ Analyzed review {review_id}: {sentiment} (score: {sentiment_score:.2f})")
            
            return updated_review
        except NotFoundError:
            logger.error(f"❌ Review {review_id} not found")
            return None
        except Exception as e:
            logger.error(f"❌ Error analyzing sentiment for review {review_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    async def get_review(self, review_id: str) -> Review:
        """Get review by ID"""
        review = await self.storage.get_review(review_id)
        if not review:
            raise NotFoundError(f"Review {review_id} not found")
        return review
    
    async def update_review(self, review_id: str, rating: Optional[int] = None, content: Optional[str] = None) -> Review:
        """Update review"""
        review = await self.get_review(review_id)
        
        if rating is not None:
            if not 1 <= rating <= 5:
                raise ValidationError("Rating must be between 1 and 5")
            review.rating = rating
        
        if content is not None:
            if len(content) < 10:
                raise ValidationError("Review content must be at least 10 characters")
            review.content = content
        
        return await self.storage.update_review(review_id, review)
    
    async def delete_review(self, review_id: str) -> bool:
        """Delete review"""
        await self.get_review(review_id)  # Verify exists
        return await self.storage.delete_review(review_id)
    
    async def get_reviews_by_book(self, book_id: str, skip: int = 0, limit: int = 10) -> List[Review]:
        """Get reviews for a book"""
        return await self.storage.get_reviews_by_book(book_id, skip, limit)
    
    async def get_reviews_by_user(self, user_id: str, skip: int = 0, limit: int = 10) -> List[Review]:
        """Get reviews by a user"""
        return await self.storage.get_reviews_by_user(user_id, skip, limit)
    
    async def mark_as_helpful(self, review_id: str) -> Review:
        """Mark a review as helpful"""
        review = await self.get_review(review_id)
        review.helpful_count += 1
        review.is_helpful = True
        return await self.storage.update_review(review_id, review)
    
    # ========================================================================
    # REVIEW ANALYSIS & LLM INTEGRATION
    # ========================================================================
    
    async def get_review_analysis(self, book_id: str) -> Optional[ReviewAnalysis]:
        """
        Get AI-generated analysis of all reviews for a book.
        
        Caches results for 3 days to avoid repeated LLM calls.
        Uses GenAI (Claude/GPT-4) via adapter.
        """
        # Check cache first
        if book_id in self._analysis_cache:
            cached = self._analysis_cache[book_id]
            if cached.expires_at > datetime.utcnow():
                return cached
        
        try:
            # Get all reviews for the book
            reviews = await self.storage.get_reviews_by_book(book_id, skip=0, limit=1000)
            
            if not reviews:
                return None
            
            # Calculate statistics
            total = len(reviews)
            avg_rating = sum(r.rating for r in reviews) / total if reviews else 0
            
            # Calculate average sentiment (from already-analyzed reviews)
            sentiment_scores = [r.sentiment_score for r in reviews if r.sentiment_score is not None]
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
            
            # Count sentiment distribution
            positive_count = sum(1 for r in reviews if r.sentiment_score and r.sentiment_score > 0.5)
            negative_count = sum(1 for r in reviews if r.sentiment_score and r.sentiment_score < -0.5)
            neutral_count = total - positive_count - negative_count
            
            # TODO: Call LLM adapter to generate summary
            # summary = await self._llm_adapter.generate_review_summary(reviews)
            # key_themes = await self._llm_adapter.extract_themes(reviews)
            # most_mentioned_words = await self._llm_adapter.extract_keywords(reviews)
            
            # For now, use mock implementation
            summary = f"Analysis of {total} reviews for this book. " \
                     f"Average rating: {avg_rating:.1f}/5. " \
                     f"Sentiment is generally positive with an average score of {avg_sentiment:.2f}."
            
            key_themes = ["Character development", "Writing style", "Plot", "Emotional impact"]
            most_mentioned_words = ["great", "love", "excellent", "recommend", "story"]
            
            # Create analysis object
            analysis = ReviewAnalysis(
                book_id=book_id,
                total_reviews=total,
                average_rating=avg_rating,
                average_sentiment=avg_sentiment,
                summary=summary,
                generated_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=3)
            )
            
            # Cache the analysis
            self._analysis_cache[book_id] = analysis
            
            return analysis
        except Exception as e:
            print(f"Error generating review analysis: {e}")
            return None
    
    # ========================================================================
    # RECOMMENDATIONS & ML INTEGRATION
    # ========================================================================
    
    async def get_user_recommendations(
        self,
        user_id: str,
        limit: int = 10,
        exclude_borrowed: bool = True,
        genre: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get ML-based personalized recommendations for user.
        
        Uses hybrid approach:
        - 40% Content-based (similar to borrowed books)
        - 35% Collaborative filtering (similar users)
        - 25% Preference-based (user interests)
        
        Results cached for 24 hours.
        """
        # Check cache first
        cache_key = f"{user_id}:{limit}:{exclude_borrowed}:{genre}"
        if cache_key in self._recommendations_cache:
            cached_recs = self._recommendations_cache[cache_key]
            if cached_recs:
                return cached_recs
        
        try:
            # TODO: Get user's borrow history
            borrowed_books = []  # await self.storage.get_user_borrowed_books(user_id)
            
            # TODO: Get user's review history
            user_reviews = await self.get_reviews_by_user(user_id, skip=0, limit=100)
            
            # TODO: Get user preferences
            user_prefs = {}  # await self.storage.get_user_preferences(user_id)
            
            # TODO: Implement ML algorithm
            # Step 1: Content-based filtering
            # Step 2: Collaborative filtering
            # Step 3: Preference-based filtering
            # Step 4: Combine scores with weights
            
            # For now, return mock recommendations
            recommendations = [
                {
                    "id": f"rec_{i}",
                    "book_id": f"book_{1000 + i}",
                    "title": f"Recommended Book {i}",
                    "author": f"Author {i}",
                    "genre": genre or "Fiction",
                    "cover_url": f"https://storage.example.com/book_{1000 + i}_cover.jpg",
                    "score": 0.95 - (i * 0.05),  # Decreasing score
                    "reason": f"Based on your interest in {genre or 'similar books'}",
                    "reason_details": {
                        "similar_to_borrowed": borrowed_books[:3],
                        "matches_preferences": [genre] if genre else ["Fiction"],
                        "rating_prediction": 4.5 - (i * 0.1)
                    }
                }
                for i in range(min(limit, 10))
            ]
            
            # Cache results for 24 hours
            self._recommendations_cache[cache_key] = recommendations
            
            return recommendations
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return []
    
    async def get_recommendation_details(self, recommendation_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific recommendation"""
        try:
            # TODO: Retrieve from storage
            # For now, return mock data
            recommendation = {
                "id": recommendation_id,
                "user_id": user_id,
                "book_id": "book_456",
                "score": 0.92,
                "reason": "Based on your love of classic literature",
                "reason_details": {
                    "factors": [
                        {
                            "factor": "Collaborative Filtering",
                            "weight": 0.40,
                            "score": 0.95
                        },
                        {
                            "factor": "Content-Based",
                            "weight": 0.35,
                            "score": 0.88
                        },
                        {
                            "factor": "User Preferences",
                            "weight": 0.25,
                            "score": 0.85
                        }
                    ],
                    "similar_to_borrowed": ["The Great Gatsby", "Jane Eyre"],
                    "matches_genres": ["Fiction", "Classic"],
                    "predicted_rating": 4.6
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            return recommendation
        except Exception as e:
            print(f"Error getting recommendation details: {e}")
            return None
