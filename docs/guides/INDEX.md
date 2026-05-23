# Guides Index

Use these guides for hands-on work.

## Primary Guides

- [Setup](SETUP.md): install dependencies and run the backend.
- [Usage](USAGE_GUIDE.md): API examples.
- [Quick Reference](QUICK_REFERENCE.md): endpoint and command cheat sheet.
- [LLM Integration](LLM_INTEGRATION.md): Gemini, OpenAI placeholder, and local/Ollama setup.
- [Frontend](FRONTEND.md): dashboard and chat app status.
- [Deployment](DEPLOYMENT.md): container and production notes.

## Component Guides

- [Foundation](PHASE_1_1_FOUNDATION_USAGE.md)
- [Embedding Service](PHASE_1_2_EMBEDDING_SERVICE_USAGE.md)
- [Similarity Search](PHASE_1_3_SIMILARITY_SEARCH_USAGE.md)
- [L1 Cache](PHASE_1_4_L1_CACHE_USAGE.md)
- [L2 Cache](PHASE_1_5_L2_CACHE_USAGE.md)
- [Deduplication](PHASE_1_6_DEDUP_USAGE.md)
- [Caching Policies](PHASE_1_7_POLICIES_USAGE.md)
- [Performance](PHASE_1_8_PERFORMANCE_USAGE.md)
- [Multi-Tenancy](PHASE_1_9_MULTITENANCY_USAGE.md)

## Recommended Flow

1. Run the backend with [Setup](SETUP.md).
2. Generate a token and call the API with [Usage](USAGE_GUIDE.md).
3. Read [Architecture](../architecture/ARCHITECTURE.md) before changing internals.
4. Use component guides only when touching that component.
