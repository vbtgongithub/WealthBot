"""
WealthBot ML Service
====================
Machine Learning service for spending predictions and "Safe-to-Spend" calculations.

This module demonstrates how the FastAPI layer integrates with XGBoost models
for predictive personal finance features.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, List, Optional

import joblib
import numpy as np
from pydantic import BaseModel, Field

from app.core.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# Response Models
# =============================================================================

class SpendingPrediction(BaseModel):
    """Spending prediction response schema."""
    
    predicted_spending: Decimal = Field(
        description="Predicted spending amount for the period"
    )
    confidence_interval_lower: Decimal = Field(
        description="Lower bound of 95% confidence interval"
    )
    confidence_interval_upper: Decimal = Field(
        description="Upper bound of 95% confidence interval"
    )
    category_breakdown: dict[str, Decimal] = Field(
        default_factory=dict,
        description="Predicted spending by category"
    )
    prediction_date: datetime = Field(
        description="Date when prediction was generated"
    )


class SafeToSpendResult(BaseModel):
    """Safe-to-Spend calculation result."""
    
    safe_to_spend: Decimal = Field(
        description="Amount safe to spend without impacting financial goals"
    )
    remaining_budget: Decimal = Field(
        description="Remaining monthly budget"
    )
    days_until_payday: int = Field(
        description="Days until next expected income"
    )
    daily_allowance: Decimal = Field(
        description="Recommended daily spending limit"
    )
    risk_level: str = Field(
        description="Spending risk level: low, medium, high"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Personalized spending recommendations"
    )


class TransactionFeatures(BaseModel):
    """Feature vector for ML model input."""
    
    user_id: str
    total_income: Decimal
    total_expenses: Decimal
    avg_daily_spending: Decimal
    transaction_count: int
    category_distribution: dict[str, float]
    days_since_last_income: int
    recurring_expenses: Decimal


# =============================================================================
# ML Service
# =============================================================================

class MLService:
    """
    Machine Learning Service for WealthBot.
    
    Handles:
    - Loading XGBoost model artifacts
    - Generating spending predictions
    - Calculating "Safe-to-Spend" amounts
    
    Uses async operations to avoid blocking the FastAPI event loop.
    """
    
    _instance: Optional["MLService"] = None
    _model: Optional[Any] = None
    _model_loaded: bool = False
    
    def __new__(cls) -> "MLService":
        """Singleton pattern for ML service."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def model_path(self) -> Path:
        """Get the configured model path."""
        return Path(settings.model_path)
    
    async def load_model(self) -> bool:
        """
        Asynchronously load the XGBoost model artifact.
        
        Uses joblib for efficient model serialization/deserialization.
        Runs in a thread pool to avoid blocking async operations.
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        if self._model_loaded and self._model is not None:
            logger.debug("Model already loaded, skipping reload")
            return True
        
        try:
            model_file = self.model_path
            
            if not model_file.exists():
                logger.warning(
                    f"Model file not found at {model_file}. "
                    "Using placeholder predictions."
                )
                return False
            
            # Load model in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self._model = await loop.run_in_executor(
                None,
                joblib.load,
                str(model_file),
            )
            
            self._model_loaded = True
            logger.info(f"Successfully loaded XGBoost model from {model_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self._model = None
            self._model_loaded = False
            return False
    
    async def predict_spending(
        self,
        features: TransactionFeatures,
        horizon_days: int = 30,
    ) -> SpendingPrediction:
        """
        Predict user spending for a given time horizon.
        
        Args:
            features: User's transaction features
            horizon_days: Prediction horizon in days (default: 30)
            
        Returns:
            SpendingPrediction with predicted amounts and confidence intervals
        """
        # Ensure model is loaded
        await self.load_model()
        
        if self._model is not None:
            # Prepare feature vector for XGBoost
            feature_vector = self._prepare_feature_vector(features)
            
            # Run prediction in thread pool
            loop = asyncio.get_event_loop()
            prediction = await loop.run_in_executor(
                None,
                self._model.predict,
                feature_vector,
            )
            
            predicted_amount = Decimal(str(round(prediction[0], 2)))
            
            # Calculate confidence interval (simplified)
            std_dev = Decimal(str(round(prediction[0] * 0.1, 2)))  # 10% std dev
            ci_lower = predicted_amount - (std_dev * 2)
            ci_upper = predicted_amount + (std_dev * 2)
        else:
            # Placeholder prediction when model is not available
            avg_spending = float(features.avg_daily_spending) * horizon_days
            predicted_amount = Decimal(str(round(avg_spending, 2)))
            ci_lower = predicted_amount * Decimal("0.8")
            ci_upper = predicted_amount * Decimal("1.2")
        
        # Generate category breakdown (placeholder logic)
        category_breakdown = self._estimate_category_breakdown(
            predicted_amount,
            features.category_distribution,
        )
        
        return SpendingPrediction(
            predicted_spending=predicted_amount,
            confidence_interval_lower=ci_lower,
            confidence_interval_upper=ci_upper,
            category_breakdown=category_breakdown,
            prediction_date=datetime.utcnow(),
        )
    
    async def calculate_safe_to_spend(
        self,
        user_id: str,
        current_balance: Decimal,
        monthly_income: Decimal,
        monthly_savings_goal: Decimal,
        recurring_expenses: Decimal,
        days_until_payday: int,
        recent_transactions: List[dict],
    ) -> SafeToSpendResult:
        """
        Calculate the "Safe-to-Spend" amount for a user.
        
        This represents money that can be spent without:
        - Missing bill payments
        - Failing to meet savings goals
        - Going into overdraft
        
        Args:
            user_id: User identifier
            current_balance: Current account balance
            monthly_income: Expected monthly income
            monthly_savings_goal: User's savings target
            recurring_expenses: Known recurring expenses
            days_until_payday: Days until next income
            recent_transactions: Recent transaction history
            
        Returns:
            SafeToSpendResult with spending recommendations
        """
        # Calculate base safe-to-spend
        reserved_for_bills = recurring_expenses
        reserved_for_savings = monthly_savings_goal
        emergency_buffer = monthly_income * Decimal("0.05")  # 5% buffer
        
        total_reserved = reserved_for_bills + reserved_for_savings + emergency_buffer
        available = current_balance - total_reserved
        
        # Ensure non-negative
        safe_amount = max(Decimal("0"), available)
        
        # Calculate daily allowance
        if days_until_payday > 0:
            daily_allowance = safe_amount / Decimal(str(days_until_payday))
        else:
            daily_allowance = safe_amount
        
        # Determine risk level
        income_ratio = float(safe_amount / monthly_income) if monthly_income > 0 else 0
        if income_ratio >= 0.3:
            risk_level = "low"
        elif income_ratio >= 0.15:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            safe_amount,
            daily_allowance,
            risk_level,
            days_until_payday,
        )
        
        return SafeToSpendResult(
            safe_to_spend=round(safe_amount, 2),
            remaining_budget=round(available, 2),
            days_until_payday=days_until_payday,
            daily_allowance=round(daily_allowance, 2),
            risk_level=risk_level,
            recommendations=recommendations,
        )
    
    def _prepare_feature_vector(
        self,
        features: TransactionFeatures,
    ) -> np.ndarray:
        """
        Convert TransactionFeatures to numpy array for model input.
        
        Args:
            features: Transaction features
            
        Returns:
            Numpy array suitable for XGBoost prediction
        """
        # Create feature vector
        # Order must match training feature order
        feature_list = [
            float(features.total_income),
            float(features.total_expenses),
            float(features.avg_daily_spending),
            features.transaction_count,
            features.days_since_last_income,
            float(features.recurring_expenses),
        ]
        
        # Add category distribution features
        categories = [
            "housing", "transportation", "food", "utilities",
            "healthcare", "entertainment", "shopping", "other"
        ]
        for cat in categories:
            feature_list.append(features.category_distribution.get(cat, 0.0))
        
        return np.array([feature_list])
    
    def _estimate_category_breakdown(
        self,
        total_amount: Decimal,
        category_distribution: dict[str, float],
    ) -> dict[str, Decimal]:
        """
        Estimate spending breakdown by category.
        
        Args:
            total_amount: Total predicted spending
            category_distribution: Historical category distribution
            
        Returns:
            Dictionary mapping categories to predicted amounts
        """
        breakdown = {}
        
        # Default distribution if none provided
        if not category_distribution:
            category_distribution = {
                "housing": 0.30,
                "food": 0.15,
                "transportation": 0.12,
                "utilities": 0.08,
                "entertainment": 0.10,
                "shopping": 0.10,
                "healthcare": 0.05,
                "other": 0.10,
            }
        
        for category, ratio in category_distribution.items():
            amount = total_amount * Decimal(str(ratio))
            breakdown[category] = round(amount, 2)
        
        return breakdown
    
    def _generate_recommendations(
        self,
        safe_amount: Decimal,
        daily_allowance: Decimal,
        risk_level: str,
        days_until_payday: int,
    ) -> List[str]:
        """
        Generate personalized spending recommendations.
        
        Args:
            safe_amount: Safe-to-spend amount
            daily_allowance: Daily spending limit
            risk_level: Current risk level
            days_until_payday: Days until next income
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if risk_level == "high":
            recommendations.append(
                "⚠️ Your spending buffer is low. Consider delaying non-essential purchases."
            )
            recommendations.append(
                f"💡 Try to keep daily spending under ${daily_allowance:.2f}."
            )
        elif risk_level == "medium":
            recommendations.append(
                f"📊 You have ${safe_amount:.2f} available for discretionary spending."
            )
            recommendations.append(
                "💰 Consider putting 20% of this into savings."
            )
        else:
            recommendations.append(
                f"✅ You're in good shape with ${safe_amount:.2f} safe to spend."
            )
            recommendations.append(
                "🎯 Great opportunity to boost your savings or investments!"
            )
        
        if days_until_payday > 10:
            recommendations.append(
                f"📅 {days_until_payday} days until your next paycheck. Plan accordingly."
            )
        
        return recommendations


# =============================================================================
# Dependency Injection Helper
# =============================================================================

def get_ml_service() -> MLService:
    """
    Dependency for FastAPI endpoints to get the ML service.
    
    Usage:
        @app.get("/predictions")
        async def get_predictions(ml: MLService = Depends(get_ml_service)):
            return await ml.predict_spending(...)
    """
    return MLService()
