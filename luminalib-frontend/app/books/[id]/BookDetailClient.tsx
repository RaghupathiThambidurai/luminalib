"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { borrowService } from "@/api/borrow-service";
import { reviewService } from "@/api/review-service";
import type { Book, Review } from "@/types";

type Props = {
    bookId: string;
    initialBook: Book;
    initialReviews: Review[];
};

export default function BookDetailClient({
    bookId,
    initialBook,
    initialReviews,
}: Props) {
    const router = useRouter();

    const [book, setBook] = useState<Book>(initialBook);
    const [reviews, setReviews] = useState<Review[]>(initialReviews);
    const [error, setError] = useState<string | null>(null);
    const [isBorrowing, setIsBorrowing] = useState(false);
    const [isSubmittingReview, setIsSubmittingReview] = useState(false);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);
    const [reviewData, setReviewData] = useState({
        rating: 5,
        content: "",
    });

    useEffect(() => {
        if (successMessage) {
            const timer = setTimeout(() => {
                setSuccessMessage(null);
            }, 3000); // disappear after 3 seconds

            return () => clearTimeout(timer);
        }
    }, [successMessage]);

    const refreshData = async () => {
        try {
            const reviewsResponse = await reviewService.getBookReviews(bookId);
            setReviews(reviewsResponse.reviews ?? []);
            router.refresh();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to refresh book");
        }
    };

    const handleBorrowBook = async () => {
        try {
            setIsBorrowing(true);
            setError(null);
            setSuccessMessage(null);

            const response = await borrowService.borrowBook(bookId, {
                due_date_days: 14,
            });

            setSuccessMessage(response.message || "Book borrowed successfully");

            await refreshData();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to borrow book");
        } finally {
            setIsBorrowing(false);
        }
    };

    const handleSubmitReview = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!reviewData.content.trim()) {
            setError("Please write a review");
            return;
        }

        if (reviewData.content.trim().length < 10) {
            setError("Review must be at least 10 characters long");
            return;
        }

        try {
            setIsSubmittingReview(true);
            setError(null);

            setSuccessMessage(null);

            const response = await reviewService.submitReview(bookId, {
                rating: reviewData.rating,
                content: reviewData.content,
            });

            setSuccessMessage(
                response?.content
                    ? "Review submitted successfully"
                    : "Review submitted successfully"
            );

            setReviewData({ rating: 5, content: "" });
            await refreshData();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to submit review");
        } finally {
            setIsSubmittingReview(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-50">
            <header className="bg-white border-b border-slate-200">
                <div className="max-w-4xl mx-auto px-4 py-6 flex items-center justify-between">
                    <Link href="/books" className="text-blue-600 hover:text-blue-700">
                        ← Back to Books
                    </Link>
                </div>
            </header>

            <main className="max-w-4xl mx-auto px-4 py-12">
                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
                        {error}
                    </div>
                )}
                {successMessage && (
                    <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md mb-6">
                        {successMessage}
                    </div>
                )}

                <div className="bg-white rounded-lg shadow-md p-8 mb-8">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
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

                            {book.metadata?.summary && (
                                <div className="mt-6 rounded-lg border border-slate-200 bg-slate-50 p-4">
                                    <h2 className="text-lg font-semibold text-slate-900 mb-2">
                                        AI Summary
                                    </h2>
                                    <p className="text-slate-700 leading-relaxed">
                                        {book.metadata.summary}
                                    </p>
                                </div>
                            )}

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

                <div className="space-y-8">
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
                                            rating: parseInt(e.target.value, 10),
                                        })
                                    }
                                    className="w-full px-4 py-2 text-black border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                                            <p className="font-semibold text-slate-900">
                                                {Array(review.rating).fill("⭐").join("")}
                                            </p>
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
            </main>
        </div>
    );
}