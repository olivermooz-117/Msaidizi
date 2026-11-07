import re
import secrets

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from backend.app import db
from backend.app.models import Business

auth_bp = Blueprint("auth", __name__)


def clean_email(value):
    return value.strip().lower() if isinstance(value, str) else ""


def validate_password(value):
    if not isinstance(value, str):
        return "Password is required."

    if len(value) < 8:
        return "Password must contain at least 8 characters."

    if len(value) > 128:
        return "Password is too long."

    if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
        return "Password must include at least one letter and one number."

    return ""


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "")
    email = clean_email(data.get("email"))
    password = data.get("password", "")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Business name is required."}), 400

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify({"error": "A valid email address is required."}), 400

    password_error = validate_password(password)
    if password_error:
        return jsonify({"error": password_error}), 400

    business = Business(
        name=name.strip(),
        owner_email=email,
        password_hash=generate_password_hash(password),
        widget_key=secrets.token_urlsafe(32),
    )

    db.session.add(business)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(
            {"error": "An account with this email already exists."}
        ), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Database unavailable. Please try again later."}), 503

    token = create_access_token(identity=business.id)

    return jsonify(
        {
            "message": "Business account created.",
            "access_token": token,
            "business": {
                "id": business.id,
                "name": business.name,
                "email": business.owner_email,
                "widget_key": business.widget_key,
            },
        }
    ), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    email = clean_email(data.get("email"))
    password = data.get("password", "")

    if not email or not isinstance(password, str):
        return jsonify({"error": "Email and password are required."}), 400

    business = db.session.query(Business).filter_by(
        owner_email=email
    ).first()

    if not business or not check_password_hash(
        business.password_hash, password
    ):
        return jsonify({"error": "Invalid email or password."}), 401

    token = create_access_token(identity=business.id)

    return jsonify(
        {
            "access_token": token,
            "business": {
                "id": business.id,
                "name": business.name,
                "email": business.owner_email,
                "widget_key": business.widget_key,
            },
        }
    ), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    business_id = get_jwt_identity()

    business = db.session.get(Business, business_id)

    if not business:
        return jsonify({"error": "Business account not found."}), 404

    return jsonify(
        {
            "business": {
                "id": business.id,
                "name": business.name,
                "email": business.owner_email,
            }
        }
    ), 200
