# Query Flow Explained

## Exact Cache Flow

1. Client calls `GET /api/v1/cache/{key}` with a bearer token.
2. JWT middleware validates the token.
3. Tenant resolver chooses the tenant ID.
4. The API builds an internal key as `{tenant_id}:{key}`.
5. `CacheManager.get()` checks cache storage.
6. The API returns a hit response or a cache-not-found error.

## Exact Write Flow

1. Client calls `PUT /api/v1/cache/{key}` with `value`, optional `domain`, and optional `metadata`.
2. The backend generates an embedding for the key when the embedding service is available.
3. A `CacheEntry` is created with response, embedding, metadata, and domain.
4. `CacheManager.put()` stores the entry.
5. `UnifiedIndexManager.add()` indexes the embedding for semantic lookup.

## Semantic Search Flow

1. Client calls `POST /api/v1/cache/semantic/search`.
2. The request includes `query`, optional `domain`, and optional `threshold`.
3. `CacheManager.get_semantic_async()` embeds the query.
4. The unified index returns candidates above the threshold.
5. The best matching cache entry is returned as a semantic hit.
6. If no hit is found, the service may call the configured LLM.
7. Generated LLM responses are cached for future requests.

## Multi-Intent Search Flow

`POST /api/v1/cache/semantic/multi/search` decomposes a multi-intent query, resolves each sub-query through semantic search, and returns:

- Normalized query.
- Sub-query hit details.
- Whether all parts hit.
- Synthesized response when available.
- Hit ratio.

## Chat Flow

`POST /api/v1/cache/chat` is the context-aware chat entry point.

1. It accepts `query`, `history`, optional `context_id`, optional `tenant_id`, optional `domain`, and optional metadata.
2. It can also read conversation ID and history from headers.
3. `SmartCacheRouter` rewrites or decomposes the query when context is available.
4. Cache lookup runs first.
5. On miss, the configured LLM can generate a response.
6. The response returns cache source information, rewritten query, and sub-query data when available.

## Streaming Flow

`POST /api/v1/cache/semantic/stream` checks for a cached stream. On hit, it replays cached tokens. On miss, it streams from the configured LLM service and caches the emitted chunks.

## Thresholds

The default semantic threshold is `0.85`. Use higher thresholds for domains where precision matters:

- Medical or legal: `0.90` to `0.95`
- General Q&A: `0.85`
- E-commerce or exploratory search: `0.75` to `0.80`

## Failure Behavior

- Missing cache manager returns `503`.
- Missing embedding service returns `503` for semantic write/search paths that require embeddings.
- Semantic lookup exceptions are treated as misses in the main semantic search endpoint.
- Missing LLM configuration means misses return `response: null` instead of generated content.
