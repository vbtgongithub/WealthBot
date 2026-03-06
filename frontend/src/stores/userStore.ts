// =============================================================================
// WealthBot UI Store — Zustand
// Client-only UI state. All server/API data lives in React Query.
// =============================================================================

import { useEffect, useSyncExternalStore } from 'react';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIState {
  devMode: boolean;
  setDevMode: (enabled: boolean) => void;

  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;

  assistantOpen: boolean;
  setAssistantOpen: (open: boolean) => void;

  statementStatus: 'idle' | 'processing' | 'success' | 'error';
  setStatementStatus: (status: 'idle' | 'processing' | 'success' | 'error') => void;

  netWorth: number;
  setNetWorth: (amount: number) => void;
}

export const useUserStore = create<UIState>()(
  persist(
    (set) => ({
      devMode: false,
      sidebarOpen: false,
      assistantOpen: false,
      statementStatus: 'idle',
      netWorth: 50000,

      setDevMode: (enabled) => set({ devMode: enabled }),
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
      setAssistantOpen: (open) => set({ assistantOpen: open }),
      setStatementStatus: (status) => set({ statementStatus: status }),
      setNetWorth: (amount) => set({ netWorth: amount }),
    }),
    {
      name: 'wealthbot-ui-storage',
      partialize: (state) => ({
        devMode: state.devMode,
        netWorth: state.netWorth,
      }),
      skipHydration: true,
    }
  )
);

/**
 * Hook to safely hydrate persisted Zustand state on the client,
 * preventing server/client mismatch during SSR.
 */
const emptySubscribe = () => () => {};

export function useHydration() {
  const hydrated = useSyncExternalStore(
    emptySubscribe,
    () => true,
    () => false,
  );

  useEffect(() => {
    useUserStore.persist.rehydrate();
  }, []);

  return hydrated;
}
