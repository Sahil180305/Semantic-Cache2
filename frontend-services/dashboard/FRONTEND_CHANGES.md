# Dashboard Backend Connection Plan

## Current State

The dashboard has polished pages for overview, query patterns, semantic clusters, and cost analytics. The current UI mostly uses dummy data.

## Backend Gap

Analytics endpoints exist in `src/api/routes/analytics.py`, but `src/api/main.py` does not mount that router. Until mounted, dashboard calls to metrics, historical metrics, top queries, or realtime WebSocket data will not work.

## Required Backend Work

1. Mount analytics routes in `src/api/main.py`.
2. Decide the prefix, for example `/api/v1/analytics`.
3. Add auth dependencies to analytics routes.
4. Connect realtime, historical, and top-query data to real cache metrics.
5. Add tests for each endpoint.

## Required Frontend Work

1. Replace hard-coded API URLs with environment variables.
2. Add bearer token handling.
3. Replace dummy data blocks in pages with live fetches.
4. Add loading and error states.
5. Add WebSocket reconnect behavior if realtime metrics are kept.

## Suggested Environment

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000
```
