# Deduplication Guide

## Scope

Deduplication reduces repeated work before cache lookup or storage by normalizing and grouping similar query strings.

## Key Files

- `src/cache/query_dedup.py`
- `src/ml/query_parser.py`
- `tests/unit/cache/test_phase_1_6_dedup.py`

## Current Role

Deduplication is an internal helper feature. Public deduplication API endpoints are described in older planning docs but are not mounted in the current FastAPI app.

## Recommended Use

Use deduplication for:

- Normalizing repeated query variants.
- Grouping nearly identical query strings.
- Reducing redundant embedding generation.

Do not treat it as a public API unless routes are added and tested.

## Checks

```bash
pytest tests/unit/cache/test_phase_1_6_dedup.py -v
python -m py_compile src/cache/query_dedup.py
```
