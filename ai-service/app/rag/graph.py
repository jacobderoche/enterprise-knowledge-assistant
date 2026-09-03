"""RAG orchestration built as a LangGraph state graph.

The graph has two nodes:

    retrieve -> generate

``retrieve`` performs permission-aware vector search; ``generate`` calls the
configured LLM with the retrieved context to produce a grounded, cited answer.

If ``langgraph`` is not installed the same nodes are executed by a lightweight
sequential fallback, so the service remains runnable in constrained
environments while preserving identical behaviour.
"""
from __future__ import annotations

from typing import Any, TypedDict

from ..config import Settings, get_settings
from ..models import get_embedder, get_llm
from ..models.llm import ContextPassage
from ..schemas import AccessContext, Citation, QueryResponse
from .chunking import chunk_text
from .vectorstore import StoredChunk, get_vector_store, new_chunk_id

try:  # pragma: no cover - exercised only when langgraph is installed
    from langgraph.graph import END, START, StateGraph

    _HAS_LANGGRAPH = True
except Exception:  # pragma: no cover
    _HAS_LANGGRAPH = False


class RagState(TypedDict, total=False):
    query: str
    access: AccessContext
    top_k: int
    passages: list[ContextPassage]
    answer: str
    model: str


class RagPipeline:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.embedder = get_embedder(self.settings)
        self.llm = get_llm(self.settings)
        self.store = get_vector_store(self.settings)
        self._graph = self._build_graph() if _HAS_LANGGRAPH else None

    # ----- graph nodes -------------------------------------------------
    def _retrieve(self, state: RagState) -> RagState:
        query = state["query"]
        access = state["access"]
        top_k = state.get("top_k") or self.settings.top_k
        embedding = self.embedder.embed_one(query)
        hits = self.store.search(embedding, access.allowed_scopes, top_k)
        passages = [
            ContextPassage(
                marker=i + 1,
                chunk_id=h.chunk.chunk_id,
                document_id=h.chunk.document_id,
                source=h.chunk.source,
                text=h.chunk.text,
                score=h.score,
            )
            for i, h in enumerate(hits)
        ]
        return {"passages": passages}

    def _generate(self, state: RagState) -> RagState:
        passages = state.get("passages", [])
        answer = self.llm.generate(state["query"], passages)
        return {"answer": answer, "model": self.llm.name}

    def _build_graph(self):
        graph = StateGraph(RagState)
        graph.add_node("retrieve", self._retrieve)
        graph.add_node("generate", self._generate)
        graph.add_edge(START, "retrieve")
        graph.add_edge("retrieve", "generate")
        graph.add_edge("generate", END)
        return graph.compile()

    # ----- public API --------------------------------------------------
    def ingest(
        self,
        document_id: str,
        source: str,
        content: str,
        scope: str,
        metadata: dict[str, Any] | None = None,
    ) -> list[StoredChunk]:
        pieces = chunk_text(content, self.settings.chunk_size, self.settings.chunk_overlap)
        embeddings = self.embedder.embed(pieces) if pieces else []
        chunks = [
            StoredChunk(
                chunk_id=new_chunk_id(),
                document_id=document_id,
                source=source,
                scope=scope,
                ordinal=i,
                text=piece,
                embedding=emb,
                metadata=metadata or {},
            )
            for i, (piece, emb) in enumerate(zip(pieces, embeddings))
        ]
        if chunks:
            self.store.upsert(chunks)
        return chunks

    def query(
        self,
        query: str,
        access: AccessContext,
        top_k: int | None = None,
        conversation_id: str | None = None,
    ) -> QueryResponse:
        initial: RagState = {"query": query, "access": access, "top_k": top_k or self.settings.top_k}
        if self._graph is not None:
            final: RagState = self._graph.invoke(initial)
        else:
            final = {**initial}
            final.update(self._retrieve(final))
            final.update(self._generate(final))

        passages = final.get("passages", [])
        citations = [
            Citation(
                chunk_id=p.chunk_id,
                document_id=p.document_id,
                source=p.source,
                score=round(p.score, 4),
                snippet=(p.text[:280] + "...") if len(p.text) > 280 else p.text,
            )
            for p in passages
        ]
        return QueryResponse(
            answer=final.get("answer", ""),
            citations=citations,
            conversation_id=conversation_id,
            model=final.get("model", self.llm.name),
            used_context=bool(passages),
        )

    def stream(self, query: str, access: AccessContext, top_k: int | None = None):
        """Yield the answer token-by-token for SSE streaming."""
        result = self.query(query, access, top_k)
        for token in result.answer.split(" "):
            yield token + " "


_pipeline: RagPipeline | None = None


def get_pipeline() -> RagPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = RagPipeline()
    return _pipeline


def reset_pipeline() -> None:
    global _pipeline
    _pipeline = None
