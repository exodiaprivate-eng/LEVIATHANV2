"""Redis caching layer with in-memory fallback."""
import json
import logging
import time
from typing import Optional

logger = logging.getLogger('leviathan.cache')


class RedisCache:
    """Cache layer using Redis, falls back to in-memory dict."""

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self._redis = None
        self._memory: dict = {}
        self._ttls: dict = {}
        try:
            import redis
            self._redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            self._redis.ping()
            logger.info("Redis connected")
        except Exception:
            logger.warning("Redis unavailable, using in-memory cache")
            self._redis = None

    def set(self, key: str, value, ttl: int = 300):
        data = json.dumps(value) if not isinstance(value, str) else value
        if self._redis:
            self._redis.setex(key, ttl, data)
        else:
            self._memory[key] = data
            self._ttls[key] = time.time() + ttl

    def get(self, key: str) -> Optional[str]:
        if self._redis:
            return self._redis.get(key)
        if key in self._memory:
            if time.time() < self._ttls.get(key, 0):
                return self._memory[key]
            del self._memory[key]
            del self._ttls[key]
        return None

    def delete(self, key: str):
        if self._redis:
            self._redis.delete(key)
        else:
            self._memory.pop(key, None)
            self._ttls.pop(key, None)

    def cache_price(self, symbol: str, price: float, ttl: int = 60):
        self.set(f"price:{symbol}", price, ttl)

    def get_cached_price(self, symbol: str) -> Optional[float]:
        val = self.get(f"price:{symbol}")
        return float(val) if val else None

    def cache_sentiment(self, symbol: str, score: float, ttl: int = 1800):
        self.set(f"sentiment:{symbol}", score, ttl)

    def get_cached_sentiment(self, symbol: str) -> Optional[float]:
        val = self.get(f"sentiment:{symbol}")
        return float(val) if val else None
