/**
 * Auth Service - Handles all authentication-related API calls
 */

import { apiClient } from "@/lib/api-client";
import type {
  TokenResponse,
  UserCreate,
  UserResponse,
  LoginRequest,
} from "@/types";

export const authService = {
  /**
   * Register a new user (signup)
   */
  async signup(userData: UserCreate): Promise<TokenResponse> {
    return apiClient.request("/api/auth/register", {
      method: "POST",
      body: userData,
    });
  },

  /**
   * Login with username and password
   */
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    return apiClient.request("/api/auth/login", {
      method: "POST",
      body: credentials,
    });
  },

  /**
   * Refresh the access token using refresh token
   */
  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    // The API endpoint expects Bearer token in Authorization header
    // We pass it directly in the headers for this specific call
    return apiClient.request("/api/auth/refresh", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${refreshToken}`,
      },
    });
  },

  /**
   * Get current authenticated user profile
   */
  async getCurrentUser(): Promise<UserResponse> {
    return apiClient.request("/api/auth/me", {
      method: "GET",
    });
  },

  /**
   * Logout user (blacklist token)
   */
  async logout(): Promise<{ message: string; status: string }> {
    return apiClient.request("/api/auth/logout", {
      method: "POST",
    });
  },
};
