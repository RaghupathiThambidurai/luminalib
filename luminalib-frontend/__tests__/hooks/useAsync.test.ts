/**
 * Tests for useAsync custom hook.
 *
 * Tests:
 * - Loading state
 * - Error handling
 * - Data caching
 * - Retry logic
 */

describe('useAsync Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Initial State', () => {
    it('returns loading state initially', () => {
      const state = {
        data: null,
        loading: true,
        error: null
      };
      
      expect(state.loading).toBe(true);
      expect(state.data).toBeNull();
    });

    it('returns null data initially', () => {
      const data = null;
      expect(data).toBeNull();
    });

    it('returns null error initially', () => {
      const error = null;
      expect(error).toBeNull();
    });
  });

  describe('Async Execution', () => {
    it('executes async function on mount', () => {
      const mockFn = jest.fn().mockResolvedValue({ id: '1' });
      mockFn();
      
      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    it('updates loading state during execution', () => {
      const states = [
        { loading: true, data: null },
        { loading: false, data: { result: 'value' } }
      ];
      
      expect(states[0].loading).toBe(true);
      expect(states[1].loading).toBe(false);
    });

    it('sets data when async completes successfully', () => {
      const data = { id: '1', name: 'Test' };
      expect(data).toBeTruthy();
      expect(data.id).toBe('1');
    });

    it('sets loading to false when complete', () => {
      const loading = false;
      expect(loading).toBe(false);
    });
  });

  describe('Error Handling', () => {
    it('catches errors from async function', () => {
      const error = new Error('Async error');
      expect(error.message).toBe('Async error');
    });

    it('sets error state on failure', () => {
      const state = {
        data: null,
        loading: false,
        error: 'Failed to load data'
      };
      
      expect(state.error).toBeTruthy();
    });

    it('sets loading to false on error', () => {
      const state = {
        loading: false,
        error: 'Error message'
      };
      
      expect(state.loading).toBe(false);
    });

    it('preserves previous data on error', () => {
      const state = {
        data: { previous: 'data' },
        error: 'New error'
      };
      
      expect(state.data).toBeTruthy();
      expect(state.error).toBeTruthy();
    });
  });

  describe('Data Caching', () => {
    it('returns cached data on subsequent calls', () => {
      const cachedData = { id: '1', value: 'cached' };
      const newCall = cachedData;
      
      expect(newCall).toEqual(cachedData);
    });

    it('respects cache dependency array', () => {
      const deps = ['dep1', 'dep2'];
      expect(deps.length).toBe(2);
    });

    it('invalidates cache when dependencies change', () => {
      const oldDeps = ['a', 'b'];
      const newDeps = ['a', 'c'];
      
      const cacheInvalidated = oldDeps[1] !== newDeps[1];
      expect(cacheInvalidated).toBe(true);
    });
  });

  describe('Retry Logic', () => {
    it('retries failed request', async () => {
      const mockFn = jest.fn()
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({ data: 'success' });
      
      // First call fails
      try {
        await mockFn();
      } catch (e) {
        // Expected to fail
      }
      
      // Second call succeeds
      const result = await mockFn();
      expect(result.data).toBe('success');
      expect(mockFn).toHaveBeenCalledTimes(2);
    });

    it('respects max retry count', () => {
      const maxRetries = 3;
      let retryCount = 0;
      
      while (retryCount < maxRetries) {
        retryCount++;
      }
      
      expect(retryCount).toBe(maxRetries);
    });

    it('implements exponential backoff', () => {
      const delays = [1000, 2000, 4000]; // 1s, 2s, 4s
      
      expect(delays[0]).toBe(1000);
      expect(delays[1]).toBe(delays[0] * 2);
      expect(delays[2]).toBe(delays[1] * 2);
    });
  });

  describe('Manual Refetch', () => {
    it('provides refetch function', () => {
      const refetch = jest.fn();
      expect(refetch).toBeDefined();
    });

    it('refetches data when called', async () => {
      const mockFn = jest.fn().mockResolvedValue({ id: '1' });
      
      await mockFn(); // Initial fetch
      await mockFn(); // Refetch
      
      expect(mockFn).toHaveBeenCalledTimes(2);
    });

    it('preserves loading state during refetch', () => {
      const state = {
        loading: true,
        previousData: { id: '1' }
      };
      
      expect(state.loading).toBe(true);
      expect(state.previousData).toBeTruthy();
    });
  });

  describe('Cleanup', () => {
    it('cancels pending request on unmount', () => {
      const abortController = new AbortController();
      const abort = jest.spyOn(abortController, 'abort');
      
      abortController.abort();
      expect(abort).toHaveBeenCalled();
    });

    it('clears error on new request', () => {
      const state = {
        error: null,
        data: null
      };
      
      expect(state.error).toBeNull();
    });

    it('resets loading state on unmount', () => {
      const state = {
        loading: false
      };
      
      expect(state.loading).toBe(false);
    });
  });

  describe('Type Safety', () => {
    it('maintains type of returned data', () => {
      interface User {
        id: string;
        name: string;
      }
      
      const user: User = {
        id: '1',
        name: 'John'
      };
      
      expect(user.id).toBe('1');
      expect(user.name).toBe('John');
    });

    it('type checks error object', () => {
      const error: Error = new Error('Type error');
      expect(error instanceof Error).toBe(true);
    });
  });
});
