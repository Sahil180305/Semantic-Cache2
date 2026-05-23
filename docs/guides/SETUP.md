# Setup Guide

## Prerequisites

- Python 3.10+
- Docker Desktop or Docker Engine
- Redis and PostgreSQL through `docker-compose.yml`
- Optional: Gemini API key or local Ollama for LLM fallback

## Backend Setup

```bash
docker-compose up -d
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` for your local setup. The most important values are:

```text
LLM_PROVIDER=gemini
LLM_API_KEY=your_key
DATABASE_URL=postgresql://semantic_cache:semantic_cache_dev@localhost:5432/semantic_cache
REDIS_HOST=localhost
REDIS_PORT=6379
LOG_LEVEL=INFO
```

Start the API:

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

## Verify

```bash
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

Generate a development token:

```bash
curl "http://localhost:8000/token?user_id=dev&tenant_id=default&role=admin"
```

## Frontend Setup

Dashboard:

```bash
cd frontend-services/dashboard
npm install
npm run dev
```

Chat app:

```bash
cd frontend-services/chat-app
npm install
npm run dev
```

## Troubleshooting

If imports fail, run:

```bash
python -m py_compile src/api/main.py src/api/routes/search.py src/api/schemas.py
```

If semantic search is slow on first use, the embedding model may still be downloading or warming up.

If protected routes return `401`, generate a token from `/token` and pass `Authorization: Bearer <token>`.
