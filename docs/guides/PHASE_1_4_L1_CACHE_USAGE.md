# L1 Cache Guide

## Scope

L1 is the local in-memory cache tier for fast reads.

## Key Files

- `src/cache/l1_cache.py`
- `src/cache/base.py`
- `src/cache/cache_manager.py`

## Runtime Role

L1 stores hot `CacheEntry` objects. Semantic indexing is handled by `UnifiedIndexManager`; L1 should be treated as storage, not as the owner of semantic search.

## Configuration

Important API settings:

```text
L1_MAX_SIZE=10000
L1_EVICTION_STRATEGY=LRU
L1_TTL_SECONDS=3600
```

## Checks

```bash
pytest tests/unit/cache/test_phase_1_4_cache.py -v
python -m py_compile src/cache/l1_cache.py src/cache/cache_manager.py
```
