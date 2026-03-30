'use client';

import { useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState, type ReactNode } from 'react';
import { Toaster } from 'sonner';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';
import { useHydration } from '@/stores/userStore';

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  useHydration();

  // Initialize Sentry on mount (if enabled)
  useEffect(() => {
    if (process.env.NEXT_PUBLIC_SENTRY_ENABLED === 'true' && process.env.NEXT_PUBLIC_SENTRY_DSN) {
      import('@sentry/react').then((Sentry) => {
        Sentry.init({
          dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
          environment: process.env.NODE_ENV,
          tracesSampleRate: 0.1,
        });
      }).catch(() => {
        // Sentry load failed — silently continue
      });
    }
  }, []);

  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        {children}
      </ErrorBoundary>
      <Toaster theme="dark" position="top-right" richColors />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
