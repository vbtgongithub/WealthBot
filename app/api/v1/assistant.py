"""
WealthBot AI Assistant Router
=============================
Rule-based financial assistant endpoint for Aura chat.
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.api.deps import get_current_user
from app.core.rate_limit import limiter
from app.db.database import get_db_session
from app.db.models import Transaction, TransactionType, User
from app.schemas.insights import AIChatRequest, AIChatResponse

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


def _contains_any(message: str, words: list[str]) -> bool:
    return any(word in message for word in words)


@router.post(
    "/chat",
    response_model=AIChatResponse,
    summary="Chat with Aura assistant",
)
@limiter.limit("20/minute")
async def chat_with_aura(
    request: Request,
    body: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> AIChatResponse:
    """Provide personalized spending guidance using current account context."""
    _ = request
    message = body.message.lower().strip()

    now = datetime.now(UTC)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    weekly_start = now - timedelta(days=7)

    month_total_q = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == TransactionType.EXPENSE.value,
        Transaction.transaction_date >= month_start,
    )
    week_total_q = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == TransactionType.EXPENSE.value,
        Transaction.transaction_date >= weekly_start,
    )

    month_total: Decimal = (await db.execute(month_total_q)).scalar_one()
    week_total: Decimal = (await db.execute(week_total_q)).scalar_one()
    monthly_income = current_user.monthly_income or Decimal("0")
    savings_goal = current_user.savings_goal or Decimal("0")

    budget_remaining = max(monthly_income - month_total - savings_goal, Decimal("0"))
    daily_budget = budget_remaining / Decimal(max(1, 30 - now.day + 1))

    if _contains_any(message, ["safe", "spend", "budget", "allowance"]):
        return AIChatResponse(
            reply=(
                f"You can safely target about ₹{daily_budget:.0f} per day for the rest "
                f"of this month if you want to protect your savings goal."
            ),
            suggestions=[
                "Show my last 7 days spending",
                "How can I reduce food spending this week?",
                "What is my monthly burn rate?",
            ],
            confidence=0.87,
        )

    if _contains_any(message, ["subscription", "recurring", "auto debit"]):
        return AIChatResponse(
            reply=(
                "I can track recurring payments from your transaction history. "
                "Open Leakage Hunter to review subscription due dates and monthly commitment."
            ),
            suggestions=[
                "Show subscriptions due soon",
                "What can I cancel this month?",
                "Estimate monthly recurring burden",
            ],
            confidence=0.84,
        )

    if _contains_any(message, ["save", "saving", "goal"]):
        progress = Decimal("0")
        if savings_goal > 0:
            progress = min((budget_remaining / savings_goal) * Decimal("100"), Decimal("100"))
        return AIChatResponse(
            reply=(
                f"Your remaining budget after expenses is ₹{budget_remaining:.0f}. "
                f"That is about {progress:.0f}% of your monthly savings target."
            ),
            suggestions=[
                "Suggest a weekly savings plan",
                "How much can I invest this month?",
                "Show low-priority expenses",
            ],
            confidence=0.82,
        )

    return AIChatResponse(
        reply=(
            f"In the last 7 days, you spent ₹{week_total:.0f}. "
            f"This month total spending is ₹{month_total:.0f}. "
            "Ask me about safe-to-spend, subscriptions, or savings goals for targeted tips."
        ),
        suggestions=[
            "What is my safe-to-spend today?",
            "Break down this month by category",
            "How do I cut spending by 10%?",
        ],
        confidence=0.8,
    )
