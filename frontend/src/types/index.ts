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

// =============================================================================
// Auth Types (match backend app/schemas/user.py)
// =============================================================================

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  monthly_income?: number;
  savings_goal?: number;
  currency?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserProfile {
  id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  monthly_income: number | null;
  savings_goal: number | null;
  currency: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
  last_login_at: string | null;
}

// =============================================================================
// Safe-to-Spend Types (match backend app/schemas/prediction.py)
// =============================================================================

export interface SafeToSpendData {
  amount: number;
  safe_until: string;
  daily_allowance: number;
  risk_level: string;
  days_until_payday: number;
  model_used: 'heuristic' | 'xgboost';
  is_ml_active: boolean;
  recommendations: string[];
}

// =============================================================================
// Transaction Types (match backend app/schemas/transaction.py)
// =============================================================================

export interface TransactionData {
  id: string;
  user_id: string;
  amount: number;
  currency: string;
  transaction_type: string;
  category: string;
  description: string | null;
  merchant_name: string | null;
  notes: string | null;
  predicted_category: string | null;
  category_confidence: number | null;
  is_recurring: boolean;
  transaction_date: string;
  created_at: string;
  updated_at: string;
}

// Legacy User type (kept for backward compat with mock-data pages)
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
  page_size: number;
  total_pages: number;
}
