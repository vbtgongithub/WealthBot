// =============================================================================
// WealthBot User Store — Zustand
// Manages Safe-to-Spend state, transactions, and user preferences
// =============================================================================

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { MOCK_TRANSACTIONS, type WBTransaction } from '@/constants/data';

interface UserState {
  // User profile
  userName: string;
  safeToSpend: number;
  safeUntil: string;
  monthlyBudget: number;
  netWorth: number;

  // Transaction data
  transactions: WBTransaction[];

  // ML / Developer settings
  devMode: boolean;
  statementStatus: 'idle' | 'processing' | 'success' | 'error';

  // Actions
  setUserName: (name: string) => void;
  setSafeToSpend: (amount: number) => void;
  setNetWorth: (amount: number) => void;
  setDevMode: (enabled: boolean) => void;
  setStatementStatus: (status: 'idle' | 'processing' | 'success' | 'error') => void;
  updateTransactionCategory: (id: string, newCategory: string) => void;
  refreshData: () => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      // Defaults — Indian student context
      userName: 'Muzaffar',
      safeToSpend: 850,
      safeUntil: 'Friday',
      monthlyBudget: 15000,
      netWorth: 50000,

      transactions: MOCK_TRANSACTIONS,

      devMode: false,
      statementStatus: 'idle',

      // Setters
      setUserName: (name) => set({ userName: name }),
      setSafeToSpend: (amount) => set({ safeToSpend: amount }),
      setNetWorth: (amount) => set({ netWorth: amount }),
      setDevMode: (enabled) => set({ devMode: enabled }),
      setStatementStatus: (status) => set({ statementStatus: status }),

      updateTransactionCategory: (id, newCategory) =>
        set((state) => ({
          transactions: state.transactions.map((t) =>
            t.id === id ? { ...t, category: newCategory } : t
          ),
        })),

      // Simulate a model refresh — randomises Safe-to-Spend slightly
      refreshData: () =>
        set((state) => ({
          safeToSpend: Math.max(
            100,
            state.safeToSpend + Math.floor(Math.random() * 200 - 100)
          ),
        })),
    }),
    {
      name: 'wealthbot-user-storage',
    }
  )
);
