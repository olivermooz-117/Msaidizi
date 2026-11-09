from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.app.extensions import db
from backend.app.models import Document, Chunk
from backend.app.services.ingest import ingest_text, ingest_pdf

documents_bp = Blueprint("documents", __name__)


@documents_bp.get("")
@jwt_required()
def list_documents():
    business_id = get_jwt_identity()
    docs = Document.query.filter_by(business_id=business_id).order_by(Document.created_at.desc()).all()
    return jsonify([
        {
            "id": d.id,
            "title": d.title,
            "source_type": d.source_type,
            "created_at": d.created_at.isoformat(),
            "chunk_count": len(d.chunks),
        }
        for d in docs
    ])


@documents_bp.post("")
@jwt_required()
def upload_document():
    business_id = get_jwt_identity()
    title = (request.form.get("title") or request.json.get("title") if request.is_json else None) or "Untitled"

    if request.files.get("file"):
        f = request.files["file"]
        if f.filename.lower().endswith(".pdf"):
            doc = ingest_pdf(business_id, title or f.filename, f.read())
        else:
            text = f.read().decode("utf-8", errors="ignore")
            doc = ingest_text(business_id, title or f.filename, text, source_type="csv" if f.filename.lower().endswith(".csv") else "paste")
    else:
        data = request.get_json() or {}
        text = data.get("text") or ""
        if not text.strip():
            return jsonify({"error": "No text or file provided"}), 400
        doc = ingest_text(business_id, title, text, source_type="paste")

    return jsonify({
        "id": doc.id,
        "title": doc.title,
        "source_type": doc.source_type,
        "chunk_count": len(doc.chunks),
    }), 201


@documents_bp.delete("/<doc_id>")
@jwt_required()
def delete_document(doc_id):
    business_id = get_jwt_identity()
    doc = Document.query.filter_by(id=doc_id, business_id=business_id).first()
    if not doc:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(doc)
    db.session.commit()
    return jsonify({"ok": True})
