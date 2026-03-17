import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import ProfileClient from "./ProfileClient";

const API_URL = process.env.API_INTERNAL_URL || "http://backend:8000";

export default async function ProfilePage() {
  const cookieStore = await cookies();
  const token = cookieStore.get("access_token")?.value;

  if (!token) {
    redirect("/auth/login");
  }

  const [meRes, borrowsRes, recsRes] = await Promise.all([
    fetch(`${API_URL}/api/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    }),
    fetch(`${API_URL}/api/books/my-borrows?include_returned=false`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    }),
    fetch(`${API_URL}/api/books/users/me/recommendations?limit=5`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    }),
  ]);

  if (meRes.status === 401) {
    redirect("/auth/login");
  }

  if (!meRes.ok) {
    throw new Error(`Failed to load profile: ${meRes.status} ${meRes.statusText}`);
  }

  if (!borrowsRes.ok) {
    throw new Error(`Failed to load borrowed books: ${borrowsRes.status} ${borrowsRes.statusText}`);
  }

  if (!recsRes.ok) {
    let details = recsRes.statusText;

    try {
      const data = await recsRes.json();
      details =
        typeof data?.detail === "string"
          ? data.detail
          : JSON.stringify(data);
    } catch {
      try {
        details = await recsRes.text();
      } catch {
        details = recsRes.statusText;
      }
    }

    throw new Error(`Failed to load recommendations: ${recsRes.status} ${details}`);
  }

  const user = await meRes.json();
  const borrows = await borrowsRes.json();
  const recsData = await recsRes.json();

  return (
    <ProfileClient
      initialUser={user}
      initialBorrows={borrows}
      initialRecommendations={recsData.recommendations ?? []}
    />
  );
}