from functools import lru_cache
from sentence_transformers import CrossEncoder
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class Reranker:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.RERANK_MODEL
        logger.info(f"Loading reranker: {self.model_name}")
        self.model = CrossEncoder(self.model_name, max_length=512)   # ← KEY LINE

    def rerank(self, query: str, docs: list[dict], top_k: int = 5) -> list[dict]:
        if not docs:
            return []
        pairs = [(query, d["text"]) for d in docs]
        scores = self.model.predict(pairs, batch_size=16, show_progress_bar=False)
        for d, s in zip(docs, scores):
            d["rerank_score"] = float(s)
        ranked = sorted(docs, key=lambda x: x["rerank_score"], reverse=True)
        return ranked[:top_k]


@lru_cache
def get_reranker() -> Reranker:
    return Reranker()
