# Quick Reference

## Run

```bash
docker-compose up -d
pip install -r requirements.txt
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

## Test

```bash
pytest tests/ -v
python -m py_compile src/api/main.py src/api/routes/search.py src/api/schemas.py
```

## URLs

| Service | URL |
| --- | --- |
| API | `http://localhost:8000` |
| Swagger | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |
| Prometheus | `http://localhost:9090` |
| Grafana | `http://localhost:3000` |

## Token

```bash
curl "http://localhost:8000/token?user_id=dev&tenant_id=default&role=admin"
```

## Core Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Basic health |
| GET | `/health/detailed` | Detailed health |
| GET | `/metrics` | Prometheus-style metrics |
| GET | `/api/v1/cache/{key}` | Exact get |
| PUT | `/api/v1/cache/{key}` | Exact put |
| DELETE | `/api/v1/cache/{key}` | Exact delete |
| POST | `/api/v1/cache/batch` | Batch get |
| DELETE | `/api/v1/cache` | Clear tenant cache, admin only |
| POST | `/api/v1/cache/semantic` | Semantic put |
| POST | `/api/v1/cache/semantic/search` | Semantic lookup |
| POST | `/api/v1/cache/semantic/multi/search` | Multi-intent lookup |
| GET | `/api/v1/cache/semantic/stats` | Semantic stats |
| POST | `/api/v1/cache/semantic/stream` | Stream lookup/cache |
| POST | `/api/v1/cache/chat` | Context-aware chat |
| GET | `/api/v1/admin/stats` | Admin stats |
| GET | `/api/v1/admin/policies` | Cache policy view |
| POST | `/api/v1/tenant/create` | Create tenant |

## Environment Keys

```text
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=postgresql://semantic_cache:semantic_cache_dev@localhost:5432/semantic_cache
REDIS_HOST=localhost
REDIS_PORT=6379
JWT_SECRET_KEY=change-me
LLM_PROVIDER=gemini
LLM_API_KEY=your-key
LLM_MODEL=gemini-pro
LOG_LEVEL=INFO
```

## Common Status Codes

| Code | Meaning |
| --- | --- |
| 401 | Missing or invalid token |
| 403 | Role or tenant access denied |
| 404 | Cache key or tenant not found |
| 503 | Cache, embedding, index, or LLM dependency unavailable |
