"""Query endpoints: structured cited answers and SSE streaming."""
from __future__ import annotations

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ..rag.graph import get_pipeline
from ..schemas import QueryRequest, QueryResponse

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    pipeline = get_pipeline()
    return pipeline.query(
        query=req.query,
        access=req.access,
        top_k=req.top_k,
        conversation_id=req.conversation_id,
    )


@router.post("/stream")
def query_stream(req: QueryRequest) -> StreamingResponse:
    pipeline = get_pipeline()
    result = pipeline.query(
        query=req.query,
        access=req.access,
        top_k=req.top_k,
        conversation_id=req.conversation_id,
    )

    def event_gen():
        # Stream the answer tokens first...
        for token in result.answer.split(" "):
            yield f"data: {json.dumps({'type': 'token', 'value': token + ' '})}\n\n"
        # ...then a final event carrying structured citations.
        payload = {
            "type": "done",
            "citations": [c.model_dump() for c in result.citations],
            "model": result.model,
            "used_context": result.used_context,
        }
        yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")
