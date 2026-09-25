from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    #LLM 
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    DEFAULT_LLM: str = "gpt-4o-mini"
    FAST_LLM: str = "llama-3.3-70b-versatile"

    # Infra
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"
    POSTGRES_URL: str = "postgresql://user:pass@localhost:5432/rag"

    # RAG
    EMBED_MODEL: str = "BAAI/bge-m3"
    RERANK_MODEL: str = "BAAI/bge-reranker-v2-m3"
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150
    TOP_K_RETRIEVE: int = 20
    TOP_K_RERANK: int = 5
    CONFIDENCE_THRESHOLD: float = 0.6
    MAX_RETRIES: int = 2
    COLLECTION_NAME: str = "documents"

    # Observability 
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    # App
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

@lru_cache
def get_settins() -> Settings:
    return Settings()


settings = Settings()
