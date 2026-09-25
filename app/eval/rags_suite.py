import json 
from pathlib import Path 
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness, 
    answer_relevancy,
    context_precision,
    context_recall,
)
from app.agents.graph import get_graph
from app.core.logging import get_logger

logger = get_logger(__name__)

def _run_agent(question: str):
    graph = get_graph()
    state = {
        "query": question,
        "message": [],
        "route": "retrieve",
        "sub_queries": [question],
        "retrieved_docs": [],
        "reranked_docs": [],
        "answer": "",
        "citations": [],
        "confidence": 0.0,
        "retry_count": 0,
        "filters": None,
    }
    result = graph.invoke(state)
    return {
        "answer": result["answer"],
        "contexts": [d["text"] for d in result.get("reranked_docs", [])],
    }

def run_eval(dataset_path: str):
    data = json.loads(Path(dataset_path).read_text())
    rows = []
    for item in data:
        out = _run_agent(item["question"])
        rows.append(
            {
                "question": item["question"],
                "answer": out["answer"],
                "contexts": out["contexts"],
                "ground_truth": item.get("ground_truth", ""),
            }
        )

    ds = Dataset.from_list(rows)
    result = evaluate(
        ds, 
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    )
    logger.info(f"RAGS: {result}")
    return dict(result)