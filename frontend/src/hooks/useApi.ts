'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import type {
  WBTransaction,
  ApiResponse,
  PaginatedResponse,
} from '@/types';

// =============================================================================
// Safe-to-Spend Hook
// =============================================================================

export function useSafeToSpend() {
  return useQuery({
    queryKey: ['safeToSpend'],
    queryFn: async () => {
      const { data } = await apiClient.get<ApiResponse<{ amount: number; safeUntil: string }>>(
        '/api/v1/safe-to-spend'
      );
      return data.data;
    },
  });
}

// =============================================================================
// Transaction Hooks
// =============================================================================

export function useTransactions(search?: string) {
  return useQuery({
    queryKey: ['transactions', search],
    queryFn: async () => {
      const params = search ? `?search=${encodeURIComponent(search)}` : '';
      const { data } = await apiClient.get<PaginatedResponse<WBTransaction>>(
        `/api/v1/transactions${params}`
      );
      return data;
    },
  });
}

export function useUpdateTransactionCategory() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, category }: { id: string; category: string }) => {
      const { data } = await apiClient.patch<ApiResponse<WBTransaction>>(
        `/api/v1/transactions/${id}/category`,
        { category }
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
// Analytics Hooks
// =============================================================================

export function useSpendingVelocity() {
  return useQuery({
    queryKey: ['spendingVelocity'],
    queryFn: async () => {
      const { data } = await apiClient.get<ApiResponse<any[]>>(
        '/api/v1/analytics/velocity'
      );
      return data.data;
    },
  });
}

export function useSubscriptions() {
  return useQuery({
    queryKey: ['subscriptions'],
    queryFn: async () => {
      const { data } = await apiClient.get<ApiResponse<any[]>>(
        '/api/v1/analytics/subscriptions'
      );
      return data.data;
    },
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
        formData
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
// AI Assistant Hooks
// =============================================================================

export function useAIChat() {
  return useMutation({
    mutationFn: async (message: string) => {
      const { data } = await apiClient.post<ApiResponse<any>>(
        '/api/v1/ai/chat',
        { message }
      );
      return data.data;
    },
  });
}
