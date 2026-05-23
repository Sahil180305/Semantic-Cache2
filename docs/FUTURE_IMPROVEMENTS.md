# Future Improvements

## Highest Priority

1. Fix syntax/import issues in API modules and make `pytest tests/ -v` pass cleanly.
2. Decide whether analytics are in scope; mount and complete routes or remove dashboard assumptions.
3. Replace frontend dummy data with real API responses.
4. Complete OpenAI provider implementation or remove it from configuration choices.
5. Add end-to-end smoke tests for exact cache, semantic cache, chat fallback, and tenant isolation.

## Backend Hardening

- Persist or snapshot the unified index.
- Add rate limiting middleware tied to tenant quota.
- Replace placeholder admin metrics with live cache and Redis statistics.
- Add structured request logging with tenant IDs.
- Add provider health checks for embedding and LLM services.
- Add background task lifecycle handling for predictive warming.

## Security

- Enforce production-only token generation policy.
- Rotate JWT secrets and API keys through a secret manager.
- Add audit logs for admin and tenant operations.
- Add tenant isolation tests around semantic index search.

## Frontend

- Make API base URLs configurable.
- Add token/session handling.
- Wire dashboard to live metrics.
- Add clear empty, loading, and error states.

## Research Extensions

- Compare cosine thresholds by domain.
- Benchmark L1/L2 hit latency and semantic lookup latency.
- Evaluate cache hit quality against a labeled query-pair dataset.
- Add cost-saved and token-saved accounting.
