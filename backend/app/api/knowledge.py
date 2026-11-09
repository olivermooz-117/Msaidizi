from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import select

from backend.app.extensions import db
from backend.app.models import Business, Chunk, Document

knowledge_bp = Blueprint("knowledge", __name__)

MAX_DOCUMENT_CHARS = 1_500_000
CHUNK_SIZE = 900


def split_text_into_chunks(text, max_chars=CHUNK_SIZE):
    paragraphs = [paragraph.strip() for paragraph in text.splitlines() if paragraph.strip()]
    chunks = []
    position = 0

    for paragraph in paragraphs:
        words = paragraph.split()
        current_words = []

        for word in words:
            candidate = " ".join(current_words + [word])
            if len(candidate) > max_chars and current_words:
                chunks.append((position, " ".join(current_words)))
                position += 1
                current_words = [word]
            else:
                current_words.append(word)

        if current_words:
            chunks.append((position, " ".join(current_words)))
            position += 1

    return chunks


def get_current_business():
    business_id = get_jwt_identity()
    if business_id is None:
        return None
    return db.session.get(Business, str(business_id))


@knowledge_bp.post("/documents")
@jwt_required()
def create_document():
    business = get_current_business()
    if not business:
        return jsonify({"error": "Business account not found."}), 404

    data = request.get_json(silent=True) or {}
    title = data.get("title", "")
    content = data.get("content", "")
    source_type = data.get("source_type", "paste")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Document title is required."}), 400
    if not isinstance(content, str) or not content.strip():
        return jsonify({"error": "Document content is required."}), 400
    if len(content) > MAX_DOCUMENT_CHARS:
        return jsonify({"error": "Document content is too large."}), 413
    if source_type not in {"paste", "pdf", "csv"}:
        return jsonify({"error": "Unsupported source type."}), 400

    document = Document(business_id=business.id, title=title.strip(), source_type=source_type)
    db.session.add(document)
    db.session.flush()

    chunks = split_text_into_chunks(content)
    if not chunks:
        db.session.rollback()
        return jsonify({"error": "No readable text was provided."}), 400

    db.session.add_all([
        Chunk(document_id=document.id, text=chunk_text, position=position)
        for position, chunk_text in chunks
    ])
    db.session.commit()

    return jsonify(
        {
            "message": "Document added to the knowledge base.",
            "document": {
                "id": document.id,
                "title": document.title,
                "source_type": document.source_type,
                "chunk_count": len(chunks),
            },
        }
    ), 201


@knowledge_bp.get("/documents")
@jwt_required()
def list_documents():
    business = get_current_business()
    if not business:
        return jsonify({"error": "Business account not found."}), 404

    documents = db.session.scalars(
        select(Document)
        .where(Document.business_id == business.id)
        .order_by(Document.created_at.desc())
    ).all()

    return jsonify({
        "documents": [
            {
                "id": document.id,
                "title": document.title,
                "source_type": document.source_type,
                "created_at": document.created_at.isoformat() if document.created_at else None,
                "chunk_count": len(document.chunks),
            }
            for document in documents
        ]
    }), 200


@knowledge_bp.delete("/documents/<document_id>")
@jwt_required()
def delete_document(document_id):
    business = get_current_business()
    if not business:
        return jsonify({"error": "Business account not found."}), 404

    document = db.session.scalar(
        select(Document).where(Document.id == document_id, Document.business_id == business.id)
    )
    if not document:
        return jsonify({"error": "Document not found."}), 404

    db.session.delete(document)
    db.session.commit()

    return jsonify({"message": "Document deleted."}), 200


@knowledge_bp.post("/search")
@jwt_required()
def search_knowledge():
    business = get_current_business()
    if not business:
        return jsonify({"error": "Business account not found."}), 404

    data = request.get_json(silent=True) or {}
    query = data.get("query", "")
    if not isinstance(query, str) or len(query.strip()) < 2:
        return jsonify({"error": "Search query must contain at least 2 characters."}), 400

    query = query.strip()[:200]
    matches = db.session.execute(
        select(Chunk, Document)
        .join(Document, Chunk.document_id == Document.id)
        .where(Document.business_id == business.id, Chunk.text.ilike(f"%{query}%"))
        .order_by(Document.created_at.desc())
        .limit(10)
    ).all()

    return jsonify({
        "query": query,
        "results": [
            {
                "document_id": document.id,
                "document_title": document.title,
                "chunk_id": chunk.id,
                "position": chunk.position,
                "text": chunk.text,
            }
            for chunk, document in matches
        ],
    }), 200
