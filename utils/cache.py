"""Caching utilities."""

import time
from typing import Any, Dict, Optional


class SimpleCache:
    """Simple in-memory cache with TTL."""

    def __init__(self, ttl_seconds: int = 300):
        """Initialize cache.

        Args:
            ttl_seconds: Time to live in seconds
        """
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get cached value.

        Args:
            key: Cache key

        Returns:
            Cached value or None if expired
        """
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl_seconds:
                return value
            else:
                del self.cache[key]

        return None

    def set(self, key: str, value: Any) -> None:
        """Set cache value.

        Args:
            key: Cache key
            value: Value to cache
        """
        self.cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()

    def cleanup_expired(self) -> int:
        """Remove expired cache entries.

        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = [
            key
            for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp >= self.ttl_seconds
        ]

        for key in expired_keys:
            del self.cache[key]

        return len(expired_keys)
