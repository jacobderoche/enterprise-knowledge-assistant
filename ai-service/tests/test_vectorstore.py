from app.models.embeddings import OfflineHashingEmbedder
from app.rag.vectorstore import InMemoryVectorStore, StoredChunk, new_chunk_id


def _chunk(text: str, scope: str, embedder) -> StoredChunk:
    return StoredChunk(
        chunk_id=new_chunk_id(),
        document_id="doc1",
        source="doc1.txt",
        scope=scope,
        ordinal=0,
        text=text,
        embedding=embedder.embed_one(text),
    )


def test_semantic_ranking():
    emb = OfflineHashingEmbedder(dim=256)
    store = InMemoryVectorStore()
    store.upsert(
        [
            _chunk("The capital of France is Paris.", "public", emb),
            _chunk("Bananas are a good source of potassium.", "public", emb),
        ]
    )
    hits = store.search(emb.embed_one("What is the capital of France?"), ["public"], top_k=2)
    assert hits[0].chunk.text.startswith("The capital of France")
    assert hits[0].score >= hits[1].score


def test_permission_filtering():
    emb = OfflineHashingEmbedder(dim=256)
    store = InMemoryVectorStore()
    store.upsert(
        [
            _chunk("secret salary data", "hr-confidential", emb),
            _chunk("public holiday schedule", "public", emb),
        ]
    )
    hits = store.search(emb.embed_one("salary"), ["public"], top_k=5)
    assert all(h.chunk.scope == "public" for h in hits)
    assert all("secret salary" not in h.chunk.text for h in hits)


def test_delete_document():
    emb = OfflineHashingEmbedder(dim=256)
    store = InMemoryVectorStore()
    store.upsert([_chunk("hello", "public", emb)])
    assert store.delete_document("doc1") == 1
    assert store.search(emb.embed_one("hello"), ["public"], top_k=5) == []
