"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { reviewService } from "@/api/review-service";
import type { Recommendation } from "@/types";
import Alert from "@/components/Alert";
import Header from "@/components/Header";
import RecommendationCard from "@/components/RecommendationCard";

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
      <Header
        backLink={{ href: "/books", label: "← Back to Books" }}
        right={<div className="text-sm text-slate-600">{user?.username}</div>}
      />

      <main className="max-w-6xl mx-auto px-4 py-12">
        <h1 className="text-3xl font-bold text-slate-900 mb-8">
          Recommendations For You
        </h1>

        {error && <Alert message={error} type="error" className="mb-6" />}

        {isLoading ? (
          <div className="text-center text-slate-600">Loading recommendations...</div>
        ) : recommendations.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <p className="text-slate-600 mb-4">
              No recommendations available yet.
            </p>
            <p className="text-slate-600 mb-6">
              Start borrowing books and writing reviews to get personalized recommendations.
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
              <RecommendationCard key={rec.book_id} rec={rec} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
