'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import apiClient from '@/lib/api';
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  UserProfile,
  SafeToSpendData,
  TransactionData,
  PaginatedResponse,
  ApiResponse,
} from '@/types';

const AUTH_TOKEN_KEY = 'auth_token';

function getToken(): string | null {
  return typeof window !== 'undefined' ? localStorage.getItem(AUTH_TOKEN_KEY) : null;
}

// =============================================================================
// Auth Hooks
// =============================================================================

export function useLogin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (body: LoginRequest) => {
      const { data } = await apiClient.post<TokenResponse>(
        '/api/v1/auth/token',
        body,
      );
      return data;
    },
    onSuccess: (data) => {
      localStorage.setItem(AUTH_TOKEN_KEY, data.access_token);
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
    },
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: async (body: RegisterRequest) => {
      const { data } = await apiClient.post<UserProfile>(
        '/api/v1/auth/register',
        body,
      );
      return data;
    },
  });
}

export function useCurrentUser() {
  return useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const { data } = await apiClient.get<UserProfile>('/api/v1/users/me');
      return data;
    },
    enabled: !!getToken(),
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return () => {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    queryClient.clear();
    router.push('/login');
  };
}

// =============================================================================
// Safe-to-Spend Hook
// =============================================================================

export function useSafeToSpend() {
  return useQuery({
    queryKey: ['safeToSpend'],
    queryFn: async () => {
      const { data } = await apiClient.get<SafeToSpendData>(
        '/api/v1/safe-to-spend',
      );
      return {
        ...data,
        amount: Number(data.amount),
        daily_allowance: Number(data.daily_allowance),
      };
    },
    enabled: !!getToken(),
  });
}

// =============================================================================
// Transaction Hooks
// =============================================================================

export function useTransactions(params?: {
  search?: string;
  limit?: number;
  offset?: number;
}) {
  const { search, limit = 20, offset = 0 } = params ?? {};

  return useQuery({
    queryKey: ['transactions', search, limit, offset],
    queryFn: async () => {
      const searchParams = new URLSearchParams();
      searchParams.set('limit', String(limit));
      searchParams.set('offset', String(offset));
      if (search) searchParams.set('search', search);

      const { data } = await apiClient.get<PaginatedResponse<TransactionData>>(
        `/api/v1/transactions?${searchParams.toString()}`,
      );
      return {
        ...data,
        data: data.data.map((tx) => ({
          ...tx,
          amount: Number(tx.amount),
        })),
      };
    },
    enabled: !!getToken(),
  });
}

export function useUpdateTransactionCategory() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, category }: { id: string; category: string }) => {
      const { data } = await apiClient.patch<TransactionData>(
        `/api/v1/transactions/${id}/category`,
        { category },
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['safeToSpend'] });
    },
  });
}

// =============================================================================
// Analytics Hooks (backend endpoints coming in Phase 3)
// =============================================================================

export function useSpendingVelocity() {
  return useQuery({
    queryKey: ['spendingVelocity'],
    queryFn: async () => {
      const { data } = await apiClient.get<ApiResponse<unknown[]>>(
        '/api/v1/analytics/velocity',
      );
      return data.data;
    },
    enabled: false, // Phase 3
  });
}

export function useSubscriptions() {
  return useQuery({
    queryKey: ['subscriptions'],
    queryFn: async () => {
      const { data } = await apiClient.get<ApiResponse<unknown[]>>(
        '/api/v1/analytics/subscriptions',
      );
      return data.data;
    },
    enabled: false, // Phase 3
  });
}

// =============================================================================
// Statement Upload Hook
// =============================================================================

export function useUploadStatement() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      const { data } = await apiClient.post<ApiResponse<{ transactionCount: number }>>(
        '/api/v1/statements/upload',
        formData,
      );
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['safeToSpend'] });
    },
  });
}

// =============================================================================
// AI Assistant Hook
// =============================================================================

export function useAIChat() {
  return useMutation({
    mutationFn: async (message: string) => {
      const { data } = await apiClient.post<ApiResponse<unknown>>(
        '/api/v1/ai/chat',
        { message },
      );
      return data.data;
    },
  });
}
