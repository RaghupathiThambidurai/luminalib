export const ACCESS_COOKIE = "access_token";
export const REFRESH_COOKIE = "refresh_token";

export function setAuthCookies(accessToken: string, refreshToken?: string) {
  document.cookie = `${ACCESS_COOKIE}=${encodeURIComponent(accessToken)}; path=/; samesite=lax`;
  if (refreshToken) {
    document.cookie = `${REFRESH_COOKIE}=${encodeURIComponent(refreshToken)}; path=/; samesite=lax`;
  }
}

export function clearAuthCookies() {
  document.cookie = `${ACCESS_COOKIE}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; samesite=lax`;
  document.cookie = `${REFRESH_COOKIE}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; samesite=lax`;
}

export function getCookie(name: string): string | null {
  if (typeof document === "undefined") return null;

  const match = document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${name}=`));

  return match ? decodeURIComponent(match.split("=")[1]) : null;
}