from typing import Annotated, Any
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    query: str
    route: str
    sub_queries: list[str]
    retrieved_docs: list[dict[str, Any]]
    reranked_docs: list[dict[str, Any]]
    answer: str
    citations: list[dict[str, Any]]
    confidence: float 
    retry_count: int 
    filters: dict[str, Any] | None