from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["vector_store"] == "in-memory"


def test_ingest_then_query():
    ingest = client.post(
        "/ingest",
        json={
            "document_id": "doc-api",
            "source": "api.md",
            "content": "The support email is help@example.com and hours are 9 to 5.",
            "scope": "public",
        },
    )
    assert ingest.status_code == 200
    assert ingest.json()["chunk_count"] >= 1

    q = client.post(
        "/query",
        json={
            "query": "What is the support email?",
            "access": {"user_id": "u1", "roles": ["employee"], "allowed_scopes": ["public"]},
        },
    )
    assert q.status_code == 200
    body = q.json()
    assert body["used_context"] is True
    assert "help@example.com" in body["answer"]
    assert body["citations"][0]["document_id"] == "doc-api"


def test_stream_endpoint():
    client.post(
        "/ingest",
        json={
            "document_id": "doc-stream",
            "source": "s.md",
            "content": "Project Falcon launches in March.",
            "scope": "public",
        },
    )
    with client.stream(
        "POST",
        "/query/stream",
        json={
            "query": "When does Project Falcon launch?",
            "access": {"user_id": "u1", "roles": ["employee"], "allowed_scopes": ["public"]},
        },
    ) as r:
        assert r.status_code == 200
        chunks = "".join(list(r.iter_text()))
    assert "data:" in chunks
    assert "done" in chunks
