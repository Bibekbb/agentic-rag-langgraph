class RAGException(Exception):
    """Base exception."""

class IngestionError(RAGException):
    pass

class RetrievalError(RAGException):
    pass

class LLMError(RAGException):
    pass
