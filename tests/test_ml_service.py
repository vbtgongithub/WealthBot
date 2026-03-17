"""
WealthBot ML Service Tests
===========================
Unit tests for MLService heuristics, risk levels, and recommendations.
These tests never load ONNX models.
"""

from decimal import Decimal

import numpy as np
import pytest

from app.services.ml_service import MLService

# =============================================================================
# Singleton
# =============================================================================


class TestSingleton:
    def test_singleton_returns_same_instance(self) -> None:
        a = MLService()
        b = MLService()
        assert a is b

    def test_singleton_default_state(self) -> None:
        svc = MLService()
        # May already be loaded if tests run after startup.
        # Just verify the attribute exists.
        assert hasattr(svc, "_model_loaded")


# =============================================================================
# Heuristic Spending
# =============================================================================


class TestHeuristicSpending:
    def test_basic_heuristic(self) -> None:
        features = np.zeros(21, dtype=np.float32)
        features[7] = 500.0  # avg_daily_spending_7d
        pred, lower, upper = MLService._heuristic_spending(features)
        assert pred == pytest.approx(3500.0)
        assert lower == pytest.approx(2450.0)
        assert upper == pytest.approx(4550.0)

    def test_zero_spending(self) -> None:
        features = np.zeros(21, dtype=np.float32)
        pred, lower, upper = MLService._heuristic_spending(features)
        assert pred == 0.0
        assert lower == 0.0
        assert upper == 0.0

    def test_short_feature_vector(self) -> None:
        features = np.zeros(5, dtype=np.float32)
        pred, _, _ = MLService._heuristic_spending(features)
        assert pred == 0.0


# =============================================================================
# Risk Computation
# =============================================================================


class TestComputeRisk:
    def test_low_risk(self) -> None:
        assert MLService._compute_risk(Decimal("35000"), Decimal("100000")) == "low"

    def test_medium_risk(self) -> None:
        assert MLService._compute_risk(Decimal("20000"), Decimal("100000")) == "medium"

    def test_high_risk(self) -> None:
        assert MLService._compute_risk(Decimal("10000"), Decimal("100000")) == "high"

    def test_zero_income(self) -> None:
        assert MLService._compute_risk(Decimal("1000"), Decimal("0")) == "high"


# =============================================================================
# Recommendations
# =============================================================================


class TestRecommendations:
    def test_high_risk_tips(self) -> None:
        tips = MLService._generate_recommendations(
            Decimal("5000"), Decimal("200"), "high", 20
        )
        assert any("cutting" in t.lower() or "high" in t.lower() for t in tips)

    def test_medium_risk_tips(self) -> None:
        tips = MLService._generate_recommendations(
            Decimal("20000"), Decimal("1000"), "medium", 20
        )
        assert any("on track" in t.lower() for t in tips)

    def test_low_risk_tips(self) -> None:
        tips = MLService._generate_recommendations(
            Decimal("40000"), Decimal("2000"), "low", 20
        )
        assert any("great" in t.lower() for t in tips)

    def test_end_of_month_warning(self) -> None:
        tips = MLService._generate_recommendations(
            Decimal("5000"), Decimal("200"), "high", 3
        )
        assert any("day(s) left" in t for t in tips)


# =============================================================================
# Calculate Safe-to-Spend (heuristic path)
# =============================================================================


class TestCalculateSafeToSpend:
    @pytest.mark.asyncio
    async def test_heuristic_path(self) -> None:
        svc = MLService()
        result = await svc.calculate_safe_to_spend(
            user_id="test-user",
            monthly_income=Decimal("50000"),
            savings_goal=Decimal("5000"),
            month_expenses=Decimal("7836"),
            recurring_expenses=Decimal("0"),
            days_remaining=20,
            features=None,
        )
        assert result["model_used"] == "heuristic"
        assert result["amount"] == Decimal("37164")
        assert result["risk_level"] == "low"
        assert len(result["recommendations"]) >= 1


# =============================================================================
# Async Method Paths (no ONNX)
# =============================================================================


class TestAsyncMethods:
    @pytest.mark.asyncio
    async def test_predict_spending_heuristic(self) -> None:
        """When no model is loaded, predict_spending falls back to heuristic."""
        svc = MLService()
        svc._spending_predictor = None
        features = np.zeros(21, dtype=np.float32)
        features[7] = 400.0
        pred, lower, upper = await svc.predict_spending(features)
        assert pred == pytest.approx(2800.0)

    @pytest.mark.asyncio
    async def test_categorize_transaction_unavailable(self) -> None:
        """When categorizer is not loaded, returns (None, None)."""
        svc = MLService()
        svc._categorizer = None
        cat, conf = await svc.categorize_transaction("Swiggy food order")
        assert cat is None
        assert conf is None
