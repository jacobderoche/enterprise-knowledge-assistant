"""Health and readiness endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from ..config import get_settings
from ..rag.graph import _HAS_LANGGRAPH

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "environment": settings.environment,
        "llm_provider": settings.llm_provider,
        "embedding_provider": settings.embedding_provider,
        "vector_store": "pgvector" if settings.use_pgvector else "in-memory",
        "langgraph": _HAS_LANGGRAPH,
    }
