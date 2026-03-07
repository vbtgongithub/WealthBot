"""
WealthBot User Schemas
======================
Pydantic models for user registration, authentication, and profile management.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# =============================================================================
# Request Schemas
# =============================================================================


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    monthly_income: Decimal | None = Field(None, ge=0, decimal_places=2)
    savings_goal: Decimal | None = Field(None, ge=0, decimal_places=2)
    currency: str = Field("INR", max_length=3)


class UserUpdate(BaseModel):
    """Schema for updating user profile. All fields optional."""

    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    monthly_income: Decimal | None = Field(None, ge=0, decimal_places=2)
    savings_goal: Decimal | None = Field(None, ge=0, decimal_places=2)
    currency: str | None = Field(None, max_length=3)


class LoginRequest(BaseModel):
    """Schema for login / token request."""

    email: EmailStr
    password: str


# =============================================================================
# Response Schemas
# =============================================================================


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Public user profile response (excludes hashed_password)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    monthly_income: Decimal | None = None
    savings_goal: Decimal | None = None
    currency: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None = None
