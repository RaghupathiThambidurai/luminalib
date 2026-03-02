"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { borrowService } from "@/api/borrow-service";
import { reviewService } from "@/api/review-service";
import type { MyBorrowsResponse, Recommendation } from "@/types";
import Alert from "@/components/Alert";
import Header from "@/components/Header";
import RecommendationCard from "@/components/RecommendationCard";

export default function ProfilePage() {
    const router = useRouter();
    const { user, logout, isLoading: authLoading } = useAuth();

    const [borrows, setBorrows] = useState<MyBorrowsResponse | null>(null);
    const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isReturning, setIsReturning] = useState<string | null>(null);


    useEffect(() => {
        if (!authLoading && !user) {
            router.push("/auth/login");
            return;
        }

        if (user) {
            loadProfileData();
        }
    }, [user, authLoading, router]);


    const handleReturnBook = async (bookId: string) => {
        try {
            setIsReturning(bookId);
            setError(null);

            await borrowService.returnBook(bookId); // ✅ use bookId passed from map

            alert("Book returned successfully!");
            await loadProfileData();
        } catch (err) {
            const message = err instanceof Error ? err.message : "Failed to return book";
            setError(message);
        } finally {
            setIsReturning(null);
        }
    };

    const loadProfileData = async () => {
        try {
            setIsLoading(true);
            setError(null);

            // Load borrowed books
            const borrowsData = await borrowService.getMyBorrows(false);
            setBorrows(borrowsData);

            // Load recommendations
            const recsData = await reviewService.getRecommendations(5);
            setRecommendations(recsData);
        } catch (err) {
            const message = err instanceof Error ? err.message : "Failed to load profile data";
            setError(message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleLogout = async () => {
        await logout();
    };

    if (authLoading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-lg text-slate-600">Loading...</div>
            </div>
        );
    }

    if (!user) {
        return null;
    }

    return (
        <div className="min-h-screen bg-slate-50">
            <Header
                backLink={{ href: "/books", label: "← Back to Books" }}
                right={
                    <button
                        onClick={handleLogout}
                        className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
                    >
                        Logout
                    </button>
                }
            />

            <main className="max-w-6xl mx-auto px-4 py-12">
                {error && <Alert message={error} type="error" className="mb-6" />}

                {/* User Profile Card */}
                <div className="bg-white rounded-lg shadow-md p-8 mb-8">
                    <h1 className="text-3xl font-bold text-slate-900 mb-6">My Profile</h1>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <p className="text-sm font-medium text-slate-600">Username</p>
                            <p className="text-lg font-semibold text-slate-900">
                                {user.username}
                            </p>
                        </div>
                        <div>
                            <p className="text-sm font-medium text-slate-600">Email</p>
                            <p className="text-lg font-semibold text-slate-900">{user.email}</p>
                        </div>
                        <div>
                            <p className="text-sm font-medium text-slate-600">Full Name</p>
                            <p className="text-lg font-semibold text-slate-900">
                                {user.full_name || "Not provided"}
                            </p>
                        </div>
                        <div>
                            <p className="text-sm font-medium text-slate-600">Member Since</p>
                            <p className="text-lg font-semibold text-slate-900">
                                {new Date(user.created_at).toLocaleDateString()}
                            </p>
                        </div>
                    </div>
                </div>

                {isLoading ? (
                    <div className="text-center text-slate-600">Loading your data...</div>
                ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        {/* My Borrowed Books */}
                        <div className="bg-white rounded-lg shadow-md p-8">
                            <h2 className="text-2xl font-bold text-slate-900 mb-6">
                                My Borrowed Books
                            </h2>

                            {borrows && borrows.borrowed_books.length > 0 ? (
                                <>
                                    <div className="space-y-4 mb-4">
                                        {borrows.borrowed_books.map((borrow) => (
                                            <div
                                                key={borrow.borrow_id}
                                                className="border border-slate-200 rounded-lg p-4"
                                            >
                                                <h3 className="font-semibold text-slate-900">
                                                    {borrow.book.title}
                                                </h3>
                                                <p className="text-sm text-slate-600">
                                                    by {borrow.book.author}
                                                </p>
                                                <div className="mt-2 text-sm">
                                                    <p className="text-slate-600">
                                                        Due:{" "}
                                                        {new Date(borrow.due_date).toLocaleDateString()}
                                                    </p>
                                                    <p
                                                        className={`font-semibold ${borrow.is_overdue
                                                                ? "text-red-600"
                                                                : "text-green-600"
                                                            }`}
                                                    >
                                                        {borrow.is_overdue
                                                            ? "Overdue"
                                                            : `${borrow.days_remaining} days remaining`}
                                                    </p>
                                                    <div className="mt-3 flex gap-2">
                                                        <Link
                                                            href={`/books/${borrow.book.id}`}
                                                            className="text-sm px-3 py-2 rounded-md border border-slate-300 hover:bg-slate-50"
                                                        >
                                                            View
                                                        </Link>

                                                        <button
                                                            onClick={() => handleReturnBook(borrow.book.id)}
                                                            disabled={isReturning === borrow.book.id}
                                                            className="text-sm px-3 py-2 rounded-md bg-slate-900 text-white hover:bg-slate-800 disabled:opacity-60"
                                                        >
                                                            {isReturning === borrow.book.id ? "Returning..." : "Return"}
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="text-sm text-slate-600 pt-4 border-t border-slate-200">
                                        <p>
                                            Active: {borrows.active_count} | Overdue:{" "}
                                            {borrows.overdue_count}
                                        </p>
                                    </div>
                                </>
                            ) : (
                                <p className="text-slate-600">
                                    You haven't borrowed any books yet.{" "}
                                    <Link href="/books" className="text-blue-600 hover:text-blue-700">
                                        Browse books
                                    </Link>
                                </p>
                            )}
                        </div>

                        {/* Recommendations */}
                        <div className="bg-white rounded-lg shadow-md p-8">
                            <h2 className="text-2xl font-bold text-slate-900 mb-6">
                                Recommended For You
                            </h2>
                            {recommendations.length > 0 ? (
                                <div className="space-y-4">
                                    {recommendations.map((rec) => (
                                        <RecommendationCard key={rec.book_id} rec={rec} />
                                    ))}
                                </div>
                            ) : (
                                <p className="text-slate-600">
                                    No recommendations yet. Borrow and review books to get personalized recommendations.
                                </p>
                            )}
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
