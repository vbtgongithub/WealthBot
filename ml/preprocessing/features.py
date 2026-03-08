"""
WealthBot Feature Engineering Pipeline
=======================================
Extracts the 21-feature vector defined in ``ml/models/feature_config.json``
for both **training** and **inference** paths — single source of truth to
prevent train-serve skew.

Public API
----------
``extract_user_features(transactions, monthly_income, as_of_date)``
    → numpy float32 vector (length 21) for a single user at a point in time.

``build_training_matrix(df)``
    → (X, y) numpy arrays ready for XGBoost training.
"""

import calendar
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# =============================================================================
# Feature Config (single source of truth)
# =============================================================================

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "models" / "feature_config.json"


def load_feature_config() -> dict[str, Any]:
    """Load and return the feature configuration dict."""
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        result: dict[str, Any] = json.load(f)
        return result


_CONFIG: dict[str, Any] = load_feature_config()
FEATURE_NAMES: list[str] = [f["name"] for f in _CONFIG["features"]]
FEATURE_COUNT: int = _CONFIG["feature_count"]
TARGET_COL: str = _CONFIG["target"]
CATEGORY_GROUPS: dict[str, list[str]] = _CONFIG["category_groups"]


# =============================================================================
# Single-User Feature Extraction (Inference Path)
# =============================================================================


def extract_user_features(
    transactions: list[dict[str, Any]],
    monthly_income: float,
    as_of_date: datetime | None = None,
) -> np.ndarray:
    """Extract the 21-feature vector for a single user.

    This function is called during both training (per snapshot) and
    real-time inference.  It accepts a plain list of transaction dicts
    (or SQLAlchemy row dicts) so it can work without a DB session.

    Args:
        transactions: List of transaction dicts with at least:
            ``amount``, ``transaction_type``, ``category``,
            ``is_recurring``, ``transaction_date``.
        monthly_income: The user's declared monthly income (INR).
        as_of_date: The reference date.  Defaults to ``utcnow()``.

    Returns:
        A float32 numpy array of shape ``(21,)``.
    """
    if as_of_date is None:
        as_of_date = datetime.now(UTC)
    elif as_of_date.tzinfo is None:
        as_of_date = as_of_date.replace(tzinfo=UTC)

    # -- Parse transactions into a lightweight DataFrame ----------------------
    if not transactions:
        return _empty_features(monthly_income, as_of_date)

    df = pd.DataFrame(transactions)
    df["amount"] = df["amount"].astype(float)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], utc=True)

    expenses = df[df["transaction_type"] == "expense"].copy()
    incomes = df[df["transaction_type"] == "income"].copy()

    # -- Temporal features (indices 0-4) --------------------------------------
    day_of_month = float(as_of_date.day)
    day_of_week = float(as_of_date.weekday())
    is_weekend = 1.0 if as_of_date.weekday() >= 5 else 0.0
    days_in_mo = calendar.monthrange(as_of_date.year, as_of_date.month)[1]
    days_until_month_end = float(days_in_mo - as_of_date.day)
    is_salary_week = 1.0 if as_of_date.day <= 7 else 0.0

    # -- Spending windows -----------------------------------------------------
    cutoff_7d = as_of_date - timedelta(days=7)
    cutoff_30d = as_of_date - timedelta(days=30)

    exp_7d = expenses[expenses["transaction_date"] >= pd.Timestamp(cutoff_7d)]
    exp_30d = expenses[expenses["transaction_date"] >= pd.Timestamp(cutoff_30d)]

    total_spending_7d = float(exp_7d["amount"].sum())
    total_spending_30d = float(exp_30d["amount"].sum())
    avg_daily_spending_7d = total_spending_7d / 7.0
    avg_daily_spending_30d = total_spending_30d / 30.0
    spending_trend = (
        (avg_daily_spending_7d / avg_daily_spending_30d)
        if avg_daily_spending_30d > 0
        else 1.0
    )
    max_single_txn_7d = float(exp_7d["amount"].max()) if len(exp_7d) > 0 else 0.0
    txn_count_7d = float(len(exp_7d))
    txn_count_30d = float(len(exp_30d))

    # -- Income features ------------------------------------------------------
    if len(incomes) > 0:
        last_income_date = incomes["transaction_date"].max()
        days_since_last_income = float(
            (as_of_date - last_income_date.to_pydatetime()).days
        )
    else:
        days_since_last_income = 30.0  # Assume a month if unknown

    income_spent_ratio = (
        (total_spending_30d / monthly_income) if monthly_income > 0 else 0.0
    )

    # -- Category distribution (30d) ------------------------------------------
    total_exp_30d = total_spending_30d if total_spending_30d > 0 else 1.0

    food_cats = CATEGORY_GROUPS["food"]
    ent_cats = CATEGORY_GROUPS["entertainment"]
    ess_cats = CATEGORY_GROUPS["essential"]

    food_pct = float(
        exp_30d[exp_30d["category"].isin(food_cats)]["amount"].sum() / total_exp_30d
    )
    entertainment_pct = float(
        exp_30d[exp_30d["category"].isin(ent_cats)]["amount"].sum() / total_exp_30d
    )
    essential_pct = float(
        exp_30d[exp_30d["category"].isin(ess_cats)]["amount"].sum() / total_exp_30d
    )

    # -- Recurring & balance --------------------------------------------------
    recurring_mask = (
        (exp_30d["is_recurring"] == True)  # noqa: E712
        | (exp_30d["is_recurring"] == "True")
        | (exp_30d["is_recurring"] == 1)
    )
    recurring_expense_total = float(exp_30d.loc[recurring_mask, "amount"].sum())
    balance_remaining = monthly_income - total_spending_30d

    # -- Assemble vector (order must match feature_config.json) ---------------
    features = np.array(
        [
            day_of_month,  # 0
            day_of_week,  # 1
            is_weekend,  # 2
            days_until_month_end,  # 3
            is_salary_week,  # 4
            total_spending_7d,  # 5
            total_spending_30d,  # 6
            avg_daily_spending_7d,  # 7
            avg_daily_spending_30d,  # 8
            spending_trend,  # 9
            max_single_txn_7d,  # 10
            txn_count_7d,  # 11
            txn_count_30d,  # 12
            monthly_income,  # 13
            income_spent_ratio,  # 14
            days_since_last_income,  # 15
            food_pct,  # 16
            entertainment_pct,  # 17
            essential_pct,  # 18
            recurring_expense_total,  # 19
            balance_remaining,  # 20
        ],
        dtype=np.float32,
    )

    assert features.shape == (
        FEATURE_COUNT,
    ), f"Expected {FEATURE_COUNT} features, got {features.shape[0]}"
    return features


def _empty_features(monthly_income: float, as_of_date: datetime) -> np.ndarray:
    """Return a zero-spending feature vector (cold-start fallback)."""
    days_in_mo = calendar.monthrange(as_of_date.year, as_of_date.month)[1]
    return np.array(
        [
            float(as_of_date.day),
            float(as_of_date.weekday()),
            1.0 if as_of_date.weekday() >= 5 else 0.0,
            float(days_in_mo - as_of_date.day),
            1.0 if as_of_date.day <= 7 else 0.0,
            0.0,  # total_spending_7d
            0.0,  # total_spending_30d
            0.0,  # avg_daily_spending_7d
            0.0,  # avg_daily_spending_30d
            1.0,  # spending_trend (neutral)
            0.0,  # max_single_txn_7d
            0.0,  # txn_count_7d
            0.0,  # txn_count_30d
            monthly_income,
            0.0,  # income_spent_ratio
            30.0,  # days_since_last_income
            0.0,  # food_pct
            0.0,  # entertainment_pct
            0.0,  # essential_pct
            0.0,  # recurring_expense_total
            monthly_income,  # balance_remaining
        ],
        dtype=np.float32,
    )


# =============================================================================
# Training Matrix Builder
# =============================================================================


def build_training_matrix(
    df: pd.DataFrame,
    snapshot_stride_days: int = 3,
) -> tuple[np.ndarray, np.ndarray]:
    """Build (X, y) arrays from a historical transaction DataFrame.

    For each user, slides a window across their history.  At every
    snapshot date, ``extract_user_features()`` produces the X row,
    and the sum of expenses in the **next 7 days** becomes the y label.

    Args:
        df: Transaction DataFrame (output of ``generate_synthetic_dataset``).
            Required columns: ``user_id``, ``amount``, ``transaction_type``,
            ``category``, ``is_recurring``, ``transaction_date``,
            ``monthly_income``.
        snapshot_stride_days: Gap between consecutive snapshot dates per
            user (default 3).  Lower → more samples but higher correlation.

    Returns:
        Tuple of ``(X, y)`` where X has shape ``(n_samples, 21)`` and
        y has shape ``(n_samples,)``, both float32.
    """
    df = df.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], utc=True)
    df["amount"] = df["amount"].astype(float)

    x_rows: list[np.ndarray] = []
    y_vals: list[float] = []

    for _user_id, user_df in df.groupby("user_id"):
        user_df = user_df.sort_values("transaction_date")
        income = float(user_df["monthly_income"].iloc[0])

        min_date = user_df["transaction_date"].min()
        max_date = user_df["transaction_date"].max()

        # Need at least 30 days of history + 7 days of future
        earliest_snapshot = min_date + timedelta(days=30)
        latest_snapshot = max_date - timedelta(days=7)

        if earliest_snapshot >= latest_snapshot:
            continue

        # Convert user DataFrame to list of dicts once
        txn_records = user_df.to_dict("records")

        snapshot = earliest_snapshot
        while snapshot <= latest_snapshot:
            snapshot_dt = snapshot.to_pydatetime()

            # History: all transactions up to snapshot
            history = [r for r in txn_records if r["transaction_date"] <= snapshot]

            # Target: sum of expenses in next 7 days
            future_start = snapshot
            future_end = snapshot + timedelta(days=7)
            future_expenses = sum(
                float(r["amount"])
                for r in txn_records
                if r["transaction_type"] == "expense"
                and future_start < r["transaction_date"] <= future_end
            )

            features = extract_user_features(history, income, snapshot_dt)
            x_rows.append(features)
            y_vals.append(future_expenses)

            snapshot += timedelta(days=snapshot_stride_days)

    X = np.vstack(x_rows).astype(np.float32)
    y = np.array(y_vals, dtype=np.float32)
    return X, y


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    from ml.preprocessing.synthetic_data import generate_synthetic_dataset

    print("Generating synthetic data...")
    dataset = generate_synthetic_dataset()
    print(f"Transactions: {len(dataset):,}")

    print("Building training matrix (stride=3 days)...")
    X, y = build_training_matrix(dataset, snapshot_stride_days=3)
    print(f"Training samples: {X.shape[0]:,}")
    print(f"Feature count:    {X.shape[1]}")
    print("Target (next_7d_spending) stats:")
    print(f"  mean:   ₹{y.mean():,.2f}")
    print(f"  median: ₹{np.median(y):,.2f}")
    print(f"  std:    ₹{y.std():,.2f}")
    print(f"  min:    ₹{y.min():,.2f}")
    print(f"  max:    ₹{y.max():,.2f}")

    # Save for training scripts
    output_dir = Path(__file__).resolve().parent.parent / "models"
    output_dir.mkdir(parents=True, exist_ok=True)
    np.save(output_dir / "X_train.npy", X)
    np.save(output_dir / "y_train.npy", y)
    print(
        f"\nSaved X_train.npy ({X.shape}) and y_train.npy ({y.shape}) "
        f"to {output_dir}"
    )
