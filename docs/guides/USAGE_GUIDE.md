# Usage Guide

## Authentication

Most API routes require a bearer token. In development, generate one with:

```bash
curl "http://localhost:8000/token?user_id=dev&tenant_id=default&role=admin"
```

Then set:

```bash
set TOKEN=<access_token>
```

## Exact Cache

Store a value:

```bash
curl -X PUT "http://localhost:8000/api/v1/cache/greeting" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"value\":\"Hello from cache\",\"domain\":\"general\"}"
```

Read it:

```bash
curl "http://localhost:8000/api/v1/cache/greeting" ^
  -H "Authorization: Bearer %TOKEN%"
```

Delete it:

```bash
curl -X DELETE "http://localhost:8000/api/v1/cache/greeting" ^
  -H "Authorization: Bearer %TOKEN%"
```

## Semantic Cache

Store a semantic response:

```bash
curl -X POST "http://localhost:8000/api/v1/cache/semantic" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"What is semantic caching?\",\"response\":\"Semantic caching reuses responses for meaningfully similar inputs.\",\"domain\":\"general\"}"
```

Search semantically:

```bash
curl -X POST "http://localhost:8000/api/v1/cache/semantic/search" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"Explain semantic cache\",\"domain\":\"general\",\"threshold\":0.85}"
```

## Multi-Intent Search

```bash
curl -X POST "http://localhost:8000/api/v1/cache/semantic/multi/search" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"Explain semantic caching and list its benefits\",\"domain\":\"general\"}"
```

## Chat Endpoint

```bash
curl -X POST "http://localhost:8000/api/v1/cache/chat" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"What did we discuss about caching?\",\"history\":[{\"role\":\"user\",\"content\":\"Explain semantic caching\"}],\"domain\":\"general\",\"context_id\":\"demo\"}"
```

## Tenant Override

Admins can pass `X-Tenant-Id` to operate on another tenant:

```bash
curl "http://localhost:8000/api/v1/cache/semantic/stats" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "X-Tenant-Id: acme"
```

Normal users always use the tenant from the JWT.

## Admin

```bash
curl "http://localhost:8000/api/v1/admin/stats" -H "Authorization: Bearer %TOKEN%"
curl "http://localhost:8000/api/v1/admin/policies" -H "Authorization: Bearer %TOKEN%"
```

## Tenant Management

```bash
curl -X POST "http://localhost:8000/api/v1/tenant/create" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"tenant_id\":\"acme\",\"quota_memory_mb\":512,\"quota_queries_daily\":10000,\"quota_request_size_kb\":500}"
```

## Notes

- Prefer `/api/v1/cache/semantic/search` for semantic lookup.
- The dashboard analytics routes are not mounted by default.
- OpenAI LLM provider is currently a placeholder.
