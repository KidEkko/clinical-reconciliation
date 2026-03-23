import pytest
from fastapi import HTTPException, status
from app.core.auth import require_api_key
from app.core.config import settings
from app.utils.crypto import hash_api_key


class TestRequireApiKey:
    def test_valid_api_key(self):
        valid_hash = hash_api_key(settings.APP_API_KEY, settings.HASH_SALT)
        result = require_api_key(valid_hash)
        assert result == valid_hash

    def test_missing_api_key(self):
        with pytest.raises(HTTPException) as exc:
            require_api_key(None)
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Missing API key" in exc.value.detail

    def test_empty_string_api_key(self):
        with pytest.raises(HTTPException) as exc:
            require_api_key("")
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Missing API key" in exc.value.detail

    def test_invalid_api_key(self):
        with pytest.raises(HTTPException) as exc:
            require_api_key("wrong-key")
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid API key" in exc.value.detail

