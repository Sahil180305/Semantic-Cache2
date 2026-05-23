# Similarity Search Guide

## Scope

Similarity search finds cached entries whose embeddings are close to the incoming query embedding.

## Key Files

- `src/cache/index_manager.py`
- `src/similarity/service.py`
- `src/similarity/base.py`
- `src/api/routes/search.py`

## Current Design

`UnifiedIndexManager` is the source of truth for vector indexing. `SimilaritySearchService` is a facade and should delegate to the unified index instead of maintaining a separate index.

## Thresholds

- General: `0.85`
- High precision domains: `0.90` to `0.95`
- Broad exploratory matching: `0.75` to `0.80`

## Preferred API

Use:

```text
POST /api/v1/cache/semantic/search
```

The standalone search route exists, but `src/api/routes/search.py` should be syntax-checked before production use.

## Checks

```bash
python -m py_compile src/api/routes/search.py src/cache/index_manager.py
pytest tests/unit/similarity -v
```
