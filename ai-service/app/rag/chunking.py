"""Text chunking with word-boundary aware sliding windows."""
from __future__ import annotations

import re

_WHITESPACE = re.compile(r"\s+")


def _normalize(text: str) -> str:
    return _WHITESPACE.sub(" ", text).strip()


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    """Split ``text`` into overlapping chunks of roughly ``chunk_size`` chars.

    Splitting happens on word boundaries so chunks stay readable, and each
    chunk overlaps the previous one by ``overlap`` characters to preserve
    context across boundaries.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")

    text = _normalize(text)
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        if end < n:
            # Prefer to break on the last space within the window.
            space = text.rfind(" ", start, end)
            if space > start:
                end = space
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return chunks
