from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.config import settings
from app.core.logging import setup_logging, get_logger
from app.rag.embedder import get_embedder
from app.rag.reranker import get_reranker

setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting Agentic RAG (env = {settings.APP_ENV})")
    try:
        get_embedder()
        get_reranker()
        logger.info("Models warmed up.")
    except Exception as e:
        logger.warning(f"Warmup skipped: {e}")
    yield
    logger.info("Shutting down.")

app = FastAPI(
    title = "Agentic RAG API",
    version="1.0.0",
    description = "Production-grade Agentic RAG with LangGraph, Qdrant, and reranking.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def root():
    return {"service": "agentic-rag", "docs": "/docs", "version": "1.0.0"}
