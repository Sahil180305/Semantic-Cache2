# Semantic Cache

Semantic Cache is a FastAPI service for caching LLM and retrieval responses by exact key and by semantic similarity. It combines an in-memory L1 cache, Redis-backed L2 cache, sentence-transformer embeddings, a unified similarity index, tenant-aware cache keys, and optional LLM fallback for misses.

## Current Status

The backend is the primary runnable application. It exposes health, cache, semantic search, admin, and tenant routes from `src/api/main.py`.

The repository also contains two frontend prototypes:

- `frontend-services/dashboard`: Next.js analytics dashboard with mostly demo/static data.
- `frontend-services/chat-app`: Vite React chat client connected to `/api/v1/cache/chat`.

Known implementation notes:

- `/api/v1` analytics routes exist in `src/api/routes/analytics.py` but are not mounted by `src/api/main.py`.
- `src/api/routes/search.py` should be syntax-checked before relying on `/api/v1/search`; the canonical semantic lookup path is `/api/v1/cache/semantic/search`.
- OpenAI LLM calls are placeholders; Gemini and local/Ollama paths are implemented.

## Architecture

```text
Client / frontend
  -> FastAPI API
  -> JWT tenant resolver
  -> CacheManager
     -> L1 in-memory cache
     -> L2 Redis cache
     -> UnifiedIndexManager
     -> EmbeddingService
     -> Domain classifier and adaptive thresholds
  -> optional LLMService on miss
```

## Quick Start

```bash
docker-compose up -d
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Open:

- API root: `http://localhost:8000/`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` with password `admin`

Generate a development token:

```bash
curl "http://localhost:8000/token?user_id=dev&tenant_id=default&role=admin"
```

Use the returned token as `Authorization: Bearer <token>`.

## Common API Calls

Store an exact cache entry:

```bash
curl -X PUT "http://localhost:8000/api/v1/cache/hello" ^
  -H "Authorization: Bearer <token>" ^
  -H "Content-Type: application/json" ^
  -d "{\"value\":\"world\",\"domain\":\"general\"}"
```

Search semantically:

```bash
curl -X POST "http://localhost:8000/api/v1/cache/semantic/search" ^
  -H "Authorization: Bearer <token>" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"say hello\",\"domain\":\"general\",\"threshold\":0.85}"
```

Chat with cache lookup and LLM fallback:

```bash
curl -X POST "http://localhost:8000/api/v1/cache/chat" ^
  -H "Authorization: Bearer <token>" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"Explain semantic caching\",\"domain\":\"general\",\"history\":[]}"
```

## Project Layout

```text
src/api/                 FastAPI app, routes, schemas, auth, middleware
src/cache/               Cache manager, L1/L2/L3 modules, index manager, policies
src/embedding/           Embedding service and providers
src/similarity/          Similarity search facade and base types
src/ml/                  Query parsing, thresholds, classifiers, warming
src/llm/                 Gemini, OpenAI placeholder, and local/Ollama service
src/core/                Config, database, tenant manager, shared models
frontend-services/       Dashboard and chat UI prototypes
docs/                    Project documentation
tests/                   Unit, integration, and performance tests
```

## Tests

```bash
pytest tests/ -v
pytest tests/ -v --cov=src --cov-report=term
```

If tests fail at import time, first run:

```bash
python -m py_compile src/api/main.py src/api/routes/search.py src/api/schemas.py
```

## Documentation

Start with [docs/INDEX.md](docs/INDEX.md). For hands-on work, use [docs/guides/SETUP.md](docs/guides/SETUP.md), [docs/guides/USAGE_GUIDE.md](docs/guides/USAGE_GUIDE.md), and [docs/guides/QUICK_REFERENCE.md](docs/guides/QUICK_REFERENCE.md).

## License

MIT
