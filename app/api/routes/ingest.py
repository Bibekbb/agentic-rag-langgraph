from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.schemas.ingest import IngestResponse
from app.rag.loader import load_document
from app.rag.chunker import recursive_chunk
from app.rag.embedder import get_embedder
from app.rag.vectorstore import VectorStore
from app.core.exceptions import IngestionError
from app.core.logging import get_logger

router = APIRouter(prefix="/ingest", tags=["ingest"])
logger = get_logger(__name__)

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/file", response_model=IngestResponse)
async def ingest_file(
    file: UploadFile = File(...),
    source: str | None = Form(None),
):
    try:
        dest = UPLOAD_DIR / file.filename
        dest.write_bytes(await file.read())

        text = load_document(dest)
        if not text.strip():
            raise IngestionError("Empty document")

        chunks = recursive_chunk(
            text, 
            metadata = {"source": source or file.filename, "type": file.content_type or "unknown"},
        )

        embedder = get_embedder()
        store = VectorStore(dim = embedder.dim)

        start = store.count()
        vectors = embedder.embed([c["text"] for c in chunks]).tolist()
        ids = list(range(start, start + len(chunks)))
        payloads = [{"text": c["text"], **c["metadata"]} for c in chunks]
        store.upsert(ids, vectors, payloads)

        logger.info(f"Ingested {len(chunks)} chunks from {file.filename}")
        return IngestResponse(
            status = "success",
            chunks_indexed=len(chunks),
            collection=store.collection,
        )
    except IngestionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Ingest failed")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/path", response_model=IngestResponse)
async def ingest_path(path: str, source: str | None = None):
    try: 
        text = load_document(path)
        chunks = recursive_chunk(
            text, metadata={"source": source or Path(path).name}
        )

        embedder = get_embedder()
        store = VectorStore(dim=embedder.dim)
        start = store.count()
        vectors = embedder.embed([c["text"] for  c in chunks]).tolist()
        ids = list(range(start, start + len(chunks)))
        payloads = [{"text": c["text"], **c["metadata"]} for c in chunks]
        store.upsert(ids, vectors, payloads)

        return IngestResponse(
            status = "success",
            chunks_indexed=len(chunks),
            collection=store.collection,
        )
    except IngestionError as e:
        raise HTTPException(status_code=400, detail=str(e))