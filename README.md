# Msaidizi

Msaidizi is a business knowledge assistant for customer support workflows. It combines a Flask API, a PostgreSQL-backed SQLAlchemy data model, and a Next.js frontend for onboarding, authentication, knowledge management, and dashboard operations.

## Features

- Business registration and login with JWT authentication
- Protected dashboard and document management
- Knowledge-base document ingestion and chunking
- PostgreSQL persistence with SQLAlchemy models
- Flask-Migrate database versioning
- Next.js App Router frontend with a liquid-glass style UI

## Architecture

- Backend: Python + Flask + Flask-SQLAlchemy + Flask-JWT-Extended
- Frontend: Next.js + TypeScript + App Router
- Database: PostgreSQL via Docker Compose
- Migrations: Alembic through Flask-Migrate

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker Desktop or Docker Engine
- Git

## Installation

1. Clone the repository.
2. Create a Python virtual environment and install dependencies:

```bash
cd msaidizi
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Install frontend dependencies:

```bash
cd frontend
npm install
```

## Environment configuration

Create `.env` from the example file and confirm the values match your local setup:

```bash
cp .env.example .env
```

Key values:

- `DATABASE_URL=postgresql+psycopg2://msaidizi:msaidizi@localhost:5433/msaidizi`
- `SECRET_KEY` and `JWT_SECRET_KEY` must be set to long, random values in production
- `CORS_ORIGINS` should include `http://localhost:3000` and `http://127.0.0.1:3000`

Frontend environment:

```bash
cd frontend
cp .env.local.example .env.local
```

Example:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:5000
```

## PostgreSQL setup

Start the database with Docker Compose:

```bash
docker compose up -d db
```

Health check:

```bash
docker compose ps
```

The app expects PostgreSQL on port `5433` for the local Docker instance.

## Database migrations

From the repo root:

```bash
source .venv/bin/activate
flask --app backend.app db upgrade
```

If the migration folder is missing or empty, run:

```bash
source .venv/bin/activate
flask --app backend.app db init
flask --app backend.app db migrate -m "initial schema"
flask --app backend.app db upgrade
```

## Backend startup

```bash
source .venv/bin/activate
flask --app backend.app run --host 127.0.0.1 --port 5000
```

Health check:

```bash
curl http://127.0.0.1:5000/health
```

## Frontend startup

```bash
cd frontend
npm run dev
```

The app should be available at:

- Frontend: http://localhost:3000
- Backend: http://127.0.0.1:5000

## API endpoints

### Authentication

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

### Knowledge base

- `GET /api/knowledge/documents`
- `POST /api/knowledge/documents`
- `DELETE /api/knowledge/documents/<document_id>`
- `POST /api/knowledge/search`

## Testing

Backend:

```bash
source .venv/bin/activate
pytest
```

Frontend:

```bash
cd frontend
npm test
npm run build
```

## Troubleshooting

- If registration fails with a network error, confirm the backend is running and the frontend API URL matches the backend server.
- If the database connection fails, confirm the Docker container is running and the `DATABASE_URL` matches the container port `5433`.
- If preflight CORS requests fail, confirm the backend includes `http://localhost:3000` and `http://127.0.0.1:3000` in its allowed origins.
- If migration commands do not work, confirm the database is reachable and the correct SQLAlchemy driver is installed.

## Security note

The current frontend stores JWTs in browser localStorage for compatibility with the existing app. For production, a more secure option is to move token handling to HttpOnly cookies while keeping the existing JWT-based backend authentication logic intact.
