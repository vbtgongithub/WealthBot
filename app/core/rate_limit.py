"""
WealthBot Rate Limiting
=======================
Slowapi configuration for endpoint-level rate limiting.
Uses Redis as the storage backend when available, otherwise falls back to
in-memory storage.
"""

import logging

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import settings

logger = logging.getLogger("wealthbot.ratelimit")


# =============================================================================
# Limiter Instance
# =============================================================================


def _build_limiter() -> Limiter:
    """Create the Limiter with Redis or in-memory storage."""
    if settings.redis_enabled:
        try:
            logger.info("Rate limiter using Redis backend: %s", settings.redis_url)
            return Limiter(
                key_func=get_remote_address, storage_uri=settings.redis_url
            )
        except Exception:
            logger.warning(
                "Failed to initialise Redis-backed rate limiter, "
                "falling back to in-memory storage."
            )

    return Limiter(key_func=get_remote_address)


limiter = _build_limiter()


# =============================================================================
# Custom 429 Handler
# =============================================================================


async def rate_limit_exceeded_handler(
    request: Request,  # noqa: ARG001 — required by Starlette handler signature
    exc: RateLimitExceeded,
) -> JSONResponse:
    """Return a structured JSON 429 response."""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
            "retry_after": exc.detail,
        },
    )
