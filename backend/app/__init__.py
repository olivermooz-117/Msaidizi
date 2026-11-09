from flask import Flask
from flask_cors import CORS

from backend.app.config import settings
from backend.app.extensions import db, jwt, migrate


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = settings.JWT_ACCESS_TOKEN_EXPIRES
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
    }

    db.init_app(app)
    jwt.init_app(app)

    # IMPORTANT: migrations live in backend/migrations (two levels up from app)
    migrate.init_app(app, db, directory="backend/migrations")

    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
    CORS(app, origins=origins, supports_credentials=True)

    # Register blueprints
    from backend.app.api.auth import auth_bp
    from backend.app.api.documents import documents_bp
    from backend.app.api.chat import chat_bp
    from backend.app.api.dashboard import dashboard_bp
    from backend.app.api.knowledge import knowledge_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(documents_bp, url_prefix="/api/documents")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(knowledge_bp, url_prefix="/api/knowledge")

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "msaidizi"}

    return app
