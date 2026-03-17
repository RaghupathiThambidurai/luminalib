"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import type { MyBorrowsResponse, Recommendation, UserResponse } from "@/types";
import { borrowService } from "@/api/borrow-service";
import { reviewService } from "@/api/review-service";
import Alert from "@/components/Alert";
import Header from "@/components/Header";
import RecommendationCard from "@/components/RecommendationCard";

type Props = {
  initialUser: UserResponse;
  initialBorrows: MyBorrowsResponse;
  initialRecommendations: Recommendation[];
};

export default function ProfileClient({
  initialUser,
  initialBorrows,
  initialRecommendations,
}: Props) {
  const router = useRouter();

  const [user] = useState(initialUser);
  const [borrows, setBorrows] = useState(initialBorrows);
  const [recommendations, setRecommendations] = useState(initialRecommendations);

  const [error, setError] = useState<string | null>(null);
  const [isReturning, setIsReturning] = useState<string | null>(null);

  const refreshData = async () => {
    try {
      const [borrowsData, recsData] = await Promise.all([
        borrowService.getMyBorrows(false),
        reviewService.getRecommendations(5),
      ]);

      setBorrows(borrowsData);
      setRecommendations(recsData);

      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to refresh profile");
    }
  };

  const handleReturnBook = async (bookId: string) => {
    try {
      setIsReturning(bookId);
      setError(null);

      await borrowService.returnBook(bookId);

      await refreshData();
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to return book";
      setError(message);
    } finally {
      setIsReturning(null);
    }
  };

  const handleLogout = () => {
    document.cookie =
      "access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    document.cookie =
      "refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";

    localStorage.removeItem("luminallib_access_token");
    localStorage.removeItem("luminallib_refresh_token");

    router.push("/auth/login");
    router.refresh();
  };

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

        {/* Profile Card */}
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
              <p className="text-lg font-semibold text-slate-900">
                {user.email}
              </p>
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
               {new Date(user.created_at).toLocaleDateString("en-GB")}
              </p>
            </div>
          </div>
        </div>

        {/* Borrow + Recommendations */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

          {/* Borrowed Books */}
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-6">
              My Borrowed Books
            </h2>

            {borrows.borrowed_books.length > 0 ? (
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

                        <div className="mt-3 flex gap-2">
                          <Link
                            href={`/books/${borrow.book.id}`}
                            className="text-sm px-3 py-2 rounded-md border border-slate-300 hover:bg-slate-50"
                          >
                            View
                          </Link>

                          <button
                            onClick={() =>
                              handleReturnBook(borrow.book.id)
                            }
                            disabled={isReturning === borrow.book.id}
                            className="text-sm px-3 py-2 rounded-md bg-slate-900 text-white hover:bg-slate-800 disabled:opacity-60"
                          >
                            {isReturning === borrow.book.id
                              ? "Returning..."
                              : "Return"}
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
                <Link
                  href="/books"
                  className="text-blue-600 hover:text-blue-700"
                >
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
                No recommendations yet. Borrow and review books to get
                personalized recommendations.
              </p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}