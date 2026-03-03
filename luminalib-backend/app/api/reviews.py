"""Review routes"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from app.domain.entities import Review, ReviewCreate, ReviewAnalysis
from app.services.review_service import ReviewService
from app.core.exceptions import NotFoundError, ValidationError
from app.core.security import HTTPBearer, security
from app.api.auth import get_current_user
from app.domain.entities import UserResponse

router = APIRouter(
    prefix="/books",
    tags=["reviews"],
    responses={404: {"description": "Not found"}},
)


# Dependency to get ReviewService
async def get_review_service() -> ReviewService:
    """Get review service instance"""
    from app.core.di import DIContainer
    return DIContainer.get("review_service")


# ============================================================================
# REVIEW ENDPOINTS
# ============================================================================

@router.post("/{book_id}/reviews", response_model=Review, status_code=status.HTTP_201_CREATED)
async def submit_review(
    book_id: str,
    review_data: ReviewCreate,
    current_user: UserResponse = Depends(get_current_user),
    authorization: HTTPBearer = Depends(security),
    service: ReviewService = Depends(get_review_service)
):
    """
    Submit a review for a book.
    
    Triggers async sentiment analysis via Celery task.
    Initial sentiment_score will be null until analysis completes.
    
    **Request:**
    ```json
    {
      "rating": 5,
      "content": "Amazing book! The storytelling is phenomenal and well-written."
    }
    ```
    
    **Response (201 Created):**
    ```json
    {
      "id": "review_101",
      "user_id": "user_123",
      "book_id": "book_456",
      "rating": 5,
      "content": "Amazing book!...",
      "sentiment_score": null,
      "sentiment_analysis_task_id": "celery_task_abc",
      "is_helpful": false,
      "helpful_count": 0,
      "created_at": "2026-02-25T11:00:00"
    }
    ```
    """
    try:
        # TODO: Extract user_id from authorization token
        # For development, use the actual test user ID from database
        user_id = current_user.id   # testuser
        
        # Validate review content
        if not review_data.content or len(review_data.content) < 10:
            raise ValidationError("Review content must be at least 10 characters long")
        
        # Create review (sentiment_score will be populated async)
        review = await service.create_review(
            user_id=user_id,
            book_id=book_id,
            rating=review_data.rating,
            content=review_data.content
        )
        
        # Trigger async sentiment analysis (non-blocking)
        # This will analyze sentiment and update the review in the background
        import asyncio
        asyncio.create_task(service.analyze_and_update_sentiment(review.id))
        
        return review
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = f"Failed to create review: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )


@router.get("/{book_id}/reviews", response_model=dict, status_code=status.HTTP_200_OK)
async def get_book_reviews(
    book_id: str,
    skip: int = Query(0, ge=0, description="Number of reviews to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of reviews to return"),
    sort: Optional[str] = Query("created_at", description="Sort by: rating, helpful_count, created_at"),
    order: Optional[str] = Query("desc", description="asc or desc"),
    service: ReviewService = Depends(get_review_service)
):
    """
    Get all reviews for a book with pagination.
    
    **Query Parameters:**
    - `skip`: Number of reviews to skip (default: 0)
    - `limit`: Number of reviews per page (default: 10, max: 100)
    - `sort`: Sort field (rating, helpful_count, created_at)
    - `order`: asc or desc
    
    **Response (200 OK):**
    ```json
    {
      "reviews": [
        {
          "id": "review_101",
          "user_id": "user_123",
          "username": "john_doe",
          "rating": 5,
          "content": "Amazing book!",
          "sentiment_score": 0.95,
          "is_helpful": true,
          "helpful_count": 15,
          "created_at": "2026-02-25T11:00:00"
        }
      ],
      "total": 45,
      "book_average_rating": 4.5,
      "skip": 0,
      "limit": 10,
      "has_more": true
    }
    ```
    """
    try:
        reviews = await service.get_reviews_by_book(book_id, skip, limit)
        total = len(reviews)  # TODO: Get actual count from database
        
        # Calculate average rating
        if reviews:
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
        else:
            avg_rating = 0.0
        
        return {
            "reviews": reviews,
            "total": total,
            "book_average_rating": avg_rating,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{book_id}/reviews/{review_id}", response_model=Review)
async def update_review(
    book_id: str,
    review_id: str,
    review_data: ReviewCreate,
    authorization: HTTPBearer = Depends(security),
    service: ReviewService = Depends(get_review_service)
):
    """Update a review (rating and/or content)"""
    try:
        # TODO: Verify user is review author
        review = await service.update_review(
            review_id=review_id,
            rating=review_data.rating,
            content=review_data.content
        )
        
        # TODO: Trigger new sentiment analysis task
        
        return review
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{book_id}/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    book_id: str,
    review_id: str,
    authorization: HTTPBearer = Depends(security),
    service: ReviewService = Depends(get_review_service)
):
    """Delete a review"""
    try:
        # TODO: Verify user is review author
        await service.delete_review(review_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{book_id}/reviews/{review_id}/helpful", response_model=Review)
async def mark_review_helpful(
    book_id: str,
    review_id: str,
    service: ReviewService = Depends(get_review_service)
):
    """Mark a review as helpful"""
    try:
        review = await service.mark_as_helpful(review_id)
        return review
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ============================================================================
# REVIEW ANALYSIS ENDPOINT
# ============================================================================

@router.get("/{book_id}/analysis", response_model=ReviewAnalysis)
async def get_review_analysis(
    book_id: str,
    service: ReviewService = Depends(get_review_service)
):
    """
    Get AI-generated aggregated summary of all reviews for a book.
    
    Uses GenAI (Claude/GPT-4) to analyze all reviews and generate:
    - Overall sentiment distribution
    - Key themes and topics
    - Most mentioned positive/negative aspects
    - Aggregated summary text
    
    Results are cached for 3 days to avoid repeated LLM calls.
    
    **Response (200 OK):**
    ```json
    {
      "book_id": "book_456",
      "total_reviews": 45,
      "average_rating": 4.5,
      "average_sentiment": 0.82,
      "sentiment_distribution": {
        "positive": 38,
        "neutral": 5,
        "negative": 2
      },
      "summary": "Readers overwhelmingly praise The Great Gatsby for its compelling characters...",
      "key_themes": [
        "American Dream",
        "Class and wealth",
        "Love and betrayal"
      ],
      "most_mentioned_words": [
        "beautiful",
        "classic",
        "compelling"
      ],
      "generated_at": "2026-02-25T14:00:00",
      "expires_at": "2026-02-28T14:00:00"
    }
    ```
    
    **Note:** Summary is cached for 3 days. For fresh analysis, delete cache.
    
    **Error Responses:**
    - `404`: Book not found or no reviews exist
    """
    try:
        # Check if book exists
        from app.services.book_service import BookService
        from app.core.di import DIContainer
        book_service = DIContainer.get("book_service")
        
        book = await book_service.get_book(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book {book_id} not found"
            )
        
        # Get review analysis (with caching)
        analysis = await service.get_review_analysis(book_id)
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No reviews found for this book or analysis generation failed"
            )
        
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# RECOMMENDATIONS ENDPOINT
# ============================================================================

@router.get("/recommendations", response_model=dict, name="get_recommendations")
async def get_recommendations(
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    exclude_borrowed: bool = Query(True, description="Exclude already borrowed books"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    authorization: HTTPBearer = Depends(security),
    current_user: UserResponse = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service)
):
    """
    Get ML-based personalized book recommendations for the current user.
    
    Uses hybrid ML approach combining:
    1. **Content-Based** (40%) - Books similar to borrowed books
    2. **Collaborative Filtering** (35%) - Books liked by similar users
    3. **Preference-Based** (25%) - Books matching user interests
    
    Results are cached for 24 hours.
    
    **Query Parameters:**
    - `limit`: Number of recommendations (default: 10, max: 50)
    - `exclude_borrowed`: Exclude already borrowed books (default: true)
    - `genre`: Filter by specific genre (optional)
    
    **Response (200 OK):**
    ```json
    {
      "recommendations": [
        {
          "id": "rec_123",
          "book_id": "book_789",
          "title": "1984",
          "author": "George Orwell",
          "genre": "Fiction/Science Fiction",
          "cover_url": "https://storage.example.com/book_789_cover.jpg",
          "score": 0.92,
          "reason": "Based on your love of classic literature and dystopian themes",
          "reason_details": {
            "similar_to_borrowed": ["The Great Gatsby"],
            "matches_preferences": ["Classic", "Literary Fiction"],
            "rating_prediction": 4.6
          }
        }
      ],
      "total": 10,
      "generated_at": "2026-02-25T10:00:00",
      "expires_at": "2026-02-28T10:00:00"
    }
    ```
    
    **Algorithm Details:**
    - Score = 0.40 × ContentBased + 0.35 × Collaborative + 0.25 × PreferenceBased
    - Score range: 0 to 1
    - Only books with score > 0.4 are included
    
    **Error Responses:**
    - `401`: Unauthorized
    - `400`: Invalid query parameters
    """
    try:
        # TODO: Extract user_id from authorization token
        user_id = current_user.id
        
        # Get recommendations (with caching)
        recommendations = await service.get_user_recommendations(
            user_id=user_id,
            limit=limit,
            exclude_borrowed=exclude_borrowed,
            genre=genre
        )
        
        return {
            "recommendations": recommendations,
            "total": len(recommendations),
            "generated_at": "2026-02-25T10:00:00",  # TODO: Use actual timestamp
            "expires_at": "2026-02-28T10:00:00"      # TODO: 24 hours from generation
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/recommendations/{recommendation_id}", response_model=dict)
async def get_recommendation_details(
    recommendation_id: str,
    authorization: HTTPBearer = Depends(security),
    current_user: UserResponse = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service)
):
    """
    Get detailed information about a specific recommendation including
    algorithm factors and scoring breakdown.
    
    **Response (200 OK):**
    ```json
    {
      "id": "rec_123",
      "user_id": "user_123",
      "book_id": "book_789",
      "score": 0.92,
      "reason": "Based on your love of classic literature",
      "reason_details": {
        "factors": [
          {
            "factor": "Collaborative Filtering",
            "weight": 0.4,
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
        "similar_to_borrowed": ["The Great Gatsby"],
        "matches_genres": ["Fiction"],
        "predicted_rating": 4.6
      },
      "generated_at": "2026-02-25T10:00:00"
    }
    ```
    """
    try:
        # TODO: Extract user_id from authorization token
        user_id = current_user.id
        
        # Get recommendation details
        recommendation = await service.get_recommendation_details(recommendation_id, user_id)
        
        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation {recommendation_id} not found"
            )
        
        return recommendation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

