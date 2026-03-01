"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { reviewService } from "@/api/review-service";
import type { Recommendation } from "@/types";

export default function ReviewsPage() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();

  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/auth/login");
      return;
    }

    if (user) {
      loadRecommendations();
    }
  }, [user, authLoading, router]);

  const loadRecommendations = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const recsData = await reviewService.getRecommendations(50);
      setRecommendations(recsData);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load recommendations";
      setError(message);
    } finally {
      setIsLoading(false);
    }
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
          <div className="text-sm text-slate-600">{user?.username}</div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-12">
        <h1 className="text-3xl font-bold text-slate-900 mb-8">
          Recommendations For You
        </h1>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="text-center text-slate-600">Loading recommendations...</div>
        ) : recommendations.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <p className="text-slate-600 mb-4">
              No recommendations available yet.
            </p>
            <p className="text-slate-600 mb-6">
              Start borrowing books and writing reviews to get personalized
              recommendations.
            </p>
            <Link
              href="/books"
              className="inline-block bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700"
            >
              Browse Books
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recommendations.map((rec) => (
              <Link
                key={rec.book_id}
                href={`/books/${rec.book_id}`}
                className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow overflow-hidden"
              >
                <div className="aspect-square bg-slate-200 flex items-center justify-center">
                  {rec.book?.cover_url ? (
                    <img
                      src={rec.book.cover_url}
                      alt={rec.book.title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="text-slate-400 text-center">
                      <div>No Cover</div>
                    </div>
                  )}
                </div>
                <div className="p-4">
                  {rec.book && (
                    <>
                      <h3 className="font-semibold text-slate-900 line-clamp-2">
                        {rec.book.title}
                      </h3>
                      <p className="text-sm text-slate-600 mb-2">
                        {rec.book.author}
                      </p>
                    </>
                  )}
                  <p className="text-xs text-slate-600 mb-3 line-clamp-2">
                    {rec.reason}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                      {(rec.score * 100).toFixed(0)}% match
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
