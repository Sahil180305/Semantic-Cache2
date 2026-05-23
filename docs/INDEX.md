# Documentation Index

This is the canonical map for the Semantic Cache project documentation.

## Start Here

- [Repository README](../README.md): project overview and first commands.
- [Setup Guide](guides/SETUP.md): local backend and infrastructure setup.
- [Usage Guide](guides/USAGE_GUIDE.md): API workflows and examples.
- [Quick Reference](guides/QUICK_REFERENCE.md): endpoints, commands, and environment keys.

## Architecture

- [System Architecture](architecture/ARCHITECTURE.md): current backend architecture and data flow.
- [Query Flow Explained](QUERY_FLOW_EXPLAINED.md): exact, semantic, chat, stream, and miss handling.
- [Architecture Comparison](ARCHITECTURE_COMPARISON.md): planned vs implemented architecture.

## Feature Guides

- [Features](FEATURES.md): current feature inventory.
- [LLM Integration](guides/LLM_INTEGRATION.md): Gemini, local/Ollama, and OpenAI status.
- [Frontend Guide](guides/FRONTEND.md): dashboard and chat app status.
- [Deployment Guide](guides/DEPLOYMENT.md): container and production notes.
- [Future Improvements](FUTURE_IMPROVEMENTS.md): cleaned roadmap.

## Component Guides

The phase guides are now concise component references. They are useful when working directly with cache internals:

- [Foundation](guides/PHASE_1_1_FOUNDATION_USAGE.md)
- [Embedding Service](guides/PHASE_1_2_EMBEDDING_SERVICE_USAGE.md)
- [Similarity Search](guides/PHASE_1_3_SIMILARITY_SEARCH_USAGE.md)
- [L1 Cache](guides/PHASE_1_4_L1_CACHE_USAGE.md)
- [L2 Cache](guides/PHASE_1_5_L2_CACHE_USAGE.md)
- [Deduplication](guides/PHASE_1_6_DEDUP_USAGE.md)
- [Caching Policies](guides/PHASE_1_7_POLICIES_USAGE.md)
- [Performance](guides/PHASE_1_8_PERFORMANCE_USAGE.md)
- [Multi-Tenancy](guides/PHASE_1_9_MULTITENANCY_USAGE.md)

## Phase 2 API Notes

- [Phase 2 Overview](phase_2/README.md)
- [API Design](phase_2/API_DESIGN.md)
- [Implementation Guide](phase_2/IMPLEMENTATION_GUIDE.md)
- [Status Report](phase_2/STATUS_REPORT.md)

## Documentation Maintenance Rules

- Prefer current code behavior over older phase claims.
- Keep examples copy-pasteable.
- Mark placeholders honestly.
- Avoid duplicate architecture diagrams across files; link to the canonical architecture page instead.
