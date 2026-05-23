# Deployment Guide

## Local Container Stack

Use Docker Compose for infrastructure:

```bash
docker-compose up -d
```

This starts:

- Redis on `6379`
- PostgreSQL on `5432`
- Prometheus on `9090`
- Grafana on `3000`

Run the API separately during development:

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

## Production Checklist

- Set a strong `JWT_SECRET_KEY`.
- Use a production PostgreSQL URL.
- Use a protected Redis instance.
- Disable development token generation by setting `ENVIRONMENT` away from `development`.
- Provide `LLM_API_KEY` only through secrets management.
- Configure CORS to trusted origins.
- Run syntax checks and the test suite.
- Decide whether analytics routes are part of production and mount them if needed.

## Suggested Runtime

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

For containers, build from the repository `Dockerfile` and pass environment variables at runtime.

## Frontends

Dashboard:

```bash
cd frontend-services/dashboard
npm run build
npm run start
```

Chat app:

```bash
cd frontend-services/chat-app
npm run build
npm run preview
```

Before production deployment, replace hard-coded local API URLs with environment-driven configuration.

## Monitoring

The health endpoints are:

- `/health`
- `/health/detailed`
- `/metrics`

Prometheus configuration lives in `monitoring/prometheus/prometheus.yml`.
