/**
 * Review Service - Handles book reviews and recommendations
 */

import { apiClient } from "@/lib/api-client";
import type {
  Review,
  ReviewAnalysis,
  Recommendation,
  CreateReviewRequest,
  ReviewPaginatedResponse,
} from "@/types";

export const reviewService = {
  /**
   * Submit a review for a book
   */
  async submitReview(
    bookId: string,
    review: CreateReviewRequest
  ): Promise<Review> {
    return apiClient.request(`/api/books/${bookId}/reviews`, {
      method: "POST",
      body: review,
    });
  },

  /**
   * Get all reviews for a specific book
   */
  async getBookReviews(
    bookId: string,
    skip: number = 0,
    limit: number = 10
  ): Promise<ReviewPaginatedResponse<Review>> {
    return apiClient.request(
      `/api/books/${bookId}/reviews?skip=${skip}&limit=${Math.min(limit, 100)}`,
      {
        method: "GET",
      }
    );
  },

  /**
   * Get analysis/statistics for book reviews
   */
  async getReviewAnalysis(bookId: string): Promise<ReviewAnalysis> {
    return apiClient.request(`/api/books/${bookId}/reviews/analysis`, {
      method: "GET",
    });
  },

  /**
   * Get personalized book recommendations for the authenticated user
   */
  async getRecommendations(limit: number = 10): Promise<Recommendation[]> {
    return apiClient.request(`/api/recommendations?limit=${Math.min(limit, 100)}`, {
      method: "GET",
    });
  },

  /**
   * Get recommendations similar to a specific book
   */
  async getBookBasedRecommendations(
    bookId: string,
    limit: number = 10
  ): Promise<Recommendation[]> {
    return apiClient.request(
      `/api/books/${bookId}/recommendations?limit=${Math.min(limit, 100)}`,
      {
        method: "GET",
      }
    );
  },

  /**
   * Mark a review as helpful
   */
  async markReviewHelpful(reviewId: string): Promise<{ helpful: boolean }> {
    return apiClient.request(`/api/reviews/${reviewId}/helpful`, {
      method: "POST",
    });
  },

  /**
   * Delete a review (only by review author)
   */
  async deleteReview(reviewId: string): Promise<void> {
    return apiClient.request(`/api/reviews/${reviewId}`, {
      method: "DELETE",
    });
  },
};
