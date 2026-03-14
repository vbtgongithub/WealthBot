"""
WealthBot ML Service
====================
Machine Learning service for spending predictions, safe-to-spend
calculations, and transaction categorization.

Loads ONNX models once at startup via the FastAPI lifespan and exposes
async-safe methods that delegate to ``run_in_executor`` for non-blocking
inference.
"""

import asyncio
import functools
import logging
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# ML Service
# =============================================================================


class MLService:
    """Singleton ML service shared across all requests.

    Handles:
    - Loading ONNX model artifacts (XGBoost + DistilBERT)
    - Generating spending predictions via ``SpendingPredictor``
    - Categorizing transactions via ``TransactionCategorizer``
    - Calculating "Safe-to-Spend" amounts
    - Graceful heuristic fallback when models are unavailable
    """

    _instance: Optional["MLService"] = None
    _spending_predictor: Any = None
    _categorizer: Any = None
    _model_loaded: bool = False
    _categorizer_loaded: bool = False

    def __new__(cls) -> "MLService":
        """Singleton pattern for ML service."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ------------------------------------------------------------------
    # Model Loading
    # ------------------------------------------------------------------

    async def load_models(self) -> None:
        """Load all ONNX models in a thread pool (non-blocking).

        Called once during FastAPI lifespan.  Individual model failures
        are logged but do not crash the application — endpoints fall
        back to heuristic logic.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._load_spending_predictor)
        await loop.run_in_executor(None, self._load_categorizer)

    def _load_spending_predictor(self) -> None:
        """Synchronously load the XGBoost ONNX spending predictor."""
        try:
            from ml.inference.predictor import SpendingPredictor

            model_path = Path(settings.xgboost_onnx_path)
            if not model_path.exists():
                logger.warning(
                    "XGBoost ONNX model not found at %s — "
                    "spending predictions will use heuristic fallback.",
                    model_path,
                )
                return
            self._spending_predictor = SpendingPredictor(model_path)
            self._model_loaded = True
            logger.info("SpendingPredictor ready.")
        except Exception:
            logger.exception("Failed to load SpendingPredictor")

    def _load_categorizer(self) -> None:
        """Synchronously load the DistilBERT ONNX categorizer."""
        try:
            from ml.inference.categorizer import TransactionCategorizer

            model_path = Path(settings.categorizer_onnx_path)
            tokenizer_path = Path(settings.tokenizer_path)
            label_encoder_path = Path(settings.label_encoder_path)

            missing = [
                p
                for p in (model_path, tokenizer_path, label_encoder_path)
                if not p.exists()
            ]
            if missing:
                logger.warning(
                    "Categorizer artifacts missing: %s — "
                    "auto-categorization disabled.",
                    [str(m) for m in missing],
                )
                return

            self._categorizer = TransactionCategorizer(
                model_path=model_path,
                tokenizer_path=tokenizer_path,
                label_encoder_path=label_encoder_path,
            )
            self._categorizer_loaded = True
            logger.info("TransactionCategorizer ready.")
        except Exception:
            logger.exception("Failed to load TransactionCategorizer")

    # Backwards-compat alias used by lifespan
    async def load_model(self) -> bool:
        """Load all models and return True if spending predictor is ready."""
        await self.load_models()
        return self._model_loaded

    # ------------------------------------------------------------------
    # Spending Prediction
    # ------------------------------------------------------------------

    async def predict_spending(
        self,
        features: np.ndarray,
        *,
        user_id: str | None = None,
    ) -> tuple[float, float, float]:
        """Predict next-7-day spending from a 21-feature vector.

        Args:
            features: float32 array of shape ``(21,)``.
            user_id: Optional user ID for structured logging.

        Returns:
            ``(prediction, lower_ci, upper_ci)`` in INR.
        """
        if self._spending_predictor is None:
            return self._heuristic_spending(features)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            functools.partial(
                self._spending_predictor.predict, features, user_id=user_id
            ),
        )

    @staticmethod
    def _heuristic_spending(features: np.ndarray) -> tuple[float, float, float]:
        """Fallback when ONNX model is unavailable.

        Uses avg_daily_spending_7d × 7 as a naive estimate.
        """
        avg_daily_7d = float(features[7]) if len(features) > 7 else 0.0
        prediction = avg_daily_7d * 7.0
        return prediction, prediction * 0.7, prediction * 1.3

    # ------------------------------------------------------------------
    # Transaction Categorization
    # ------------------------------------------------------------------

    async def categorize_transaction(
        self,
        text: str,
        *,
        user_id: str | None = None,
    ) -> tuple[str | None, float | None]:
        """Categorize a transaction from merchant + description text.

        Args:
            text: ``"merchant_name description"`` string.
            user_id: Optional user ID for structured logging.

        Returns:
            ``(category, confidence)`` or ``(None, None)`` when
            the categorizer is unavailable.
        """
        if self._categorizer is None:
            return None, None

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            functools.partial(self._categorizer.categorize, text, user_id=user_id),
        )

    # ------------------------------------------------------------------
    # Safe-to-Spend Calculation
    # ------------------------------------------------------------------

    async def calculate_safe_to_spend(
        self,
        *,
        user_id: str,
        monthly_income: Decimal,
        savings_goal: Decimal,
        month_expenses: Decimal,
        recurring_expenses: Decimal,
        days_remaining: int,
        features: np.ndarray | None = None,
    ) -> dict[str, Any]:
        """Calculate the daily safe-to-spend amount.

        When the ONNX model is loaded and ``features`` are provided, the
        predicted next-7-day spending is incorporated into the budget
        calculation.  Otherwise, a simple heuristic is used.

        Returns a dict with keys: ``amount``, ``daily_allowance``,
        ``risk_level``, ``recommendations``, ``model_used``.
        """
        if (
            self._model_loaded
            and self._spending_predictor is not None
            and features is not None
        ):
            prediction, lower, upper = await self.predict_spending(
                features, user_id=user_id
            )
            predicted_remaining = Decimal(str(round(prediction, 2)))
            # Adjust budget by predicted upcoming spending
            buffer = monthly_income * Decimal("0.05")
            available = (
                monthly_income
                - savings_goal
                - month_expenses
                - recurring_expenses
                - buffer
            )
            # Nudge down if model predicts heavy upcoming spend
            if predicted_remaining > available:
                available = max(
                    Decimal("0"),
                    available - (predicted_remaining - available) / 2,
                )
            safe_amount = max(Decimal("0"), available)
            model_used = "xgboost"
        else:
            available = (
                monthly_income - savings_goal - month_expenses - recurring_expenses
            )
            safe_amount = max(Decimal("0"), available)
            model_used = "heuristic"

        daily_allowance = (
            (safe_amount / Decimal(str(days_remaining))).quantize(Decimal("0.01"))
            if days_remaining > 0
            else safe_amount
        )

        risk_level = self._compute_risk(safe_amount, monthly_income)
        recommendations = self._generate_recommendations(
            safe_amount, daily_allowance, risk_level, days_remaining
        )

        return {
            "amount": safe_amount,
            "daily_allowance": daily_allowance,
            "risk_level": risk_level,
            "recommendations": recommendations,
            "model_used": model_used,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_risk(safe_amount: Decimal, monthly_income: Decimal) -> str:
        if monthly_income <= 0:
            return "high"
        ratio = safe_amount / monthly_income
        if ratio >= Decimal("0.30"):
            return "low"
        if ratio >= Decimal("0.15"):
            return "medium"
        return "high"

    @staticmethod
    def _generate_recommendations(
        safe_amount: Decimal,
        daily_allowance: Decimal,
        risk_level: str,
        days_remaining: int,
    ) -> list[str]:
        tips: list[str] = []
        if risk_level == "high":
            tips.append(
                "Your spending is high — consider cutting discretionary purchases."
            )
            tips.append(f"Try to keep daily spending under ₹{daily_allowance:,.0f}.")
        elif risk_level == "medium":
            tips.append("You're on track but watch large one-time expenses.")
            tips.append(
                f"You have ₹{safe_amount:,.0f} available for discretionary spending."
            )
        else:
            tips.append("Great job! You're well within your budget this month.")

        if days_remaining <= 5:
            tips.append(
                f"Only {days_remaining} day(s) left this month — spend carefully."
            )
        return tips


# =============================================================================
# Dependency Injection Helper
# =============================================================================


def get_ml_service() -> MLService:
    """FastAPI dependency that returns the singleton MLService."""
    return MLService()
