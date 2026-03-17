"""
WealthBot Test Configuration
============================
Pytest fixtures for async PostgreSQL tests with mocked ML service.
"""

import os
from collections.abc import AsyncGenerator
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Override DATABASE_URL before any app import touches settings
os.environ["DATABASE_URL"] = (
    "postgresql+asyncpg://wealthbot_user:wealthbot_secret@localhost:5432/wealthbot_test"
)

from app.core.security import create_access_token, hash_password  # noqa: E402
from app.db.database import get_db_session  # noqa: E402
from app.db.models import Base, User  # noqa: E402
from app.main import app  # noqa: E402
from app.services.ml_service import MLService, get_ml_service  # noqa: E402

# =============================================================================
# Test Database Engine (PostgreSQL)
# =============================================================================

TEST_DATABASE_URL = os.environ["DATABASE_URL"]


# =============================================================================
# Core Fixtures
# =============================================================================


@pytest_asyncio.fixture(autouse=True)
async def _setup_tables() -> AsyncGenerator[None, None]:
    """Create tables before each test and drop after."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean async DB session per test."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()
    await engine.dispose()


@pytest_asyncio.fixture
async def mock_ml_service() -> MagicMock:
    """Return a deterministic mock of MLService — never loads ONNX."""
    mock = MagicMock(spec=MLService)
    mock._model_loaded = False
    mock._categorizer_loaded = False

    mock.predict_spending = AsyncMock(return_value=(5000.0, 3500.0, 6500.0))
    mock.categorize_transaction = AsyncMock(return_value=("Food", 0.95))
    mock.calculate_safe_to_spend = AsyncMock(
        return_value={
            "amount": Decimal("37164.00"),
            "daily_allowance": Decimal("1905.85"),
            "risk_level": "low",
            "recommendations": [
                "Great job! You're well within your budget this month."
            ],
            "model_used": "heuristic",
        }
    )
    return mock


@pytest_asyncio.fixture
async def client(
    db_session: AsyncSession,
    mock_ml_service: MagicMock,
) -> AsyncGenerator[AsyncClient, None]:
    """HTTP test client with DB and ML service overrides."""

    async def _override_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = _override_db
    app.dependency_overrides[get_ml_service] = lambda: mock_ml_service

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# =============================================================================
# User Fixtures
# =============================================================================


@pytest_asyncio.fixture
async def sample_user(db_session: AsyncSession) -> User:
    """Insert and return a test user."""
    user = User(
        email="test@example.com",
        hashed_password=hash_password("SecurePassword123!"),
        first_name="Test",
        last_name="User",
        monthly_income=Decimal("50000.00"),
        savings_goal=Decimal("5000.00"),
        currency="INR",
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(sample_user: User) -> dict[str, str]:
    """Return Authorization headers for the sample_user."""
    token = create_access_token(subject=sample_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def authed_client(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> AsyncClient:
    """Client with auth headers pre-set."""
    client.headers.update(auth_headers)
    return client


# =============================================================================
# Data Fixtures
# =============================================================================


def sample_user_data() -> dict:
    """Sample user registration payload."""
    return {
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "first_name": "New",
        "last_name": "User",
        "monthly_income": "50000.00",
        "savings_goal": "5000.00",
        "currency": "INR",
    }


def sample_transaction_data() -> dict:
    """Sample transaction creation payload."""
    return {
        "amount": "499.00",
        "currency": "INR",
        "transaction_type": "expense",
        "category": "Food",
        "description": "Swiggy order",
        "merchant_name": "Swiggy",
    }
