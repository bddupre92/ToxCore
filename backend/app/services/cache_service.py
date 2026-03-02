"""Upstash Redis caching layer."""

import json
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based caching with TTL support."""

    def __init__(self, redis_url: str, redis_token: str) -> None:
        self._enabled = bool(redis_url and redis_token)
        self._redis = None
        if self._enabled:
            try:
                from upstash_redis import Redis

                self._redis = Redis(url=redis_url, token=redis_token)
            except Exception:
                logger.warning("Failed to connect to Upstash Redis, caching disabled")
                self._enabled = False

    @property
    def enabled(self) -> bool:
        return self._enabled

    def get(self, key: str) -> Any | None:
        if not self._enabled or not self._redis:
            return None
        try:
            value = self._redis.get(key)
            if value is not None:
                return json.loads(value) if isinstance(value, str) else value
        except Exception:
            logger.warning("Cache get failed for key: %s", key)
        return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        if not self._enabled or not self._redis:
            return
        try:
            self._redis.set(key, json.dumps(value), ex=ttl)
        except Exception:
            logger.warning("Cache set failed for key: %s", key)

    async def get_or_compute(
        self, key: str, compute_fn: Callable, ttl: int = 3600
    ) -> Any:
        """Get from cache or compute and store."""
        cached = self.get(key)
        if cached is not None:
            return cached
        result = await compute_fn()
        self.set(key, result, ttl)
        return result


class NoOpCacheService(CacheService):
    """Cache service that does nothing (for testing)."""

    def __init__(self) -> None:
        self._enabled = False
        self._redis = None
