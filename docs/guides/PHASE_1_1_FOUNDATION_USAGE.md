# Foundation Component Guide

## Scope

The foundation layer contains shared cache models, configuration, exceptions, and database/tenant utilities.

## Key Files

- `src/core/config.py`
- `src/core/models.py`
- `src/core/schemas.py`
- `src/core/database.py`
- `src/core/tenant_manager.py`
- `src/cache/base.py`

## Core Concepts

- `CacheEntry` is the main cached response record.
- Cache entries carry query text, embedding, response payload, metadata, domain, and memory estimate.
- Configuration is split between API settings in `src/api/config.py` and broader core config in `src/core/config.py`.

## When To Touch This Layer

- Adding fields common to all cache entries.
- Changing database initialization.
- Changing tenant quota behavior.
- Adding shared exceptions or model types.

## Checks

```bash
pytest tests/unit/test_phase1_1_foundation.py -v
python -m py_compile src/core/config.py src/cache/base.py
```
