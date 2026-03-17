"""
WealthBot Analytics Router
==========================
Spending velocity and recurring subscription insights.
"""

from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.database import get_db_session
from app.db.models import Transaction, TransactionType, User
from app.schemas.insights import (
    CategorySpendingComparison,
    SpendingVelocityResponse,
    SubscriptionInsight,
    SubscriptionsResponse,
    WeeklyVelocityPoint,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _first_day_of_month(target: date) -> date:
    return target.replace(day=1)


def _previous_month(target: date) -> date:
    first = _first_day_of_month(target)
    return (first - timedelta(days=1)).replace(day=1)


def _week_bucket(day: int) -> int:
    if day <= 7:
        return 0
    if day <= 14:
        return 1
    if day <= 21:
        return 2
    return 3


@router.get(
    "/velocity",
    response_model=SpendingVelocityResponse,
    summary="Get weekly spending velocity",
)
async def get_spending_velocity(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> SpendingVelocityResponse:
    """Return weekly cumulative expense velocity and category deltas."""
    today = datetime.now(UTC).date()
    this_month_start = _first_day_of_month(today)
    last_month_start = _previous_month(today)

    tx_rows = await db.execute(
        select(Transaction).where(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == TransactionType.EXPENSE.value,
            Transaction.transaction_date >= datetime.combine(last_month_start, datetime.min.time(), tzinfo=UTC),
        )
    )
    expenses = list(tx_rows.scalars().all())

    weekly_totals = {
        "this": [Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0")],
        "last": [Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0")],
    }
    category_totals_this: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    category_totals_last: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))

    for tx in expenses:
        tx_date = tx.transaction_date.date()
        bucket = _week_bucket(tx_date.day)
        amount = Decimal(tx.amount)
        category = tx.category or "Other"

        if tx_date >= this_month_start:
            weekly_totals["this"][bucket] += amount
            category_totals_this[category] += amount
        elif tx_date >= last_month_start:
            weekly_totals["last"][bucket] += amount
            category_totals_last[category] += amount

    this_cumulative: list[Decimal] = []
    last_cumulative: list[Decimal] = []
    this_running = Decimal("0")
    last_running = Decimal("0")
    for idx in range(4):
        this_running += weekly_totals["this"][idx]
        last_running += weekly_totals["last"][idx]
        this_cumulative.append(this_running)
        last_cumulative.append(last_running)

    weekly = [
        WeeklyVelocityPoint(
            week=f"W{i + 1}",
            this_month=this_cumulative[i],
            last_month=last_cumulative[i],
        )
        for i in range(4)
    ]

    all_categories = set(category_totals_this.keys()) | set(category_totals_last.keys())
    categories = sorted(
        [
            CategorySpendingComparison(
                category=category,
                this_month=category_totals_this.get(category, Decimal("0")),
                last_month=category_totals_last.get(category, Decimal("0")),
            )
            for category in all_categories
        ],
        key=lambda item: item.this_month,
        reverse=True,
    )

    return SpendingVelocityResponse(weekly=weekly, categories=categories)


@router.get(
    "/subscriptions",
    response_model=SubscriptionsResponse,
    summary="Detect recurring subscription-like expenses",
)
async def get_subscriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> SubscriptionsResponse:
    """Infer recurring subscriptions from repeating merchant+amount patterns."""
    cutoff = datetime.now(UTC) - timedelta(days=120)
    tx_rows = await db.execute(
        select(Transaction).where(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == TransactionType.EXPENSE.value,
            Transaction.merchant_name.is_not(None),
            Transaction.transaction_date >= cutoff,
        )
    )
    expenses = list(tx_rows.scalars().all())

    grouped: dict[tuple[str, Decimal, str], list[Transaction]] = defaultdict(list)
    for tx in expenses:
        key = (
            (tx.merchant_name or "Unknown").strip(),
            Decimal(tx.amount),
            tx.currency,
        )
        grouped[key].append(tx)

    today = datetime.now(UTC).date()
    subscriptions: list[SubscriptionInsight] = []
    monthly_commitment = Decimal("0")

    for (merchant, amount, currency), txs in grouped.items():
        if len(txs) < 2:
            continue

        txs.sort(key=lambda item: item.transaction_date)
        date_points = [item.transaction_date.date() for item in txs]
        deltas = [
            (date_points[idx] - date_points[idx - 1]).days
            for idx in range(1, len(date_points))
        ]
        avg_gap = sum(deltas) / len(deltas)

        if avg_gap > 45:
            continue

        if avg_gap >= 25:
            frequency = "monthly"
            monthly_commitment += amount
        elif avg_gap >= 6:
            frequency = "weekly"
            monthly_commitment += amount * Decimal("4")
        else:
            continue

        next_due_date = date_points[-1] + timedelta(days=max(1, round(avg_gap)))
        subscriptions.append(
            SubscriptionInsight(
                merchant_name=merchant,
                amount=amount,
                currency=currency,
                frequency=frequency,
                occurrences=len(txs),
                last_charge_date=date_points[-1],
                next_due_date=next_due_date,
                next_due_in_days=max((next_due_date - today).days, 0),
            )
        )

    subscriptions.sort(key=lambda item: item.next_due_in_days)
    return SubscriptionsResponse(
        subscriptions=subscriptions,
        total_monthly_commitment=monthly_commitment,
    )
