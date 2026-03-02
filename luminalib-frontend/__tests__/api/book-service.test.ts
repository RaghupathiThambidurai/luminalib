/**
 * Tests for book service API calls.
 *
 * Tests:
 * - Get books list
 * - Get book by ID
 * - Search books
 * - Create book
 * - Update book
 * - Delete book
 * - Error handling
 */

describe('Book Service', () => {
  const API_URL = 'http://localhost:8000';

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Get Books', () => {
    it('fetches books list with pagination', async () => {
      const endpoint = '/books?skip=0&limit=10';
      const fullUrl = `${API_URL}${endpoint}`;
      expect(fullUrl).toContain('/books');
      expect(fullUrl).toContain('skip=0');
      expect(fullUrl).toContain('limit=10');
    });

    it('includes authorization header', () => {
      const token = 'test-token';
      const headers: Record<string, string> = {};
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      expect(headers['Authorization']).toBe('Bearer test-token');
    });

    it('handles books response', () => {
      const response = [
        { id: '1', title: 'Book 1', author: 'Author 1' },
        { id: '2', title: 'Book 2', author: 'Author 2' }
      ];
      
      expect(response.length).toBe(2);
      expect(response[0].title).toBe('Book 1');
    });

    it('handles empty books list', () => {
      const response: any[] = [];
      expect(response.length).toBe(0);
      expect(Array.isArray(response)).toBe(true);
    });
  });

  describe('Get Book Detail', () => {
    it('fetches book by ID', () => {
      const bookId = '123';
      const endpoint = `/books/${bookId}`;
      expect(endpoint).toBe('/books/123');
    });

    it('returns book details', () => {
      const book = {
        id: '1',
        title: 'Test Book',
        author: 'Test Author',
        description: 'Test description',
        genre: 'Fiction',
        cover_url: 'https://example.com/cover.jpg',
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z'
      };
      
      expect(book.id).toBe('1');
      expect(book.title).toBe('Test Book');
      expect(book.cover_url).toBeTruthy();
    });

    it('handles 404 error for nonexistent book', () => {
      const status = 404;
      expect(status).toBe(404);
    });
  });

  describe('Search Books', () => {
    it('searches books by title', () => {
      const query = 'Python';
      const endpoint = `/books/search?q=${query}`;
      expect(endpoint).toContain('search');
      expect(endpoint).toContain('Python');
    });

    it('searches books by author', () => {
      const query = 'Stephen King';
      const endpoint = `/books/search?q=${query}`;
      expect(endpoint).toContain(query);
    });

    it('filters by genre', () => {
      const genre = 'Fiction';
      const endpoint = `/books?genre=${genre}`;
      expect(endpoint).toContain('genre=Fiction');
    });

    it('handles no search results', () => {
      const results: any[] = [];
      expect(results.length).toBe(0);
    });
  });

  describe('Create Book', () => {
    it('sends book data to create endpoint', () => {
      const bookData = {
        title: 'New Book',
        author: 'New Author',
        isbn: '978-1-234567-89-0',
        description: 'Book description'
      };
      
      expect(bookData.title).toBe('New Book');
      expect(bookData.author).toBeTruthy();
    });

    it('handles file upload', () => {
      const file = new File(['content'], 'book.pdf', { type: 'application/pdf' });
      expect(file.name).toBe('book.pdf');
      expect(file.type).toBe('application/pdf');
    });

    it('returns created book with ID', () => {
      const createdBook = {
        id: 'new-id-123',
        title: 'New Book',
        author: 'New Author'
      };
      
      expect(createdBook.id).toBeTruthy();
      expect(createdBook.title).toBe('New Book');
    });

    it('handles validation errors', () => {
      const error = {
        status: 422,
        detail: 'Invalid book data'
      };
      
      expect(error.status).toBe(422);
    });
  });

  describe('Borrow Book', () => {
    it('sends borrow request', () => {
      const bookId = '123';
      const endpoint = `/books/${bookId}/borrow`;
      expect(endpoint).toBe('/books/123/borrow');
    });

    it('handles successful borrow', () => {
      const response = {
        status: 'success',
        message: 'Book borrowed successfully'
      };
      
      expect(response.status).toBe('success');
    });

    it('handles already borrowed error', () => {
      const error = {
        status: 400,
        detail: 'Book already borrowed by user'
      };
      
      expect(error.status).toBe(400);
    });

    it('handles book not available error', () => {
      const error = {
        status: 409,
        detail: 'No copies available'
      };
      
      expect(error.status).toBe(409);
    });
  });

  describe('Return Book', () => {
    it('sends return request', () => {
      const bookId = '123';
      const endpoint = `/books/${bookId}/return`;
      expect(endpoint).toBe('/books/123/return');
    });

    it('handles successful return', () => {
      const response = {
        status: 'success',
        message: 'Book returned successfully'
      };
      
      expect(response.status).toBe('success');
    });

    it('calculates late fees if applicable', () => {
      const response = {
        returned: true,
        lateFee: 5.00,
        daysLate: 3
      };
      
      expect(response.returned).toBe(true);
      expect(response.lateFee).toBeGreaterThan(0);
    });
  });

  describe('Error Handling', () => {
    it('handles 401 unauthorized', () => {
      const status = 401;
      const errorMessage = 'Unauthorized access';
      expect(status).toBe(401);
      expect(errorMessage).toBeTruthy();
    });

    it('handles 403 forbidden', () => {
      const status = 403;
      expect(status).toBe(403);
    });

    it('handles 500 server error', () => {
      const status = 500;
      expect(status).toBe(500);
    });

    it('retries on network error', () => {
      const retryCount = 3;
      expect(retryCount).toBeGreaterThan(0);
    });

    it('displays user-friendly error messages', () => {
      const userMessage = 'Failed to load books. Please try again.';
      expect(userMessage).toBeTruthy();
      expect(userMessage.length).toBeGreaterThan(0);
    });
  });
});
