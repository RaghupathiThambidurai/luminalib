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
        Uses configured LLM adapter when available.
        """
        if book_id in self._analysis_cache:
            cached = self._analysis_cache[book_id]
            if cached.expires_at > datetime.utcnow():
                return cached

        try:
            reviews = await self.storage.get_reviews_by_book(book_id, skip=0, limit=1000)
            if not reviews:
                return None

            total = len(reviews)
            avg_rating = sum(r.rating for r in reviews) / total if total else 0.0

            sentiment_scores = [
                r.sentiment_score for r in reviews
                if r.sentiment_score is not None
            ]
            avg_sentiment = (
                sum(sentiment_scores) / len(sentiment_scores)
                if sentiment_scores else 0.0
            )

            positive_count = sum(
                1 for r in reviews
                if r.sentiment_score is not None and r.sentiment_score > 0.6
            )
            negative_count = sum(
                1 for r in reviews
                if r.sentiment_score is not None and r.sentiment_score < 0.4
            )
            neutral_count = total - positive_count - negative_count

            review_texts = [
                f"Rating: {r.rating}/5. Review: {r.content}"
                for r in reviews
                if r.content
            ]
            combined_text = "\n".join(review_texts)

            if self.llm_adapter and combined_text.strip():
                try:
                    summary = await self.llm_adapter.generate_summary(
                        combined_text,
                        max_length=250
                    )
                except Exception:
                    summary = (
                        f"Based on {total} reviews, this book has an average rating "
                        f"of {avg_rating:.1f}/5."
                    )
                try:
                    most_mentioned_words = await self.llm_adapter.extract_keywords(
                        combined_text,
                        max_keywords=5
                    )
                except Exception:
                    most_mentioned_words = []
            else:
                summary = (
                    f"Based on {total} reviews, this book has an average rating "
                    f"of {avg_rating:.1f}/5. Average sentiment score is "
                    f"{avg_sentiment:.2f}."
                )
                most_mentioned_words = []

            key_themes = most_mentioned_words[:4] if most_mentioned_words else []

            analysis = ReviewAnalysis(
                book_id=book_id,
                total_reviews=total,
                average_rating=avg_rating,
                average_sentiment=avg_sentiment,
                sentiment_distribution={
                    "positive": positive_count,
                    "neutral": neutral_count,
                    "negative": negative_count,
                },
                summary=summary,
                key_themes=key_themes,
                most_mentioned_words=most_mentioned_words,
                generated_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=3),
            )

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

        cache_key = f"{user_id}:{limit}:{exclude_borrowed}:{genre}"
        if cache_key in self._recommendations_cache:
            return self._recommendations_cache[cache_key]

        try:

            # Get borrow history
            borrow_records = await self.storage.get_user_borrow_records(user_id)
            borrowed_ids = [b.book_id for b in borrow_records]

            # Get available books
            books = await self.storage.list_books(skip=0, limit=200)

            recommendations = []

            for book in books:

                if exclude_borrowed and book.id in borrowed_ids:
                    continue

                if genre and book.genre != genre:
                    continue

                recommendations.append({
                    "id": f"rec_{book.id}",
                    "book_id": book.id,
                    "title": book.title,
                    "author": book.author,
                    "genre": book.genre,
                    "cover_url": book.cover_url,
                    "score": 0.85,
                    "reason": "Recommended based on available books in library",
                    "reason_details": {
                    "similar_to_borrowed": borrowed_ids[:3],
                    "matches_preferences": [book.genre],
                    "rating_prediction": 4.2
                 }
                })

                if len(recommendations) >= limit:
                    break

            self._recommendations_cache[cache_key] = recommendations
            return recommendations

        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return []

        async def get_recommendation_details(
        self,
        recommendation_id: str,
        user_id: str
        ) -> Optional[Dict[str, Any]]:
            """Get detailed information about a specific recommendation"""
            try:
                # First search existing cached recommendations for this user
                for cache_key, recommendations in self._recommendations_cache.items():
                    if not cache_key.startswith(f"{user_id}:"):
                        continue

                    for rec in recommendations:
                        if rec.get("id") == recommendation_id:
                            return {
                                **rec,
                                "user_id": user_id,
                                "generated_at": datetime.utcnow().isoformat(),
                            }

                # If not in cache, regenerate a fresh recommendation list from real books
                recommendations = await self.get_user_recommendations(
                    user_id=user_id,
                    limit=50,
                    exclude_borrowed=True,
                    genre=None,
                )

                for rec in recommendations:
                    if rec.get("id") == recommendation_id:
                        return {
                            **rec,
                            "user_id": user_id,
                            "generated_at": datetime.utcnow().isoformat(),
                        }

                return None

            except Exception as e:
                print(f"Error getting recommendation details: {e}")
                return None