"""
WealthBot Health Endpoint Tests
================================
Tests for root, health, readiness, and liveness probes.
"""

import pytest
from httpx import AsyncClient


class TestHealthEndpoints:
    @pytest.mark.asyncio
    async def test_root(self, client: AsyncClient) -> None:
        resp = await client.get("/")
        assert resp.status_code == 200
        body = resp.json()
        assert "WealthBot" in body["message"]
        assert body["docs_url"] == "/docs"

    @pytest.mark.asyncio
    async def test_health(self, client: AsyncClient) -> None:
        resp = await client.get("/health")
        assert resp.status_code in (200, 503)
        body = resp.json()
        assert "status" in body
        assert "database" in body

    @pytest.mark.asyncio
    async def test_readiness(self, client: AsyncClient) -> None:
        resp = await client.get("/ready")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ready"

    @pytest.mark.asyncio
    async def test_liveness(self, client: AsyncClient) -> None:
        resp = await client.get("/live")
        assert resp.status_code == 200
        assert resp.json()["status"] == "alive"
