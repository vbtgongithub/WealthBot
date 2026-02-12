import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, AssistantMessage } from '@/types';

// =============================================================================
// Auth Store
// =============================================================================

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setToken: (token) => set({ token }),
      logout: () => set({ user: null, token: null, isAuthenticated: false }),
    }),
    {
      name: 'auth-storage',
    }
  )
);

// =============================================================================
// UI Store
// =============================================================================

interface UIState {
  isSidebarOpen: boolean;
  isAssistantOpen: boolean;
  toggleSidebar: () => void;
  toggleAssistant: () => void;
  setSidebarOpen: (open: boolean) => void;
  setAssistantOpen: (open: boolean) => void;
}

export const useUIStore = create<UIState>((set) => ({
  isSidebarOpen: true,
  isAssistantOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  toggleAssistant: () => set((state) => ({ isAssistantOpen: !state.isAssistantOpen })),
  setSidebarOpen: (open) => set({ isSidebarOpen: open }),
  setAssistantOpen: (open) => set({ isAssistantOpen: open }),
}));

// =============================================================================
// Assistant Store
// =============================================================================

interface AssistantState {
  messages: AssistantMessage[];
  isLoading: boolean;
  addMessage: (message: AssistantMessage) => void;
  setMessages: (messages: AssistantMessage[]) => void;
  clearMessages: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAssistantStore = create<AssistantState>((set) => ({
  messages: [],
  isLoading: false,
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  setMessages: (messages) => set({ messages }),
  clearMessages: () => set({ messages: [] }),
  setLoading: (loading) => set({ isLoading: loading }),
}));

// =============================================================================
// Preferences Store
// =============================================================================

interface PreferencesState {
  currency: string;
  dateFormat: 'short' | 'medium' | 'long';
  theme: 'dark' | 'light';
  notifications: boolean;
  setCurrency: (currency: string) => void;
  setDateFormat: (format: 'short' | 'medium' | 'long') => void;
  setTheme: (theme: 'dark' | 'light') => void;
  setNotifications: (enabled: boolean) => void;
}

export const usePreferencesStore = create<PreferencesState>()(
  persist(
    (set) => ({
      currency: 'USD',
      dateFormat: 'medium',
      theme: 'dark',
      notifications: true,
      setCurrency: (currency) => set({ currency }),
      setDateFormat: (dateFormat) => set({ dateFormat }),
      setTheme: (theme) => set({ theme }),
      setNotifications: (notifications) => set({ notifications }),
    }),
    {
      name: 'preferences-storage',
    }
  )
);
