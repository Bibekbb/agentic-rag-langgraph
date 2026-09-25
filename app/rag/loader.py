from pathlib import Path
from pypdf import PdfReader
from app.core.exceptions import IngestionError
from app.core.logging import get_logger

logger = get_logger(__name__)

def load_document(path: str | Path):
    path = Path(path)
    if not path.exists():
        raise IngestionError(f"File not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _load_pdf(path)
    elif suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    raise IngestionError(f"Unsupported file type: {suffix}")

def _load_pdf(path: Path):
    try: 
        reader = PdfReader(str(path))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        raise IngestionError(f"PDF load failed:{e}") from e