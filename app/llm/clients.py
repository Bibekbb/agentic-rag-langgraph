from functools import lru_cache
from langchain_openai import ChatOpenAI
from app.config import settings

try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


@lru_cache
def get_default_llm(temperature: float = 0.0) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.DEFAULT_LLM,
        temperature=temperature,
        api_key=settings.OPENAI_API_KEY,
        timeout=60,
        max_retries=2,
    )


@lru_cache
def get_fast_llm(temperature: float = 0.0):
    if GROQ_AVAILABLE and settings.GROQ_API_KEY:
        return ChatGroq(
            model=settings.FAST_LLM,
            temperature=temperature,
            api_key=settings.GROQ_API_KEY,
            timeout=30,
        )
    return get_default_llm(temperature)
