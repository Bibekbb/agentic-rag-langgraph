from app.llm.clients import get_default_llm

ROUTING_TABLE = {
    "analyze": "default",
    "rewrite": "default",
    "grade": "default",
    "generate": "default",
}


def get_llm_for(task: str):
    # Simple router — always OpenAI (bypass Groq for stability)
    return get_default_llm()
