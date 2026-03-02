import React from "react";
import Link from "next/link";
import type { Book } from "@/types";

export interface BookCardProps {
  book: Book;
  className?: string;
  children?: React.ReactNode;
}

const BookCard: React.FC<BookCardProps> = ({ book, className = "", children }) => (
  <Link
    href={`/books/${book.id}`}
    className={
      "bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow overflow-hidden " +
      className
    }
  >
    <div className="aspect-square bg-slate-200 flex items-center justify-center">
      {book.cover_url ? (
        <img
          src={book.cover_url}
          alt={book.title}
          className="w-full h-full object-cover"
        />
      ) : (
        <div className="text-slate-400 text-center">
          <div>No Cover</div>
        </div>
      )}
    </div>
    <div className="p-4">
      <h3 className="font-semibold text-slate-900 line-clamp-2">{book.title}</h3>
      <p className="text-sm text-slate-600 mb-2">{book.author}</p>
      {book.genre && (
        <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
          {book.genre}
        </span>
      )}
      {children}
    </div>
  </Link>
);

export default BookCard;
