from fastapi import APIRouter
from app.dependencies import retriever_dep, cache_dep

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    try:
        r = retriever_dep()
        count = r.store.count()
        return {"status": "ok", "indexed_docs": count}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}


@router.get("/ready")
def ready():
    return {"ready": True}
