from pathlib import Path
from app.rag.loader import load_document
from app.rag.chunker import recursive_chunk
from app.rag.embedder import get_embedder
from app.rag.vectorstore import VectorStore
from app.core.logging import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

DOCS_DIR = Path("data/docs")
SUPPORTED = {".pdf", ".txt", ".md"}


def main() -> None:
    files = [f for f in DOCS_DIR.rglob("*") if f.suffix.lower() in SUPPORTED]
    if not files:
        logger.warning(f"No documents in {DOCS_DIR}")
        return

    embedder = get_embedder()
    store = VectorStore(dim=embedder.dim)

    total = 0
    for path in files:
        try:
            text = load_document(path)
            chunks = recursive_chunk(text, metadata={"source": path.name})
            start = store.count()
            vectors = embedder.embed([c["text"] for c in chunks]).tolist()
            ids = list(range(start, start + len(chunks)))
            payloads = [{"text": c["text"], **c["metadata"]} for c in chunks]
            store.upsert(ids, vectors, payloads)
            total += len(chunks)
            logger.info(f"{path.name}: {len(chunks)} chunks")
        except Exception as e:
            logger.error(f"{path.name} failed: {e}")

    logger.info(f"Done. Total chunks: {total} | Collection size: {store.count()}")


if __name__ == "__main__":
    main()