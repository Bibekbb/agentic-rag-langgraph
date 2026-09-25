from pydantic import BaseModel

class Ingestrequest(BaseModel):
    source: str 
    metadata: dict | None = None

class IngestResponse(BaseModel):
    status: str
    chunks_indexed: int 
    collection: str