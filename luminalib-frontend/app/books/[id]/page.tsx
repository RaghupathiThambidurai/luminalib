"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { bookService } from "@/api/book-service";
import { borrowService } from "@/api/borrow-service";
import { reviewService } from "@/api/review-service";
import type { Book, Review, CreateReviewRequest } from "@/types";

export default function BookDetailPage() {
  const router = useRouter();
  const params = useParams();
  const bookId = params.id as string;
  const { user, isLoading: authLoading } = useAuth();

  const [book, setBook] = useState<Book | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isBorrowing, setIsBorrowing] = useState(false);
  const [isSubmittingReview, setIsSubmittingReview] = useState(false);
  const [reviewData, setReviewData] = useState({
    rating: 5,
    content: "",
  });

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/auth/login");
      return;
    }

    if (user) {
      loadBookDetails();
    }
  }, [user, authLoading, router]);

  const loadBookDetails = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const bookData = await bookService.getBook(bookId);
      setBook(bookData);

      // Load reviews
      const reviewsResponse = await reviewService.getBookReviews(bookId);
      setReviews(reviewsResponse.reviews);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load book";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBorrowBook = async () => {
    try {
      setIsBorrowing(true);
      setError(null);
      await borrowService.borrowBook(bookId);
      alert("Book borrowed successfully!");
      loadBookDetails();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to borrow book";
      setError(message);
    } finally {
      setIsBorrowing(false);
    }
  };

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reviewData.content.trim()) {
      alert("Please write a review");
      return;
    }

    if (reviewData.content.trim().length < 10) {
      alert("Review must be at least 10 characters long");
      return;
    }

    try {
      setIsSubmittingReview(true);
      await reviewService.submitReview(bookId, {
        rating: reviewData.rating,
        content: reviewData.content,
      });
      setReviewData({ rating: 5, content: "" });
      loadBookDetails();
      alert("Review submitted successfully!");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to submit review";
      setError(message);
    } finally {
      setIsSubmittingReview(false);
    }
  };

  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg text-slate-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-4 py-6 flex items-center justify-between">
          <Link href="/books" className="text-blue-600 hover:text-blue-700">
            ← Back to Books
          </Link>
          <div className="text-sm text-slate-600">{user?.username}</div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-12">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="text-center text-slate-600">Loading book details...</div>
        ) : book ? (
          <>
            {/* Book Info */}
            <div className="bg-white rounded-lg shadow-md p-8 mb-8">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                {/* Cover Image */}
                <div className="md:col-span-1">
                  <div className="aspect-square bg-slate-200 rounded-lg flex items-center justify-center overflow-hidden">
                    {book.cover_url ? (
                      <img
                        src={book.cover_url}
                        alt={book.title}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="text-slate-400">No Cover</div>
                    )}
                  </div>
                </div>

                {/* Book Details */}
                <div className="md:col-span-3">
                  <h1 className="text-3xl font-bold text-slate-900 mb-2">
                    {book.title}
                  </h1>
                  <p className="text-xl text-slate-600 mb-4">by {book.author}</p>

                  {book.genre && (
                    <p className="text-slate-600 mb-2">
                      <span className="font-semibold">Genre:</span> {book.genre}
                    </p>
                  )}
                  {book.isbn && (
                    <p className="text-slate-600 mb-2">
                      <span className="font-semibold">ISBN:</span> {book.isbn}
                    </p>
                  )}
                  {book.published_date && (
                    <p className="text-slate-600 mb-4">
                      <span className="font-semibold">Published:</span>{" "}
                      {new Date(book.published_date).toLocaleDateString()}
                    </p>
                  )}

                  <p className="text-slate-600 mb-6 leading-relaxed">
                    {book.description || "No description available."}
                  </p>

                  {/* AI-Generated Summary Section */}
                  {book.metadata?.summary && typeof book.metadata.summary === "string" ? (
                    <div className="bg-blue-50 border-l-4 border-blue-500 rounded-r-lg p-6 mb-6">
                      <div className="flex items-start gap-3">
                        <span className="text-2xl">✨</span>
                        <div className="flex-1">
                          <h3 className="text-lg font-bold text-blue-900 mb-2">
                            AI-Generated Summary
                          </h3>
                          <p className="text-slate-700 leading-relaxed mb-3">
                            {book.metadata.summary}
                          </p>
                          {book.metadata.summary_generated_at && typeof book.metadata.summary_generated_at === "string" && (
                            <p className="text-xs text-slate-500">
                              Generated {new Date(book.metadata.summary_generated_at).toLocaleDateString()}
                              {book.metadata.summary_model && typeof book.metadata.summary_model === "string" && ` using ${book.metadata.summary_model}`}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : book.file_url ? (
                    <div className="bg-amber-50 border-l-4 border-amber-500 rounded-r-lg p-6 mb-6">
                      <div className="flex items-start gap-3">
                        <span className="text-2xl">⏳</span>
                        <div>
                          <h3 className="text-lg font-bold text-amber-900 mb-1">
                            Summary Loading
                          </h3>
                          <p className="text-amber-800 text-sm">
                            AI is generating a summary of this book. Please refresh the page in a moment to see it.
                          </p>
                        </div>
                      </div>
                    </div>
                  ) : null}

                  <button
                    onClick={handleBorrowBook}
                    disabled={isBorrowing}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white font-semibold px-6 py-3 rounded-md transition-colors"
                  >
                    {isBorrowing ? "Borrowing..." : "Borrow Book"}
                  </button>
                </div>
              </div>
            </div>

            {/* Reviews Section */}
            <div className="space-y-8">
              {/* Submit Review Form */}
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-bold text-slate-900 mb-6">
                  Write a Review
                </h2>

                <form onSubmit={handleSubmitReview} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Rating
                    </label>
                    <select
                      value={reviewData.rating}
                      onChange={(e) =>
                        setReviewData({
                          ...reviewData,
                          rating: parseInt(e.target.value),
                        })
                      }
                      className="w-full px-4 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {[5, 4, 3, 2, 1].map((rating) => (
                        <option key={rating} value={rating}>
                          {rating} Star{rating > 1 ? "s" : ""}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Your Review
                    </label>
                    <textarea
                      value={reviewData.content}
                      onChange={(e) =>
                        setReviewData({
                          ...reviewData,
                          content: e.target.value,
                        })
                      }
                      rows={4}
                      className="w-full px-4 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
                      placeholder="Share your thoughts about this book..."
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={isSubmittingReview}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white font-semibold px-6 py-2 rounded-md transition-colors"
                  >
                    {isSubmittingReview ? "Submitting..." : "Submit Review"}
                  </button>
                </form>
              </div>

              {/* Reviews List */}
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-bold text-slate-900 mb-6">
                  Reviews ({reviews.length})
                </h2>

                {reviews.length === 0 ? (
                  <p className="text-slate-600">
                    No reviews yet. Be the first to review!
                  </p>
                ) : (
                  <div className="space-y-4">
                    {reviews.map((review) => (
                      <div key={review.id} className="border-t border-slate-200 pt-4">
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <p className="font-semibold text-slate-900">
                              {Array(review.rating).fill("⭐").join("")}
                            </p>
                          </div>
                          <p className="text-sm text-slate-500">
                            {new Date(review.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <p className="text-slate-700">{review.content}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </>
        ) : (
          <div className="text-center text-slate-600">Book not found</div>
        )}
      </main>
    </div>
  );
}
