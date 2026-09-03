from app.rag.chunking import chunk_text


def test_short_text_single_chunk():
    assert chunk_text("hello world", chunk_size=800) == ["hello world"]


def test_empty_text():
    assert chunk_text("   ") == []


def test_overlapping_chunks_cover_text():
    text = " ".join(f"word{i}" for i in range(500))
    chunks = chunk_text(text, chunk_size=200, overlap=50)
    assert len(chunks) > 1
    # every chunk within the size bound (allowing word-boundary slack)
    assert all(len(c) <= 200 for c in chunks)
    # first token preserved
    assert chunks[0].startswith("word0")


def test_invalid_overlap():
    import pytest

    with pytest.raises(ValueError):
        chunk_text("abc", chunk_size=10, overlap=10)
