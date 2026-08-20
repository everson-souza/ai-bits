"""
MCP server with a simple vector knowledge base.

Exposes two tools:
    - search_docs(query, top_k): semantic search over the knowledge base
    - add_doc(id, text, source): index a new document

The "vector search" here uses TF-IDF + cosine similarity in pure Python,
(Chroma, Qdrant, pgvector, Pinecone...). The MCP interface stays the same.
In production, replace `_vectorize` and `_search` with your embeddings model + vector DB
(Chroma, Qdrant, pgvector, Pinecone...). The MCP interface stays the same.
(Chroma, Qdrant, pgvector, Pinecone...). The MCP interface stays the same.

Run directly (the client typically launches this process via stdio):
    python vector_server.py
"""

import math
import re
from collections import Counter

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("base-de-conhecimento")



# ---------------------------------------------------------------------------
# Toy "vector DB" (replace with Chroma/Qdrant/pgvector etc.)
# ---------------------------------------------------------------------------

_DOCUMENTS: dict[str, dict] = {}


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def _vectorize(text: str) -> Counter:
    # In production: return embeddings_model.encode(text)
    return Counter(_tokenize(text))


def _cosine(a: Counter, b: Counter) -> float:
    common = set(a) & set(b)
    num = sum(a[t] * b[t] for t in common)
    den = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(
        sum(v * v for v in b.values())
    )
    return num / den if den else 0.0


def _search(query: str, top_k: int) -> list[tuple[float, dict]]:
    qvec = _vectorize(query)
    scored = [(_cosine(qvec, doc["vector"]), doc) for doc in _DOCUMENTS.values()]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [(score, doc) for score, doc in scored[:top_k] if score > 0]


def _index(doc_id: str, text: str, source: str) -> None:
    _DOCUMENTS[doc_id] = {
        "id": doc_id,
        "text": text,
        "source": source,
        "vector": _vectorize(text),
    }


# Alguns documentos de exemplo para a demonstração funcionar de imediato
_index(
    "refund-policy",
    "Our refund policy allows returns up to 30 days after purchase with the product in its original condition. Refunds are processed to the same payment method within 7 business days.",
    "internal-manual/policies.md",
)
_index(
    "support-hours",
    "Customer support is available Monday to Friday, 9:00 to 18:00 (local time), via the website chat or support@example.com.",
    "internal-manual/support.md",
)
_index(
    "pricing-plans",
    "We offer three plans: Basic ($49/month, 1 user), Pro ($149/month, up to 5 users) and Enterprise (pricing on request, unlimited users and dedicated support).",
    "internal-manual/plans.md",
)

# ---------------------------------------------------------------------------
# Ferramentas MCP
# ---------------------------------------------------------------------------


@mcp.tool()
def search_docs(query: str, top_k: int = 3) -> str:
    """Search for relevant passages in the internal knowledge base.

    Use this tool whenever the user's question depends on company-specific
    information (policies, pricing, opening hours, documentation).

    Args:
        query: Natural language query or search terms.
        top_k: Maximum number of passages to return (default 3).
    """
    results = _search(query, top_k)
    if not results:
        return "No relevant documents found."
    return "\n\n".join(
        f"[source: {doc['source']} | id: {doc['id']} | score: {score:.2f}]\n"
        f"{doc['text']}"
        for score, doc in results
    )


@mcp.tool()
def add_doc(doc_id: str, text: str, source: str = "manual") -> str:
    """Index a new document in the knowledge base.

    Args:
        doc_id: Unique identifier for the document.
        text: Document content.
        source: Document source (path, URL, etc.).
    """
    _index(doc_id, text, source)
    return f"Document '{doc_id}' indexed successfully."


if __name__ == "__main__":
    # Transporte stdio: o cliente MCP sobe este processo e conversa
    # pelos pipes de entrada/saída. Para servir via HTTP remoto, use:
    # mcp.run(transport="streamable-http")
    mcp.run(transport="stdio")