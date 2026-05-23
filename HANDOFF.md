# Handoff

## What This Repository Contains

This repository contains a semantic cache backend, documentation, tests, and two frontend prototypes. The main runnable service is `src/api/main.py`.

## Current Backend Shape

Startup initializes:

- Database tables through `src/core/database.py`.
- `UnifiedIndexManager` with 384-dimensional cosine embeddings.
- `EmbeddingService` using `all-MiniLM-L6-v2`.
- Domain classifier and adaptive threshold manager.
- `CacheManager` with L1, Redis L2, semantic search, compression, and promotion settings.
- `SimilaritySearchService` as a facade over the unified index.
- Advanced policies, performance optimizer, tenant manager, predictive warmer, and LLM service.

Mounted routers:

- `/health`, `/health/detailed`, `/metrics`
- `/api/v1/cache/*`
- `/api/v1/search`, `/api/v1/similarity/embedding`, `/api/v1/index/stats`
- `/api/v1/admin/*`
- `/api/v1/tenant/*`

## Things To Check First

```bash
python -m py_compile src/api/main.py src/api/routes/search.py src/api/schemas.py
pytest tests/ -v
```

`src/api/routes/search.py` and `src/api/schemas.py` should be checked carefully because they currently look like likely import or syntax failure points.

## Running Locally

```bash
docker-compose up -d
pip install -r requirements.txt
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Generate a dev token:

```bash
curl "http://localhost:8000/token?user_id=dev&tenant_id=default&role=admin"
```

## Useful Smoke Tests

```bash
curl http://localhost:8000/health
curl http://localhost:8000/docs
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/cache/semantic/stats
```

## Frontend Notes

- Dashboard: `frontend-services/dashboard`, Next.js 16, mostly dummy data.
- Chat app: `frontend-services/chat-app`, Vite React, posts to `/api/v1/cache/chat`.

## Next Best Engineering Steps

1. Fix Python syntax/import issues and run the test suite.
2. Mount or remove analytics routes depending on product scope.
3. Replace dashboard dummy data with real backend calls.
4. Complete OpenAI provider implementation or document it as unsupported.
5. Add an integration smoke test for exact cache, semantic cache, and chat miss fallback.
