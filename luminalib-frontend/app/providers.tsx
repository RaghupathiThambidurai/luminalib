'use client';

import { ReactNode } from 'react';

/**
 * Providers wrapper - Currently a simple pass-through
 * Can be extended to add additional providers (React Query, Redux, etc.)
 */
export function QueryProvider({ children }: { children: ReactNode }) {
  return <>{children}</>;
}
