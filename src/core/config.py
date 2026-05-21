"""
Configuration management for Semantic Cache system.

Handles loading and validation of configuration from YAML, environment variables, and CLI.
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from dataclasses import dataclass, field, asdict
from dotenv import load_dotenv

from src.core.exceptions import ConfigurationError, ConfigurationValidationError
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Load environment variables from .env file
load_dotenv()


@dataclass
class L1CacheConfig:
    """L1 Cache (In-Memory) configuration."""

    type: str = "hnsw"
    max_entries: int = 100000
    dimension: int = 384
    ef_construction: int = 200
    ef_search: int = 100

    def validate(self) -> None:
        """Validate L1 configuration."""
        if self.max_entries < 1000:
            raise ConfigurationValidationError(
                "l1.max_entries", "Must be at least 1000"
            )
        if self.dimension < 32:
            raise ConfigurationValidationError("l1.dimension", "Must be at least 32")


@dataclass
class L2CacheConfig:
    """L2 Cache (SSD) configuration."""

    type: str = "faiss"
    max_entries: int = 1000000
    index_type: str = "IVF"
    nlist: int = 1000

    def validate(self) -> None:
        """Validate L2 configuration."""
        if self.max_entries < 10000:
            raise ConfigurationValidationError(
                "l2.max_entries", "Must be at least 10000"
            )


@dataclass
class L3CacheConfig:
    """L3 Cache (Disk) configuration."""

    type: str = "disk"
    max_entries: int = 10000000
    quantization: str = "int8"
    storage_path: str = "./data/l3_cache"

    def validate(self) -> None:
        """Validate L3 configuration."""
        if self.max_entries < 100000:
            raise ConfigurationValidationError(
                "l3.max_entries", "Must be at least 100000"
            )


@dataclass
class CacheConfig:
    """Cache configuration."""

    l1: L1CacheConfig = field(default_factory=L1CacheConfig)
    l2: L2CacheConfig = field(default_factory=L2CacheConfig)
    l3: L3CacheConfig = field(default_factory=L3CacheConfig)

    def validate(self) -> None:
        """Validate cache configuration."""
        self.l1.validate()
        self.l2.validate()
        self.l3.validate()


@dataclass
class EmbeddingConfig:
    """Embedding service configuration."""

    model: str = "sentence-transformers/all-MiniLM-L6-v2"
    dimension: int = 384
    batch_size: int = 32
    provider: str = "local"  # local, openai, cohere, huggingface
    cache_embeddings: bool = True

    def validate(self) -> None:
        """Validate embedding configuration."""
        if self.dimension < 32:
            raise ConfigurationValidationError(
                "embedding.dimension", "Must be at least 32"
            )
        if self.batch_size < 1:
            raise ConfigurationValidationError(
                "embedding.batch_size", "Must be at least 1"
            )
        if self.provider not in ["local", "openai", "cohere", "huggingface"]:
            raise ConfigurationValidationError(
                "embedding.provider",
                f"Must be one of: local, openai, cohere, huggingface",
            )


@dataclass
class SimilarityConfig:
    """Similarity search configuration."""

    default_threshold: float = 0.85
    metric: str = "cosine"
    adaptive_thresholds: Dict[str, float] = field(
        default_factory=lambda: {
            "medical": 0.95,
            "legal": 0.92,
            "ecommerce": 0.80,
            "general": 0.85,
        }
    )

    def validate(self) -> None:
        """Validate similarity configuration."""
        if not 0.0 <= self.default_threshold <= 1.0:
            raise ConfigurationValidationError(
                "similarity.default_threshold", "Must be between 0 and 1"
            )
        if self.metric not in ["cosine", "euclidean", "inner_product"]:
            raise ConfigurationValidationError(
                "similarity.metric",
                "Must be one of: cosine, euclidean, inner_product",
            )
        for domain, threshold in self.adaptive_thresholds.items():
            if not 0.0 <= threshold <= 1.0:
                raise ConfigurationValidationError(
                    f"similarity.adaptive_thresholds.{domain}",
                    "Must be between 0 and 1",
                )


@dataclass
class RedisConfig:
    """Redis configuration."""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ssl: bool = False
    max_connections: int = 50

    def validate(self) -> None:
        """Validate Redis configuration."""
        if self.port < 1 or self.port > 65535:
            raise ConfigurationValidationError("redis.port", "Invalid port number")
        if self.max_connections < 1:
            raise ConfigurationValidationError(
                "redis.max_connections", "Must be at least 1"
            )


@dataclass
class DatabaseConfig:
    """Database configuration."""

    url: str = "postgresql://user:password@localhost/semantic_cache"
    pool_size: int = 20
    max_overflow: int = 40
    echo: bool = False

    def validate(self) -> None:
        """Validate database configuration."""
        if not self.url:
            raise ConfigurationValidationError("database.url", "Database URL required")
        if self.pool_size < 1:
            raise ConfigurationValidationError("database.pool_size", "Must be at least 1")


@dataclass
class MultiTenancyConfig:
    """Multi-tenancy configuration."""

    enabled: bool = True
    isolation_level: str = "full"
    default_quota: Dict[str, Any] = field(
        default_factory=lambda: {
            "max_entries": 100000,
            "max_qps": 1000,
            "storage_gb": 10,
        }
    )


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""

    enabled: bool = True
    prometheus_port: int = 9090
    log_level: str = "INFO"
    metrics_interval_seconds: int = 60


@dataclass
class LLMConfig:
    """LLM service configuration."""

    provider: str = "gemini"
    api_key: Optional[str] = None
    model: str = "gemini-pro"
    
    # Local LLM (Ollama) configuration
    local_base_url: str = "http://localhost:11434"
    local_model: str = "qwen2.5:1.5b"
    local_temperature: float = 0.7
    local_timeout: float = 60.0
    local_stream_timeout: float = 120.0

    def validate(self) -> None:
        """Validate LLM configuration."""
        valid_providers = ["gemini", "openai", "local", "ollama"]
        if self.provider not in valid_providers:
            raise ConfigurationValidationError(
                "llm.provider", f"Must be one of: {', '.join(valid_providers)}"
            )
            
        # Validate local URL format if local provider is used
        if self.provider in ["local", "ollama"]:
            if not self.local_base_url.startswith(("http://", "https://")):
                raise ConfigurationValidationError(
                    "llm.local_base_url", "Must be a valid URL starting with http:// or https://"
                )


@dataclass
class APIConfig:
    """API configuration."""

    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    debug: bool = False


@dataclass
class SemanticCacheConfig:
    """Main configuration for Semantic Cache system."""

    api: APIConfig = field(default_factory=APIConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    similarity: SimilarityConfig = field(default_factory=SimilarityConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    multi_tenancy: MultiTenancyConfig = field(default_factory=MultiTenancyConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)

    def validate(self) -> None:
        """Validate entire configuration."""
        logger.debug("Validating configuration...")
        self.cache.validate()
        self.embedding.validate()
        self.similarity.validate()
        self.redis.validate()
        self.database.validate()
        self.llm.validate()
        logger.info("Configuration validated successfully")

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)


class ConfigLoader:
    """Load and manage application configuration."""

    def __init__(self, config_path: Optional[Path] = None, env: str = "development"):
        """Initialize config loader.

        Args:
            config_path: Path to YAML configuration file
            env: Environment (development, production, etc.)
        """
        self.env = env
        self.config_path = config_path or Path("config/default.yaml")
        self.config: SemanticCacheConfig = SemanticCacheConfig()

    def load(self) -> SemanticCacheConfig:
        """Load configuration from YAML and environment variables.

        Returns:
            SemanticCacheConfig instance

        Raises:
            ConfigurationError: If configuration loading or validation fails
        """
        try:
            # Load from YAML file
            if self.config_path.exists():
                logger.info(f"Loading configuration from {self.config_path}")
                self._load_yaml()
            else:
                logger.warning(f"Config file not found: {self.config_path}")

            # Override with environment variables
            self._load_env_vars()

            # Validate configuration
            self.config.validate()

            logger.info(f"Configuration loaded for environment: {self.env}")
            return self.config

        except ConfigurationError as e:
            logger.error(f"Configuration error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise ConfigurationError(f"Failed to load configuration: {e}")

    def _load_yaml(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path) as f:
                yaml_config = yaml.safe_load(f) or {}

            # Update config from YAML
            if "api" in yaml_config:
                self.config.api = APIConfig(**yaml_config["api"])
            if "cache" in yaml_config:
                cache_conf = yaml_config["cache"]
                self.config.cache = CacheConfig(
                    l1=L1CacheConfig(**cache_conf.get("l1", {})),
                    l2=L2CacheConfig(**cache_conf.get("l2", {})),
                    l3=L3CacheConfig(**cache_conf.get("l3", {})),
                )
            if "embedding" in yaml_config:
                self.config.embedding = EmbeddingConfig(**yaml_config["embedding"])
            if "similarity" in yaml_config:
                self.config.similarity = SimilarityConfig(**yaml_config["similarity"])
            if "redis" in yaml_config:
                self.config.redis = RedisConfig(**yaml_config["redis"])
            if "database" in yaml_config:
                self.config.database = DatabaseConfig(**yaml_config["database"])
            if "multi_tenancy" in yaml_config:
                self.config.multi_tenancy = MultiTenancyConfig(
                    **yaml_config["multi_tenancy"]
                )
            if "monitoring" in yaml_config:
                self.config.monitoring = MonitoringConfig(**yaml_config["monitoring"])
            # Added missing LLM YAML loading
            if "llm" in yaml_config:
                self.config.llm = LLMConfig(**yaml_config["llm"])

        except Exception as e:
            raise ConfigurationError(f"Failed to parse YAML configuration: {e}")

    def _load_env_vars(self) -> None:
        """Load configuration from environment variables."""
        # API configuration
        if api_host := os.getenv("API_HOST"):
            self.config.api.host = api_host
        if api_port := os.getenv("API_PORT"):
            self.config.api.port = int(api_port)
        if api_debug := os.getenv("API_DEBUG"):
            self.config.api.debug = api_debug.lower() == "true"

        # Redis configuration
        if redis_host := os.getenv("REDIS_HOST"):
            self.config.redis.host = redis_host
        if redis_port := os.getenv("REDIS_PORT"):
            self.config.redis.port = int(redis_port)

        # Database configuration
        if db_url := os.getenv("DATABASE_URL"):
            self.config.database.url = db_url

        # Embedding configuration
        if emb_model := os.getenv("EMBEDDING_MODEL"):
            self.config.embedding.model = emb_model
        if emb_provider := os.getenv("EMBEDDING_PROVIDER"):
            self.config.embedding.provider = emb_provider

        # Similarity configuration
        if sim_threshold := os.getenv("SIMILARITY_THRESHOLD"):
            self.config.similarity.default_threshold = float(sim_threshold)

        # Monitoring configuration
        if log_level := os.getenv("LOG_LEVEL"):
            self.config.monitoring.log_level = log_level

        # LLM configuration
        if llm_provider := os.getenv("LLM_PROVIDER"):
            self.config.llm.provider = llm_provider
        if llm_api_key := os.getenv("LLM_API_KEY"):
            self.config.llm.api_key = llm_api_key
        if llm_model := os.getenv("LLM_MODEL"):
            self.config.llm.model = llm_model
            
        # Local LLM (Ollama) configuration from ENV
        if local_base_url := os.getenv("LOCAL_LLM_BASE_URL"):
            self.config.llm.local_base_url = local_base_url
        if local_model := os.getenv("LOCAL_LLM_MODEL"):
            self.config.llm.local_model = local_model
        if local_temp := os.getenv("LOCAL_LLM_TEMPERATURE"):
            self.config.llm.local_temperature = float(local_temp)
        if local_timeout := os.getenv("LOCAL_LLM_TIMEOUT"):
            self.config.llm.local_timeout = float(local_timeout)
        if local_stream_timeout := os.getenv("LOCAL_LLM_STREAM_TIMEOUT"):
            self.config.llm.local_stream_timeout = float(local_stream_timeout)

        logger.debug("Environment variables applied to configuration")


def get_config(config_path: Optional[Path] = None) -> SemanticCacheConfig:
    """Get application configuration.

    Args:
        config_path: Optional path to YAML configuration file

    Returns:
        SemanticCacheConfig instance
    """
    loader = ConfigLoader(config_path=config_path)
    return loader.load()


# Module-level singleton — allows `from src.core.config import settings`
settings: SemanticCacheConfig = SemanticCacheConfig()