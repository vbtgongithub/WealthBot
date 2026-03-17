"""
WealthBot Phase 6A Middleware Tests
===================================
Validation for request hardening middleware stack.
"""

import pytest
from httpx import AsyncClient
from starlette.requests import Request

from app.main import internal_server_error_handler


class TestMiddlewareHardening:
    @pytest.mark.asyncio
    async def test_request_id_and_security_headers(
        self,
        client: AsyncClient,
    ) -> None:
        response = await client.get("/")
        assert response.status_code == 200
        assert response.headers.get("X-Request-ID") is not None
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert "max-age=" in response.headers.get("Strict-Transport-Security", "")

    @pytest.mark.asyncio
    async def test_trusted_host_rejects_unknown_host(
        self,
        client: AsyncClient,
    ) -> None:
        response = await client.get("/", headers={"host": "evil.example.com"})
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_internal_server_error_handler_safe_payload(self) -> None:
        scope = {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "path": "/boom",
            "raw_path": b"/boom",
            "query_string": b"",
            "headers": [],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
            "scheme": "http",
        }
        request = Request(scope)
        request.state.request_id = "req-test-123"

        response = await internal_server_error_handler(request, RuntimeError("boom"))
        assert response.status_code == 500
        assert b"Internal Server Error" in response.body
        assert b"req-test-123" in response.body
