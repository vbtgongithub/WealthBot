"""
WealthBot Logging Configuration Tests
======================================
Verify structlog setup for both development and production modes.
"""

from unittest.mock import patch

from app.core.logging import configure_logging


class TestConfigureLogging:
    def test_dev_mode(self) -> None:
        with patch("app.core.logging.settings") as mock_settings:
            mock_settings.app_env = "development"
            mock_settings.log_level = "DEBUG"
            configure_logging()

    def test_production_mode(self) -> None:
        with patch("app.core.logging.settings") as mock_settings:
            mock_settings.app_env = "production"
            mock_settings.log_level = "INFO"
            configure_logging()
