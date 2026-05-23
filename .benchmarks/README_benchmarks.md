# Benchmarks

This folder contains benchmark artifacts for Semantic Cache.

## Contents

- `benchmark_results/`: generated benchmark reports.

## How To Read Results

Treat benchmark reports as point-in-time experiment outputs, not current production guarantees. Before citing a report, verify:

- The commit or code version used for the run.
- The infrastructure used for Redis, PostgreSQL, and model inference.
- Whether the API passed syntax/import checks before the benchmark.
- Whether LLM fallback was real, mocked, or disabled.
- Whether dashboard and analytics routes were involved.

## Suggested Fresh Run Checklist

```bash
python -m py_compile src/api/main.py src/api/routes/search.py src/api/schemas.py
pytest tests/ -v
docker-compose up -d
```

Then run the benchmark tool used by the current experiment and write results to `benchmark_results/`.
