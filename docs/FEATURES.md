# Feature Reference

## Implemented Backend Features

| Feature | Status | Location |
| --- | --- | --- |
| FastAPI REST API | Implemented | `src/api/main.py` |
| JWT auth and dev token route | Implemented | `src/api/auth/jwt.py` |
| Tenant-aware cache keys | Implemented | `src/api/auth/jwt.py`, `src/cache/*` |
| Exact cache get/put/delete | Implemented | `src/api/routes/cache.py` |
| Batch cache get | Implemented | `src/api/routes/cache.py` |
| Semantic cache write/search | Implemented | `src/api/routes/cache.py` |
| Multi-intent semantic search | Implemented | `src/api/routes/cache.py`, `src/ml/query_parser.py` |
| Stream cache | Implemented | `src/cache/streaming.py` |
| Chat endpoint | Implemented | `src/api/routes/cache.py`, `src/cache/context.py` |
| Unified similarity index | Implemented | `src/cache/index_manager.py` |
| Sentence-transformer embeddings | Implemented | `src/embedding/service.py` |
| Adaptive thresholds | Implemented | `src/ml/adaptive_thresholds.py` |
| Domain classification | Implemented | `src/ml/domain_classifier.py` |
| Gemini LLM fallback | Implemented | `src/llm/service.py` |
| Local/Ollama fallback | Implemented | `src/llm/service.py` |
| OpenAI fallback | Placeholder | `src/llm/service.py` |
| Admin stats and policies | Partial | `src/api/routes/admin.py` |
| Tenant management | Partial | `src/api/routes/tenant.py` |
| Analytics routes | Exists but unmounted | `src/api/routes/analytics.py` |

## Frontend Features

| App | Status | Notes |
| --- | --- | --- |
| Dashboard | Prototype | Next.js app with mostly dummy data. |
| Chat app | Prototype | Vite React app calls `/api/v1/cache/chat`. |

## Core API Capabilities

### Exact Cache

- `GET /api/v1/cache/{key}`
- `PUT /api/v1/cache/{key}`
- `DELETE /api/v1/cache/{key}`
- `POST /api/v1/cache/batch`
- `DELETE /api/v1/cache`

### Semantic Cache

- `POST /api/v1/cache/semantic`
- `POST /api/v1/cache/semantic/search`
- `POST /api/v1/cache/semantic/multi/search`
- `GET /api/v1/cache/semantic/stats`
- `POST /api/v1/cache/semantic/stream`
- `POST /api/v1/cache/chat`

### Operations

- `GET /health`
- `GET /health/detailed`
- `GET /metrics`
- `GET /api/v1/admin/stats`
- `GET /api/v1/tenant/{tenant_id}/metrics`

## Feature Boundaries

This project is suitable for demonstration, experimentation, and project evaluation. Before production use, fix syntax/import issues, complete analytics wiring, replace placeholders, and add deployment-grade observability and security hardening.
