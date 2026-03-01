/**
 * API Client - Abstracted network layer for LuminalLib Backend
 * Provides a single point of configuration and error handling
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface RequestConfig {
  method?: "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
  headers?: Record<string, string>;
  body?: unknown;
  signal?: AbortSignal;
}

export interface ApiErrorResponse {
  detail: string | string[];
  status?: number;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public details?: ApiErrorResponse
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Core API client with error handling and authentication
 */
class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Set authentication token
   */
  setToken(token: string): void {
    this.token = token;
  }

  /**
   * Clear authentication token
   */
  clearToken(): void {
    this.token = null;
  }

  /**
   * Make a typed API request
   */
  async request<T>(
    endpoint: string,
    config: RequestConfig = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...config.headers,
    };

    // Add authorization header if token exists
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        method: config.method || "GET",
        headers,
        body: config.body ? JSON.stringify(config.body) : undefined,
        signal: config.signal,
      });

      if (!response.ok) {
        const error = await this.parseError(response);
        throw new ApiError(response.status, error.message, error.details);
      }

      // Handle empty responses (204 No Content)
      if (response.status === 204) {
        return undefined as T;
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }

      if (error instanceof TypeError && error.message.includes("fetch")) {
        throw new ApiError(
          0,
          "Network error. Unable to connect to the server.",
          { detail: error.message }
        );
      }

      throw error;
    }
  }

  /**
   * Upload a file with form data
   */
  async uploadFile<T>(
    endpoint: string,
    formData: FormData,
    config: RequestConfig = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: Record<string, string> = {
      ...config.headers,
    };

    // Don't set Content-Type, let the browser set it with boundary
    delete headers["Content-Type"];

    // Add authorization header if token exists
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        method: "POST",
        headers,
        body: formData,
        signal: config.signal,
      });

      if (!response.ok) {
        const error = await this.parseError(response);
        throw new ApiError(response.status, error.message, error.details);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }

      throw new ApiError(0, "File upload failed", { detail: String(error) });
    }
  }

  /**
   * Parse error response
   */
  private async parseError(
    response: Response
  ): Promise<{ message: string; details?: ApiErrorResponse }> {
    try {
      const data = (await response.json()) as ApiErrorResponse;
      const message = Array.isArray(data.detail)
        ? data.detail.join(", ")
        : data.detail || response.statusText;

      return {
        message,
        details: data,
      };
    } catch {
      return {
        message: response.statusText || "Unknown error",
      };
    }
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
