from typing import Any, Optional
import hashlib
import json
import time


class SimpleCache:
    """In-memory cache with TTL and size limits."""

    def __init__(self, ttl: int = 300, max_size: int = 100):
        self._cache: dict[str, tuple[Any, float]] = {}
        self._ttl = ttl
        self._max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        """Get cached value if exists and not expired."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return value
            del self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Set cache value with current timestamp."""
        if len(self._cache) >= self._max_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()

    def stats(self) -> dict[str, int]:
        """Get cache statistics."""
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "ttl": self._ttl,
        }


def hash_request(data: dict) -> str:
    """Create deterministic hash of request data."""
    json_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(json_str.encode()).hexdigest()
