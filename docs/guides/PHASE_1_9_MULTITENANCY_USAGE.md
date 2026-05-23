# Multi-Tenancy Guide

## Scope

Multi-tenancy isolates cache and management operations by tenant ID.

## Key Files

- `src/api/auth/jwt.py`
- `src/api/routes/tenant.py`
- `src/core/tenant_manager.py`
- `src/cache/multi_tenancy.py`

## Tenant Resolution

The tenant ID comes from:

- `X-Tenant-Id` when the user role is `admin` or `superadmin`.
- JWT `tenant_id` for regular users.

Cache routes prefix internal keys with the tenant ID.

## Tenant API

```text
POST /api/v1/tenant/create
GET /api/v1/tenant/{tenant_id}/metrics
GET /api/v1/tenant/{tenant_id}/usage
PUT /api/v1/tenant/{tenant_id}/quota
DELETE /api/v1/tenant/{tenant_id}
GET /api/v1/tenant/verify-isolation
```

## Example Tenant Create

```bash
curl -X POST "http://localhost:8000/api/v1/tenant/create" ^
  -H "Authorization: Bearer <token>" ^
  -H "Content-Type: application/json" ^
  -d "{\"tenant_id\":\"acme\",\"quota_memory_mb\":512,\"quota_queries_daily\":10000,\"quota_request_size_kb\":500}"
```

## Checks

```bash
pytest tests/unit/cache/test_phase_1_9_multitenancy.py -v
pytest test_tenant_api.py -v
```
