import os
from datetime import timedelta

from flask_jwt_extended import create_access_token

from backend.app import create_app, db


os.environ.setdefault("TEST_DATABASE_URL", "sqlite:///:memory:")


def _make_app():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        db.create_all()
    return app


def test_register_success_returns_token():
    app = _make_app()
    with app.test_client() as client:
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Nairobi Threads",
                "email": "owner@company.com",
                "password": "secret123",
            },
        )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["access_token"]
    assert payload["business"]["email"] == "owner@company.com"


def test_register_missing_field():
    app = _make_app()
    with app.test_client() as client:
        response = client.post(
            "/api/auth/register",
            json={"email": "owner@company.com", "password": "secret123"},
        )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Business name is required."


def test_register_invalid_email():
    app = _make_app()
    with app.test_client() as client:
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Nairobi Threads",
                "email": "not-an-email",
                "password": "secret123",
            },
        )

    assert response.status_code == 400
    assert response.get_json()["error"] == "A valid email address is required."


def test_register_duplicate_email():
    app = _make_app()
    with app.test_client() as client:
        client.post(
            "/api/auth/register",
            json={
                "name": "Nairobi Threads",
                "email": "owner@company.com",
                "password": "secret123",
            },
        )
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Other Business",
                "email": "owner@company.com",
                "password": "secret123",
            },
        )

    assert response.status_code == 409
    assert "already exists" in response.get_json()["error"]


def test_register_weak_password():
    app = _make_app()
    with app.test_client() as client:
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Nairobi Threads",
                "email": "owner@company.com",
                "password": "short",
            },
        )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Password must contain at least 8 characters."


def test_login_success_returns_token():
    app = _make_app()
    with app.app_context():
        from backend.app.models import Business
        from werkzeug.security import generate_password_hash

        business = Business(
            name="Nairobi Threads",
            owner_email="owner@company.com",
            password_hash=generate_password_hash("secret123"),
            widget_key="widget-key",
        )
        db.session.add(business)
        db.session.commit()

    with app.test_client() as client:
        response = client.post(
            "/api/auth/login",
            json={"email": "owner@company.com", "password": "secret123"},
        )

    assert response.status_code == 200
    assert response.get_json()["access_token"]


def test_login_wrong_password():
    app = _make_app()
    with app.app_context():
        from backend.app.models import Business
        from werkzeug.security import generate_password_hash

        business = Business(
            name="Nairobi Threads",
            owner_email="owner@company.com",
            password_hash=generate_password_hash("secret123"),
            widget_key="widget-key",
        )
        db.session.add(business)
        db.session.commit()

    with app.test_client() as client:
        response = client.post(
            "/api/auth/login",
            json={"email": "owner@company.com", "password": "wrong-pass"},
        )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid email or password."


def test_unknown_email():
    app = _make_app()
    with app.test_client() as client:
        response = client.post(
            "/api/auth/login",
            json={"email": "missing@company.com", "password": "secret123"},
        )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid email or password."


def test_invalid_jwt_is_rejected():
    app = _make_app()
    with app.test_client() as client:
        response = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid-token"})

    assert response.status_code == 401


def test_expired_jwt_is_rejected():
    app = _make_app()
    with app.app_context():
        token = create_access_token(identity="123", expires_delta=timedelta(seconds=-5))

    with app.test_client() as client:
        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_protected_route_requires_auth():
    app = _make_app()
    with app.test_client() as client:
        response = client.get("/api/knowledge/documents")

    assert response.status_code == 401


def test_authenticated_document_access_is_scoped_to_business():
    app = _make_app()
    with app.app_context():
        from backend.app.models import Business, Document
        from werkzeug.security import generate_password_hash

        business_one = Business(
            name="One Business",
            owner_email="one@company.com",
            password_hash=generate_password_hash("secret123"),
            widget_key="widget-one",
        )
        business_two = Business(
            name="Two Business",
            owner_email="two@company.com",
            password_hash=generate_password_hash("secret123"),
            widget_key="widget-two",
        )
        db.session.add_all([business_one, business_two])
        db.session.commit()
        db.session.add(Document(business_id=business_one.id, title="Private doc", source_type="paste"))
        db.session.add(Document(business_id=business_two.id, title="Owned doc", source_type="paste"))
        db.session.commit()

        token = create_access_token(identity=str(business_two.id))

    with app.test_client() as client:
        response = client.get(
            "/api/knowledge/documents",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload["documents"]) == 1
    assert payload["documents"][0]["title"] == "Owned doc"


def test_me_returns_authenticated_business():
    app = _make_app()
    with app.app_context():
        from backend.app.models import Business
        from werkzeug.security import generate_password_hash

        business = Business(
            name="Business Profile",
            owner_email="profile@company.com",
            password_hash=generate_password_hash("secret123"),
            widget_key="widget-profile",
        )
        db.session.add(business)
        db.session.commit()
        token = create_access_token(identity=str(business.id))

    with app.test_client() as client:
        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["business"]["email"] == "profile@company.com"
