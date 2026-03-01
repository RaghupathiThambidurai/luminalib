/**
 * Borrow Service - Handles book borrowing and returning operations
 */

import { apiClient } from "@/lib/api-client";
import type { BorrowResponse, MyBorrowsResponse, BorrowBookRequest } from "@/types";

export const borrowService = {
  /**
   * Borrow a book by ID
   */
  async borrowBook(
    bookId: string,
    request?: BorrowBookRequest
  ): Promise<BorrowResponse> {
    return apiClient.request(`/api/books/${bookId}/borrow`, {
      method: "POST",
      body: request || {},
    });
  },

  /**
   * Return a borrowed book
   */
  async returnBook(bookId: string): Promise<BorrowResponse> {
    return apiClient.request(`/api/books/${bookId}/return`, {
      method: "POST",
    });
  },

  /**
   * Get list of books currently borrowed by the authenticated user
   */
  async getMyBorrows(
    includeReturned: boolean = false
  ): Promise<MyBorrowsResponse> {
    const params = new URLSearchParams();
    if (includeReturned) {
      params.append("include_returned", "true");
    }

    const queryString = params.toString();
    const endpoint = queryString
      ? `/api/books/my-borrows?${queryString}`
      : "/api/books/my-borrows";

    return apiClient.request(endpoint, {
      method: "GET",
    });
  },
};
