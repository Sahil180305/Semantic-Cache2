# Performance Guide

## Scope

Performance support covers compression, batching, connection reuse, cache warming, and measurement.

## Key Files

- `src/cache/performance_opt.py`
- `src/cache/streaming.py`
- `src/ml/predictive_warmer.py`
- `tests/performance/locustfile.py`
- `research_metrics.py`

## Runtime Features

- GZip middleware is enabled for API responses larger than 1000 bytes.
- L2 compression can be enabled through `ENABLE_L2_COMPRESSION`.
- Streaming cache can replay or cache generated token streams.
- Predictive warming starts during API startup when initialization succeeds.

## Metrics

Available mounted endpoint:

```text
GET /metrics
```

This endpoint currently returns Prometheus-style sample metrics. For production, connect it to live cache statistics.

## Checks

```bash
pytest tests/unit/cache/test_phase_1_8_performance.py -v
pytest tests/performance -v
```
