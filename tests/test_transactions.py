"""
WealthBot Transaction Endpoint Tests
=====================================
Integration tests for transaction CRUD, search, and category patching.
"""

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Transaction, User
from tests.conftest import sample_transaction_data

# =============================================================================
# Helpers
# =============================================================================


async def _seed_transaction(
    db: AsyncSession,
    user: User,
    *,
    merchant: str = "Swiggy",
    category: str = "Food",
    amount: str = "499.00",
) -> Transaction:
    txn = Transaction(
        user_id=user.id,
        amount=Decimal(amount),
        currency="INR",
        transaction_type="expense",
        category=category,
        merchant_name=merchant,
        description=f"Order from {merchant}",
        transaction_date=datetime.now(UTC),
    )
    db.add(txn)
    await db.flush()
    await db.refresh(txn)
    return txn


# =============================================================================
# List / Search
# =============================================================================


class TestListTransactions:
    @pytest.mark.asyncio
    async def test_list_empty(self, authed_client: AsyncClient) -> None:
        resp = await authed_client.get("/api/v1/transactions")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 0
        assert body["data"] == []

    @pytest.mark.asyncio
    async def test_list_with_data(
        self,
        authed_client: AsyncClient,
        db_session: AsyncSession,
        sample_user: User,
    ) -> None:
        await _seed_transaction(db_session, sample_user)
        resp = await authed_client.get("/api/v1/transactions")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    @pytest.mark.asyncio
    async def test_pagination(
        self,
        authed_client: AsyncClient,
        db_session: AsyncSession,
        sample_user: User,
    ) -> None:
        for i in range(5):
            await _seed_transaction(
                db_session, sample_user, merchant=f"Shop{i}", amount=f"{100 + i}.00"
            )
        resp = await authed_client.get("/api/v1/transactions?limit=2&offset=0")
        body = resp.json()
        assert body["page_size"] == 2
        assert len(body["data"]) == 2
        assert body["total"] == 5

    @pytest.mark.asyncio
    async def test_search_by_merchant(
        self,
        authed_client: AsyncClient,
        db_session: AsyncSession,
        sample_user: User,
    ) -> None:
        await _seed_transaction(db_session, sample_user, merchant="Zomato")
        await _seed_transaction(db_session, sample_user, merchant="Amazon")
        resp = await authed_client.get("/api/v1/transactions?search=zomato")
        assert resp.json()["total"] == 1

    @pytest.mark.asyncio
    async def test_search_by_category(
        self,
        authed_client: AsyncClient,
        db_session: AsyncSession,
        sample_user: User,
    ) -> None:
        await _seed_transaction(
            db_session, sample_user, merchant="Uber", category="Transportation"
        )
        resp = await authed_client.get("/api/v1/transactions?search=transportation")
        assert resp.json()["total"] == 1


# =============================================================================
# CRUD
# =============================================================================


class TestCreateTransaction:
    @pytest.mark.asyncio
    async def test_create_success(self, authed_client: AsyncClient) -> None:
        resp = await authed_client.post(
            "/api/v1/transactions", json=sample_transaction_data()
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["merchant_name"] == "Swiggy"
        assert Decimal(body["amount"]) == Decimal("499.00")

    @pytest.mark.asyncio
    async def test_create_auto_categorization(
        self,
        authed_client: AsyncClient,
        mock_ml_service: MagicMock,
    ) -> None:
        """When category=OTHER, the ML service should be called."""
        data = sample_transaction_data()
        data["category"] = "Other"
        resp = await authed_client.post("/api/v1/transactions", json=data)
        assert resp.status_code == 201
        mock_ml_service.categorize_transaction.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_invalid_amount(self, authed_client: AsyncClient) -> None:
        data = sample_transaction_data()
        data["amount"] = "-10.00"
        resp = await authed_client.post("/api/v1/transactions", json=data)
        assert resp.status_code == 422


class TestGetTransaction:
    @pytest.mark.asyncio
    async def test_get_by_id(
        self,
        authed_client: AsyncClient,
        db_session: AsyncSession,
        sample_user: User,
    ) -> None:
        txn = await _seed_transaction(db_session, sample_user)
        resp = await authed_client.get(f"/api/v1/transactions/{txn.id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == txn.id

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, authed_client: AsyncClient) -> None:
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await authed_client.get(f"/api/v1/transactions/{fake_id}")
        assert resp.status_code == 404


class TestDeleteTransaction:
    @pytest.mark.asyncio
    async def test_delete_success(
        self,
        authed_client: AsyncClient,
        db_session: AsyncSession,
        sample_user: User,
    ) -> None:
        txn = await _seed_transaction(db_session, sample_user)
        resp = await authed_client.delete(f"/api/v1/transactions/{txn.id}")
        assert resp.status_code == 204


# =============================================================================
# Category Patch
# =============================================================================


class TestCategoryPatch:
    @pytest.mark.asyncio
    async def test_patch_category(
        self,
        authed_client: AsyncClient,
        db_session: AsyncSession,
        sample_user: User,
    ) -> None:
        txn = await _seed_transaction(db_session, sample_user)
        resp = await authed_client.patch(
            f"/api/v1/transactions/{txn.id}/category",
            json={"category": "Entertainment"},
        )
        assert resp.status_code == 200
        assert resp.json()["category"] == "Entertainment"
