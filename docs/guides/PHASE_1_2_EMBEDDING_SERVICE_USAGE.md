# Embedding Service Guide

## Scope

Embeddings convert query text into vectors used for semantic lookup.

## Key Files

- `src/embedding/service.py`
- `src/embedding/base.py`
- `src/embedding/providers.py`

## Current Runtime Path

`src/api/main.py` initializes:

```text
provider: sentence-transformer
model: all-MiniLM-L6-v2
dimension: 384
```

## Usage Pattern

The API uses embeddings when:

- Storing exact cache entries with semantic index support.
- Storing semantic cache entries.
- Searching semantic cache entries.
- Running similarity endpoints.

## Operational Notes

- First startup may download or warm the model.
- Keep index dimension aligned with the embedding model.
- If the embedding service is unavailable, semantic endpoints return `503`.

## Checks

```bash
pytest tests/unit/embedding -v
python -m py_compile src/embedding/service.py
```
