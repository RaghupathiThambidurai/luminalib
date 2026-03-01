/**
 * Domain types for LuminalLib
 */

export interface Book {
  id: string;
  title: string;
  author: string;
  isbn?: string;
  description?: string;
  genre?: string;
  published_date?: string;
  cover_url?: string;
  file_url?: string;
  file_size?: number;
  created_at: string;
  updated_at: string;
  metadata?: {
    summary?: string;
    summary_generated_at?: string;
    summary_model?: string;
    [key: string]: unknown;
  };
}

export interface BorrowRecord {
  id: string;
  book_id: string;
  user_id: string;
  borrowed_at: string;
  due_date: string;
  returned_at?: string;
  status: "active" | "returned" | "overdue";
  is_overdue?: boolean;
}

export interface BorrowedBook extends BorrowRecord {
  book?: Book;
}

export interface Review {
  id: string;
  book_id: string;
  user_id: string;
  rating: number;
  content: string;
  sentiment_score?: number;
  is_helpful?: boolean;
  helpful_count?: number;
  created_at: string;
  updated_at: string;
}

export interface ReviewAnalysis {
  book_id: string;
  average_rating: number;
  total_reviews: number;
  sentiment_distribution: {
    positive: number;
    neutral: number;
    negative: number;
  };
  key_themes: string[];
  keywords: string[];
  summary?: string;
}

export interface Recommendation {
  book_id: string;
  book?: Book;
  score: number;
  reason: string;
  scoring_breakdown?: {
    content_similarity: number;
    collaborative_filtering: number;
    user_preferences: number;
  };
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

export interface PaginatedResponse<T> {
  books: T[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

export interface ReviewPaginatedResponse<T> {
  reviews: T[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
  book_average_rating?: number;
}

export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  preferences?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface CreateBookRequest {
  title: string;
  author: string;
  isbn?: string;
  description?: string;
  genre?: string;
  published_date?: string;
  cover_url?: string;
  file?: File;
}

export interface CreateReviewRequest {
  rating: number;
  content: string;
}

export interface BorrowBookRequest {
  due_date_days?: number;
}

// Authentication Types
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface UserResponse {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  preferences?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

// Books Stats
export interface BookStats {
  review_count: number;
  average_rating: number;
  borrow_count: number;
  active_borrows: number;
}

export interface BookWithStats extends Book {
  stats?: BookStats;
}

// Borrow Response
export interface BorrowResponse {
  id: string;
  user_id: string;
  book_id: string;
  borrowed_at: string;
  due_date: string;
  returned_at?: string;
  status: "active" | "returned" | "overdue";
  is_overdue: boolean;
}

export interface MyBorrowsResponse {
  borrowed_books: Array<{
    borrow_id: string;
    book_id: string;
    title: string;
    author: string;
    borrowed_at: string;
    due_date: string;
    status: string;
    days_remaining: number;
    is_overdue: boolean;
  }>;
  active_count: number;
  overdue_count: number;
}

// Sentiment Analysis
export interface ReviewAnalysisResult {
  sentiment_score: number;
  sentiment_label: "positive" | "neutral" | "negative";
  confidence: number;
}
