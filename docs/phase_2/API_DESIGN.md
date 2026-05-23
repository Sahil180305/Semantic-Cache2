# API Design

## Base URLs

```text
http://localhost:8000
http://localhost:8000/api/v1
```

## Authentication

Protected routes use:

```text
Authorization: Bearer <jwt>
```

Development token route:

```text
GET /token?user_id=dev&tenant_id=default&role=admin
```

## Health

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Root service metadata |
| GET | `/health` | Basic health |
| GET | `/health/detailed` | Detailed service status |
| GET | `/metrics` | Prometheus-style metrics |

## Cache

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/v1/cache/{key}` | Exact cache get |
| PUT | `/api/v1/cache/{key}` | Exact cache put with embedding/index update |
| DELETE | `/api/v1/cache/{key}` | Exact cache delete |
| POST | `/api/v1/cache/batch` | Batch exact get |
| DELETE | `/api/v1/cache` | Clear cache, admin only |
| POST | `/api/v1/cache/semantic` | Semantic store |
| POST | `/api/v1/cache/semantic/search` | Semantic lookup |
| POST | `/api/v1/cache/semantic/multi/search` | Multi-intent semantic lookup |
| GET | `/api/v1/cache/semantic/stats` | Semantic stats |
| POST | `/api/v1/cache/semantic/stream` | Streaming cache lookup |
| POST | `/api/v1/cache/chat` | Context-aware chat |

## Search

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/v1/search` | Similarity search route |
| POST | `/api/v1/similarity/embedding` | Generate embedding and search similar items |
| GET | `/api/v1/index/stats` | Unified index statistics |

Check `src/api/routes/search.py` before relying on these routes in production.

## Admin

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/v1/admin/stats` | Global stats |
| POST | `/api/v1/admin/cache/optimize` | Trigger optimization placeholder |
| POST | `/api/v1/admin/cache/compress` | Compression placeholder |
| GET | `/api/v1/admin/policies` | View policies |
| PUT | `/api/v1/admin/policies` | Update selected policies |

## Tenant

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/v1/tenant/create` | Create tenant |
| GET | `/api/v1/tenant/{tenant_id}/metrics` | Tenant metrics |
| GET | `/api/v1/tenant/{tenant_id}/usage` | Tenant usage |
| PUT | `/api/v1/tenant/{tenant_id}/quota` | Update quota |
| DELETE | `/api/v1/tenant/{tenant_id}` | Delete tenant |
| GET | `/api/v1/tenant/verify-isolation` | Verify isolation |

## Response Conventions

- Success responses use route-specific JSON models.
- Errors use FastAPI HTTP errors and custom middleware.
- Missing infrastructure generally returns `503`.
- Unauthorized requests return `401`.
- Role or tenant violations return `403`.
