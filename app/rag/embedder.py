from functools import lru_cache
from typing import List
import numpy as np 
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class Embedder:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.EMBED_MODEL
        logger.info(f"Loading embedder: {self.model_name}")
        self.model = SentenceTransformer(self .model_name)
        self.dim = self.model.get_sentence_embedding_dimension()

    def embed(self, texts: List[str]):
        return self.model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=32, 
            show_progress_bar=False,
            convert_to_numpy=True,
        )

    def embed_one(self, text: str):
        return self.embed([text])[0]

@lru_cache
def get_embedder():
    return Embedder()