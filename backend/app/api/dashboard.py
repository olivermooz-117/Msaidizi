from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from backend.app.extensions import db
from backend.app.models import Conversation, Handoff, Message

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/stats")
@jwt_required()
def stats():
    business_id = get_jwt_identity()

    total = Conversation.query.filter_by(business_id=business_id).count()
    escalated = Conversation.query.filter_by(business_id=business_id, status="escalated").count()
    open_ = Conversation.query.filter_by(business_id=business_id, status="open").count()
    resolved = Conversation.query.filter_by(business_id=business_id, status="resolved").count()

    pending_handoffs = Handoff.query.join(Conversation).filter(
        Conversation.business_id == business_id,
        Handoff.status == "pending",
    ).count()

    return jsonify({
        "total_conversations": total,
        "open": open_,
        "escalated": escalated,
        "resolved": resolved,
        "pending_handoffs": pending_handoffs,
    })
