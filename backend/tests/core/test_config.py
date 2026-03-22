import pytest
from app.core.config import Settings, get_settings


class TestSettings:
    def test_settings_has_required_fields(self):
        settings = Settings()
        assert hasattr(settings, "APP_API_KEY")
        assert hasattr(settings, "GEMINI_API_KEY")
        assert hasattr(settings, "CORS_ORIGINS")
        assert hasattr(settings, "ENVIRONMENT")
        assert hasattr(settings, "API_TITLE")
        assert hasattr(settings, "API_VERSION")
        assert hasattr(settings, "CACHE_ENABLED")
        assert hasattr(settings, "CACHE_TTL")
        assert hasattr(settings, "CACHE_MAX_SIZE")

    def test_cors_origins_list_property(self):
        settings = Settings()
        origins_list = settings.cors_origins_list
        assert isinstance(origins_list, list)
        assert len(origins_list) > 0
        assert all(isinstance(origin, str) for origin in origins_list)

    def test_cors_origins_list_splits_by_comma(self):
        settings = Settings()
        settings.CORS_ORIGINS = "http://localhost:3000,http://localhost:5173"
        origins_list = settings.cors_origins_list
        assert len(origins_list) == 2
        assert "http://localhost:3000" in origins_list
        assert "http://localhost:5173" in origins_list

    def test_cors_origins_list_strips_whitespace(self):
        settings = Settings()
        settings.CORS_ORIGINS = "http://localhost:3000 , http://localhost:5173"
        origins_list = settings.cors_origins_list
        assert "http://localhost:3000" in origins_list
        assert "http://localhost:5173" in origins_list
        assert " http://localhost:5173" not in origins_list

    def test_environment_is_development_or_production(self):
        settings = Settings()
        assert settings.ENVIRONMENT in ["development", "production"]

    def test_cache_enabled_is_boolean(self):
        settings = Settings()
        assert isinstance(settings.CACHE_ENABLED, bool)

    def test_cache_ttl_is_integer(self):
        settings = Settings()
        assert isinstance(settings.CACHE_TTL, int)
        assert settings.CACHE_TTL > 0

    def test_cache_max_size_is_integer(self):
        settings = Settings()
        assert isinstance(settings.CACHE_MAX_SIZE, int)
        assert settings.CACHE_MAX_SIZE > 0

    def test_api_title_is_string(self):
        settings = Settings()
        assert isinstance(settings.API_TITLE, str)
        assert len(settings.API_TITLE) > 0

    def test_api_version_is_string(self):
        settings = Settings()
        assert isinstance(settings.API_VERSION, str)
        assert len(settings.API_VERSION) > 0


class TestGetSettings:
    def test_get_settings_returns_settings_instance(self):
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_get_settings_returns_same_instance(self):
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2
