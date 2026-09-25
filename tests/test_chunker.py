from app.rag.chunker import recursive_chunk, count_tokens


def test_recursive_chunk_basic():
    text = "Hello world. " * 500
    chunks = recursive_chunk(text, metadata={"source": "test"})
    assert len(chunks) > 0
    assert all("text" in c for c in chunks)
    assert all(c["metadata"]["source"] == "test" for c in chunks)


def test_count_tokens():
    assert count_tokens("hello") > 0