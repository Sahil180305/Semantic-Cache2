# Caching Policies Guide

## Scope

Policy modules decide what to keep, evict, prefetch, or prioritize.

## Key Files

- `src/cache/policies.py`
- `src/cache/advanced_policies.py`
- `src/ml/cost_aware_eviction.py`
- `src/ml/predictive_warmer.py`

## Current Runtime Path

`src/api/main.py` initializes `AdvancedCachingPolicyManager` and `PredictiveCacheWarmer` when available. Admin policy endpoints expose and update a small subset of runtime settings.

## API

```text
GET /api/v1/admin/policies
PUT /api/v1/admin/policies
POST /api/v1/admin/cache/optimize
```

Some admin responses are placeholders and should be connected to live cache metrics before production use.

## Checks

```bash
pytest tests/unit/cache/test_phase_1_7_policies.py -v
python -m py_compile src/cache/advanced_policies.py src/ml/predictive_warmer.py
```
