"""
WealthBot Predictions Endpoint Tests
=====================================
Integration tests for the safe-to-spend endpoint.
"""

from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient

# =============================================================================
# Safe-to-Spend
# =============================================================================


class TestSafeToSpend:
    @pytest.mark.asyncio
    async def test_heuristic_response(self, authed_client: AsyncClient) -> None:
        resp = await authed_client.get("/api/v1/safe-to-spend")
        assert resp.status_code == 200
        body = resp.json()
        assert "amount" in body
        assert body["model_used"] == "heuristic"
        assert body["is_ml_active"] is False
        assert "recommendations" in body

    @pytest.mark.asyncio
    async def test_response_has_required_fields(
        self, authed_client: AsyncClient
    ) -> None:
        resp = await authed_client.get("/api/v1/safe-to-spend")
        body = resp.json()
        required = {
            "amount",
            "safe_until",
            "daily_allowance",
            "risk_level",
            "days_until_payday",
            "model_used",
            "is_ml_active",
            "recommendations",
        }
        assert required.issubset(body.keys())

    @pytest.mark.asyncio
    async def test_unauthenticated(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/safe-to-spend")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_ml_service_called(
        self,
        authed_client: AsyncClient,
        mock_ml_service: MagicMock,
    ) -> None:
        await authed_client.get("/api/v1/safe-to-spend")
        mock_ml_service.calculate_safe_to_spend.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_safe_until_format(self, authed_client: AsyncClient) -> None:
        resp = await authed_client.get("/api/v1/safe-to-spend")
        safe_until = resp.json()["safe_until"]
        # Should be YYYY-MM-DD
        parts = safe_until.split("-")
        assert len(parts) == 3
        assert len(parts[0]) == 4
