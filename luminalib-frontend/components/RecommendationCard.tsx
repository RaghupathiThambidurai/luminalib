import React from "react";
import Link from "next/link";
import type { Recommendation } from "@/types";

export interface RecommendationCardProps {
  rec: Recommendation;
  className?: string;
}

const RecommendationCard: React.FC<RecommendationCardProps> = ({ rec, className = "" }) => (
  <Link
    href={`/books/${rec.book_id}`}
    className={
      "bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow overflow-hidden " +
      className
    }
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
          <h3 className="font-semibold text-slate-900 line-clamp-2">{rec.book.title}</h3>
          <p className="text-sm text-slate-600 mb-2">{rec.book.author}</p>
        </>
      )}
      <p className="text-xs text-slate-600 mb-3 line-clamp-2">{rec.reason}</p>
      <div className="flex items-center justify-between">
        <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
          {(rec.score * 100).toFixed(0)}% match
        </span>
      </div>
    </div>
  </Link>
);

export default RecommendationCard;
