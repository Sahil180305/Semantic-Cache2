# Semantic Cache Dashboard

This is a Next.js dashboard prototype for Semantic Cache analytics.

## Status

The UI is present, but most data is currently demo/static data. Backend analytics routes exist in `src/api/routes/analytics.py`, but they are not mounted in the main FastAPI app yet.

## Run

```bash
npm install
npm run dev
```

Default local URL:

```text
http://localhost:3000
```

## Scripts

```bash
npm run dev
npm run build
npm run start
npm run lint
```

## Backend Assumptions

The dashboard currently assumes a backend near:

```text
http://localhost:8000/api/v1
```

Before using it as a live dashboard:

- Mount analytics routes in `src/api/main.py`.
- Add authentication/token handling.
- Replace hard-coded API URLs with environment variables.
- Replace dummy data with real API calls.
