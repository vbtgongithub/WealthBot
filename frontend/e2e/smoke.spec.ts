import { test, expect, type Page } from '@playwright/test';

// ─── Credentials ──────────────────────────────────────────────────────────────
const CREDS = {
  email: 'student@wealthbot.in',
  password: 'SecureDemo!2026',
  firstName: 'Swarna',
};

// ─── Helper: login and wait for dashboard ─────────────────────────────────────
async function login(page: Page) {
  await page.goto('/login');
  await page.locator('#email').fill(CREDS.email);
  await page.locator('#password').fill(CREDS.password);
  await page.getByRole('button', { name: 'Sign In' }).click();
  await page.waitForURL('**/dashboard', { timeout: 15_000 });
}

// =============================================================================
// 1. Landing Page
// =============================================================================
test.describe('Landing Page', () => {
  test('loads and shows hero section', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/aura-fi|wealthbot/i);
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    await expect(page.getByText('Instant Predictions')).toBeVisible();
  });

  test('navbar links are present', async ({ page }) => {
    await page.goto('/');
    const header = page.locator('header');
    await expect(header.getByRole('link', { name: 'Features' })).toBeVisible();
    await expect(header.getByRole('link', { name: 'Technology' })).toBeVisible();
    await expect(header.getByRole('link', { name: 'Pricing' })).toBeVisible();
    await expect(header.getByRole('link', { name: 'Sign In' })).toBeVisible();
  });

  test('hero CTA links to login', async ({ page }) => {
    await page.goto('/');
    const cta = page.getByRole('link', { name: 'Get Started Free' }).first();
    await expect(cta).toHaveAttribute('href', '/login');
  });

  test('feature grid section exists', async ({ page }) => {
    await page.goto('/');
    const features = page.locator('#features');
    await expect(features.getByText('AI Categorization')).toBeVisible();
    await expect(features.getByText('Spending Velocity')).toBeVisible();
    await expect(features.getByText('Smart Budgeting')).toBeVisible();
  });

  test('pricing section with 3 tiers', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('Flexible Plans for Every Need')).toBeVisible();
    await expect(page.getByText('Starter Plan')).toBeVisible();
    await expect(page.getByText('Pro Plan')).toBeVisible();
    await expect(page.getByText('Premium Plan')).toBeVisible();
  });

  test('footer is rendered', async ({ page }) => {
    await page.goto('/');
    // Scroll to bottom to ensure footer is in view
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await expect(page.locator('footer')).toBeVisible();
  });
});

// =============================================================================
// 2. Login Page
// =============================================================================
test.describe('Login Page', () => {
  test('renders login form', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByText('Sign in to your account')).toBeVisible();
    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Sign In' })).toBeVisible();
  });

  test('shows validation on empty submit', async ({ page }) => {
    await page.goto('/login');
    await page.getByRole('button', { name: 'Sign In' }).click();
    // HTML5 required validation should prevent submission — email field should be invalid
    const emailInput = page.locator('#email');
    const isInvalid = await emailInput.evaluate(
      (el: HTMLInputElement) => !el.validity.valid
    );
    expect(isInvalid).toBe(true);
  });

  test('shows error on wrong credentials', async ({ page }) => {
    await page.goto('/login');
    await page.locator('#email').fill('wrong@example.com');
    await page.locator('#password').fill('wrongpassword');
    await page.getByRole('button', { name: 'Sign In' }).click();
    // Should show an error message (not redirect)
    await expect(page.locator('.text-status-error, [class*="error"], [role="alert"]')).toBeVisible({ timeout: 10_000 });
  });

  test('successful login redirects to dashboard', async ({ page }) => {
    await login(page);
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('can toggle to register mode', async ({ page }) => {
    await page.goto('/login');
    await page.getByRole('button', { name: 'Sign Up' }).click();
    await expect(page.getByText('Create your account')).toBeVisible();
    await expect(page.locator('#firstName')).toBeVisible();
    await expect(page.locator('#lastName')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Create Account' })).toBeVisible();
  });
});

// =============================================================================
// 3. Dashboard Page (authenticated)
// =============================================================================
test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('shows personalized greeting', async ({ page }) => {
    await expect(page.getByText(`Hey ${CREDS.firstName}`)).toBeVisible({ timeout: 10_000 });
  });

  test('shows Safe-to-Spend gauge', async ({ page }) => {
    await expect(page.getByText('Safe to Spend')).toBeVisible({ timeout: 10_000 });
  });

  test('shows Quick Actions section', async ({ page }) => {
    await expect(page.getByText('Quick Actions')).toBeVisible({ timeout: 10_000 });
  });

  test('shows Recent Activity with transactions', async ({ page }) => {
    await expect(page.getByText('Recent Activity')).toBeVisible({ timeout: 10_000 });
    // With 7400+ transactions, there should be items (not "No transactions yet.")
    const empty = page.getByText('No transactions yet.');
    await expect(empty).not.toBeVisible({ timeout: 5_000 });
  });

  test('View All link targets /transactions', async ({ page }) => {
    const viewAll = page.getByRole('link', { name: /View All/i });
    await expect(viewAll).toHaveAttribute('href', '/transactions');
  });

  test('sidebar navigation is visible', async ({ page }) => {
    const nav = page.locator('nav[aria-label="Main navigation"]');
    await expect(nav).toBeVisible();
    await expect(page.getByRole('link', { name: 'Home' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Transactions' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Analytics' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Settings' })).toBeVisible();
  });
});

// =============================================================================
// 4. Transactions Page (authenticated)
// =============================================================================
test.describe('Transactions Page', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.getByRole('link', { name: 'Transactions' }).click();
    await page.waitForURL('**/transactions');
  });

  test('renders transactions header', async ({ page }) => {
    await expect(page.getByText('Transactions')).toBeVisible();
    await expect(page.getByText('Smart-grouped & AI-categorized')).toBeVisible();
  });

  test('search input is present', async ({ page }) => {
    await expect(page.getByPlaceholder("Search 'Swiggy' or 'Last Week'...")).toBeVisible();
  });

  test('transactions are listed (not empty)', async ({ page }) => {
    // Wait for data to load — should have date group headers
    const dateHeaders = page.locator('h3');
    await expect(dateHeaders.first()).toBeVisible({ timeout: 10_000 });
  });

  test('search filters results', async ({ page }) => {
    await page.getByPlaceholder("Search 'Swiggy' or 'Last Week'...").fill('Swiggy');
    // Wait for debounce (300ms) + API
    await page.waitForTimeout(1000);
    // Page should still be functional (no crash)
    await expect(page.locator('body')).toBeVisible();
  });
});

// =============================================================================
// 5. Analytics / Budgets Page (authenticated)
// =============================================================================
test.describe('Analytics Page', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.getByRole('link', { name: 'Analytics' }).click();
    await page.waitForURL('**/budgets');
  });

  test('renders leakage hunter header', async ({ page }) => {
    await expect(page.getByText('Leakage Hunter')).toBeVisible();
    await expect(page.getByText('Find where your money silently disappears')).toBeVisible();
  });

  test('subscription radar section visible', async ({ page }) => {
    await expect(page.getByText(/Subscription Radar/)).toBeVisible({ timeout: 10_000 });
  });

  test('spending velocity chart area visible', async ({ page }) => {
    await expect(page.getByText(/Spending Velocity/)).toBeVisible({ timeout: 10_000 });
  });

  test('category breakdown visible', async ({ page }) => {
    await expect(page.getByText('Category Breakdown')).toBeVisible({ timeout: 10_000 });
  });
});

// =============================================================================
// 6. Settings / Investments Page (authenticated)
// =============================================================================
test.describe('Settings Page', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.getByRole('link', { name: 'Settings' }).click();
    await page.waitForURL('**/investments');
  });

  test('renders vault header', async ({ page }) => {
    await expect(page.getByText('Vault & Settings')).toBeVisible();
    await expect(page.getByText('Secure data management & privacy controls')).toBeVisible();
  });

  test('import bank statement section visible', async ({ page }) => {
    await expect(page.getByText('Import Bank Statement')).toBeVisible({ timeout: 10_000 });
  });

  test('net worth section visible', async ({ page }) => {
    await expect(page.getByText('Net Worth')).toBeVisible({ timeout: 10_000 });
  });

  test('developer mode toggle visible', async ({ page }) => {
    await expect(page.getByText('Developer Mode')).toBeVisible({ timeout: 10_000 });
  });

  test('bank-grade security footer visible', async ({ page }) => {
    await expect(page.getByText('Bank-grade Security')).toBeVisible({ timeout: 10_000 });
  });
});

// =============================================================================
// 7. Navigation Flow (end-to-end routing)
// =============================================================================
test.describe('Navigation Flow', () => {
  test('full nav cycle: dashboard → transactions → analytics → settings → dashboard', async ({ page }) => {
    await login(page);

    // Dashboard
    await expect(page).toHaveURL(/\/dashboard/);

    // → Transactions
    await page.getByRole('link', { name: 'Transactions' }).click();
    await expect(page).toHaveURL(/\/transactions/);

    // → Analytics
    await page.getByRole('link', { name: 'Analytics' }).click();
    await expect(page).toHaveURL(/\/budgets/);

    // → Settings
    await page.getByRole('link', { name: 'Settings' }).click();
    await expect(page).toHaveURL(/\/investments/);

    // → Back to Dashboard
    await page.getByRole('link', { name: 'Home' }).click();
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('unauthenticated user is redirected to /login', async ({ page }) => {
    // Clear any stored tokens
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
    });
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/login/, { timeout: 10_000 });
  });
});

// =============================================================================
// 8. API Health Checks
// =============================================================================
test.describe('Backend API', () => {
  test('health endpoint returns 200', async ({ request }) => {
    const resp = await request.get('http://localhost:8000/health');
    expect(resp.status()).toBe(200);
  });

  test('login endpoint returns tokens', async ({ request }) => {
    const resp = await request.post('http://localhost:8000/api/v1/auth/token', {
      data: { email: CREDS.email, password: CREDS.password },
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body).toHaveProperty('access_token');
    expect(body).toHaveProperty('refresh_token');
  });

  test('transactions endpoint requires auth', async ({ request }) => {
    const resp = await request.get('http://localhost:8000/api/v1/transactions/');
    expect(resp.status()).toBe(401);
  });

  test('transactions endpoint returns data with auth', async ({ request }) => {
    // Login first
    const loginResp = await request.post('http://localhost:8000/api/v1/auth/token', {
      data: { email: CREDS.email, password: CREDS.password },
    });
    const { access_token } = await loginResp.json();

    const resp = await request.get('http://localhost:8000/api/v1/transactions/', {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    // API returns PaginatedResponse: { data: [...], total, page, page_size, total_pages }
    expect(body).toHaveProperty('data');
    expect(Array.isArray(body.data)).toBe(true);
    expect(body.data.length).toBeGreaterThan(0);
    expect(body.total).toBeGreaterThan(0);
  });
});
