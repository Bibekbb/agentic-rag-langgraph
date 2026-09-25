from langfuse import Langfuse
from app.config import settings

client = Langfuse(
    public_key=settings.LANGFUSE_PUBLIC_KEY,
    secret_key=settings.LANGFUSE_SECRET_KEY,
    host=settings.LANGFUSE_HOST,
)

trace = client.trace(name="test-trace", metadata={"env": "dev"})
trace.generation(
    name="test-gen",
    model="gpt-4o-mini",
    input="Hello",
    output="Hi there!",
)
client.flush()
print("✅ Trace sent. Check Langfuse dashboard.")