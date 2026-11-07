from unittest.mock import MagicMock, patch

from sqlalchemy.exc import SQLAlchemyError

from backend.app import create_app


def test_register_success_returns_token():
    app = create_app()
    app.config.update(TESTING=True)

    with app.test_client() as client:
        with (
            patch("backend.app.api.auth.db.session.add") as add_mock,
            patch("backend.app.api.auth.db.session.commit") as commit_mock,
            patch("backend.app.api.auth.generate_password_hash", return_value="hashed-password"),
            patch("backend.app.api.auth.secrets.token_urlsafe", return_value="widget-key"),
        ):
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
    add_mock.assert_called_once()
    commit_mock.assert_called_once()


def test_register_missing_field():
    app = create_app()
    app.config.update(TESTING=True)

    with app.test_client() as client:
        response = client.post(
            "/api/auth/register",
            json={"email": "owner@company.com", "password": "secret123"},
        )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Business name is required."


def test_register_invalid_email():
    app = create_app()
    app.config.update(TESTING=True)

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


def test_register_duplicate_email_returns_503_when_db_unavailable():
    app = create_app()
    app.config.update(TESTING=True)

    with app.test_client() as client:
        with patch("backend.app.api.auth.db.session.add"), patch(
            "backend.app.api.auth.db.session.commit",
            side_effect=SQLAlchemyError("database unavailable"),
        ):
            response = client.post(
                "/api/auth/register",
                json={
                    "name": "Nairobi Threads",
                    "email": "owner@company.com",
                    "password": "secret123",
                },
            )

    assert response.status_code == 503
    assert response.get_json()["error"] == "Database unavailable. Please try again later."


def test_register_weak_password():
    app = create_app()
    app.config.update(TESTING=True)

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
    app = create_app()
    app.config.update(TESTING=True)

    business = MagicMock()
    business.id = "123"
    business.name = "Nairobi Threads"
    business.owner_email = "owner@company.com"
    business.password_hash = "hashed-password"
    business.widget_key = "widget-key"

    query = MagicMock()
    query.filter_by.return_value.first.return_value = business

    with app.test_client() as client:
        with (
            patch("backend.app.api.auth.db.session.query", return_value=query),
            patch("backend.app.api.auth.check_password_hash", return_value=True),
        ):
            response = client.post(
                "/api/auth/login",
                json={"email": "owner@company.com", "password": "secret123"},
            )

    assert response.status_code == 200
    assert response.get_json()["access_token"]


def test_login_wrong_password():
    app = create_app()
    app.config.update(TESTING=True)

    business = MagicMock()
    business.owner_email = "owner@company.com"
    business.password_hash = "hashed-password"

    query = MagicMock()
    query.filter_by.return_value.first.return_value = business

    with app.test_client() as client:
        with (
            patch("backend.app.api.auth.db.session.query", return_value=query),
            patch("backend.app.api.auth.check_password_hash", return_value=False),
        ):
            response = client.post(
                "/api/auth/login",
                json={"email": "owner@company.com", "password": "wrong-pass"},
            )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid email or password."


def test_invalid_jwt_is_rejected():
    app = create_app()
    app.config.update(TESTING=True)

    with app.test_client() as client:
        response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_protected_route_requires_auth():
    app = create_app()
    app.config.update(TESTING=True)

    with app.test_client() as client:
        response = client.get("/api/knowledge/documents")

    assert response.status_code == 401
