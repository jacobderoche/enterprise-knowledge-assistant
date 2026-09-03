"""Pydantic request/response models shared across the API and RAG graph."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AccessContext(BaseModel):
    """Permission scope propagated from the Spring backend for permission-aware RAG."""

    user_id: str = Field(..., description="Subject id of the requesting user.")
    roles: list[str] = Field(default_factory=list)
    # Documents are tagged with these; retrieval is filtered to the intersection.
    allowed_scopes: list[str] = Field(
        default_factory=lambda: ["public"],
        description="ACL scopes the user may read (e.g. tenant or group ids).",
    )


class IngestChunkResult(BaseModel):
    chunk_id: str
    ordinal: int


class IngestRequest(BaseModel):
    document_id: str
    source: str = Field(..., description="Human-readable source name, e.g. filename.")
    content: str
    scope: str = Field("public", description="ACL scope tag applied to every chunk.")
    metadata: dict[str, Any] = Field(default_factory=dict)


class IngestResponse(BaseModel):
    document_id: str
    chunks: list[IngestChunkResult]
    chunk_count: int


class Citation(BaseModel):
    chunk_id: str
    document_id: str
    source: str
    score: float
    snippet: str


class QueryRequest(BaseModel):
    query: str
    access: AccessContext
    top_k: int | None = Field(default=None, ge=1, le=20)
    conversation_id: str | None = None


class QueryResponse(BaseModel):
    """Structured, cited answer."""

    answer: str
    citations: list[Citation]
    conversation_id: str | None = None
    model: str
    used_context: bool
