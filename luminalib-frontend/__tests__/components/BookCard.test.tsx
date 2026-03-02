/**
 * Tests for BookCard component.
 *
 * Tests:
 * - Component rendering
 * - Props handling
 * - User interactions
 * - Loading states
 * - Error states
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BookCard } from '@/components/BookCard';
import type { Book } from '@/types';

describe('BookCard Component', () => {
  const mockBook: Book = {
    id: '1',
    title: 'Test Book Title',
    author: 'Test Author',
    isbn: '978-1-234567-89-0',
    description: 'A test book description',
    genre: 'Fiction',
    published_date: '2023-01-15',
    cover_url: 'https://example.com/cover.jpg',
    file_url: 'https://example.com/file.pdf',
    file_size: 1024000,
    created_at: '2023-01-15T00:00:00Z',
    updated_at: '2023-01-15T00:00:00Z',
    metadata: {
      summary: 'Test summary',
      summary_generated_at: '2023-01-15T00:00:00Z',
      summary_model: 'gpt-3.5-turbo'
    }
  };

  describe('Rendering', () => {
    it('renders book title', () => {
      render(<BookCard book={mockBook} />);

      expect(screen.getByText('Test Book Title')).toBeInTheDocument();
    });

    it('renders author name', () => {
      render(<BookCard book={mockBook} />);

      expect(screen.getByText('Test Author')).toBeInTheDocument();
    });

    it('renders book cover image', () => {
      render(<BookCard book={mockBook} />);

      const image = screen.getByAltText('Test Book Title');
      expect(image).toBeInTheDocument();
      expect(image).toHaveAttribute('src', expect.stringContaining('cover.jpg'));
    });

    it('renders description if available', () => {
      render(<BookCard book={mockBook} />);

      expect(screen.getByText(mockBook.description!)).toBeInTheDocument();
    });

    it('renders without description if not provided', () => {
      const bookWithoutDesc = { ...mockBook, description: undefined };
      render(<BookCard book={bookWithoutDesc} />);

      expect(screen.queryByText('A test book description')).not.toBeInTheDocument();
    });

    it('renders view details button', () => {
      render(<BookCard book={mockBook} />);

      expect(screen.getByRole('link', { name: /view details/i })).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('calls onBorrow when borrow button clicked', async () => {
      const mockOnBorrow = jest.fn();
      render(<BookCard book={mockBook} onBorrow={mockOnBorrow} />);

      const borrowButton = screen.getByRole('button', { name: /borrow/i });
      fireEvent.click(borrowButton);

      expect(mockOnBorrow).toHaveBeenCalledWith('1');
    });

    it('navigates to book detail when clicking view details', () => {
      render(<BookCard book={mockBook} />);

      const detailLink = screen.getByRole('link', { name: /view details/i });
      expect(detailLink).toHaveAttribute('href', `/books/${mockBook.id}`);
    });

    it('calls onBorrow only once per click', async () => {
      const mockOnBorrow = jest.fn();
      render(<BookCard book={mockBook} onBorrow={mockOnBorrow} />);

      const borrowButton = screen.getByRole('button', { name: /borrow/i });
      fireEvent.click(borrowButton);

      expect(mockOnBorrow).toHaveBeenCalledTimes(1);
    });
  });

  describe('Loading States', () => {
    it('disables borrow button when loading', () => {
      render(<BookCard book={mockBook} isLoading={true} />);

      const borrowButton = screen.getByRole('button', { name: /borrow/i });
      expect(borrowButton).toBeDisabled();
    });

    it('shows loading text when loading', () => {
      render(<BookCard book={mockBook} isLoading={true} />);

      expect(screen.getByText(/loading|borrowing/i)).toBeInTheDocument();
    });

    it('enables borrow button when not loading', () => {
      const mockOnBorrow = jest.fn();
      render(<BookCard book={mockBook} onBorrow={mockOnBorrow} isLoading={false} />);

      const borrowButton = screen.getByRole('button', { name: /borrow/i });
      expect(borrowButton).not.toBeDisabled();
    });
  });

  describe('Error Handling', () => {
    it('handles missing cover image gracefully', () => {
      const bookWithoutCover = { ...mockBook, cover_url: undefined };
      render(<BookCard book={bookWithoutCover} />);

      expect(screen.queryByAltText('Test Book Title')).not.toBeInTheDocument();
    });

    it('handles missing ISBN gracefully', () => {
      const bookWithoutISBN = { ...mockBook, isbn: undefined };
      render(<BookCard book={bookWithoutISBN} />);

      expect(screen.getByText('Test Book Title')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper heading hierarchy', () => {
      render(<BookCard book={mockBook} />);

      const heading = screen.getByRole('heading', { name: 'Test Book Title' });
      expect(heading).toBeInTheDocument();
    });

    it('has accessible button labels', () => {
      render(<BookCard book={mockBook} onBorrow={jest.fn()} />);

      expect(screen.getByRole('button', { name: /borrow/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /view details/i })).toBeInTheDocument();
    });

    it('image has alt text', () => {
      render(<BookCard book={mockBook} />);

      const image = screen.getByAltText('Test Book Title');
      expect(image).toHaveAttribute('alt', 'Test Book Title');
    });
  });
});
