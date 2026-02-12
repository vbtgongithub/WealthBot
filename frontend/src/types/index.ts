// =============================================================================
// WealthBot TypeScript Type Definitions
// =============================================================================

// Re-export the data types from constants for convenience
export type {
  WBTransaction,
  Subscription,
  SpendingStat,
  PrivacyLog,
} from '@/constants/data';

// User Types
export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  plan: 'free' | 'pro' | 'student';
  createdAt: string;
}

// Transaction Categories (Indian student context)
export type TransactionCategory =
  | 'Food'
  | 'Travel'
  | 'Shopping'
  | 'Coffee'
  | 'Groceries'
  | 'Entertainment'
  | 'Income'
  | 'Other';

export type TransactionType = 'debit' | 'credit';

// Safe-to-Spend gauge thresholds
export interface GaugeThreshold {
  min: number;
  max: number;
  color: string;
  label: string;
}

export const GAUGE_THRESHOLDS: GaugeThreshold[] = [
  { min: 0, max: 200, color: '#ef4444', label: 'Danger' },
  { min: 200, max: 500, color: '#f59e0b', label: 'Caution' },
  { min: 500, max: 800, color: '#eab308', label: 'Okay' },
  { min: 800, max: 2000, color: '#22c55e', label: 'Safe' },
];

// AI Assistant Types
export type AssistantMessageType = 'info' | 'suggestion' | 'alert' | 'question';

export interface AssistantAction {
  label: string;
  variant: 'primary' | 'secondary';
  onClick?: () => void;
}

export interface AssistantMessage {
  id: string;
  type: AssistantMessageType;
  content: string;
  timestamp: string;
  actions?: AssistantAction[];
  data?: Record<string, unknown>;
}

// Chart Types
export interface ChartDataPoint {
  week: string;
  amount: number;
}

export interface TimeRange {
  label: string;
  value: '1W' | '1M' | '3M' | '6M' | '1Y';
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}
