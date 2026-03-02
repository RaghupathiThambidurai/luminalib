"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { bookService } from "@/api/book-service";
import type { Book } from "@/types";
import Alert from "@/components/Alert";
import Header from "@/components/Header";
import BookCard from "@/components/BookCard";

export default function BooksPage() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const [books, setBooks] = useState<Book[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [skip, setSkip] = useState(0);
  const [total, setTotal] = useState(0);
  const limit = 10;

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/auth/login");
      return;
    }

    if (user) {
      loadBooks();
    }
  }, [user, authLoading, router, skip]);

  const loadBooks = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await bookService.getBooks(skip, limit);
      setBooks(response.books);
      setTotal(response.total);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load books";
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

  return (
    <div className="min-h-screen bg-slate-50">
      <Header
        title="LuminalLib"
        right={
          <div className="flex items-center gap-4">
            <Link href="/books/upload" className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
              Upload Book
            </Link>
            <Link href="/profile" className="text-slate-700 hover:text-slate-900">
              Profile
            </Link>
            <div className="text-sm text-slate-600">{user?.username}</div>
          </div>
        }
      />

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-12">
        <h2 className="text-2xl font-bold text-slate-900 mb-8">Browse Books</h2>

        {error && <Alert message={error} type="error" className="mb-6" />}

        {isLoading ? (
          <div className="text-center text-slate-600">Loading books...</div>
        ) : books.length === 0 ? (
          <div className="text-center text-slate-600">No books found</div>
        ) : (
          <>
            {/* Books Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {books.map((book) => (
                <BookCard key={book.id} book={book} />
              ))}
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between">
              <button
                onClick={() => setSkip(Math.max(0, skip - limit))}
                disabled={skip === 0}
                className="px-4 py-2 bg-slate-200 text-slate-900 rounded-md hover:bg-slate-300 disabled:opacity-50"
              >
                Previous
              </button>
              <span className="text-slate-600">
                Showing {skip + 1} to {Math.min(skip + limit, total)} of {total}
              </span>
              <button
                onClick={() => setSkip(skip + limit)}
                disabled={skip + limit >= total}
                className="px-4 py-2 bg-slate-200 text-slate-900 rounded-md hover:bg-slate-300 disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
