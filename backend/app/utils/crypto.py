"""Cryptographic utilities for API key hashing."""
import hashlib
import logging

logger = logging.getLogger(__name__)


def hash_api_key(api_key: str, salt: str) -> str:
    """
    Hash the API key with a salt using SHA256.

    Args:
        api_key: The plain text API key
        salt: Salt to add to the API key before hashing

    Returns:
        Hexadecimal hash string
    """
    logger.debug(f"Hashing API key with salt")
    salted_key = api_key + salt
    hash_value = hashlib.sha256(salted_key.encode('utf-8')).hexdigest()
    logger.debug(f"Hash generated: {hash_value[:16]}...")
    return hash_value
