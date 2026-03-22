from fastapi import Header, HTTPException, status

from app.core.config import settings


def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key")
) -> str:
    """Validate API key from request header."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )

    if x_api_key != settings.APP_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    return x_api_key
