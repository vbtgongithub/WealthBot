"""
WealthBot Common Schemas
========================
Shared response models used across multiple API endpoints.
"""

from pydantic import BaseModel

# =============================================================================
# Generic Responses
# =============================================================================


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str


class PaginatedResponse[T](BaseModel):
    """Paginated list response matching frontend PaginatedResponse<T> interface."""

    data: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
