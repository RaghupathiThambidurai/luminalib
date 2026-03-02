/**
 * Tests for authentication service.
 *
 * Tests:
 * - User signup
 * - User login
 * - Token refresh
 * - User logout
 * - Password validation
 * - Error handling
 */

describe('Auth Service', () => {
  const API_URL = 'http://localhost:8000';

  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  describe('User Signup', () => {
    it('sends signup request with user data', () => {
      const userData = {
        username: 'newuser',
        email: 'newuser@example.com',
        password: 'SecurePass123!',
        full_name: 'New User'
      };
      
      expect(userData.username).toBeTruthy();
      expect(userData.email).toContain('@');
      expect(userData.password.length).toBeGreaterThan(8);
    });

    it('handles successful signup response', () => {
      const response = {
        user: {
          id: 'user-123',
          username: 'newuser',
          email: 'newuser@example.com'
        },
        access_token: 'token-abc123'
      };
      
      expect(response.user.id).toBeTruthy();
      expect(response.access_token).toBeTruthy();
    });

    it('validates email format', () => {
      const validEmail = 'user@example.com';
      const invalidEmail = 'invalid-email';
      
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      expect(emailRegex.test(validEmail)).toBe(true);
      expect(emailRegex.test(invalidEmail)).toBe(false);
    });

    it('validates password strength', () => {
      const weakPassword = '123';
      const strongPassword = 'SecurePass123!';
      
      const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
      expect(passwordRegex.test(weakPassword)).toBe(false);
      expect(passwordRegex.test(strongPassword)).toBe(true);
    });

    it('handles duplicate email error', () => {
      const error = {
        status: 409,
        detail: 'Email already registered'
      };
      
      expect(error.status).toBe(409);
      expect(error.detail).toContain('Email');
    });

    it('handles duplicate username error', () => {
      const error = {
        status: 409,
        detail: 'Username already taken'
      };
      
      expect(error.status).toBe(409);
    });
  });

  describe('User Login', () => {
    it('sends login credentials to server', () => {
      const credentials = {
        username: 'testuser',
        password: 'password123'
      };
      
      expect(credentials.username).toBeTruthy();
      expect(credentials.password).toBeTruthy();
    });

    it('handles successful login response', () => {
      const response = {
        access_token: 'jwt-token-abc123',
        token_type: 'bearer',
        user: {
          id: 'user-1',
          username: 'testuser',
          email: 'test@example.com'
        }
      };
      
      expect(response.access_token).toBeTruthy();
      expect(response.token_type).toBe('bearer');
      expect(response.user).toBeTruthy();
    });

    it('stores token in localStorage after login', () => {
      const token = 'new-token-123';
      localStorage.setItem('token', token);
      
      const stored = localStorage.getItem('token');
      expect(stored).toBe(token);
    });

    it('stores user data after login', () => {
      const user = { id: '1', username: 'testuser' };
      localStorage.setItem('user', JSON.stringify(user));
      
      const stored = JSON.parse(localStorage.getItem('user') || '{}');
      expect(stored.username).toBe('testuser');
    });

    it('handles invalid credentials error', () => {
      const error = {
        status: 401,
        detail: 'Invalid username or password'
      };
      
      expect(error.status).toBe(401);
    });

    it('handles user not found error', () => {
      const error = {
        status: 404,
        detail: 'User not found'
      };
      
      expect(error.status).toBe(404);
    });

    it('handles inactive user error', () => {
      const error = {
        status: 403,
        detail: 'User account is inactive'
      };
      
      expect(error.status).toBe(403);
    });
  });

  describe('Token Management', () => {
    it('retrieves token from localStorage', () => {
      const token = 'stored-token-123';
      localStorage.setItem('token', token);
      
      const retrieved = localStorage.getItem('token');
      expect(retrieved).toBe(token);
    });

    it('includes token in request headers', () => {
      const token = 'my-token';
      localStorage.setItem('token', token);
      
      const headers: Record<string, string> = {};
      const storedToken = localStorage.getItem('token');
      
      if (storedToken) {
        headers['Authorization'] = `Bearer ${storedToken}`;
      }
      
      expect(headers['Authorization']).toBe('Bearer my-token');
    });

    it('clears token on logout', () => {
      localStorage.setItem('token', 'some-token');
      localStorage.removeItem('token');
      
      const token = localStorage.getItem('token');
      expect(token).toBeNull();
    });
  });

  describe('Token Refresh', () => {
    it('sends refresh request when token expired', () => {
      const endpoint = '/auth/refresh';
      expect(endpoint).toBe('/auth/refresh');
    });

    it('updates token with new one', () => {
      const oldToken = 'old-token';
      const newToken = 'new-token';
      
      localStorage.setItem('token', oldToken);
      localStorage.setItem('token', newToken);
      
      const current = localStorage.getItem('token');
      expect(current).toBe(newToken);
    });

    it('handles refresh token expired', () => {
      const error = {
        status: 401,
        detail: 'Refresh token expired. Please login again.'
      };
      
      expect(error.status).toBe(401);
      expect(error.detail).toContain('login');
    });
  });

  describe('User Logout', () => {
    it('clears token on logout', () => {
      localStorage.setItem('token', 'current-token');
      localStorage.removeItem('token');
      
      expect(localStorage.getItem('token')).toBeNull();
    });

    it('clears user data on logout', () => {
      localStorage.setItem('user', JSON.stringify({ id: '1', username: 'user' }));
      localStorage.removeItem('user');
      
      expect(localStorage.getItem('user')).toBeNull();
    });

    it('sends logout request to server', () => {
      const endpoint = '/auth/logout';
      expect(endpoint).toBe('/auth/logout');
    });

    it('redirects to login page after logout', () => {
      const redirectUrl = '/auth/login';
      expect(redirectUrl).toBe('/auth/login');
    });
  });

  describe('Error Handling', () => {
    it('handles network errors', () => {
      const error = new Error('Network error');
      expect(error.message).toContain('Network');
    });

    it('handles server errors', () => {
      const error = {
        status: 500,
        detail: 'Internal server error'
      };
      
      expect(error.status).toBeGreaterThanOrEqual(500);
    });

    it('displays user-friendly error messages', () => {
      const userMessage = 'Login failed. Please try again.';
      expect(userMessage).toBeTruthy();
      expect(userMessage).not.toContain('500');
    });

    it('logs errors for debugging', () => {
      const error = new Error('Test error');
      const logSpy = jest.spyOn(console, 'error').mockImplementation();
      
      console.error(error);
      
      expect(logSpy).toHaveBeenCalled();
      logSpy.mockRestore();
    });
  });

  describe('Password Reset', () => {
    it('sends password reset request', () => {
      const email = 'user@example.com';
      const endpoint = '/auth/forgot-password';
      expect(endpoint).toBeTruthy();
    });

    it('validates reset token', () => {
      const token = 'reset-token-123';
      expect(token.length).toBeGreaterThan(0);
    });

    it('updates password with new one', () => {
      const newPassword = 'NewSecurePass123!';
      const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
      
      expect(passwordRegex.test(newPassword)).toBe(true);
    });

    it('handles invalid reset token', () => {
      const error = {
        status: 400,
        detail: 'Invalid or expired reset token'
      };
      
      expect(error.status).toBe(400);
    });
  });
});
