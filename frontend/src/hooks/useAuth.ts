'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useCurrentUser } from '@/hooks/useApi';

const PUBLIC_ROUTES = ['/login'];

/**
 * Core auth hook — returns current user state from React Query.
 */
export function useAuth() {
  const { data: user, isLoading, isError } = useCurrentUser();

  const isAuthenticated =
    typeof window !== 'undefined' && !!localStorage.getItem('auth_token') && !!user;

  return { user: user ?? null, isLoading, isError, isAuthenticated };
}

/**
 * Guard hook — redirects unauthenticated users to /login.
 * Use at the top of every protected page.
 */
export function useRequireAuth() {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isLoading, isAuthenticated } = useAuth();

  useEffect(() => {
    if (isLoading) return;

    const hasToken =
      typeof window !== 'undefined' && !!localStorage.getItem('auth_token');

    if (!hasToken && !PUBLIC_ROUTES.includes(pathname)) {
      router.replace('/login');
    }
  }, [isLoading, isAuthenticated, pathname, router]);

  return { user: user ?? null, isLoading };
}
