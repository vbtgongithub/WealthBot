"""
WealthBot Phase 5 Endpoint Tests
================================
Integration tests for analytics, statement upload, and AI chat endpoints.
"""

import io
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient

from app.api.v1 import statements


class TestAnalyticsEndpoints:
    @pytest.mark.asyncio
    async def test_velocity_success(self, authed_client: AsyncClient) -> None:
        resp = await authed_client.get("/api/v1/analytics/velocity")
        assert resp.status_code == 200

        body = resp.json()
        assert "weekly" in body
        assert "categories" in body
        assert len(body["weekly"]) == 4
        assert {"week", "this_month", "last_month"}.issubset(body["weekly"][0].keys())

    @pytest.mark.asyncio
    async def test_subscriptions_success(self, authed_client: AsyncClient) -> None:
        resp = await authed_client.get("/api/v1/analytics/subscriptions")
        assert resp.status_code == 200

        body = resp.json()
        assert "subscriptions" in body
        assert "total_monthly_commitment" in body


class TestStatementUploadEndpoint:
    @pytest.mark.asyncio
    async def test_upload_csv_success(self, authed_client: AsyncClient) -> None:
        csv_content = io.BytesIO(
            b"date,amount,merchant,description,type,currency\n"
            b"2026-03-10,250.50,Swiggy,Lunch,expense,INR\n"
            b"2026-03-11,1200,Salary,Monthly stipend,income,INR\n"
        )
        files = {"file": ("statement.csv", csv_content, "text/csv")}

        resp = await authed_client.post("/api/v1/statements/upload", files=files)
        assert resp.status_code == 200

        body = resp.json()
        assert body["created_count"] == 2
        assert body["detected_file_type"] == "csv"

    @pytest.mark.asyncio
    async def test_upload_pdf_success_with_parser(
        self,
        authed_client: AsyncClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            statements,
            "_parse_pdf_rows",
            MagicMock(
                return_value=[
                    {
                        "date": "2026-03-12",
                        "amount": "550.00",
                        "description": "Zomato order",
                        "type": "debit",
                        "currency": "INR",
                    }
                ]
            ),
        )

        files = {"file": ("statement.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")}
        resp = await authed_client.post("/api/v1/statements/upload", files=files)
        assert resp.status_code == 200

        body = resp.json()
        assert body["created_count"] == 1
        assert body["detected_file_type"] == "pdf"

    async def test_upload_rejects_unsupported_file_type(
        self,
        authed_client: AsyncClient,
    ) -> None:
        files = {"file": ("statement.txt", io.BytesIO(b"not a statement"), "text/plain")}
        resp = await authed_client.post("/api/v1/statements/upload", files=files)
        assert resp.status_code == 400


class TestAIChatEndpoint:
    @pytest.mark.asyncio
    async def test_ai_chat_success(self, authed_client: AsyncClient) -> None:
        resp = await authed_client.post(
            "/api/v1/ai/chat",
            json={"message": "How much can I safely spend today?"},
        )
        assert resp.status_code == 200

        body = resp.json()
        assert "reply" in body
        assert "suggestions" in body
        assert isinstance(body["suggestions"], list)
        assert "confidence" in body
