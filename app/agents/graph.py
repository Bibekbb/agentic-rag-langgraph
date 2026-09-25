from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.state import AgentState
from app.agents import nodes
from app.core.logging import get_logger

logger = get_logger(__name__)


def build_graph(with_checkpointer: bool = True):
    g = StateGraph(AgentState)

    # --- Register all nodes (name, function) ---
    g.add_node("analyze", nodes.analyze_query)
    g.add_node("retrieve", nodes.retrieve_docs)      # NOTE: "retrieve" (verb)
    g.add_node("grade", nodes.grade_context)
    g.add_node("rewrite", nodes.rewrite_query)
    g.add_node("generate", nodes.generate_answer)

    # --- Entry ---
    g.set_entry_point("analyze")

    # --- Edges (MUST match node names above) ---
    g.add_edge("analyze", "retrieve")
    g.add_edge("retrieve", "grade")

    g.add_conditional_edges(
        "grade",
        nodes.should_retry,
        {"rewrite": "rewrite", "generate": "generate"},
    )

    g.add_edge("rewrite", "retrieve")   # loop back to retrieve
    g.add_edge("generate", END)

    checkpointer = MemorySaver() if with_checkpointer else None
    return g.compile(checkpointer=checkpointer)


_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph
