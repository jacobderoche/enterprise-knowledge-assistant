# AI Service (FastAPI + LangGraph + pgvector)

Permission-aware RAG microservice that ingests documents and answers questions
with **cited, grounded** responses.

## Capabilities
- **RAG** over pgvector (falls back to an in-memory store with no DB)
- **LangGraph** `retrieve -> generate` pipeline (falls back to a sequential
  runner if `langgraph` isn't installed)
- **Embeddings & LLM** via OpenAI/Anthropic, or a deterministic **offline**
  provider so the whole service runs with zero API keys
- **Permission-aware retrieval**: chunks are ACL-scoped and filtered per request
- **Structured outputs** (`answer` + `citations`) and **SSE streaming**
- **Automated LLM evaluation** harness with quality gates

## Run locally (offline, no keys required)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt        # test deps
pip install -r requirements.txt            # full runtime (langgraph, providers)
uvicorn app.main:app --reload
```

## Endpoints
| Method | Path            | Purpose                              |
|--------|-----------------|--------------------------------------|
| GET    | `/health`       | Readiness + active providers         |
| POST   | `/ingest`       | Chunk + embed + store a document     |
| POST   | `/query`        | Structured cited answer              |
| POST   | `/query/stream` | SSE token stream + final citations   |

## Test & evaluate
```bash
pytest                    # unit + API + RAG tests
pytest tests/eval         # automated LLM/RAG evaluation gates
```

## Configuration
See `.env.example`. Set `LLM_PROVIDER`/`EMBEDDING_PROVIDER` to `openai` or
`anthropic` (with keys) and `DATABASE_URL` to enable pgvector.
