from sqlalchemy import text
from backend.app.extensions import db
from backend.app.models import Chunk, Document
from backend.app.llm import embed_query


def search_knowledge(business_id: str, query: str, top_k: int = 4) -> list[dict]:
    """Return top_k chunks with cosine similarity."""
    if not query.strip():
        return []

    query_emb = embed_query(query)

    # Use pgvector cosine distance
    sql = text("""
        SELECT c.id, c.text, c.position, d.title AS source_title,
               1 - (c.embedding <=> :emb) AS score
        FROM chunks c
        JOIN documents d ON d.id = c.document_id
        WHERE d.business_id = :business_id
          AND c.embedding IS NOT NULL
        ORDER BY c.embedding <=> :emb
        LIMIT :top_k
    """)

    rows = db.session.execute(
        sql,
        {
            "emb": str(query_emb),
            "business_id": business_id,
            "top_k": top_k,
        },
    ).fetchall()

    results = []
    for r in rows:
        results.append({
            "chunk_id": r.id,
            "text": r.text,
            "source_title": r.source_title,
            "score": float(r.score) if r.score is not None else 0.0,
        })
    return results
