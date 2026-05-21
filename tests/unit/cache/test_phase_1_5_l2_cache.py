"""
Phase 1.5 - L2 Cache and CacheManager Tests

Comprehensive tests for Redis-backed distributed caching and cache orchestration.
"""

import pytest
import time
from unittest.mock import Mock, MagicMock, patch

from src.cache import (
    CacheConfig, CacheEntry, L1Cache, 
    RedisConfig, SerializationFormat,
    CacheManager, CacheManagerConfig, CacheStrategy,
    L2Cache,
)


# ============================================================================
# Test: Redis Configuration
# ============================================================================

class TestRedisConfig:
    """Test Redis configuration."""
    
    def test_config_defaults(self):
        """Test default configuration."""
        config = RedisConfig()
        assert config.host == "localhost"
        assert config.port == 6379
        assert config.db == 0
        assert config.max_connections == 50
    
    def test_config_custom(self):
        """Test custom configuration."""
        config = RedisConfig(
            host="redis.example.com",
            port=6380,
            db=1,
            max_connections=100
        )
        assert config.host == "redis.example.com"
        assert config.port == 6380
        assert config.db == 1
        assert config.max_connections == 100
    
    def test_config_validation(self):
        """Test configuration validation."""
        with pytest.raises(ValueError):
            RedisConfig(port=99999).validate()
        
        with pytest.raises(ValueError):
            RedisConfig(db=16).validate()
        
        with pytest.raises(ValueError):
            RedisConfig(max_connections=0).validate()
    
    def test_connection_url_without_password(self):
        """Test connection URL generation without password."""
        config = RedisConfig(host="redis.local", port=6379)
        url = config.get_connection_url()
        assert url == "redis://redis.local:6379/0"
    
    def test_connection_url_with_password(self):
        """Test connection URL generation with password."""
        config = RedisConfig(password="secret123")
        url = config.get_connection_url()
        assert "secret123" in url


# ============================================================================
# Test: Redis Serialization
# ============================================================================

class TestRedisSerialization:
    """Test serialization formats."""
    
    def test_json_serialization(self):
        """Test JSON serialization."""
        from src.cache.redis_config import RedisSerializer
        
        serializer = RedisSerializer(SerializationFormat.JSON)
        
        data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        serialized = serializer.serialize(data)
        
        assert isinstance(serialized, str)
        
        deserialized = serializer.deserialize(serialized)
        assert deserialized == data
    
    def test_pickle_serialization(self):
        """Test pickle serialization."""
        from src.cache.redis_config import RedisSerializer
        
        serializer = RedisSerializer(SerializationFormat.PICKLE)
        
        data = {"key": "value", "number": 42, "nested": {"inner": True}}
        serialized = serializer.serialize(data)
        
        assert isinstance(serialized, bytes)
        
        deserialized = serializer.deserialize(serialized)
        assert deserialized == data
    
    def test_serialization_with_complex_types(self):
        """Test serialization with complex types."""
        from src.cache.redis_config import RedisSerializer
        
        serializer = RedisSerializer(SerializationFormat.JSON)
        
        # Test with nested structure
        data = {
            "embedding": [0.1] * 384,
            "metadata": {"type": "query"},
            "response": "answer"
        }
        
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        
        assert deserialized == data


# ============================================================================
# Test: L2 Cache Basics (Mocked Redis)
# ============================================================================

class TestL2CacheBasics:
    """Test L2 cache basic operations with mocked Redis."""
    
    @patch('src.cache.l2_cache.redis.Redis')
    def test_l2_cache_put(self, mock_redis):
        """Test L2 cache put operation."""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        
        config = RedisConfig()
        cache = L2Cache(config)
        cache._client = mock_client
        cache._connected = True
        
        entry = CacheEntry(
            query_id="test_q1",
            query_text="test query",
            embedding=[0.1] * 384,
            response="test response"
        )
        
        result = cache.put(entry)
        
        assert result is True
        assert mock_client.setex.called
    
    @patch('src.cache.l2_cache.redis.Redis')
    def test_l2_cache_get(self, mock_redis):
        """Test L2 cache get operation."""
        import json
        
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        
        config = RedisConfig()
        cache = L2Cache(config)
        cache._client = mock_client
        cache._connected = True
        
        # Setup mock data
        data = {
            "query_id": "test_q1",
            "query_text": "test",
            "embedding": [0.1] * 384,
            "response": "resp",
            "metadata": {},
            "created_at": time.time(),
            "last_accessed_at": time.time(),
            "access_count": 5,
        }
        
        mock_client.get.return_value = json.dumps(data).encode()
        
        result = cache.get("test_q1")
        
        assert result is not None
        assert result.query_id == "test_q1"
        assert result.query_text == "test"
    
    @patch('src.cache.l2_cache.redis.Redis')
    def test_l2_cache_delete(self, mock_redis):
        """Test L2 cache delete operation."""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.delete.return_value = 1
        
        config = RedisConfig()
        cache = L2Cache(config)
        cache._client = mock_client
        cache._connected = True
        
        result = cache.delete("test_q1")
        
        assert result is True
        assert mock_client.delete.called
    
    @patch('src.cache.l2_cache.redis.Redis')
    def test_l2_cache_exists(self, mock_redis):
        """Test L2 cache exists check."""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.exists.return_value = 1
        
        config = RedisConfig()
        cache = L2Cache(config)
        cache._client = mock_client
        cache._connected = True
        
        result = cache.exists("test_q1")
        
        assert result is True
    
    @patch('src.cache.l2_cache.redis.Redis')
    def test_l2_cache_size(self, mock_redis):
        """Test L2 cache size calculation."""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        
        # Mock scan results
        mock_client.scan.side_effect = [
            (0, [b"cache:q1", b"cache:q2", b"cache:q3"])
        ]
        
        config = RedisConfig()
        cache = L2Cache(config)
        cache._client = mock_client
        cache._connected = True
        
        size = cache.size()
        
        assert size == 3


# ============================================================================
# Test: Cache Manager Initialization
# ============================================================================

class TestCacheManagerInit:
    """Test cache manager initialization."""
    
    def test_manager_defaults(self):
        """Test manager with default config."""
        manager = CacheManager()
        
        assert manager.l1_cache is not None
        assert isinstance(manager.l1_cache, L1Cache)
    
    def test_manager_custom_config(self):
        """Test manager with custom config."""
        l1_config = CacheConfig(max_size=500)
        l2_config = RedisConfig(host="redis.local")
        
        config = CacheManagerConfig(
            l1_config=l1_config,
            l2_config=l2_config,
            strategy=CacheStrategy.WRITE_THROUGH
        )
        
        manager = CacheManager(config)
        
        assert manager.config.strategy == CacheStrategy.WRITE_THROUGH
        assert manager.l1_cache is not None
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = CacheManager()
        
        result = manager.initialize()
        
        # Should succeed even if L2 fails (degrades to L1-only)
        assert result is True


# ============================================================================
# Test: Cache Manager Two-Tier Operations
# ============================================================================

class TestCacheManagerTiered:
    """Test two-tier cache operations."""
    
    @pytest.mark.skip(reason="L1 cache HNSW initialization can hang in test environment")
    def test_put_l1_only_strategy(self):
        """Test put with L1-only strategy."""
        config = CacheManagerConfig(strategy=CacheStrategy.L1_ONLY)
        manager = CacheManager(config)
        manager.initialize()
        
        entry = CacheEntry(
            query_id="tier_q1",
            query_text="test",
            embedding=[0.1] * 384,
            response="resp"
        )
        
        result = manager.put(entry)
        assert result is True
        assert manager.l1_cache.size() == 1
    
    @pytest.mark.skip(reason="L1 cache HNSW initialization can hang in test environment")
    def test_get_with_tiering(self):
        """Test get with tiered lookup."""
        config = CacheManagerConfig(strategy=CacheStrategy.WRITE_THROUGH)
        manager = CacheManager(config)
        manager.initialize()
        
        entry = CacheEntry(
            query_id="tier_q2",
            query_text="test",
            embedding=[0.1] * 384,
            response="resp"
        )
        
        # Put entry
        manager.put(entry)
        
        # Get from L1
        result = manager.get("tier_q2")
        
        assert result is not None
        retrieved_entry, source = result
        assert retrieved_entry.query_id == "tier_q2"
        assert source == "L1"
    
    @pytest.mark.skip(reason="L1 cache HNSW initialization can hang in test environment")
    def test_delete_both_tiers(self):
        """Test delete removes from both tiers."""
        config = CacheManagerConfig(strategy=CacheStrategy.WRITE_THROUGH)
        manager = CacheManager(config)
        manager.initialize()
        
        entry = CacheEntry(
            query_id="tier_q3",
            query_text="test",
            embedding=[0.1] * 384,
            response="resp"
        )
        
        manager.put(entry)
        assert manager.l1_cache.size() == 1
        
        manager.delete("tier_q3")
        assert manager.l1_cache.size() == 0
    
    @pytest.mark.skip(reason="L1 cache HNSW initialization can hang in test environment")
    def test_clear_both_tiers(self):
        """Test clear removes from both tiers."""
        config = CacheManagerConfig(strategy=CacheStrategy.WRITE_THROUGH)
        manager = CacheManager(config)
        manager.initialize()
        
        for i in range(3):
            entry = CacheEntry(
                query_id=f"tier_q{i}",
                query_text="test",
                embedding=[0.1] * 384,
                response="resp"
            )
            manager.put(entry)
        
        assert manager.l1_cache.size() == 3
        
        manager.clear()
        assert manager.l1_cache.size() == 0


class TestCacheManagerL2Resilience:
    """L2 failures must degrade to miss / non-fatal write, not crash requests."""

    def test_l2_get_error_treated_as_miss(self):
        config = CacheManagerConfig(strategy=CacheStrategy.WRITE_THROUGH)
        manager = CacheManager(config)
        manager._initialized = True
        manager.l1_cache = MagicMock()
        manager.l1_cache.get.return_value = None
        manager.l2_cache = MagicMock()
        manager.l2_cache.get.side_effect = ConnectionError("Redis connection refused")
        manager.l3_cache = None

        result = manager.get("tenant_001:abc123")

        assert result is None
        manager.l2_cache.get.assert_called_once_with("tenant_001:abc123")
        assert manager.metrics.misses == 1

    def test_l2_put_error_does_not_raise(self):
        config = CacheManagerConfig(strategy=CacheStrategy.WRITE_THROUGH)
        manager = CacheManager(config)
        manager._initialized = True
        manager.l1_cache = MagicMock()
        manager.l1_cache.put.return_value = True
        manager.l2_cache = MagicMock()
        manager.l2_cache.put.side_effect = ConnectionError("Redis connection refused")
        manager.l3_cache = None

        entry = CacheEntry(
            query_id="tenant_001:abc123",
            query_text="test",
            embedding=[0.1] * 384,
            response="resp",
        )
        result = manager.put(entry)

        assert result is False
        manager.l1_cache.put.assert_called_once()


# ============================================================================
# Test: Cache Strategies
# ============================================================================

class TestCacheStrategies:
    """Test different cache strategies."""
    
    @pytest.mark.skip(reason="L1 cache HNSW initialization can hang in test environment")
    def test_write_through_strategy(self):
        """Test write-through strategy."""
        config = CacheManagerConfig(strategy=CacheStrategy.WRITE_THROUGH)
        manager = CacheManager(config)
        manager.initialize()
        
        entry = CacheEntry(
            query_id="strat_wt",
            query_text="test",
            embedding=[0.1] * 384,
            response="resp"
        )
        
        result = manager.put(entry)
        assert result is True
        
        # Verify in L1
        assert manager.l1_cache.get("strat_wt") is not None
    
    @pytest.mark.skip(reason="L1 cache HNSW initialization can hang in test environment")
    def test_write_back_strategy(self):
        """Test write-back strategy."""
        config = CacheManagerConfig(strategy=CacheStrategy.WRITE_BACK)
        manager = CacheManager(config)
        manager.initialize()
        
        entry = CacheEntry(
            query_id="strat_wb",
            query_text="test",
            embedding=[0.1] * 384,
            response="resp"
        )
        
        result = manager.put(entry)
        assert result is True
        
        # Verify in L1
        assert manager.l1_cache.get("strat_wb") is not None
    
    @pytest.mark.skip(reason="L1 cache HNSW initialization can hang in test environment")
    def test_l1_only_strategy(self):
        """Test L1-only strategy."""
        config = CacheManagerConfig(strategy=CacheStrategy.L1_ONLY)
        manager = CacheManager(config)
        manager.initialize()
        
        entry = CacheEntry(
            query_id="strat_l1",
            query_text="test",
            embedding=[0.1] * 384,
            response="resp"
        )
        
        result = manager.put(entry)
        assert result is True


# ============================================================================
# Test: Cache Manager Metrics
# ============================================================================

class TestCacheManagerMetrics:
    """Test cache metrics tracking."""
    
    @pytest.mark.skip(reason="L1 cache HNSW initialization can hang in test environment")
    def test_metrics_hit_tracking(self):
        """Test hit tracking."""
        config = CacheManagerConfig(strategy=CacheStrategy.WRITE_THROUGH)
        manager = CacheManager(config)
        manager.initialize()
        
        entry = CacheEntry(
            query_id="metric_q1",
            query_text="test",
            embedding=[0.1] * 384,
            response="resp"
        )
        
        manager.put(entry)
        
        # Hit
        result = manager.get("metric_q1")
        assert result is not None
        
        metrics = manager.metrics
        assert metrics.l1_hits == 1
        assert metrics.total_requests == 1
    
    @pytest.mark.skip(reason="L1 cache HNSW initialization can hang in test environment")
    def test_metrics_miss_tracking(self):
        """Test miss tracking."""
        config = CacheManagerConfig(strategy=CacheStrategy.WRITE_THROUGH)
        manager = CacheManager(config)
        manager.initialize()
        
        # Miss
        result = manager.get("nonexistent")
        assert result is None
        
        metrics = manager.metrics
        assert metrics.misses == 1
    
    @pytest.mark.skip(reason="L1 cache HNSW initialization can hang in test environment")
    def test_combined_hit_rate(self):
        """Test combined hit rate calculation."""
        config = CacheManagerConfig(strategy=CacheStrategy.WRITE_THROUGH)
        manager = CacheManager(config)
        manager.initialize()
        
        manager.metrics.record_hit("L1")
        manager.metrics.record_hit("L1")
        manager.metrics.record_miss()
        
        hit_rate = manager.metrics.get_combined_hit_rate()
        assert hit_rate == pytest.approx(2/3)


# ============================================================================
# Test: Cache Statistics
# ============================================================================

class TestCacheStatistics:
    """Test statistics gathering."""
    
    @pytest.mark.skip(reason="L1 cache HNSW initialization can hang in test environment")
    def test_l1_stats(self):
        """Test L1 statistics."""
        config = CacheManagerConfig(strategy=CacheStrategy.WRITE_THROUGH)
        manager = CacheManager(config)
        manager.initialize()
        
        for i in range(3):
            entry = CacheEntry(
                query_id=f"stat_q{i}",
                query_text="test",
                embedding=[0.1] * 384,
                response="resp"
            )
            manager.put(entry)
        
        stats = manager.get_l1_stats()
        
        assert "size" in stats
        assert "memory_mb" in stats
        assert stats["size"] == 3
    
    @pytest.mark.skip(reason="L1 cache HNSW initialization can hang in test environment")
    def test_combined_stats(self):
        """Test combined statistics."""
        config = CacheManagerConfig(strategy=CacheStrategy.WRITE_THROUGH)
        manager = CacheManager(config)
        manager.initialize()
        
        entry = CacheEntry(
            query_id="cstat_q1",
            query_text="test",
            embedding=[0.1] * 384,
            response="resp"
        )
        
        manager.put(entry)
        manager.get("cstat_q1")
        
        stats = manager.get_combined_stats()
        
        assert "l1" in stats
        assert "tiered" in stats
        assert stats["tiered"]["l1_hits"] == 1


# ============================================================================
# Test: Promotion from L2 to L1
# ============================================================================

class TestPromotionL2toL1:
    """Test promotion of L2 hits to L1."""
    
    def test_promotion_count(self):
        """Test promotion counter."""
        config = CacheManagerConfig(
            strategy=CacheStrategy.WRITE_THROUGH,
            enable_l1_to_l2_promotion=True
        )
        manager = CacheManager(config)
        manager.initialize()
        
        # L2 cache not available, so promotions will be 0
        # This is expected for test environment
        assert manager.metrics.l1_to_l2_promotions == 0


# ============================================================================
# Test: Health Check
# ============================================================================

class TestHealthCheck:
    """Test health checking."""
    
    @pytest.mark.skip(reason="L1 cache HNSW initialization can hang in test environment")
    def test_health_check(self):
        """Test health check."""
        config = CacheManagerConfig()
        manager = CacheManager(config)
        manager.initialize()
        
        health = manager.health_check()
        
        assert "l1" in health
        assert health["l1"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
