"""
WealthBot Prediction Schemas
=============================
Pydantic models for Safe-to-Spend and spending prediction responses.
"""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

# =============================================================================
# Response Schemas
# =============================================================================


class SafeToSpendResponse(BaseModel):
    """
    Safe-to-Spend response.

    Always returns a number — never 503.
    ``model_used`` lets the frontend show a badge when predictions are
    heuristic-based (e.g. "Learning your habits…").
    """

    amount: Decimal
    safe_until: str
    daily_allowance: Decimal
    risk_level: str
    days_until_payday: int
    model_used: Literal["heuristic", "xgboost"]
    is_ml_active: bool
    recommendations: list[str]


class SpendingPredictionResponse(BaseModel):
    """ML-powered spending forecast response."""

    predicted_spending: Decimal
    confidence_interval_lower: Decimal
    confidence_interval_upper: Decimal
    category_breakdown: dict[str, Decimal]
    prediction_date: datetime
    model_used: Literal["heuristic", "xgboost"]
