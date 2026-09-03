"""Embedding providers.

The offline embedder is a deterministic, dependency-light hashing embedder
(bag-of-token-hashes + L2 normalisation). It produces stable vectors whose
cosine similarity is meaningful for retrieval, so the whole RAG pipeline is
demonstrable without any API keys or network access.

When ``EMBEDDING_PROVIDER=openai`` and a key is present, the OpenAI embeddings
API is used instead.
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol

from ..config import Settings, get_settings

_TOKEN_RE = re.compile(r"[a-z0-9]+")


class Embedder(Protocol):
    dim: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...

    def embed_one(self, text: str) -> list[float]: ...


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class OfflineHashingEmbedder:
    """Deterministic embedder usable without external services."""

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def _embed_single(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for token in _tokenize(text):
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            sign = 1.0 if (h >> 8) % 2 == 0 else -1.0
            vec[idx] += sign
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_single(t) for t in texts]

    def embed_one(self, text: str) -> list[float]:
        return self._embed_single(text)


class OpenAIEmbedder:
    """OpenAI embeddings provider (lazy import of the openai SDK)."""

    def __init__(self, model: str, dim: int, api_key: str) -> None:
        from openai import OpenAI  # type: ignore

        self._client = OpenAI(api_key=api_key)
        self.model = model
        self.dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        resp = self._client.embeddings.create(
            model=self.model, input=texts, dimensions=self.dim
        )
        return [d.embedding for d in resp.data]

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]


def get_embedder(settings: Settings | None = None) -> Embedder:
    settings = settings or get_settings()
    if settings.embedding_provider == "openai" and settings.openai_api_key:
        return OpenAIEmbedder(
            model=settings.embedding_model,
            dim=settings.embedding_dim,
            api_key=settings.openai_api_key,
        )
    return OfflineHashingEmbedder(dim=settings.embedding_dim)
