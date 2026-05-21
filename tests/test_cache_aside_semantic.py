"""
Cache-aside flow tests for POST /api/v1/cache/semantic/search.

Scenario A: cache hit — external LLM not called.
Scenario B: cache miss — LLM called once, response written back.
Scenario C: cache lookup failure — treated as miss, LLM fallback succeeds.
"""

import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

# Avoid loading real API Settings (.env may contain fields not on Settings model)
if "src.api.config" not in sys.modules:
    _mock_config = MagicMock()
    _mock_config.settings = MagicMock(
        JWT_SECRET_KEY="test-secret",
        JWT_ALGORITHM="HS256",
        JWT_EXPIRATION_HOURS=24,
    )
    sys.modules["src.api.config"] = _mock_config

from src.api.routes.cache import SemanticCacheRequest, semantic_cache_search
from src.cache.base import CacheEntry, CacheHitReason
from src.cache.cache_manager import SemanticSearchResult


def _make_request(cache_manager, llm_service=None):
    request = MagicMock()
    request.app.state.cache_manager = cache_manager
    request.app.state.llm_service = llm_service
    return request


def _cache_hit_result(response_text: str = "cached answer") -> SemanticSearchResult:
    entry = CacheEntry(
        query_id="tenant_001:abc123",
        query_text="What is Python?",
        embedding=[0.1] * 384,
        response=response_text,
    )
    return SemanticSearchResult(
        entry=entry,
        similarity=0.95,
        hit_source="L1",
        hit_reason=CacheHitReason.SEMANTIC_MATCH,
        is_exact_match=False,
        domain="general",
        threshold_used=0.85,
    )


@pytest.mark.asyncio
async def test_scenario_a_cache_hit_no_llm():
    """Cache hit: return cached data without calling external LLM."""
    cache_manager = MagicMock()
    cache_manager.get_semantic_async = AsyncMock(return_value=_cache_hit_result())

    llm_service = MagicMock()
    llm_service.generate_response = AsyncMock(return_value="should not be used")

    request = _make_request(cache_manager, llm_service)
    body = SemanticCacheRequest(query="What is Python?")

    response = await semantic_cache_search(
        request=request,
        body=body,
        current_user=MagicMock(),
        tenant_id="tenant_001",
    )

    assert response.hit is True
    assert response.response == "cached answer"
    assert response.hit_reason == "semantic_match"
    llm_service.generate_response.assert_not_called()
    cache_manager.put_semantic_async.assert_not_called()


@pytest.mark.asyncio
async def test_scenario_b_cache_miss_llm_and_write_back():
    """Cache miss: invoke LLM once, write back, return generated response."""
    cache_manager = MagicMock()
    cache_manager.get_semantic_async = AsyncMock(return_value=None)
    cache_manager.put_semantic_async = AsyncMock(return_value=True)

    llm_service = MagicMock()
    llm_service.generate_response = AsyncMock(return_value="LLM generated answer")

    request = _make_request(cache_manager, llm_service)
    body = SemanticCacheRequest(query="What is Rust?")

    response = await semantic_cache_search(
        request=request,
        body=body,
        current_user=MagicMock(),
        tenant_id="tenant_001",
    )

    assert response.hit is False
    assert response.response == "LLM generated answer"
    assert response.hit_reason == "miss_llm_generated"
    llm_service.generate_response.assert_called_once_with("What is Rust?")
    cache_manager.put_semantic_async.assert_called_once_with(
        query_text="What is Rust?",
        response="LLM generated answer",
        tenant_id="tenant_001",
        domain=None,
        metadata={"source": "llm_generated"},
    )


@pytest.mark.asyncio
async def test_scenario_c_cache_lookup_error_falls_back_to_llm():
    """Cache lookup exception: treat as miss and fall back to external LLM."""
    cache_manager = MagicMock()
    cache_manager.get_semantic_async = AsyncMock(
        side_effect=ConnectionError("Redis connection refused")
    )
    cache_manager.put_semantic_async = AsyncMock(return_value=True)

    llm_service = MagicMock()
    llm_service.generate_response = AsyncMock(return_value="Fallback from LLM")

    request = _make_request(cache_manager, llm_service)
    body = SemanticCacheRequest(query="Explain caching")

    response = await semantic_cache_search(
        request=request,
        body=body,
        current_user=MagicMock(),
        tenant_id="tenant_001",
    )

    assert response.hit is False
    assert response.response == "Fallback from LLM"
    assert response.hit_reason == "miss_llm_generated"
    llm_service.generate_response.assert_called_once_with("Explain caching")
    cache_manager.put_semantic_async.assert_called_once()


@pytest.mark.asyncio
async def test_cache_miss_skips_write_on_llm_error_prefix():
    """Do not cache responses that start with 'Error:'."""
    cache_manager = MagicMock()
    cache_manager.get_semantic_async = AsyncMock(return_value=None)

    llm_service = MagicMock()
    llm_service.generate_response = AsyncMock(
        return_value="Error: Local LLM service is not available."
    )

    request = _make_request(cache_manager, llm_service)
    body = SemanticCacheRequest(query="broken llm query")

    response = await semantic_cache_search(
        request=request,
        body=body,
        current_user=MagicMock(),
        tenant_id="tenant_001",
    )

    assert response.hit is False
    assert response.response is None
    assert response.hit_reason == "miss"
    cache_manager.put_semantic_async.assert_not_called()
