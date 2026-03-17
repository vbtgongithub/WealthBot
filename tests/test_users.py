"""
WealthBot Users & Auth Endpoint Tests
======================================
Integration tests for registration, login, profile CRUD.
"""

from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.models import User
from tests.conftest import sample_user_data

# =============================================================================
# Registration
# =============================================================================


class TestRegister:
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/auth/register", json=sample_user_data())
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == "newuser@example.com"
        assert body["first_name"] == "New"
        assert "hashed_password" not in body

    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self, client: AsyncClient, sample_user: User
    ) -> None:
        data = sample_user_data()
        data["email"] = sample_user.email  # Already exists
        resp = await client.post("/api/v1/auth/register", json=data)
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient) -> None:
        data = sample_user_data()
        data["password"] = "short"
        resp = await client.post("/api/v1/auth/register", json=data)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient) -> None:
        data = sample_user_data()
        data["email"] = "not-an-email"
        resp = await client.post("/api/v1/auth/register", json=data)
        assert resp.status_code == 422


# =============================================================================
# Login
# =============================================================================


class TestLogin:
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, sample_user: User) -> None:
        resp = await client.post(
            "/api/v1/auth/token",
            json={"email": "test@example.com", "password": "SecurePassword123!"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"
        assert body["expires_in"] == 1800  # 30 min * 60

    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self, client: AsyncClient, sample_user: User
    ) -> None:
        resp = await client.post(
            "/api/v1/auth/token",
            json={"email": "test@example.com", "password": "WrongPassword!"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_email(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/v1/auth/token",
            json={"email": "nobody@example.com", "password": "whatever"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_login_deactivated_account(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        user = User(
            email="inactive@example.com",
            hashed_password=hash_password("SecurePassword123!"),
            is_active=False,
        )
        db_session.add(user)
        await db_session.flush()

        resp = await client.post(
            "/api/v1/auth/token",
            json={"email": "inactive@example.com", "password": "SecurePassword123!"},
        )
        assert resp.status_code == 403


# =============================================================================
# Profile
# =============================================================================


class TestProfile:
    @pytest.mark.asyncio
    async def test_get_profile(self, authed_client: AsyncClient) -> None:
        resp = await authed_client.get("/api/v1/users/me")
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == "test@example.com"
        assert body["first_name"] == "Test"

    @pytest.mark.asyncio
    async def test_get_profile_unauthenticated(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/users/me")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_update_profile(self, authed_client: AsyncClient) -> None:
        resp = await authed_client.put(
            "/api/v1/users/me",
            json={"first_name": "Updated", "monthly_income": "75000.00"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["first_name"] == "Updated"
        assert Decimal(body["monthly_income"]) == Decimal("75000.00")

    @pytest.mark.asyncio
    async def test_delete_account(self, authed_client: AsyncClient) -> None:
        resp = await authed_client.delete("/api/v1/users/me")
        assert resp.status_code == 200
        assert "deactivated" in resp.json()["message"].lower()

        # Subsequent requests should fail with 403
        resp2 = await authed_client.get("/api/v1/users/me")
        assert resp2.status_code == 403
