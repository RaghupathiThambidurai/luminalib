/**
 * useAuth Hook - Manages authentication state and operations
 */

"use client";

import { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { authService } from "@/api/auth-service";
import { apiClient } from "@/lib/api-client";
import {
  setAuthCookies,
  clearAuthCookies,
  getCookie,
  ACCESS_COOKIE,
  REFRESH_COOKIE,
} from "@/lib/auth-cookies";
import type {
  UserResponse,
  TokenResponse,
  UserCreate,
  LoginRequest,
} from "@/types";

const TOKEN_KEY = "luminallib_access_token";
const REFRESH_TOKEN_KEY = "luminallib_refresh_token";

export function useAuth() {
  const router = useRouter();
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const clearTokens = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    clearAuthCookies();
    apiClient.clearToken();
  }, []);

  const saveTokens = useCallback(async (tokenResponse: TokenResponse) => {
    // Keep localStorage for existing client-side code compatibility
    localStorage.setItem(TOKEN_KEY, tokenResponse.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokenResponse.refresh_token);

    // Add cookies so SSR pages can read auth
    setAuthCookies(tokenResponse.access_token, tokenResponse.refresh_token);

    apiClient.setToken(tokenResponse.access_token);
  }, []);

  const initializeAuth = useCallback(async () => {
    try {
      // Prefer cookie for SSR-compatible auth model, fallback to localStorage
      const token =
        getCookie(ACCESS_COOKIE) || localStorage.getItem(TOKEN_KEY);

      if (token) {
        apiClient.setToken(token);
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
      }
    } catch {
      clearTokens();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, [clearTokens]);

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  const signup = useCallback(
    async (userData: UserCreate) => {
      setError(null);
      try {
        const response = await authService.signup(userData);
        await saveTokens(response);
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
        router.push("/");
        router.refresh();
        return { success: true };
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Signup failed";
        setError(message);
        return { success: false, error: message };
      }
    },
    [router, saveTokens]
  );

  const login = useCallback(
    async (credentials: LoginRequest) => {
      setError(null);
      try {
        const response = await authService.login(credentials);
        await saveTokens(response);
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
        router.push("/");
        router.refresh();
        return { success: true };
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Login failed";
        setError(message);
        return { success: false, error: message };
      }
    },
    [router, saveTokens]
  );

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } catch (err) {
      console.error("Logout API call failed:", err);
    } finally {
      clearTokens();
      setUser(null);
      router.push("/auth/login");
      router.refresh();
    }
  }, [router, clearTokens]);

  const refreshToken = useCallback(async () => {
    try {
      const refresh =
        getCookie(REFRESH_COOKIE) || localStorage.getItem(REFRESH_TOKEN_KEY);

      if (!refresh) {
        throw new Error("No refresh token available");
      }

      const response = await authService.refreshToken(refresh);
      await saveTokens(response);
      return { success: true };
    } catch {
      clearTokens();
      setUser(null);
      return { success: false };
    }
  }, [saveTokens, clearTokens]);

  const isAuthenticated = user !== null;

  return {
    user,
    isLoading,
    error,
    isAuthenticated,
    signup,
    login,
    logout,
    refreshToken,
  };
}