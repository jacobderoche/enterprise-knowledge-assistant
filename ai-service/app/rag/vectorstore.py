"""Vector store abstraction with pgvector and in-memory implementations.

Both implementations support permission-aware retrieval: a chunk is only
returned if its ``scope`` is in the caller's ``allowed_scopes``.
"""
from __future__ import annotations

import math
import threading
import uuid
from dataclasses import dataclass, field
from typing import Any, Protocol

from ..config import Settings, get_settings


@dataclass
class StoredChunk:
    chunk_id: str
    document_id: str
    source: str
    scope: str
    ordinal: int
    text: str
    embedding: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchHit:
    chunk: StoredChunk
    score: float


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class VectorStore(Protocol):
    def upsert(self, chunks: list[StoredChunk]) -> None: ...

    def search(
        self, embedding: list[float], allowed_scopes: list[str], top_k: int
    ) -> list[SearchHit]: ...

    def delete_document(self, document_id: str) -> int: ...


class InMemoryVectorStore:
    """Thread-safe in-memory store; ideal for local dev and tests."""

    def __init__(self) -> None:
        self._chunks: dict[str, StoredChunk] = {}
        self._lock = threading.Lock()

    def upsert(self, chunks: list[StoredChunk]) -> None:
        with self._lock:
            for c in chunks:
                self._chunks[c.chunk_id] = c

    def search(
        self, embedding: list[float], allowed_scopes: list[str], top_k: int
    ) -> list[SearchHit]:
        allowed = set(allowed_scopes)
        with self._lock:
            candidates = [c for c in self._chunks.values() if c.scope in allowed]
        hits = [SearchHit(c, cosine_similarity(embedding, c.embedding)) for c in candidates]
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:top_k]

    def delete_document(self, document_id: str) -> int:
        with self._lock:
            to_remove = [k for k, v in self._chunks.items() if v.document_id == document_id]
            for k in to_remove:
                del self._chunks[k]
        return len(to_remove)


class PgVectorStore:
    """PostgreSQL + pgvector backed store (lazy psycopg import)."""

    def __init__(self, dsn: str, dim: int) -> None:
        import psycopg  # type: ignore
        from pgvector.psycopg import register_vector  # type: ignore

        self._psycopg = psycopg
        self._register_vector = register_vector
        self._dsn = dsn
        self._dim = dim
        self._init_schema()

    def _connect(self):
        conn = self._psycopg.connect(self._dsn, autocommit=True)
        self._register_vector(conn)
        return conn

    def _init_schema(self) -> None:
        with self._psycopg.connect(self._dsn, autocommit=True) as conn:
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    chunk_id    TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    source      TEXT NOT NULL,
                    scope       TEXT NOT NULL,
                    ordinal     INT  NOT NULL,
                    text        TEXT NOT NULL,
                    metadata    JSONB NOT NULL DEFAULT '{{}}',
                    embedding   vector({self._dim}) NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_chunks_document ON document_chunks(document_id)"
            )

    def upsert(self, chunks: list[StoredChunk]) -> None:
        import json

        with self._connect() as conn:
            with conn.cursor() as cur:
                for c in chunks:
                    cur.execute(
                        """
                        INSERT INTO document_chunks
                            (chunk_id, document_id, source, scope, ordinal, text, metadata, embedding)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (chunk_id) DO UPDATE SET
                            text = EXCLUDED.text,
                            embedding = EXCLUDED.embedding,
                            metadata = EXCLUDED.metadata
                        """,
                        (
                            c.chunk_id,
                            c.document_id,
                            c.source,
                            c.scope,
                            c.ordinal,
                            c.text,
                            json.dumps(c.metadata),
                            c.embedding,
                        ),
                    )

    def search(
        self, embedding: list[float], allowed_scopes: list[str], top_k: int
    ) -> list[SearchHit]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT chunk_id, document_id, source, scope, ordinal, text, metadata,
                       1 - (embedding <=> %s) AS score
                FROM document_chunks
                WHERE scope = ANY(%s)
                ORDER BY embedding <=> %s
                LIMIT %s
                """,
                (embedding, list(allowed_scopes), embedding, top_k),
            ).fetchall()
        hits: list[SearchHit] = []
        for r in rows:
            hits.append(
                SearchHit(
                    StoredChunk(
                        chunk_id=r[0],
                        document_id=r[1],
                        source=r[2],
                        scope=r[3],
                        ordinal=r[4],
                        text=r[5],
                        metadata=r[6] or {},
                        embedding=[],
                    ),
                    score=float(r[7]),
                )
            )
        return hits

    def delete_document(self, document_id: str) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM document_chunks WHERE document_id = %s", (document_id,)
            )
            return cur.rowcount


_store_singleton: VectorStore | None = None
_store_lock = threading.Lock()


def get_vector_store(settings: Settings | None = None) -> VectorStore:
    global _store_singleton
    settings = settings or get_settings()
    with _store_lock:
        if _store_singleton is None:
            if settings.use_pgvector:
                _store_singleton = PgVectorStore(settings.database_url, settings.embedding_dim)
            else:
                _store_singleton = InMemoryVectorStore()
        return _store_singleton


def reset_vector_store() -> None:
    """Test helper to clear the singleton."""
    global _store_singleton
    with _store_lock:
        _store_singleton = None


def new_chunk_id() -> str:
    return str(uuid.uuid4())
