from contextlib import contextmanager
from app.config import settings


@contextmanager
def trace(name: str, metadata: dict | None = None):
    """No-op-safe Langfuse tracing wrapper."""
    client = None
    handler = None
    try:
        if settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
            from langfuse import Langfuse
            client = Langfuse(
                public_key=settings.LANGFUSE_PUBLIC_KEY,
                secret_key=settings.LANGFUSE_SECRET_KEY,   # ← secret_KEY, not secret
                host=settings.LANGFUSE_HOST,
            )
            handler = client.trace(name=name, metadata=metadata or {})
    except Exception:
        handler = None
    try:
        yield handler
    finally:
        try:
            if client:
                client.flush()
        except Exception:
            pass
