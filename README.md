# Msaidizi
cat > README.md << 'EOF'
# Msaidizi — AI Support Agent for Kenyan SMEs

Embeddable chat agent that answers from your documents, checks orders & M-Pesa (mock), and hands off to a human.

## Quick start (local)

```bash
# 1. Start Postgres
docker compose up -d

# 2. Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and add your GEMINI_API_KEY

# 3. Run migrations & seed (coming next)
# flask db upgrade
# python scripts/seed_demo.py

# 4. Start API
flask --app backend.app run --debug --port 5000