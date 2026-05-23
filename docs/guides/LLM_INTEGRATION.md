# LLM Integration

## Purpose

The LLM service is used when semantic cache lookup misses. A generated response can then be cached for future exact or semantic hits.

## Providers

| Provider | Status | Notes |
| --- | --- | --- |
| Gemini | Implemented | Uses Google Generative Language REST API. |
| Local/Ollama | Implemented | Uses `/api/generate` on a local Ollama server. |
| OpenAI | Placeholder | Methods return placeholder text. |

## Environment

Gemini:

```text
LLM_PROVIDER=gemini
LLM_API_KEY=your_gemini_key
LLM_MODEL=gemini-pro
```

Local/Ollama:

```text
LLM_PROVIDER=local
LOCAL_LLM_BASE_URL=http://localhost:11434
LOCAL_LLM_MODEL=qwen2.5:1.5b
LOCAL_LLM_TEMPERATURE=0.7
LOCAL_LLM_TIMEOUT=60
LOCAL_LLM_STREAM_TIMEOUT=120
```

## Miss Flow

1. Semantic search runs first.
2. If no hit is found, the API checks `app.state.llm_service`.
3. The configured provider generates a response.
4. The response is cached with metadata `source=llm_generated`.
5. The client receives `hit=false` and `hit_reason=miss_llm_generated`.

## Streaming

`POST /api/v1/cache/semantic/stream` can stream from the configured LLM and cache tokens. On a future hit, the cached stream is replayed.

## Production Notes

- Store API keys in environment variables, not source files.
- Use local/Ollama for offline demos.
- Implement OpenAI methods before documenting OpenAI as supported.
- Add provider health checks for production deployments.
