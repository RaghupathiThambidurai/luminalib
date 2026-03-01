/**
 * Book Service - Handles all book-related API calls
 */

import { apiClient } from "@/lib/api-client";
import type {
  Book,
  BorrowRecord,
  BorrowedBook,
  CreateBookRequest,
  PaginatedResponse,
} from "@/types";

export const bookService = {
  /**
   * Get all books with pagination
   */
  async getBooks(
    skip: number = 0,
    limit: number = 10
  ): Promise<PaginatedResponse<Book>> {
    return apiClient.request(
      `/api/books?skip=${skip}&limit=${Math.min(limit, 100)}`,
      {
        method: "GET",
      }
    );
  },

  /**
   * Get a single book by ID
   */
  async getBook(bookId: string): Promise<Book> {
    return apiClient.request(`/api/books/${bookId}`, {
      method: "GET",
    });
  },

  /**
   * Search books by title, author, or description
   */
  async searchBooks(
    query: string,
    skip: number = 0,
    limit: number = 10
  ): Promise<PaginatedResponse<Book>> {
    const encodedQuery = encodeURIComponent(query);
    return apiClient.request(
      `/api/books/search/${encodedQuery}?skip=${skip}&limit=${Math.min(limit, 100)}`,
      {
        method: "GET",
      }
    );
  },

  /**
   * Create a new book with optional file upload
   */
  async createBook(data: CreateBookRequest): Promise<Book> {
    const formData = new FormData();

    // Add metadata fields
    formData.append("title", data.title);
    formData.append("author", data.author);

    if (data.isbn) formData.append("isbn", data.isbn);
    if (data.description) formData.append("description", data.description);
    if (data.genre) formData.append("genre", data.genre);
    if (data.published_date)
      formData.append("published_date", data.published_date);
    if (data.cover_url) formData.append("cover_url", data.cover_url);

    // Add file if provided
    if (data.file) {
      formData.append("file", data.file);
    }

    return apiClient.uploadFile("/api/books/", formData);
  },

  /**
   * Update book metadata
   */
  async updateBook(bookId: string, updates: Partial<Book>): Promise<Book> {
    return apiClient.request(`/api/books/${bookId}`, {
      method: "PUT",
      body: updates,
    });
  },

  /**
   * Delete a book
   */
  async deleteBook(bookId: string): Promise<void> {
    return apiClient.request(`/api/books/${bookId}`, {
      method: "DELETE",
    });
  },

  /**
   * Borrow a book
   */
  async borrowBook(
    bookId: string,
    dueDateDays: number = 14
  ): Promise<{ borrow_id: string; status: string; due_date: string }> {
    return apiClient.request(`/api/books/${bookId}/borrow`, {
      method: "POST",
      body: { due_date_days: dueDateDays },
    });
  },

  /**
   * Return a borrowed book
   */
  async returnBook(bookId: string): Promise<BorrowRecord> {
    return apiClient.request(`/api/books/${bookId}/return`, {
      method: "POST",
    });
  },

  /**
   * Get books borrowed by current user
   */
  async getMyBorrowedBooks(
    includeReturned: boolean = false
  ): Promise<{
    borrowed_books: BorrowedBook[];
    active_count: number;
    overdue_count: number;
    total_count: number;
    user_id: string;
  }> {
    return apiClient.request(
      `/api/books/my-borrows?include_returned=${includeReturned}`,
      {
        method: "GET",
      }
    );
  },
};
