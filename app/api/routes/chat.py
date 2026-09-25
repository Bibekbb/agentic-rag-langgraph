import json 
import time 
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.dependencies import graph_dep, session_dep, cache_dep
from app.core.logging import get_logger
from app.observability.langfuse_client import trace

router = APIRouter(prefix="/chat", tags=['chat'])
logger = get_logger(__name__)

def _initial_state(req: ChatRequest):
    return {
        "query": req.query,
        "messages": [],
        "route": "retrieve",
        "sub_queries": [req.query],
        "retrieved_docs": [],
        "reranked_docs": [],
        "answer": "",
        "citations": [],
        "confidence": 0.0,
        "retry_count": 0,
        "filters": req.filters,
    }

@router.post("", response_model=ChatResponse)
async def chat(
    req:ChatRequest,
    graph = Depends(graph_dep),
    memory=Depends(session_dep),
    cache=Depends(cache_dep),
):
    start = time.time()

    cached = cache.get(req.query)
    if cached and not req.filters:
        logger.info("Cache HIT")
        memory.append(req.session_id, "user", req.query)
        memory.append(req.session_id, "assistant", cached["answer"])
        cached["latency_ms"] = (time.time() - start)*1000
        return ChatResponse(**cached)

    with trace("chat_request", {"query": req.query, "session": req.session_id}):
        config = {"configurable": {"thread_id": req.session_id}}
        state = _initial_state(req)
        result = graph.invoke(state, config=config)

    response = {
        "answer": result["answer"],
        "citations": result.get("citations", []),
        "confidence": result.get("confidence", 0.0),
        "route": result.get("route", "retrieve"),
        "sub_queries": result.get("sub_queries", []),
    }

    if not req.filters:
        cache.set(req.query, response)

    memory.append(req.session_id, "user", req.query)
    memory.append(req.session_id, "assistant", response["answer"])

    response["latency_ms"] = (time.time()- start) * 1000
    return ChatResponse(**response)

@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    graph=Depends(graph_dep),
    memory=Depends(session_dep),
):
    async def event_gen():
        start = time.time()
        config = {"configurable": {"thread_id": req.session_id}}
        state = _initial_state(req)

        try:
            async for event in graph.astream(state, config=config):
                for node, output in event.items():
                    if node == "analyze":
                        yield _sse({"type": "step", "node": "analyze",
                                    "sub_queries": output.get("sub_queries", [])})
                    elif node == "retrieve":
                        yield _sse({"type": "step", "node": "retrieve",
                                    "docs": len(output.get("reranked_docs", []))})
                    elif node == "grade":
                        yield _sse({"type": "step", "node": "grade",
                                    "confidence": output.get("confidence", 0.0)})
                    elif node == "rewrite":
                        yield _sse({"type": "step", "node": "rewrite"})
                    elif node == "generate":
                        yield _sse({"type": "answer",
                                    "data": output.get("answer", ""),
                                    "citations": output.get("citations", [])})

            yield _sse({"type": "done", "latency_ms": (time.time() - start) * 1000})
        except Exception as e:
            logger.exception("Stream failed")
            yield _sse({"type": "error", "message": str(e)})

    memory.append(req.session_id, "user", req.query)
    return StreamingResponse(event_gen(), media_type="text/event-stream")


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"
