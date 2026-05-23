# Semantic Cache Chat App

This is a Vite React chat prototype for the Semantic Cache backend.

## Run

```bash
npm install
npm run dev
```

## Scripts

```bash
npm run dev
npm run build
npm run lint
npm run preview
```

## Backend Endpoint

The app sends chat requests to:

```text
POST http://localhost:8000/api/v1/cache/chat
```

The request includes:

- `Authorization: Bearer <token>`
- Optional `X-Conversation-Id`
- Optional `X-Conversation-History`
- JSON body with `query`, `domain`, `history`, and `context_id`

## Backend Setup

From the repository root:

```bash
docker-compose up -d
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Generate a development token:

```bash
curl "http://localhost:8000/token?user_id=dev&tenant_id=default&role=user"
```

## Next Work

- Move API base URL to environment config.
- Add token entry or login flow.
- Add stronger error states for `401`, `403`, and backend downtime.
