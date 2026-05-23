# Phase 2 API Documentation

Phase 2 covers the FastAPI REST layer and tenant-aware API access.

## Current Mounted API Areas

- Health: `/health`, `/health/detailed`, `/metrics`
- Cache: `/api/v1/cache/*`
- Search: `/api/v1/search`, `/api/v1/similarity/embedding`, `/api/v1/index/stats`
- Admin: `/api/v1/admin/*`
- Tenant: `/api/v1/tenant/*`

## Recommended Docs

- [API Design](API_DESIGN.md)
- [Implementation Guide](IMPLEMENTATION_GUIDE.md)
- [Status Report](STATUS_REPORT.md)
- [Usage Guide](../guides/USAGE_GUIDE.md)

## Notes

Older Phase 2 planning mentioned deduplication and analytics endpoints as public API. Those routes are not currently mounted by `src/api/main.py`.
