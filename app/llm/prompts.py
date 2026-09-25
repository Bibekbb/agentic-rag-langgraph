from langchain_core.prompts import ChatPromptTemplate


ANALYZER_PROMPT = ChatPromptTemplate.from_template(
    """You are a query analyzer for a RAG system.
Given a user question, decide:
- route: "retrieve" (needs internal docs) | "direct" (general knowledge)
- sub_queries: split complex questions into 1-4 focused sub-queries
- reasoning: brief explanation

Return ONLY valid JSON:
{{"route": "...", "sub_queries": ["..."], "reasoning": "..."}}

Question: {query}
"""
)


GRADER_PROMPT = ChatPromptTemplate.from_template(
    """You are a strict relevance grader.
Given a question and retrieved context, decide if the context is sufficient.
Return ONLY valid JSON:
{{"sufficient": true|false, "confidence": 0.0-1.0, "missing": "..."}}

Question: {query}

Context:
{context}
"""
)


REWRITE_PROMPT = ChatPromptTemplate.from_template(
    """Rewrite the following question to be more specific and retrievable.
Add relevant keywords. Return ONLY the rewritten question, no explanation.

Original: {query}
Rewritten:"""
)


GENERATE_PROMPT = ChatPromptTemplate.from_template(
    """You are a helpful AI assistant. Answer the question using ONLY the provided context.
Cite sources with [1], [2] notation where relevant.
If the context does not contain the answer, say "I don't have enough information to answer that."

Context:
{context}

Question: {query}

Answer:"""
)