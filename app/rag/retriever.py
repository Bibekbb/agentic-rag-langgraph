from typing import Any
from app.rag.embedder import get_embedder
from app.rag.vectorstore import VectorStore
from app.rag.reranker import get_reranker
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class Retriever:
    def __init__(self):
        self.embedder = get_embedder()
        self.reranker = get_reranker()
        self.store = VectorStore(dim=self.embedder.dim)

    def retrieve(
            self, 
            query:str,
            top_k: int | None = None,
            filters: dict[str, Any] | None = None,
    ):
        top_k = top_k or settings.TOP_K_RETRIEVE
        q_vec = self.embedder.embed_one(query).tolist()
        return self.store.search(q_vec, top_k=top_k, filters=filters)

    def retrieve_and_rerank(
            self, 
            query: str,
            top_k_retrieve: int | None = None,
            top_k_rerank: int | None = None,
            filters: dict[str, Any] | None = None,
    ):
        docs = self.retrieve(query, top_k_retrieve, filters)
        return self.reranker.rerank(query, docs, top_k_rerank or settings.TOP_K_RERANK)

    def multi_query_retrieve(
            self, 
            queries: list[str],
            top_k_retrieve: int | None = None,
            top_k_rerank: int | None = None,
            filters: dict[str, Any] | None = None,
    ):
        all_docs: list[dict] = []
        seen: set[str] = set()
        for q in queries:
            for d in self.retrieve(q, top_k_retrieve, filters):
                key = d["text"][:120]
                if key not in seen:
                    seen.add(key)
                    all_docs.append(d)
        return self.reranker.rerank(queries[0], all_docs, top_k_rerank or settings.TOP_K_RERANK)

_retriever: Retriever | None = None

def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever