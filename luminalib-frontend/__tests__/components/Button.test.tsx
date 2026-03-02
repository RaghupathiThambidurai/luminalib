/**
 * Tests for Button component.
 *
 * Tests:
 * - Rendering with different variants
 * - Click handlers
 * - Disabled states
 * - Loading states
 * - Accessibility
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/Button';

describe('Button Component', () => {
  describe('Rendering', () => {
    it('renders button with text', () => {
      render(<Button>Click me</Button>);
      expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
    });

    it('renders primary variant by default', () => {
      render(<Button>Submit</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-blue');
    });

    it('renders secondary variant', () => {
      render(<Button variant="secondary">Cancel</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-gray');
    });

    it('renders danger variant', () => {
      render(<Button variant="danger">Delete</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-red');
    });

    it('renders small size', () => {
      render(<Button size="small">Small</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('px-2');
    });

    it('renders large size', () => {
      render(<Button size="large">Large</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('px-6');
    });
  });

  describe('Click Handling', () => {
    it('calls onClick handler when clicked', () => {
      const mockClick = jest.fn();
      render(<Button onClick={mockClick}>Click</Button>);
      
      fireEvent.click(screen.getByRole('button'));
      expect(mockClick).toHaveBeenCalledTimes(1);
    });

    it('does not call onClick when disabled', () => {
      const mockClick = jest.fn();
      render(<Button disabled onClick={mockClick}>Click</Button>);
      
      fireEvent.click(screen.getByRole('button'));
      expect(mockClick).not.toHaveBeenCalled();
    });
  });

  describe('Disabled State', () => {
    it('disables button when disabled prop is true', () => {
      render(<Button disabled>Disabled</Button>);
      expect(screen.getByRole('button')).toBeDisabled();
    });

    it('enables button when disabled prop is false', () => {
      render(<Button disabled={false}>Enabled</Button>);
      expect(screen.getByRole('button')).not.toBeDisabled();
    });

    it('shows disabled styling', () => {
      render(<Button disabled>Disabled</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('opacity-50');
    });
  });

  describe('Loading State', () => {
    it('disables button when loading', () => {
      render(<Button isLoading>Loading</Button>);
      expect(screen.getByRole('button')).toBeDisabled();
    });

    it('shows loading text', () => {
      render(<Button isLoading>Submit</Button>);
      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });

    it('shows spinner when loading', () => {
      render(<Button isLoading>Submit</Button>);
      const spinner = screen.getByTestId('spinner');
      expect(spinner).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper button role', () => {
      render(<Button>Click</Button>);
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('supports aria-label', () => {
      render(<Button aria-label="Submit form">Submit</Button>);
      expect(screen.getByLabelText('Submit form')).toBeInTheDocument();
    });

    it('shows aria-disabled when disabled', () => {
      render(<Button disabled aria-disabled="true">Disabled</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-disabled', 'true');
    });
  });
});
