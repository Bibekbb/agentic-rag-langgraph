from functools import lru_cache
from app.rag.retriever import get_retriever, Retriever
from app.agents.graph import get_graph
from app.memory.session import get_session_memory, SessionMemory
from app.memory.semantic_cache import get_semantic_cache, SemanticCache


def retriever_dep() -> Retriever:
    return get_retriever()


def graph_dep():
    return get_graph()


def session_dep() -> SessionMemory:
    return get_session_memory()


def cache_dep() -> SemanticCache:
    return get_semantic_cache()
