# Project Context

## Purpose

Semantic Cache is a BTech project that demonstrates a production-style semantic caching layer for LLM applications. The core idea is simple: reuse expensive responses when a new request is either an exact match or a close semantic match to a previous request.

## Current Implementation

The current backend is a FastAPI service with:

- JWT-based authentication and tenant resolution.
- Exact cache operations under `/api/v1/cache`.
- Semantic storage, search, multi-intent search, stream caching, and chat routing under `/api/v1/cache`.
- L1 in-memory and L2 Redis cache coordination through `CacheManager`.
- A `UnifiedIndexManager` used by cache and search flows.
- Sentence-transformer embeddings using `all-MiniLM-L6-v2` with 384 dimensions.
- Domain classification and adaptive thresholds.
- Optional LLM fallback through Gemini or local/Ollama.
- Admin and tenant management routes.

## Important Reality Checks

- Analytics route code exists but is not mounted in `src/api/main.py`.
- The dashboard currently uses dummy data unless backend wiring is completed.
- OpenAI LLM integration is a placeholder.
- Some older phase documents were planning notes; the cleaned docs now point readers to current behavior first.
- `src/api/routes/search.py` appears to need a syntax pass before the `/api/v1/search` route is treated as production-ready.

## Key Commands

```bash
docker-compose up -d
pip install -r requirements.txt
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
pytest tests/ -v
```

## Main Directories

```text
src/api/           API app, route modules, schemas, auth, middleware
src/cache/         Cache tiers, policies, streaming cache, unified index
src/embedding/     Embedding service and providers
src/similarity/    Similarity abstractions and service facade
src/ml/            Query parsing, thresholds, predictive warming
src/llm/           Cloud and local model integration
src/core/          Config, database, tenant management, common models
docs/              Documentation
tests/             Test suite
frontend-services/ Dashboard and chat prototypes
```

## Success Criteria

The project is successful when it can:

- Return exact cache hits for repeated keys.
- Return semantic hits for similar queries above the configured threshold.
- Keep tenant data isolated.
- Fall back to an LLM on miss and cache the generated response.
- Expose enough metrics and admin controls for demonstration and evaluation.

## Recommended Reading Order

1. `README.md`
2. `docs/INDEX.md`
3. `docs/architecture/ARCHITECTURE.md`
4. `docs/guides/SETUP.md`
5. `docs/guides/USAGE_GUIDE.md`
6. `docs/QUERY_FLOW_EXPLAINED.md`
