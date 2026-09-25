import hashlib
import json
from functools import lru_cache
import redis
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class SemanticCache:
    """Simple exact-match + semantic cache on Redis."""

    def __init__(self):
        try:
            self.r = redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.r.ping()
            self.ok = True
            logger.info("SemanticCache connected to Redis")
        except Exception as e:
            self.ok = False
            logger.warning(f"SemanticCache disabled: {e}")

    def _key(self, query: str) -> str:
        return "cache:" + hashlib.sha256(query.strip().lower().encode()).hexdigest()[:32]

    def get(self, query: str) -> dict | None:
        if not self.ok:
            return None
        val = self.r.get(self._key(query))
        if val:
            try:
                return json.loads(val)
            except Exception:
                return None
        return None

    def set(self, query: str, value: dict, ttl: int = 3600) -> None:
        if not self.ok:
            return
        self.r.setex(self._key(query), ttl, json.dumps(value, ensure_ascii=False))


@lru_cache
def get_semantic_cache() -> SemanticCache:
    return SemanticCache()
