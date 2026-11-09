from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

from backend.app.extensions import db
from backend.app.models import Business

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip()

    if not email or not password or len(password) < 6:
        return jsonify({"error": "Valid email and password (min 6 chars) required"}), 400
    if Business.query.filter_by(owner_email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    business = Business(
        name=name or "My Business",
        owner_email=email,
        password_hash=generate_password_hash(password),
        widget_key=secrets.token_urlsafe(24),
    )
    db.session.add(business)
    db.session.commit()

    token = create_access_token(identity=business.id)
    return jsonify({
        "access_token": token,
        "business": {
            "id": business.id,
            "name": business.name,
            "email": business.owner_email,
            "widget_key": business.widget_key,
        },
    }), 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    business = Business.query.filter_by(owner_email=email).first()
    if not business or not check_password_hash(business.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=business.id)
    return jsonify({
        "access_token": token,
        "business": {
            "id": business.id,
            "name": business.name,
            "email": business.owner_email,
            "widget_key": business.widget_key,
        },
    })


@auth_bp.get("/me")
@jwt_required()
def me():
    business_id = get_jwt_identity()
    business = db.session.get(Business, business_id)
    if not business:
        return jsonify({"error": "Business not found"}), 404
    return jsonify({
        "id": business.id,
        "name": business.name,
        "email": business.owner_email,
        "widget_key": business.widget_key,
    })
