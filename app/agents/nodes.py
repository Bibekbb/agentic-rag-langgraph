import json
import re
from langchain_core.output_parsers import JsonOutputParser
from app.agents.state import AgentState
from app.llm.prompts import (
    ANALYZER_PROMPT,
    GRADER_PROMPT,
    REWRITE_PROMPT,
    GENERATE_PROMPT,
)
from app.llm.router import get_llm_for
from app.rag.retriever import get_retriever
from app.rag.citations import build_citations
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)
parser = JsonOutputParser()

def _safe_json(text: str):
    try:
        return parser.parse(text)
    except Exception as e:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except Exception:
                pass
    return {}

# Node 1: Analyze query
def analyze_query(state: AgentState):
    llm = get_llm_for("analyze")
    chain = ANALYZER_PROMPT | llm
    resp = chain.invoke({"query": state['query']})
    data = _safe_json(resp.content)

    return {
        "route": data.get("route", "retrieve"),
        "sub_queries": data.get("sub_queries", [state["query"]]) or [state["query"]],
        "retry_count": state.get("retry_count", 0),
    }

# Node 2: Retrieve
def retrieve_docs(state: AgentState):
    retriever = get_retriever()
    queries = state.get("sub_queries") or [state['query']]
    docs = retriever.multi_query_retrieve(
        queries,
        top_k_retrieve=settings.TOP_K_RETRIEVE,
        top_k_rerank=settings.TOP_K_RERANK,
        filters=state.get("filters"),
    )
    logger.info(f"Retrieved {len(docs)} docs for queries={queries}")
    return {"reranked_docs": docs, "retrieved_docs": docs}

# Node 3: Grade
def grade_context(state: AgentState):
    docs = state.get("reranked_docs") or []
    if not docs:
        return {"confidence": 0.0, "retry_count": state.get("retry_count", 0) + 1}

    context = "\n\n".join(f"[{i}] {d['text']}" for i, d in enumerate(docs, 1))
    llm = get_llm_for("grade")
    chain = GRADER_PROMPT | llm
    resp = chain.invoke({"query": state["query"], "context": context})
    data = _safe_json(resp.content)

    return {
        "confidence": float(data.get("confidence", 0.5)),
        "retry_count": state.get("retry_count", 0) + 1,
    }

# Node 4: Rewrite
def rewrite_query(state: AgentState):
    llm = get_llm_for("rewrite")
    chain = REWRITE_PROMPT | llm
    resp = chain.invoke({"query": state["query"]})
    new_q = resp.content.strip().strip('"').strip("'")
    logger.info(f"Rewrite query: '{state['query']}' -> '{new_q}'")
    return {"sub_queries": [new_q], "query": new_q}

# Node 5: Generate
def generate_answer(state: AgentState):
    docs = state.get("reranked_docs") or []
    if not docs:
        return { 
            "answer": "I don't have enough information to answer that.",
            "citations": [],
            "messages": [{"role": "assistabt", "content": "I don't have enough information to answer that."}],
        }
    context = "\n\n".join(
        f"[{i}] (source: {d['metadata'].get('source', 'unknown')}\n{d['text']})"
        for i, d in enumerate(docs, 1)
    )
    llm = get_llm_for("generate")
    chain = GENERATE_PROMPT | llm
    resp = chain.invoke({"query": state["query"], "context": context})
    answer = resp.content.strip()
    citations = build_citations(docs)

    return {
        "answer": answer,
        "citations": citations,
        "messages": [{"role": "assistant", "content": answer}],
    }

# Router edge
def should_retry(state: AgentState):
    if (
        state.get("confidence", 0.0) < settings.CONFIDENCE_THRESHOLD
        and state.get("retry_count", 0) < settings.MAX_RETRIES
    ):
        return "rewrite"
    return "generate"