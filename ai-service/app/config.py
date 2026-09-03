"""Runtime configuration loaded from environment variables.

Kept dependency-free (plain os.environ) so the service starts even in a
minimal environment. All external integrations degrade gracefully to
offline/in-memory implementations when their configuration is absent.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache


def _get_bool(key: str, default: bool = False) -> bool:
    val = os.environ.get(key)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Application settings resolved from the environment."""

    app_name: str = "knowledge-assistant-ai"
    environment: str = field(default_factory=lambda: os.environ.get("ENVIRONMENT", "local"))

    # LLM / embedding providers: "openai", "anthropic", "bedrock" or "offline".
    llm_provider: str = field(default_factory=lambda: os.environ.get("LLM_PROVIDER", "offline"))
    embedding_provider: str = field(
        default_factory=lambda: os.environ.get("EMBEDDING_PROVIDER", "offline")
    )
    openai_api_key: str | None = field(default_factory=lambda: os.environ.get("OPENAI_API_KEY"))
    anthropic_api_key: str | None = field(
        default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY")
    )
    openai_model: str = field(default_factory=lambda: os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))
    anthropic_model: str = field(
        default_factory=lambda: os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
    )
    embedding_model: str = field(
        default_factory=lambda: os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
    )
    embedding_dim: int = field(default_factory=lambda: int(os.environ.get("EMBEDDING_DIM", "256")))

    # Vector store. When DATABASE_URL is set, pgvector is used; else in-memory.
    database_url: str | None = field(default_factory=lambda: os.environ.get("DATABASE_URL"))

    # Retrieval tuning.
    top_k: int = field(default_factory=lambda: int(os.environ.get("RAG_TOP_K", "4")))
    chunk_size: int = field(default_factory=lambda: int(os.environ.get("RAG_CHUNK_SIZE", "800")))
    chunk_overlap: int = field(
        default_factory=lambda: int(os.environ.get("RAG_CHUNK_OVERLAP", "120"))
    )

    # Observability.
    otel_enabled: bool = field(default_factory=lambda: _get_bool("OTEL_ENABLED", False))
    langsmith_enabled: bool = field(default_factory=lambda: _get_bool("LANGSMITH_TRACING", False))

    @property
    def use_pgvector(self) -> bool:
        return bool(self.database_url)


@lru_cache
def get_settings() -> Settings:
    return Settings()
