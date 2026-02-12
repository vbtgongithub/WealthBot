// =============================================================================
// WealthBot Mock Data — Indian Student Finance Context
// Realistic ₹ currency, UPI-heavy merchants, Gen Z spending patterns
// =============================================================================

export interface WBTransaction {
  id: string;
  merchant: string;
  amount: number;
  type: 'debit' | 'credit';
  category: string;
  categoryColor: string;
  date: string; // ISO string
  upiApp?: string;
  note?: string;
  aiConfidence?: number; // ML confidence score for category prediction
}

export interface Subscription {
  id: string;
  name: string;
  amount: number;
  icon: string;
  nextDue: string;
  frequency: 'monthly' | 'yearly';
  color: string;
}

export interface SpendingStat {
  category: string;
  thisMonth: number;
  lastMonth: number;
  color: string;
  icon: string;
}

export interface PrivacyLog {
  id: string;
  action: string;
  timestamp: string;
  status: 'encrypted' | 'accessed' | 'synced';
}

// ---------------------------------------------------------------------------
// Mock Transactions (Indian student context)
// ---------------------------------------------------------------------------
export const MOCK_TRANSACTIONS: WBTransaction[] = [
  // Today
  {
    id: 't1',
    merchant: 'Swiggy',
    amount: 189,
    type: 'debit',
    category: 'Food',
    categoryColor: '#f59e0b',
    date: new Date().toISOString(),
    upiApp: 'GPay',
    note: 'Lunch - Biryani',
    aiConfidence: 0.94,
  },
  {
    id: 't2',
    merchant: 'Uber Auto',
    amount: 85,
    type: 'debit',
    category: 'Travel',
    categoryColor: '#3b82f6',
    date: new Date().toISOString(),
    upiApp: 'PhonePe',
    aiConfidence: 0.97,
  },
  {
    id: 't3',
    merchant: 'Zepto',
    amount: 320,
    type: 'debit',
    category: 'Groceries',
    categoryColor: '#22c55e',
    date: new Date().toISOString(),
    upiApp: 'Paytm',
    note: '10-min delivery',
    aiConfidence: 0.91,
  },
  // Yesterday
  {
    id: 't4',
    merchant: 'Cafe Coffee Day',
    amount: 450,
    type: 'debit',
    category: 'Coffee',
    categoryColor: '#a855f7',
    date: new Date(Date.now() - 86400000).toISOString(),
    upiApp: 'GPay',
    note: '2 cappuccinos + brownie',
    aiConfidence: 0.88,
  },
  {
    id: 't5',
    merchant: 'Amazon',
    amount: 1299,
    type: 'debit',
    category: 'Shopping',
    categoryColor: '#ec4899',
    date: new Date(Date.now() - 86400000).toISOString(),
    note: 'USB-C Hub',
    aiConfidence: 0.96,
  },
  {
    id: 't6',
    merchant: 'Dad - UPI',
    amount: 5000,
    type: 'credit',
    category: 'Income',
    categoryColor: '#22c55e',
    date: new Date(Date.now() - 86400000).toISOString(),
    upiApp: 'GPay',
    note: 'Monthly pocket money',
    aiConfidence: 0.99,
  },
  // This Week
  {
    id: 't7',
    merchant: 'Rapido Bike',
    amount: 62,
    type: 'debit',
    category: 'Travel',
    categoryColor: '#3b82f6',
    date: new Date(Date.now() - 2 * 86400000).toISOString(),
    upiApp: 'PhonePe',
    aiConfidence: 0.93,
  },
  {
    id: 't8',
    merchant: 'Blinkit',
    amount: 210,
    type: 'debit',
    category: 'Groceries',
    categoryColor: '#22c55e',
    date: new Date(Date.now() - 3 * 86400000).toISOString(),
    upiApp: 'Paytm',
    aiConfidence: 0.89,
  },
  {
    id: 't9',
    merchant: 'Instamart',
    amount: 154,
    type: 'debit',
    category: 'Groceries',
    categoryColor: '#22c55e',
    date: new Date(Date.now() - 3 * 86400000).toISOString(),
    upiApp: 'GPay',
    aiConfidence: 0.85,
  },
  {
    id: 't10',
    merchant: 'BookMyShow',
    amount: 599,
    type: 'debit',
    category: 'Entertainment',
    categoryColor: '#8b5cf6',
    date: new Date(Date.now() - 4 * 86400000).toISOString(),
    note: 'Movie ticket - Oppenheimer',
    aiConfidence: 0.98,
  },
  {
    id: 't11',
    merchant: 'Zomato',
    amount: 345,
    type: 'debit',
    category: 'Food',
    categoryColor: '#f59e0b',
    date: new Date(Date.now() - 5 * 86400000).toISOString(),
    upiApp: 'GPay',
    note: 'Dinner with friends',
    aiConfidence: 0.95,
  },
  {
    id: 't12',
    merchant: 'Myntra',
    amount: 1899,
    type: 'debit',
    category: 'Shopping',
    categoryColor: '#ec4899',
    date: new Date(Date.now() - 6 * 86400000).toISOString(),
    note: 'Sneakers',
    aiConfidence: 0.92,
  },
];

// ---------------------------------------------------------------------------
// Subscriptions
// ---------------------------------------------------------------------------
export const SUBSCRIPTIONS: Subscription[] = [
  {
    id: 's1',
    name: 'Netflix',
    amount: 649,
    icon: '🎬',
    nextDue: '2 days',
    frequency: 'monthly',
    color: '#e50914',
  },
  {
    id: 's2',
    name: 'Spotify',
    amount: 119,
    icon: '🎵',
    nextDue: '12 days',
    frequency: 'monthly',
    color: '#1db954',
  },
  {
    id: 's3',
    name: 'iCloud+',
    amount: 75,
    icon: '☁️',
    nextDue: '18 days',
    frequency: 'monthly',
    color: '#007aff',
  },
  {
    id: 's4',
    name: 'ChatGPT Plus',
    amount: 1950,
    icon: '🤖',
    nextDue: '5 days',
    frequency: 'monthly',
    color: '#10a37f',
  },
];

// ---------------------------------------------------------------------------
// Spending Stats (for Analytics Velocity Chart)
// ---------------------------------------------------------------------------
export const SPENDING_STATS: SpendingStat[] = [
  { category: 'Food', thisMonth: 4200, lastMonth: 3800, color: '#f59e0b', icon: '🍕' },
  { category: 'Travel', thisMonth: 1800, lastMonth: 2100, color: '#3b82f6', icon: '🚗' },
  { category: 'Shopping', thisMonth: 3200, lastMonth: 1500, color: '#ec4899', icon: '🛍️' },
  { category: 'Coffee', thisMonth: 2400, lastMonth: 1800, color: '#a855f7', icon: '☕' },
  { category: 'Entertainment', thisMonth: 1200, lastMonth: 900, color: '#8b5cf6', icon: '🎮' },
  { category: 'Groceries', thisMonth: 2800, lastMonth: 2600, color: '#22c55e', icon: '🥦' },
];

// ---------------------------------------------------------------------------
// Spending Velocity Chart Data (weekly comparison)
// ---------------------------------------------------------------------------
export const VELOCITY_THIS_MONTH = [
  { week: 'W1', amount: 3200 },
  { week: 'W2', amount: 4800 },
  { week: 'W3', amount: 6100 },
  { week: 'W4', amount: 8400 },
];

export const VELOCITY_LAST_MONTH = [
  { week: 'W1', amount: 2800 },
  { week: 'W2', amount: 4200 },
  { week: 'W3', amount: 5600 },
  { week: 'W4', amount: 7200 },
];

// ---------------------------------------------------------------------------
// Privacy / Access Logs
// ---------------------------------------------------------------------------
export const PRIVACY_LOGS: PrivacyLog[] = [
  { id: 'p1', action: 'ML Model accessed transaction data', timestamp: '10:42 AM', status: 'encrypted' },
  { id: 'p2', action: 'Statement parsed and tokenized', timestamp: '10:38 AM', status: 'synced' },
  { id: 'p3', action: 'Safe-to-Spend recalculated', timestamp: '10:35 AM', status: 'encrypted' },
  { id: 'p4', action: 'Category prediction model run', timestamp: '09:15 AM', status: 'accessed' },
  { id: 'p5', action: 'User session authenticated', timestamp: '09:00 AM', status: 'encrypted' },
  { id: 'p6', action: 'Data export requested (CSV)', timestamp: 'Yesterday', status: 'synced' },
];

// ---------------------------------------------------------------------------
// Quick Actions for Home
// ---------------------------------------------------------------------------
export const QUICK_ACTIONS = [
  { id: 'qa1', label: 'Scan QR', icon: '📷', color: '#3b82f6' },
  { id: 'qa2', label: 'Add Cash', icon: '💰', color: '#22c55e' },
  { id: 'qa3', label: 'Split Bill', icon: '🔀', color: '#a855f7' },
  { id: 'qa4', label: 'Pay Bills', icon: '📄', color: '#f59e0b' },
  { id: 'qa5', label: 'Invest', icon: '📈', color: '#ec4899' },
];

// ---------------------------------------------------------------------------
// Category config for consistent icon/color mapping
// ---------------------------------------------------------------------------
export const CATEGORY_CONFIG: Record<string, { icon: string; color: string }> = {
  Food: { icon: '🍕', color: '#f59e0b' },
  Travel: { icon: '🚗', color: '#3b82f6' },
  Shopping: { icon: '🛍️', color: '#ec4899' },
  Coffee: { icon: '☕', color: '#a855f7' },
  Groceries: { icon: '🥦', color: '#22c55e' },
  Entertainment: { icon: '🎮', color: '#8b5cf6' },
  Income: { icon: '💸', color: '#22c55e' },
  Other: { icon: '📦', color: '#64748b' },
};
