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

    if settings.APP_ENV.lower() == "production":
        if settings.SECRET_KEY.startswith("development-only"):
            raise RuntimeError("Set a secure SECRET_KEY in production.")

        if settings.JWT_SECRET_KEY.startswith("development-only"):
            raise RuntimeError("Set a secure JWT_SECRET_KEY in production.")

    app.config.update(
        SECRET_KEY=settings.SECRET_KEY,
        JWT_SECRET_KEY=settings.JWT_SECRET_KEY,
        JWT_ACCESS_TOKEN_EXPIRES=settings.JWT_ACCESS_TOKEN_EXPIRES,
        SQLALCHEMY_DATABASE_URI=settings.DATABASE_URL,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={
            "pool_pre_ping": True,
            "pool_size": 5,
            "max_overflow": 10,
        },
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
    )

    db.init_app(app)
    jwt.init_app(app)

    # Import models so SQLAlchemy and Alembic can discover their tables.
    from backend.app import models  # noqa: F401

    migrate.init_app(app, db, directory="migrations")

    if not app.config.get("TESTING"):
        with app.app_context():
            try:
                db.create_all()
            except SQLAlchemyError:
                pass

    origins = [
        origin.strip()
        for origin in settings.CORS_ORIGINS.split(",")
        if origin.strip()
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
        return jsonify(
            {
                "status": "ok",
                "service": "msaidizi",
            }
        ), 200

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
