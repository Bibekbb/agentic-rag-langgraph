from typing import Any 
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, 
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
)
from app.config import settings
from app.core.logging import get_logger 

logger = get_logger(__name__)

class VectorStore:
    def __init__(self, dim: int, collection: str | None=None):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY or None,
            timeout=60,
        )
        self.collection = collection or settings.COLLECTION_NAME
        self.dim = dim
        self._ensure_collection()

    def _ensure_collection(self):
        existing = {c.name for c in self.client.get_collections().collections}
        if self.collection in existing:
            return 
        logger.info(f"Creating Qdrant collection: {self.collection}")
        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE),
        )
        try:
            self.client.create_payload_index(
                collection_name=self.collection,
                field_name="source",
                field_schema=PayloadSchemaType.KEYWORD,
            )
        except Exception as e:
            pass

    def upsert(self, ids: list[int], vector: list[list[float]], payloads: list[dict]):
        points = [
            PointStruct(id=i, vector=v, payload=p)
            for i, v, p in zip(ids, vector, payloads)
        ]
        self.client.upsert(collection_name=self.collection, points=points, wait=True)

    def search(
            self, 
            query_vector: list[float],
            top_k: int, 
            filters: dict[str, Any] | None = None,
    ):
        q_filter = None
        if filters:
            q_filer = Filter(
                must = [
                    FieldCondition(key=k, match=MatchValue(value=v))
                    for k, v in filters.items()
                ]
            )
        hits = self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            limit = top_k,
            query_filter=q_filter,
            with_payload=True,
        )
        return [
            {"text": h.payload.get("text", ""), "score": h.score, "metadata": h.payload}
            for h in hits
        ]

    def count(self):
        return self.client.count(collection_name=self.collection, exact=True).count
    
    