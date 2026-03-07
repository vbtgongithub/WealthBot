"""
WealthBot Transaction Schemas
==============================
Pydantic models for transaction CRUD and category updates.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import TransactionCategory, TransactionType

# =============================================================================
# Request Schemas
# =============================================================================


class TransactionCreate(BaseModel):
    """Schema for creating a new transaction."""

    amount: Decimal = Field(gt=0, decimal_places=2)
    currency: str = Field("INR", max_length=3)
    transaction_type: TransactionType = TransactionType.EXPENSE
    category: TransactionCategory = TransactionCategory.OTHER
    description: str | None = Field(None, max_length=500)
    merchant_name: str | None = Field(None, max_length=255)
    notes: str | None = None
    is_recurring: bool = False
    transaction_date: datetime | None = None


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction. All fields optional."""

    amount: Decimal | None = Field(None, gt=0, decimal_places=2)
    currency: str | None = Field(None, max_length=3)
    transaction_type: TransactionType | None = None
    category: TransactionCategory | None = None
    description: str | None = Field(None, max_length=500)
    merchant_name: str | None = Field(None, max_length=255)
    notes: str | None = None
    is_recurring: bool | None = None
    transaction_date: datetime | None = None


class CategoryUpdateRequest(BaseModel):
    """Schema for PATCH /transactions/{id}/category endpoint."""

    category: TransactionCategory


# =============================================================================
# Response Schemas
# =============================================================================


class TransactionResponse(BaseModel):
    """Full transaction response matching frontend WBTransaction shape."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    amount: Decimal
    currency: str
    transaction_type: str
    category: str
    description: str | None = None
    merchant_name: str | None = None
    notes: str | None = None
    predicted_category: str | None = None
    category_confidence: Decimal | None = None
    is_recurring: bool
    transaction_date: datetime
    created_at: datetime
    updated_at: datetime
