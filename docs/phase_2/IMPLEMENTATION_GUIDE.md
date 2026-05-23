# API Implementation Guide

## Main Entry Point

`src/api/main.py` creates the FastAPI app, configures middleware, mounts routers, and initializes runtime services.

## Adding A Route

1. Add or update a route module under `src/api/routes`.
2. Define request/response schemas in `src/api/schemas.py` or local route models.
3. Add auth dependencies where needed.
4. Mount the router in `src/api/main.py`.
5. Add tests.
6. Update `docs/phase_2/API_DESIGN.md`.

## Auth Pattern

Use:

```python
current_user: TokenPayload = Depends(get_current_user)
tenant_id: str = Depends(get_tenant_id)
```

Use `get_current_admin` for admin-only routes.

## App State Pattern

Runtime services are read from `request.app.state`, for example:

```python
cache_manager = getattr(request.app.state, "cache_manager", None)
embedding_service = getattr(request.app.state, "embedding_service", None)
index_manager = getattr(request.app.state, "index_manager", None)
```

Return `503` when a required service is unavailable.

## Current Cautions

- Do not document a route as live unless it is mounted in `src/api/main.py`.
- Keep tenant IDs resolved through auth dependencies.
- Avoid separate vector indexes; use `UnifiedIndexManager`.
- Syntax-check route files after edits.
