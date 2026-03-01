/**
 * useAuth Hook - Manages authentication state and operations
 */

"use client";

import { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { authService } from "@/api/auth-service";
import { apiClient } from "@/lib/api-client";
import type { UserResponse, TokenResponse, UserCreate, LoginRequest } from "@/types";

const TOKEN_KEY = "luminallib_access_token";
const REFRESH_TOKEN_KEY = "luminallib_refresh_token";

export function useAuth() {
  const router = useRouter();
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize auth state on mount
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = useCallback(async () => {
    try {
      const token = localStorage.getItem(TOKEN_KEY);
      if (token) {
        apiClient.setToken(token);
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
      }
    } catch (err) {
      // Token invalid or expired, clear it
      clearTokens();
    } finally {
      setIsLoading(false);
    }
  }, []);

  const signup = useCallback(
    async (userData: UserCreate) => {
      setError(null);
      try {
        const response = await authService.signup(userData);
        await saveTokens(response);
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
        router.push("/");
        return { success: true };
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Signup failed";
        setError(message);
        return { success: false, error: message };
      }
    },
    [router]
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
        return { success: true };
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Login failed";
        setError(message);
        return { success: false, error: message };
      }
    },
    [router]
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
    }
  }, [router]);

  const refreshToken = useCallback(async () => {
    try {
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
      if (!refreshToken) {
        throw new Error("No refresh token available");
      }

      const response = await authService.refreshToken(refreshToken);
      await saveTokens(response);
      return { success: true };
    } catch (err) {
      // Refresh failed, clear auth
      clearTokens();
      setUser(null);
      return { success: false };
    }
  }, []);

  const saveTokens = async (tokenResponse: TokenResponse) => {
    localStorage.setItem(TOKEN_KEY, tokenResponse.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokenResponse.refresh_token);
    apiClient.setToken(tokenResponse.access_token);
  };

  const clearTokens = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    apiClient.clearToken();
  };

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
