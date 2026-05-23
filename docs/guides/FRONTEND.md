# Frontend Guide

## Apps

The repository includes two frontend prototypes under `frontend-services`.

| App | Framework | Status |
| --- | --- | --- |
| `dashboard` | Next.js 16, React 19 | Prototype with mostly dummy data |
| `chat-app` | Vite, React 19 | Chat UI wired to `/api/v1/cache/chat` |

## Dashboard

Run:

```bash
cd frontend-services/dashboard
npm install
npm run dev
```

The dashboard pages show overview, patterns, clusters, and cost views. Current backend analytics endpoints are not mounted in `src/api/main.py`, so live metrics require additional backend wiring.

## Chat App

Run:

```bash
cd frontend-services/chat-app
npm install
npm run dev
```

The chat app posts to:

```text
POST http://localhost:8000/api/v1/cache/chat
```

It sends:

- `Authorization: Bearer <token>`
- Optional `X-Conversation-Id`
- Optional `X-Conversation-History`
- JSON body with `query`, `domain`, `history`, and `context_id`

## Backend Requirements

Start the API before testing either frontend:

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Generate a token from `/token` and configure the frontend flow to use it.

## Next Frontend Work

- Replace dashboard dummy data with mounted analytics APIs.
- Add token setup UX or a development token helper.
- Add loading, error, and unauthorized states.
- Keep API base URLs configurable instead of hard-coded.
