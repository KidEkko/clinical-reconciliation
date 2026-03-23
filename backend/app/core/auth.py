from fastapi import Header, HTTPException, status
import logging

from app.core.config import settings
from app.utils.crypto import hash_api_key

logger = logging.getLogger(__name__)


def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key")
) -> str:
    """Validate API key from request header by comparing hashes."""
    if not x_api_key:
        logger.warning("API key missing from request header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )

    logger.debug(f"Received hashed API key: {x_api_key[:16]}...")

    # Compare the received hash with the stored hash
    expected_hash = settings.APP_API_KEY_HASH

    # If no hash is configured, generate it on the fly (for backward compatibility)
    if not expected_hash:
        logger.warning("APP_API_KEY_HASH not configured, generating from APP_API_KEY")
        expected_hash = hash_api_key(settings.APP_API_KEY, settings.HASH_SALT)

    if x_api_key != expected_hash:
        logger.warning("API key hash does not match expected value")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    logger.info("API key validation successful")
    return x_api_key
