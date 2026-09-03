"""Document ingestion endpoint."""
from __future__ import annotations

from fastapi import APIRouter

from ..rag.graph import get_pipeline
from ..schemas import IngestChunkResult, IngestRequest, IngestResponse

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("", response_model=IngestResponse)
def ingest(req: IngestRequest) -> IngestResponse:
    pipeline = get_pipeline()
    chunks = pipeline.ingest(
        document_id=req.document_id,
        source=req.source,
        content=req.content,
        scope=req.scope,
        metadata=req.metadata,
    )
    return IngestResponse(
        document_id=req.document_id,
        chunks=[IngestChunkResult(chunk_id=c.chunk_id, ordinal=c.ordinal) for c in chunks],
        chunk_count=len(chunks),
    )
