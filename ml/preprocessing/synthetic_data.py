"""
WealthBot Synthetic Data Generator
===================================
Generates realistic Indian-student transaction datasets for ML training.

Produces ~10k transactions across 100 synthetic users with realistic
temporal patterns: weekend food spikes, month-end crunch, recurring
bills, and UPI-style merchant names.

Usage
-----
    python -m ml.preprocessing.synthetic_data          # writes CSV
    from ml.preprocessing.synthetic_data import generate_synthetic_dataset
    df = generate_synthetic_dataset()                   # returns DataFrame
"""

import calendar
from datetime import UTC, datetime
from pathlib import Path
from typing import Final, TypedDict

import numpy as np
import pandas as pd


class _RecurringItem(TypedDict):
    category: str
    amount: float


# =============================================================================
# Constants — Indian Student Finance Context
# =============================================================================

CATEGORIES: Final[list[str]] = [
    "Housing",
    "Transportation",
    "Food",
    "Coffee",
    "Groceries",
    "Travel",
    "Utilities",
    "Healthcare",
    "Insurance",
    "Entertainment",
    "Shopping",
    "Education",
    "Savings",
    "Investments",
    "Debt Payment",
    "Income",
    "Other",
]

EXPENSE_CATEGORIES: Final[list[str]] = [
    c for c in CATEGORIES if c not in ("Income", "Savings", "Investments")
]

# Merchant pools keyed by category — realistic Indian / UPI names
MERCHANTS: Final[dict[str, list[str]]] = {
    "Food": [
        "Swiggy",
        "Zomato",
        "Dominos India",
        "Pizza Hut IN",
        "McDonald's IN",
        "Burger King IN",
        "KFC India",
        "Chai Point",
        "Haldirams",
        "Barbeque Nation",
        "Biryani Blues",
        "Behrouz Biryani",
    ],
    "Coffee": [
        "Third Wave Coffee",
        "Blue Tokai Coffee",
        "Starbucks India",
        "Cafe Coffee Day",
    ],
    "Groceries": [
        "Zepto",
        "BigBasket",
        "Blinkit",
        "JioMart",
        "DMart Ready",
        "Swiggy Instamart",
        "Nature's Basket",
    ],
    "Transportation": [
        "Rapido",
        "Uber India",
        "Ola Cabs",
        "Delhi Metro",
        "Mumbai Local",
        "Bangalore BMTC",
        "Namma Yatri",
    ],
    "Entertainment": [
        "BookMyShow",
        "PVR Cinemas",
        "Netflix India",
        "Spotify India",
        "Disney+ Hotstar",
        "Amazon Prime IN",
        "YouTube Premium",
    ],
    "Shopping": [
        "Amazon India",
        "Flipkart",
        "Myntra",
        "Ajio",
        "Nykaa",
        "Meesho",
        "Croma",
    ],
    "Education": [
        "Unacademy",
        "Coursera",
        "Udemy India",
        "College Fees",
        "Campus Bookstore",
        "Kindle India",
    ],
    "Housing": ["PG Rent", "Hostel Fee", "NoBroker Rent", "Flatmate Split"],
    "Utilities": [
        "Jio Recharge",
        "Airtel Recharge",
        "Vi Recharge",
        "Electricity Bill",
        "Water Bill",
        "WiFi Bill",
    ],
    "Healthcare": [
        "Apollo Pharmacy",
        "Pharmeasy",
        "1mg",
        "Practo Consult",
        "Dr. Lal PathLabs",
    ],
    "Insurance": ["ICICI Lombard", "Star Health", "Digit Insurance"],
    "Travel": [
        "IRCTC",
        "MakeMyTrip",
        "RedBus",
        "IndiGo",
        "Cleartrip",
    ],
    "Debt Payment": ["Education Loan EMI", "Credit Card Bill"],
    "Other": ["GPay Transfer", "PhonePe Transfer", "Paytm Transfer", "UPI"],
}

# Monthly income ranges for Indian students (INR)
INCOME_BRACKETS: Final[list[tuple[float, float, float]]] = [
    # (min_income, max_income, population_weight)
    (8_000.0, 15_000.0, 0.30),  # Pocket money / part-time
    (15_000.0, 30_000.0, 0.35),  # Stipend / internship
    (30_000.0, 50_000.0, 0.25),  # Working student / entry job
    (50_000.0, 80_000.0, 0.10),  # Well-off / full-time
]

# Spending distribution weights per category (relative, sums ~1.0)
# These control how the monthly budget is split across categories
CATEGORY_WEIGHTS: Final[dict[str, float]] = {
    "Housing": 0.25,
    "Food": 0.18,
    "Transportation": 0.08,
    "Groceries": 0.10,
    "Coffee": 0.03,
    "Entertainment": 0.06,
    "Shopping": 0.07,
    "Education": 0.05,
    "Utilities": 0.05,
    "Healthcare": 0.02,
    "Insurance": 0.02,
    "Travel": 0.03,
    "Debt Payment": 0.03,
    "Other": 0.03,
}


# =============================================================================
# Helper Functions
# =============================================================================


def _sample_income(rng: np.random.Generator) -> float:
    """Sample a monthly income from weighted brackets."""
    brackets = np.array(INCOME_BRACKETS)
    weights = brackets[:, 2].astype(float)
    weights /= weights.sum()
    idx = rng.choice(len(brackets), p=weights)
    low, high = float(brackets[idx, 0]), float(brackets[idx, 1])
    return float(rng.uniform(low, high))


def _days_in_month(year: int, month: int) -> int:
    """Return the number of days in a given month."""
    return calendar.monthrange(year, month)[1]


def _generate_user_transactions(
    user_id: int,
    monthly_income: float,
    rng: np.random.Generator,
    start_date: datetime,
    n_months: int,
) -> list[dict[str, object]]:
    """Generate transactions for a single user over n_months.

    Applies realistic temporal patterns:
    - Recurring bills on 1st-5th of month
    - Weekend food/entertainment spikes (1.4x multiplier)
    - Month-end crunch (spending drops to 60% in last 5 days)
    - Salary credited on 1st of each month
    """
    transactions: list[dict[str, object]] = []

    # Per-user spending personality: how aggressively they spend
    spend_ratio = float(rng.uniform(0.55, 0.90))
    monthly_budget = monthly_income * spend_ratio

    # Per-user category preference noise (±30%)
    cat_noise = {cat: float(rng.uniform(0.7, 1.3)) for cat in CATEGORY_WEIGHTS}

    # Recurring expenses (rent, subscriptions) — fixed each month
    recurring_items = _pick_recurring(monthly_budget, rng)

    for month_offset in range(n_months):
        # Proper month arithmetic to avoid landing in the same month
        new_month = ((start_date.month - 1 + month_offset) % 12) + 1
        new_year = start_date.year + (start_date.month - 1 + month_offset) // 12
        dt = datetime(new_year, new_month, 1, tzinfo=UTC)
        year, month = dt.year, dt.month
        days = _days_in_month(year, month)

        # --- Income transaction on 1st ---
        income_date = datetime(year, month, 1, 9, 0, tzinfo=UTC)
        transactions.append(
            {
                "user_id": f"user_{user_id:04d}",
                "amount": round(monthly_income, 2),
                "currency": "INR",
                "transaction_type": "income",
                "category": "Income",
                "description": "Monthly salary / stipend",
                "merchant_name": "Employer UPI",
                "is_recurring": True,
                "transaction_date": income_date,
            }
        )

        # --- Recurring bills (1st–5th) ---
        for item in recurring_items:
            bill_day = min(int(rng.integers(1, 6)), days)
            bill_date = datetime(year, month, bill_day, 10, 0, tzinfo=UTC)
            cat_key = item["category"]
            merchant = rng.choice(MERCHANTS.get(cat_key, ["UPI"]))
            transactions.append(
                {
                    "user_id": f"user_{user_id:04d}",
                    "amount": round(item["amount"], 2),
                    "currency": "INR",
                    "transaction_type": "expense",
                    "category": cat_key,
                    "description": f"{cat_key} - recurring",
                    "merchant_name": str(merchant),
                    "is_recurring": True,
                    "transaction_date": bill_date,
                }
            )

        # --- Variable daily spending ---
        remaining_budget = monthly_budget - sum(i["amount"] for i in recurring_items)
        remaining_budget = max(remaining_budget, monthly_budget * 0.2)

        daily_base = remaining_budget / days

        for day in range(1, days + 1):
            date = datetime(year, month, day, tzinfo=UTC)
            dow = date.weekday()  # 0=Mon, 6=Sun
            is_weekend = dow >= 5

            # Temporal multipliers
            multiplier = 1.0
            if is_weekend:
                multiplier *= 1.4  # Weekend spike
            if day > days - 5:
                multiplier *= 0.6  # Month-end crunch
            if day <= 5:
                multiplier *= 1.2  # Post-salary looseness

            daily_budget = daily_base * multiplier

            # How many transactions today? (Poisson λ=2 on weekdays, 3 weekends)
            n_txns = int(rng.poisson(3 if is_weekend else 2))
            if n_txns == 0:
                continue

            # Split daily budget across transactions
            splits = rng.dirichlet(np.ones(n_txns))
            for split_frac in splits:
                amount = float(daily_budget * split_frac)
                if amount < 5.0:
                    continue  # Skip dust amounts

                # Pick category weighted by preferences
                cat = _pick_category(rng, cat_noise, is_weekend)
                merchant_pool = MERCHANTS.get(cat, ["UPI Transfer"])
                merchant = str(rng.choice(merchant_pool))

                # Add small per-txn noise (±20%)
                amount *= float(rng.uniform(0.8, 1.2))
                amount = round(amount, 2)

                # Random hour between 7am and 11pm
                hour = int(rng.integers(7, 23))
                minute = int(rng.integers(0, 60))
                txn_date = date.replace(hour=hour, minute=minute)

                transactions.append(
                    {
                        "user_id": f"user_{user_id:04d}",
                        "amount": amount,
                        "currency": "INR",
                        "transaction_type": "expense",
                        "category": cat,
                        "description": f"{cat} purchase",
                        "merchant_name": merchant,
                        "is_recurring": False,
                        "transaction_date": txn_date,
                    }
                )

    return transactions


def _pick_recurring(
    monthly_budget: float,
    rng: np.random.Generator,
) -> list[_RecurringItem]:
    """Pick recurring monthly expenses (rent, subscriptions, etc.)"""
    items: list[_RecurringItem] = []

    # Rent / housing — 20-30% of budget
    rent_pct = float(rng.uniform(0.20, 0.30))
    items.append({"category": "Housing", "amount": monthly_budget * rent_pct})

    # Utilities — 3-5%
    util_pct = float(rng.uniform(0.03, 0.05))
    items.append({"category": "Utilities", "amount": monthly_budget * util_pct})

    # Subscriptions — 1-3 of [Netflix, Spotify, YouTube Premium, Hotstar]
    sub_count = int(rng.integers(1, 4))
    sub_prices = [199.0, 119.0, 129.0, 299.0]  # INR monthly
    chosen_subs = rng.choice(len(sub_prices), size=sub_count, replace=False)
    for idx in chosen_subs:
        items.append({"category": "Entertainment", "amount": sub_prices[int(idx)]})

    # Mobile recharge — ~300-600 INR
    items.append({"category": "Utilities", "amount": float(rng.uniform(300, 600))})

    # Insurance (30% chance)
    if rng.random() < 0.3:
        items.append({"category": "Insurance", "amount": float(rng.uniform(500, 1500))})

    # Debt payment (20% chance)
    if rng.random() < 0.2:
        items.append(
            {
                "category": "Debt Payment",
                "amount": float(rng.uniform(2000, 5000)),
            }
        )

    return items


def _pick_category(
    rng: np.random.Generator,
    cat_noise: dict[str, float],
    is_weekend: bool,
) -> str:
    """Pick a spending category with weighted randomness.

    Weekend bias: Food, Coffee, Entertainment get 1.5x boost.
    """
    weights: dict[str, float] = {}
    for cat, base_w in CATEGORY_WEIGHTS.items():
        w = base_w * cat_noise.get(cat, 1.0)
        if is_weekend and cat in ("Food", "Coffee", "Entertainment", "Shopping"):
            w *= 1.5
        weights[cat] = w

    cats = list(weights.keys())
    probs = np.array([weights[c] for c in cats], dtype=np.float64)
    probs /= probs.sum()

    return str(rng.choice(cats, p=probs))


# =============================================================================
# Public API
# =============================================================================


def generate_synthetic_dataset(
    n_users: int = 100,
    txns_per_user: int = 100,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate a synthetic Indian-student transaction dataset.

    Args:
        n_users: Number of synthetic users to generate.
        txns_per_user: Target transactions per user (actual count varies
            due to Poisson sampling; ``n_months`` is calibrated to hit
            this target approximately).
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with columns: user_id, amount, currency,
        transaction_type, category, description, merchant_name,
        is_recurring, transaction_date, monthly_income.
    """
    rng = np.random.default_rng(seed)

    # Calibrate months so each user produces ~txns_per_user transactions
    # Average ~2.5 txns/day * 30 days ≈ 75 variable + ~5 recurring ≈ 80/month
    # Need at least 2 months for training (30d lookback + 7d future window)
    avg_txns_per_month = 80
    n_months = max(2, round(txns_per_user / avg_txns_per_month))

    start_date = datetime(2025, 1, 1, tzinfo=UTC)
    all_transactions: list[dict[str, object]] = []

    for user_idx in range(n_users):
        income = _sample_income(rng)
        user_txns = _generate_user_transactions(
            user_id=user_idx,
            monthly_income=income,
            rng=rng,
            start_date=start_date,
            n_months=n_months,
        )
        # Attach income metadata for feature engineering
        for txn in user_txns:
            txn["monthly_income"] = round(income, 2)
        all_transactions.extend(user_txns)

    df = pd.DataFrame(all_transactions)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], utc=True)
    df = df.sort_values(["user_id", "transaction_date"]).reset_index(drop=True)

    return df


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    output_dir = Path(__file__).resolve().parent.parent / "models"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "synthetic_transactions.csv"

    print("Generating synthetic dataset (100 users × ~100 txns)...")
    dataset = generate_synthetic_dataset()
    dataset.to_csv(output_path, index=False)
    print(f"Saved {len(dataset):,} transactions to {output_path}")
    print(f"Users: {dataset['user_id'].nunique()}")
    print(
        f"Date range: {dataset['transaction_date'].min()} → "
        f"{dataset['transaction_date'].max()}"
    )
    print(f"\nCategory distribution:\n{dataset['category'].value_counts()}")
