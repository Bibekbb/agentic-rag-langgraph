import json
from functools import lru_cache
import redis
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class SessionMemory:
    def __init__(self):
        try:
            self.r = redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.r.ping()
            self.ok = True
            logger.info("SessionMemory connected to Redis")
        except Exception as e:
            self.ok = False
            self.r = None
            logger.warning(f"SessionMemory disabled: {e}")

    def append(self, session_id: str, role: str, content: str) -> None:
        if not self.ok:
            return
        key = f"session:{session_id}"
        self.r.rpush(key, json.dumps({"role": role, "content": content}))
        self.r.ltrim(key, -20, -1)
        self.r.expire(key, 60 * 60 * 24)

    def history(self, session_id: str) -> list[dict]:
        if not self.ok:
            return []
        items = self.r.lrange(f"session:{session_id}", 0, -1)
        return [json.loads(i) for i in items]


@lru_cache
def get_session_memory() -> SessionMemory:
    return SessionMemory()
