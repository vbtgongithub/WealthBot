"""
WealthBot Auth Refresh Token Tests
===================================
Integration tests for the POST /auth/refresh endpoint and token lifecycle.
"""

from datetime import timedelta

import pytest
from httpx import AsyncClient

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
)
from app.db.models import User

# =============================================================================
# Unit Tests — Token Creation & Validation
# =============================================================================


class TestTokenCreation:
    """Verify that access and refresh tokens have correct type claims."""

    def test_access_token_has_access_type(self, sample_user: User) -> None:
        token = create_access_token(subject=sample_user.id)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload.type == "access"

    def test_refresh_token_has_refresh_type(self, sample_user: User) -> None:
        token = create_refresh_token(subject=sample_user.id)
        payload = decode_refresh_token(token)
        assert payload is not None
        assert payload.type == "refresh"

    def test_access_token_rejected_as_refresh(self, sample_user: User) -> None:
        token = create_access_token(subject=sample_user.id)
        payload = decode_refresh_token(token)
        assert payload is None

    def test_refresh_token_rejected_as_access(self, sample_user: User) -> None:
        token = create_refresh_token(subject=sample_user.id)
        payload = decode_access_token(token)
        assert payload is None

    def test_expired_refresh_token_returns_none(self, sample_user: User) -> None:
        token = create_refresh_token(
            subject=sample_user.id,
            expires_delta=timedelta(seconds=-1),
        )
        payload = decode_refresh_token(token)
        assert payload is None


# =============================================================================
# Integration Tests — POST /auth/refresh Endpoint
# =============================================================================


class TestRefreshEndpoint:
    """Integration tests for the /api/v1/auth/refresh endpoint."""

    @pytest.mark.asyncio
    async def test_refresh_success(
        self, client: AsyncClient, sample_user: User
    ) -> None:
        """Valid refresh token should return new access + refresh tokens."""
        refresh = create_refresh_token(subject=sample_user.id)

        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"
        assert body["expires_in"] == 1800

        # New access token should be valid
        new_payload = decode_access_token(body["access_token"])
        assert new_payload is not None
        assert new_payload.sub == sample_user.id

    @pytest.mark.asyncio
    async def test_refresh_with_expired_token(self, client: AsyncClient, sample_user: User) -> None:
        """Expired refresh token should return 401."""
        expired_refresh = create_refresh_token(
            subject=sample_user.id,
            expires_delta=timedelta(seconds=-1),
        )

        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": expired_refresh},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_with_access_token_rejected(
        self, client: AsyncClient, sample_user: User
    ) -> None:
        """Access token cannot be used at the refresh endpoint."""
        access = create_access_token(subject=sample_user.id)

        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_with_garbage_token(self, client: AsyncClient) -> None:
        """Random string should return 401."""
        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "totally.invalid.token"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_nonexistent_user(self, client: AsyncClient) -> None:
        """Refresh token for a deleted/nonexistent user should return 401."""
        refresh = create_refresh_token(subject="00000000-0000-0000-0000-000000000000")

        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_deactivated_user(
        self,
        client: AsyncClient,
        sample_user: User,
        authed_client: AsyncClient,
    ) -> None:
        """Refresh token for a deactivated user should return 403."""
        # Deactivate the account first
        resp = await authed_client.delete("/api/v1/users/me")
        assert resp.status_code == 200

        refresh = create_refresh_token(subject=sample_user.id)
        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh},
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_refresh_missing_body(self, client: AsyncClient) -> None:
        """Missing request body should return 422."""
        resp = await client.post("/api/v1/auth/refresh", json={})
        assert resp.status_code == 422


# =============================================================================
# Full Flow — Login → Refresh → Use New Token
# =============================================================================


class TestFullRefreshFlow:
    @pytest.mark.asyncio
    async def test_login_then_refresh_then_access(
        self, client: AsyncClient, sample_user: User
    ) -> None:
        """Login → extract refresh token → refresh → use new access token."""
        # Step 1: Login
        login_resp = await client.post(
            "/api/v1/auth/token",
            json={"email": "test@example.com", "password": "SecurePassword123!"},
        )
        assert login_resp.status_code == 200
        login_body = login_resp.json()
        refresh_token = login_body["refresh_token"]

        # Step 2: Refresh
        refresh_resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert refresh_resp.status_code == 200
        new_access = refresh_resp.json()["access_token"]

        # Step 3: Use new access token to hit a protected endpoint
        profile_resp = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {new_access}"},
        )
        assert profile_resp.status_code == 200
        assert profile_resp.json()["email"] == "test@example.com"
