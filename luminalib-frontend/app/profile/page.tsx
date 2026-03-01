"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { borrowService } from "@/api/borrow-service";
import { reviewService } from "@/api/review-service";
import type { MyBorrowsResponse, Recommendation } from "@/types";

export default function ProfilePage() {
  const router = useRouter();
  const { user, logout, isLoading: authLoading } = useAuth();

  const [borrows, setBorrows] = useState<MyBorrowsResponse | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/auth/login");
      return;
    }

    if (user) {
      loadProfileData();
    }
  }, [user, authLoading, router]);

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
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-4 py-6 flex items-center justify-between">
          <Link href="/books" className="text-blue-600 hover:text-blue-700">
            ← Back to Books
          </Link>
          <button
            onClick={handleLogout}
            className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-12">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
            {error}
          </div>
        )}

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
                          {borrow.title}
                        </h3>
                        <p className="text-sm text-slate-600">
                          by {borrow.author}
                        </p>
                        <div className="mt-2 text-sm">
                          <p className="text-slate-600">
                            Due:{" "}
                            {new Date(borrow.due_date).toLocaleDateString()}
                          </p>
                          <p
                            className={`font-semibold ${
                              borrow.is_overdue
                                ? "text-red-600"
                                : "text-green-600"
                            }`}
                          >
                            {borrow.is_overdue
                              ? "Overdue"
                              : `${borrow.days_remaining} days remaining`}
                          </p>
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
                    <div
                      key={rec.book_id}
                      className="border border-slate-200 rounded-lg p-4"
                    >
                      {rec.book && (
                        <>
                          <Link
                            href={`/books/${rec.book.id}`}
                            className="font-semibold text-blue-600 hover:text-blue-700"
                          >
                            {rec.book.title}
                          </Link>
                          <p className="text-sm text-slate-600">
                            by {rec.book.author}
                          </p>
                        </>
                      )}
                      <p className="text-sm text-slate-600 mt-2">
                        {rec.reason}
                      </p>
                      <div className="mt-2 text-sm">
                        <span className="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          Match: {(rec.score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-slate-600">
                  No recommendations yet. Borrow and review books to get personalized
                  recommendations.
                </p>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
