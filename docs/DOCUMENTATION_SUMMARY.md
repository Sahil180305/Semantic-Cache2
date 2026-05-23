# Documentation Summary

## What Changed

The documentation has been cleaned into a smaller, current, and role-oriented structure. Old session notes, repeated phase summaries, and outdated claims were replaced with direct references to the codebase as it exists now.

## Canonical Documents

- `README.md`: repository entry point.
- `PROJECT_CONTEXT.md`: project purpose, current implementation, and reality checks.
- `docs/INDEX.md`: documentation navigation.
- `docs/architecture/ARCHITECTURE.md`: canonical architecture.
- `docs/guides/SETUP.md`: local setup.
- `docs/guides/USAGE_GUIDE.md`: API usage.
- `docs/guides/QUICK_REFERENCE.md`: compact operational reference.

## Supporting Documents

- `docs/FEATURES.md`: feature inventory.
- `docs/QUERY_FLOW_EXPLAINED.md`: request lifecycle.
- `docs/guides/LLM_INTEGRATION.md`: model provider behavior.
- `docs/guides/FRONTEND.md`: dashboard and chat app status.
- `docs/FUTURE_IMPROVEMENTS.md`: roadmap.

## Cleanup Principles Used

- Removed duplicate "phase complete" narratives where they repeated feature docs.
- Replaced broad claims with code-backed descriptions.
- Marked unmounted, placeholder, or demo-only areas clearly.
- Kept old phase guide filenames for discoverability, but converted them to concise component references.

## Reader Paths

- New developer: `README.md` -> `docs/INDEX.md` -> `docs/guides/SETUP.md`.
- Backend contributor: `docs/architecture/ARCHITECTURE.md` -> `docs/guides/USAGE_GUIDE.md`.
- Frontend contributor: `docs/guides/FRONTEND.md` -> frontend app README.
- Evaluator: `PROJECT_CONTEXT.md` -> `docs/FEATURES.md` -> `docs/QUERY_FLOW_EXPLAINED.md`.
