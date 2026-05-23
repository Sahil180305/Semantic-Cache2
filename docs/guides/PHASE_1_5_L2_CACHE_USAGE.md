# L2 Cache Guide

## Scope

L2 is the Redis-backed cache tier used for shared or longer-lived cache storage.

## Key Files

- `src/cache/l2_cache.py`
- `src/cache/redis_config.py`
- `src/cache/cache_manager.py`

## Runtime Role

`CacheManager` coordinates L1 and L2 behavior using a configured strategy:

```text
CACHE_STRATEGY=write_through
ENABLE_L1_TO_L2_PROMOTION=true
ENABLE_L2_COMPRESSION=true
```

## Infrastructure

Start Redis through:

```bash
docker-compose up -d redis
```

Default connection:

```text
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

## Checks

```bash
pytest tests/unit/cache/test_phase_1_5_l2_cache.py -v
pytest tests/integration/test_l2_cache_integration.py -v
```
