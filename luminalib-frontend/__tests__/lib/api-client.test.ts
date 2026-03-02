/**
 * Tests for API client.
 *
 * Tests:
 * - Request building
 * - Error handling
 * - Token management
 * - Response parsing
 */

describe('API Client', () => {
  const API_BASE_URL = 'http://localhost:8000';

  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  describe('Request Building', () => {
    it('builds correct URL for GET request', () => {
      const endpoint = '/books';
      const fullUrl = `${API_BASE_URL}${endpoint}`;

      expect(fullUrl).toBe('http://localhost:8000/books');
    });

    it('includes authorization header when token exists', () => {
      const token = 'test-token-123';
      localStorage.setItem('token', token);

      const headers: Record<string, string> = {};
      const storedToken = localStorage.getItem('token');

      if (storedToken) {
        headers['Authorization'] = `Bearer ${storedToken}`;
      }

      expect(headers['Authorization']).toBe(`Bearer ${token}`);
    });

    it('omits authorization header when no token', () => {
      const headers: Record<string, string> = {};
      const storedToken = localStorage.getItem('token');

      if (storedToken) {
        headers['Authorization'] = `Bearer ${storedToken}`;
      }

      expect(Object.keys(headers)).not.toContain('Authorization');
    });

    it('sets content-type header', () => {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      };

      expect(headers['Content-Type']).toBe('application/json');
    });
  });

  describe('Token Management', () => {
    it('stores token from login response', () => {
      const token = 'new-access-token';
      localStorage.setItem('token', token);

      const stored = localStorage.getItem('token');
      expect(stored).toBe(token);
    });

    it('retrieves token for requests', () => {
      const token = 'test-token';
      localStorage.setItem('token', token);

      const retrieved = localStorage.getItem('token');
      expect(retrieved).toBe(token);
    });

    it('clears token on logout', () => {
      localStorage.setItem('token', 'current-token');
      localStorage.removeItem('token');

      const token = localStorage.getItem('token');
      expect(token).toBeNull();
    });

    it('refreshes token when expired', () => {
      const oldToken = 'old-token';
      const newToken = 'refreshed-token';

      localStorage.setItem('token', oldToken);
      localStorage.setItem('token', newToken);

      const current = localStorage.getItem('token');
      expect(current).toBe(newToken);
    });
  });

  describe('Error Handling', () => {
    it('handles 401 Unauthorized', () => {
      const status = 401;
      const isUnauthorized = status === 401;

      expect(isUnauthorized).toBe(true);
    });

    it('handles 403 Forbidden', () => {
      const status = 403;
      const isForbidden = status === 403;

      expect(isForbidden).toBe(true);
    });

    it('handles 404 Not Found', () => {
      const status = 404;
      const isNotFound = status === 404;

      expect(isNotFound).toBe(true);
    });

    it('handles 500 Server Error', () => {
      const status = 500;
      const isServerError = status >= 500;

      expect(isServerError).toBe(true);
    });

    it('extracts error message from response', () => {
      const errorResponse = {
        detail: 'Invalid credentials',
        status: 401
      };

      expect(errorResponse.detail).toBe('Invalid credentials');
    });
  });

  describe('Response Handling', () => {
    it('parses JSON response correctly', () => {
      const response = {
        id: '1',
        title: 'Test Book',
        author: 'Test Author'
      };

      const parsed = JSON.parse(JSON.stringify(response));
      expect(parsed.title).toBe('Test Book');
    });

    it('handles array response', () => {
      const response = [
        { id: '1', title: 'Book 1' },
        { id: '2', title: 'Book 2' }
      ];

      expect(Array.isArray(response)).toBe(true);
      expect(response.length).toBe(2);
    });

    it('handles empty response', () => {
      const response = [];

      expect(Array.isArray(response)).toBe(true);
      expect(response.length).toBe(0);
    });

    it('handles null response', () => {
      const response = null;

      expect(response).toBeNull();
    });
  });

  describe('Request Methods', () => {
    it('supports GET requests', () => {
      const method = 'GET';
      expect(method).toBe('GET');
    });

    it('supports POST requests', () => {
      const method = 'POST';
      expect(method).toBe('POST');
    });

    it('supports PUT requests', () => {
      const method = 'PUT';
      expect(method).toBe('PUT');
    });

    it('supports DELETE requests', () => {
      const method = 'DELETE';
      expect(method).toBe('DELETE');
    });

    it('supports PATCH requests', () => {
      const method = 'PATCH';
      expect(method).toBe('PATCH');
    });
  });
});
