from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import secrets

from backend.app.extensions import db
from backend.app.models import Business, Conversation, Message
from backend.app.services.agent import run_agent

chat_bp = Blueprint("chat", __name__)


@chat_bp.post("/widget")
def widget_chat():
    """Public endpoint used by the embeddable widget."""
    data = request.get_json() or {}
    widget_key = data.get("widget_key")
    session_id = data.get("session_id") or secrets.token_urlsafe(16)
    message = (data.get("message") or "").strip()

    if not widget_key or not message:
        return jsonify({"error": "widget_key and message required"}), 400

    business = Business.query.filter_by(widget_key=widget_key).first()
    if not business:
        return jsonify({"error": "Invalid widget key"}), 404

    conv = Conversation.query.filter_by(
        business_id=business.id,
        session_id=session_id,
    ).first()
    if not conv:
        conv = Conversation(
            business_id=business.id,
            session_id=session_id,
            language="mixed",
            status="open",
        )
        db.session.add(conv)
        db.session.commit()

    if conv.status == "escalated":
        return jsonify({
            "reply": "A human agent will reply shortly. / Mhudumu atakujibu hivi karibuni.",
            "session_id": session_id,
            "escalated": True,
        })

    result = run_agent(business.id, conv.id, message)
    return jsonify({
        "reply": result["reply"],
        "sources": result.get("sources") or [],
        "session_id": session_id,
        "escalated": result.get("escalated", False),
    })


@chat_bp.get("/conversations")
@jwt_required()
def list_conversations():
    business_id = get_jwt_identity()
    convs = Conversation.query.filter_by(business_id=business_id).order_by(Conversation.created_at.desc()).limit(50).all()
    return jsonify([
        {
            "id": c.id,
            "session_id": c.session_id,
            "status": c.status,
            "created_at": c.created_at.isoformat(),
            "message_count": len(c.messages),
        }
        for c in convs
    ])
