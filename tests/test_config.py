"""Test configuration."""

import pytest

from mcp_rag.config import Settings, get_settings, settings


class TestSettings:
    def test_singleton(self) -> None:
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_app_name(self) -> None:
        assert settings.app_name == "mcp-server-rag"

    def test_app_version(self) -> None:
        assert settings.app_version == "1.0.0"

    def test_environment(self) -> None:
        assert settings.environment in ("development", "staging", "production")

    def test_is_production_property(self) -> None:
        assert isinstance(settings.is_production, bool)

    def test_jwt_secret_length(self) -> None:
        assert len(settings.jwt_secret) >= 32

    def test_jwt_algorithm(self) -> None:
        assert settings.jwt_algorithm in ("HS256", "HS384", "HS512")

    def test_database_url_safe(self) -> None:
        safe = settings.database_url_safe
        assert "***" in safe or "pass" not in safe

    def test_max_query_length(self) -> None:
        assert settings.max_query_length > 0

    def test_max_top_k(self) -> None:
        assert settings.max_top_k > 0


class TestSettingsValidation:
    def test_jwt_secret_too_short(self) -> None:
        with pytest.raises(Exception):
            Settings(
                jwt_secret="short",
                database_url="postgresql://x:y@localhost/db",
            )

    def test_chunk_overlap_too_large(self) -> None:
        # chunk_overlap phải < chunk_size
        with pytest.raises(Exception):
            Settings(
                jwt_secret="a" * 32,
                database_url="postgresql://x:y@localhost/db",
                chunk_size=100,
                chunk_overlap=100,
            )
