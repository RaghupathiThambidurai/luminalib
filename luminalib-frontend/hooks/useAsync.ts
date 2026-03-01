/**
 * Custom hooks for React Query integration
 */

'use client';

import { useQuery, useMutation, UseQueryResult, UseMutationResult } from '@tanstack/react-query';
import { ApiError } from '@/lib/api-client';

interface UseAsyncOptions<T> {
  enabled?: boolean;
  retry?: boolean | number;
  staleTime?: number;
  gcTime?: number;
}

/**
 * Wrapper around useQuery for type-safe async operations
 */
export function useAsync<T>(
  queryKey: readonly unknown[],
  queryFn: () => Promise<T>,
  options: UseAsyncOptions<T> = {}
): UseQueryResult<T, ApiError> {
  return useQuery<T, ApiError>({
    queryKey,
    queryFn,
    enabled: options.enabled ?? true,
    retry: options.retry ?? 1,
    staleTime: options.staleTime,
    gcTime: options.gcTime,
  });
}

interface UseMutationOptions<T, E> {
  onSuccess?: (data: T) => void;
  onError?: (error: E) => void;
}

/**
 * Wrapper around useMutation for type-safe mutations
 */
export function useMutationAsync<TData, TError = ApiError, TVariables = void>(
  mutationFn: (variables: TVariables) => Promise<TData>,
  options: UseMutationOptions<TData, TError> = {}
): UseMutationResult<TData, TError, TVariables> {
  return useMutation<TData, TError, TVariables>({
    mutationFn,
    onSuccess: options.onSuccess,
    onError: options.onError,
  });
}
