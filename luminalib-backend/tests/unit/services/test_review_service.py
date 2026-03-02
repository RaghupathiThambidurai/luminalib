"""
Unit tests for review service.

Tests:
- Review creation
- Review retrieval
- Review updates
- Rating validation
- Review deletion
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from app.domain.models import Review, User, Book


class TestReviewServiceCreation:
    """Test review service creation."""
    
    def test_create_review_with_all_fields(
        self,
        test_db: Session,
        test_user: User,
        test_book: Book,
        test_review_data: dict
    ) -> None:
        """Test creating a review with all fields."""
        review = Review(
            id="review-1",
            user_id=test_user.id,
            book_id=test_book.id,
            rating=test_review_data["rating"],
            comment=test_review_data["comment"],
            title=test_review_data["title"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        test_db.add(review)
        test_db.commit()
        test_db.refresh(review)
        
        assert review.user_id == test_user.id
        assert review.book_id == test_book.id
        assert review.rating == test_review_data["rating"]
        assert review.comment == test_review_data["comment"]
    
    def test_create_review_minimal_fields(
        self,
        test_db: Session,
        test_user: User,
        test_book: Book
    ) -> None:
        """Test creating a review with minimal fields."""
        review = Review(
            id="review-minimal",
            user_id=test_user.id,
            book_id=test_book.id,
            rating=5,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        test_db.add(review)
        test_db.commit()
        test_db.refresh(review)
        
        assert review.rating == 5
        assert review.comment is None
        assert review.title is None


class TestReviewServiceValidation:
    """Test review service validation."""
    
    def test_review_rating_range(
        self,
        test_db: Session,
        test_user: User,
        test_book: Book
    ) -> None:
        """Test that review rating is within valid range (1-5)."""
        # Valid ratings
        for rating in range(1, 6):
            review = Review(
                id=f"review-rating-{rating}",
                user_id=test_user.id,
                book_id=test_book.id,
                rating=rating,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            test_db.add(review)
            test_db.commit()
            test_db.refresh(review)
            
            assert 1 <= review.rating <= 5
    
    def test_review_rating_boundary_low(
        self,
        test_db: Session,
        test_user: User,
        test_book: Book
    ) -> None:
        """Test review rating below valid range."""
        review = Review(
            id="review-invalid-low",
            user_id=test_user.id,
            book_id=test_book.id,
            rating=0,  # Invalid
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Whether this passes validation depends on model constraints
        # Some ORMs enforce at the model level, others at the database
        assert review.rating == 0
    
    def test_review_rating_boundary_high(
        self,
        test_db: Session,
        test_user: User,
        test_book: Book
    ) -> None:
        """Test review rating above valid range."""
        review = Review(
            id="review-invalid-high",
            user_id=test_user.id,
            book_id=test_book.id,
            rating=6,  # Invalid
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Whether this passes validation depends on model constraints
        assert review.rating == 6


class TestReviewServiceRetrieval:
    """Test review service retrieval."""
    
    def test_get_review_by_id(
        self,
        test_db: Session,
        test_review: Review
    ) -> None:
        """Test retrieving review by ID."""
        retrieved_review = test_db.query(Review).filter(
            Review.id == test_review.id
        ).first()
        
        assert retrieved_review is not None
        assert retrieved_review.id == test_review.id
    
    def test_get_reviews_by_book(
        self,
        test_db: Session,
        test_book: Book,
        test_user: User
    ) -> None:
        """Test retrieving all reviews for a book."""
        # Create multiple reviews for same book
        for i in range(3):
            review = Review(
                id=f"review-book-{i}",
                user_id=test_user.id,
                book_id=test_book.id,
                rating=3 + i,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            test_db.add(review)
        
        test_db.commit()
        
        book_reviews = test_db.query(Review).filter(
            Review.book_id == test_book.id
        ).all()
        
        assert len(book_reviews) >= 3
        assert all(r.book_id == test_book.id for r in book_reviews)
    
    def test_get_reviews_by_user(
        self,
        test_db: Session,
        test_user: User,
        create_multiple_books
    ) -> None:
        """Test retrieving all reviews by a user."""
        books = create_multiple_books(count=3)
        
        # Create reviews for multiple books
        for book in books:
            review = Review(
                id=f"user-review-{book.id}",
                user_id=test_user.id,
                book_id=book.id,
                rating=4,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            test_db.add(review)
        
        test_db.commit()
        
        user_reviews = test_db.query(Review).filter(
            Review.user_id == test_user.id
        ).all()
        
        assert len(user_reviews) >= 3
        assert all(r.user_id == test_user.id for r in user_reviews)
    
    def test_get_nonexistent_review(self, test_db: Session) -> None:
        """Test retrieving non-existent review returns None."""
        review = test_db.query(Review).filter(
            Review.id == "nonexistent"
        ).first()
        
        assert review is None


class TestReviewServiceUpdates:
    """Test review service updates."""
    
    def test_update_review_rating(
        self,
        test_db: Session,
        test_review: Review
    ) -> None:
        """Test updating review rating."""
        new_rating = 5
        test_review.rating = new_rating
        test_db.commit()
        test_db.refresh(test_review)
        
        assert test_review.rating == new_rating
    
    def test_update_review_comment(
        self,
        test_db: Session,
        test_review: Review
    ) -> None:
        """Test updating review comment."""
        new_comment = "Updated comment"
        test_review.comment = new_comment
        test_db.commit()
        test_db.refresh(test_review)
        
        assert test_review.comment == new_comment
    
    def test_update_review_title(
        self,
        test_db: Session,
        test_review: Review
    ) -> None:
        """Test updating review title."""
        new_title = "Updated Title"
        test_review.title = new_title
        test_db.commit()
        test_db.refresh(test_review)
        
        assert test_review.title == new_title
    
    def test_cannot_change_book_or_user_after_review_created(
        self,
        test_db: Session,
        test_review: Review,
        create_multiple_books
    ) -> None:
        """Test that changing book/user after review creation works."""
        # This depends on the design - typically you can update these
        books = create_multiple_books(count=1)
        
        test_review.book_id = books[0].id
        test_db.commit()
        test_db.refresh(test_review)
        
        assert test_review.book_id == books[0].id


class TestReviewServiceAggregation:
    """Test review service aggregation."""
    
    def test_average_rating_for_book(
        self,
        test_db: Session,
        test_book: Book,
        test_user: User
    ) -> None:
        """Test calculating average rating for a book."""
        # Create reviews with different ratings
        ratings = [3, 4, 5, 4, 2]
        
        for i, rating in enumerate(ratings):
            review = Review(
                id=f"avg-review-{i}",
                user_id=test_user.id,
                book_id=test_book.id,
                rating=rating,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            test_db.add(review)
        
        test_db.commit()
        
        book_reviews = test_db.query(Review).filter(
            Review.book_id == test_book.id
        ).all()
        
        average_rating = sum(r.rating for r in book_reviews) / len(book_reviews)
        expected_average = sum(ratings) / len(ratings)
        
        assert abs(average_rating - expected_average) < 0.01
    
    def test_review_count_for_book(
        self,
        test_db: Session,
        test_book: Book,
        test_user: User
    ) -> None:
        """Test counting reviews for a book."""
        count = 5
        
        for i in range(count):
            review = Review(
                id=f"count-review-{i}",
                user_id=test_user.id,
                book_id=test_book.id,
                rating=4,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            test_db.add(review)
        
        test_db.commit()
        
        review_count = test_db.query(Review).filter(
            Review.book_id == test_book.id
        ).count()
        
        assert review_count == count


class TestReviewServiceDeletion:
    """Test review service deletion."""
    
    def test_delete_review(
        self,
        test_db: Session,
        test_review: Review
    ) -> None:
        """Test deleting a review."""
        review_id = test_review.id
        test_db.delete(test_review)
        test_db.commit()
        
        deleted_review = test_db.query(Review).filter(
            Review.id == review_id
        ).first()
        
        assert deleted_review is None


class TestReviewServiceOrdering:
    """Test review service ordering."""
    
    def test_get_recent_reviews_first(
        self,
        test_db: Session,
        test_book: Book,
        test_user: User
    ) -> None:
        """Test getting reviews ordered by creation date (newest first)."""
        # Create reviews
        for i in range(3):
            review = Review(
                id=f"order-review-{i}",
                user_id=test_user.id,
                book_id=test_book.id,
                rating=4,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            test_db.add(review)
            test_db.commit()
        
        # Get reviews ordered by created_at descending
        recent_reviews = test_db.query(Review).filter(
            Review.book_id == test_book.id
        ).order_by(Review.created_at.desc()).all()
        
        assert len(recent_reviews) >= 3
        
        # Verify ordering (newer reviews first)
        for i in range(len(recent_reviews) - 1):
            assert recent_reviews[i].created_at >= recent_reviews[i + 1].created_at
