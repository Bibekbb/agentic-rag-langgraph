from typing import Any
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    session_id: str = Field(default="default", max_length=100)
    filters: dict[str, Any] | None = None
    stream: bool = False

class Citation(BaseModel):
    id: int
    source: str
    snippet: str 
    score: float | None = None

class ChatResponse(BaseModel):
    answer: str 
    citations: list[Citation]
    confidence: float 
    route: str
    sub_queries: list[str]
    latency_ms: float

