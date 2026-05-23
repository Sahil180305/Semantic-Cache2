# System Architecture

## Overview

Semantic Cache is a FastAPI backend that stores responses by exact key and by semantic meaning. It is designed for LLM applications where repeated or similar prompts should avoid expensive model calls.

```text
Client
  -> FastAPI routes
  -> JWT auth and tenant resolver
  -> CacheManager
     -> L1 in-memory cache
     -> L2 Redis cache
     -> UnifiedIndexManager
     -> EmbeddingService
     -> Domain classifier and adaptive thresholds
  -> LLMService on miss
```

## Runtime Startup

`src/api/main.py` performs startup wiring in this order:

1. Initialize database tables.
2. Create the singleton `UnifiedIndexManager`.
3. Initialize `EmbeddingService` with `all-MiniLM-L6-v2`.
4. Initialize domain classifier and adaptive threshold manager.
5. Initialize `CacheManager` and attach index, embedding, domain, and threshold services.
6. Initialize `SimilaritySearchService` as a facade.
7. Initialize policies, performance optimizer, tenant manager, predictive warmer, and LLM service.

## Main Components

### API Layer

The API layer lives in `src/api`. Mounted routes include:

- Health: `/health`, `/health/detailed`, `/metrics`
- Cache: `/api/v1/cache/*`
- Search: `/api/v1/search`, `/api/v1/similarity/embedding`, `/api/v1/index/stats`
- Admin: `/api/v1/admin/*`
- Tenant: `/api/v1/tenant/*`

The app also serves `/docs`, `/redoc`, and `/openapi.json`.

### Authentication And Tenancy

JWT auth is implemented in `src/api/auth/jwt.py`. Tokens include `sub`, `tenant_id`, `role`, `scopes`, and `exp`.

Tenant IDs are resolved from:

- `X-Tenant-Id` when the token role is `admin` or `superadmin`.
- The token's `tenant_id` for normal users.

Cache keys are prefixed internally with the resolved tenant ID.

### Cache Manager

`src/cache/cache_manager.py` coordinates cache reads, writes, semantic lookups, L1/L2 behavior, promotions, and invalidation.

L1 is optimized for local low-latency access. L2 is backed by Redis. The unified index is separate from storage and handles semantic lookup.

### Unified Index

`src/cache/index_manager.py` is the shared similarity index path. Cache storage and search flows should use this manager instead of building separate indexes.

### Embeddings

`src/embedding/service.py` creates query embeddings. The current backend startup uses `all-MiniLM-L6-v2`, which produces 384-dimensional vectors.

### LLM Fallback

`src/llm/service.py` supports:

- Gemini REST calls.
- Local/Ollama calls and streaming.
- OpenAI placeholders.

When semantic search misses and a provider is configured, the backend can generate a response and cache it.

### Frontends

The repository includes:

- `frontend-services/dashboard`: Next.js dashboard prototype. It currently uses mostly dummy data.
- `frontend-services/chat-app`: Vite React chat client targeting `/api/v1/cache/chat`.

## Important Gaps

- Analytics routes exist but are not mounted by the main app.
- Dashboard backend integration is incomplete.
- OpenAI provider logic is not implemented.
- Search route and schema modules should be syntax-checked before production use.

## Operational Dependencies

- Redis for L2 cache.
- PostgreSQL for database-backed project data.
- Optional Prometheus and Grafana through `docker-compose.yml`.
- Optional Gemini API key or local Ollama runtime for LLM fallback.
