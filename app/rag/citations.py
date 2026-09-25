def build_citations(docs: list[dict]):
    return [
        {
            "id": i,
            "source": d["metadata"].get("source", "unknown"),
            "snippet": d["text"][:240].strip(),
            "score": d.get("rerank_score") or d.get("score"),
        }
        for i, d in enumerate(docs, 1)
    ]