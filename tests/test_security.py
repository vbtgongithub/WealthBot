"""
WealthBot Security Module Tests
================================
Unit tests for password hashing, JWT tokens, and PII protection.
"""

from datetime import timedelta
from unittest.mock import patch

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    hash_pii,
    mask_email,
    mask_pii,
    sanitize_log_data,
    verify_password,
)

# =============================================================================
# Password Hashing
# =============================================================================


class TestPasswordHashing:
    def test_hash_password_returns_bcrypt_hash(self) -> None:
        hashed = hash_password("SecurePassword123!")
        assert hashed.startswith("$2b$")
        assert len(hashed) == 60

    def test_verify_password_correct(self) -> None:
        hashed = hash_password("SecurePassword123!")
        assert verify_password("SecurePassword123!", hashed) is True

    def test_verify_password_wrong(self) -> None:
        hashed = hash_password("SecurePassword123!")
        assert verify_password("WrongPassword!", hashed) is False

    def test_hash_password_unique_salts(self) -> None:
        h1 = hash_password("same_password")
        h2 = hash_password("same_password")
        assert h1 != h2  # Different salts


# =============================================================================
# JWT Tokens
# =============================================================================


class TestJWT:
    def test_create_and_decode_token(self) -> None:
        token = create_access_token(subject="user-123")
        payload = decode_access_token(token)
        assert payload is not None
        assert payload.sub == "user-123"
        assert payload.type == "access"

    def test_custom_expiration(self) -> None:
        token = create_access_token(
            subject="user-456",
            expires_delta=timedelta(minutes=5),
        )
        payload = decode_access_token(token)
        assert payload is not None
        assert payload.sub == "user-456"

    def test_expired_token_returns_none(self) -> None:
        token = create_access_token(
            subject="user-789",
            expires_delta=timedelta(seconds=-1),
        )
        assert decode_access_token(token) is None

    def test_invalid_token_returns_none(self) -> None:
        assert decode_access_token("not.a.valid.jwt") is None


# =============================================================================
# PII Masking
# =============================================================================


class TestPIIMasking:
    def test_mask_email_standard(self) -> None:
        assert mask_email("john.doe@example.com") == "j***e@e***.com"

    def test_mask_email_short_local(self) -> None:
        result = mask_email("ab@x.com")
        assert "***" in result

    def test_mask_email_empty(self) -> None:
        assert mask_email("") == ""

    def test_mask_email_no_at(self) -> None:
        assert mask_email("not-an-email") == "not-an-email"

    @patch("app.core.security.settings")
    def test_mask_pii_email(self, mock_settings: object) -> None:
        mock_settings.enable_pii_masking = True  # type: ignore[attr-defined]
        result = mask_pii("contact user@example.com for info", "email")
        assert "user@example.com" not in result
        assert "***@***.***" in result

    @patch("app.core.security.settings")
    def test_mask_pii_disabled(self, mock_settings: object) -> None:
        mock_settings.enable_pii_masking = False  # type: ignore[attr-defined]
        result = mask_pii("user@example.com")
        assert result == "user@example.com"

    def test_hash_pii_deterministic(self) -> None:
        h1 = hash_pii("user@example.com")
        h2 = hash_pii("user@example.com")
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex digest

    def test_hash_pii_different_values(self) -> None:
        h1 = hash_pii("alice@example.com")
        h2 = hash_pii("bob@example.com")
        assert h1 != h2


# =============================================================================
# Log Sanitization
# =============================================================================


class TestSanitizeLogData:
    def test_redacts_sensitive_keys(self) -> None:
        data = {"password": "secret123", "username": "test"}
        result = sanitize_log_data(data)
        assert result["password"] == "[REDACTED]"
        assert result["username"] == "test"

    def test_redacts_nested_dicts(self) -> None:
        data = {"user": {"token": "abc123", "name": "Test"}}
        result = sanitize_log_data(data)
        assert result["user"]["token"] == "[REDACTED]"
        assert result["user"]["name"] == "Test"

    def test_preserves_non_sensitive_values(self) -> None:
        data = {"count": 42, "active": True}
        result = sanitize_log_data(data)
        assert result == data
