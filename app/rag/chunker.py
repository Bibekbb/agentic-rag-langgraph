from typing import Any
import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings

_enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str):
    return len(_enc.encode(text))

def recursive_chunk(text: str, metadata: dict[str, Any] | None = None,
                    size: int | None = None,
                    overlap: int | None = None):
    size = size or settings.CHUNK_SIZE
    overlap = overlap or settings.CHUNK_OVERLAP
    metadata = metadata or {}

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = size,
        chunk_overlap = overlap,
        separators= ["\n\n,", "\n", ". ", "! ", "? ", " ", ""],
        length_function=count_tokens
    )
    chunks = splitter.split_text(text)

    return [
        {
            "text": c.strip(),
            "metadata": {
                **metadata, 
                "chunk_id": i,
                "tokens": count_tokens(c),
                "strategy": "recursive",
            },
        }
        for i, c in enumerate(chunks)
        if c.strip()
    ]