import { cookies } from "next/headers";
import { redirect, notFound } from "next/navigation";
import BookDetailClient from "./BookDetailClient";

const API_URL = process.env.API_INTERNAL_URL || "http://backend:8000";

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function BookDetailPage({ params }: PageProps) {
  const { id } = await params;

  const cookieStore = await cookies();
  const token = cookieStore.get("access_token")?.value;

  if (!token) {
    redirect("/auth/login");
  }

  const [bookRes, reviewsRes] = await Promise.all([
    fetch(`${API_URL}/api/books/${id}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    }),
    fetch(`${API_URL}/api/books/${id}/reviews`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    }),
  ]);

  if (bookRes.status === 404) {
    notFound();
  }

  if (!bookRes.ok) {
    let details = bookRes.statusText;
    try {
      const data = await bookRes.json();
      details =
        typeof data?.detail === "string"
          ? data.detail
          : JSON.stringify(data);
    } catch {}
    throw new Error(`Failed to load book: ${bookRes.status} ${details}`);
  }

  if (!reviewsRes.ok) {
    let details = reviewsRes.statusText;
    try {
      const data = await reviewsRes.json();
      details =
        typeof data?.detail === "string"
          ? data.detail
          : JSON.stringify(data);
    } catch {}
    throw new Error(`Failed to load reviews: ${reviewsRes.status} ${details}`);
  }

  const book = await bookRes.json();
  const reviewsData = await reviewsRes.json();

  return (
    <BookDetailClient
      bookId={id}
      initialBook={book}
      initialReviews={reviewsData.reviews ?? []}
    />
  );
}