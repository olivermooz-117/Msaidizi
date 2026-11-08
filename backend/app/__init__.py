import os
from pathlib import Path

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

from backend.app.config import settings


db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def create_app() -> Flask:
    app = Flask(__name__)

    database_url = (
        os.getenv("TEST_DATABASE_URL")
        if os.getenv("TEST_DATABASE_URL")
        else settings.DATABASE_URL
    )

    engine_options = {"pool_pre_ping": True}
    if not database_url.startswith("sqlite"):
        engine_options.update({"pool_size": 5, "max_overflow": 10})

    app.config.update(
        SECRET_KEY=settings.SECRET_KEY,
        JWT_SECRET_KEY=settings.JWT_SECRET_KEY,
        JWT_ACCESS_TOKEN_EXPIRES=settings.JWT_ACCESS_TOKEN_EXPIRES,
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS=engine_options,
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
    )

    if app.config.get("TESTING") or os.getenv("PYTEST_CURRENT_TEST"):
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
            "TEST_DATABASE_URL", "sqlite:///:memory:"
        )
        if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
            app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

    db.init_app(app)
    jwt.init_app(app)

    @jwt.unauthorized_loader
    def unauthorized_callback(_reason):
        return jsonify({"error": "Authentication required."}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(_callback):
        return jsonify({"error": "Invalid or expired token."}), 401

    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, _jwt_payload):
        return jsonify({"error": "Token has expired."}), 401

    from backend.app import models  # noqa: F401

    migration_dir = str(Path(__file__).resolve().parent / "migrations")
    migrate.init_app(app, db, directory=migration_dir)

    origins = [
        origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()
    ]
    CORS(
        app,
        resources={r"/api/*": {"origins": origins}},
        supports_credentials=False,
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "Accept"],
    )

    from backend.app.api.auth import auth_bp
    from backend.app.api.knowledge import knowledge_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(knowledge_bp, url_prefix="/api/knowledge")

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "msaidizi"}), 200

    @app.errorhandler(413)
    def request_too_large(_error):
        return jsonify({"error": "Request body is too large."}), 413

    @app.errorhandler(SQLAlchemyError)
    def database_error(_error):
        return jsonify({"error": "Database unavailable. Please try again later."}), 503

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Resource not found."}), 404

    return app
