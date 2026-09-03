# Secure Enterprise Knowledge Assistant

A production-flavored, permission-aware **RAG** knowledge assistant: upload
documents, then get **cited, grounded answers** scoped to what each user is
allowed to read. Built as three services in a monorepo.

```
┌────────────┐     JWT      ┌──────────────────┐    HTTP     ┌────────────────────┐
│  Frontend  │ ───────────▶ │  Backend (Spring)│ ──────────▶ │  AI service (Py)   │
│ Next.js/TS │  documents/  │  auth, RBAC,     │  /ingest    │ FastAPI + LangGraph│
│            │  chat/feedbk │  persistence,    │  /query     │ RAG, embeddings,   │
│            │ ◀─────────── │  audit, orchestr.│ ◀────────── │ pgvector, cited out│
└────────────┘   answers    └──────────────────┘             └────────────────────┘
                                    │                                  │
                              ┌─────▼──────┐                    ┌──────▼──────┐
                              │ PostgreSQL │                    │  pgvector    │
                              │ (metadata) │                    │ (embeddings) │
                              └────────────┘                    └──────────────┘
```

## Tech stack
| Area          | Choice |
|---------------|--------|
| Frontend      | React, Next.js, TypeScript |
| Main backend  | Java 21, Spring Boot, Spring Security (OAuth2/OIDC resource server, JWT, RBAC) |
| AI service    | Python, FastAPI, LangGraph |
| Models        | OpenAI / Anthropic (with an offline deterministic fallback) |
| AI capabilities | RAG, embeddings, structured cited outputs, SSE streaming, permission-aware retrieval |
| Data          | PostgreSQL + pgvector |
| Messaging/cache | Redis + Amazon SQS (compose includes Redis) |
| Cloud         | AWS (ECS/EKS, RDS, S3, Secrets Manager) |
| Infra         | Docker, Terraform, GitHub Actions |
| Observability | OpenTelemetry, Datadog, LangSmith (opt-in hooks) |
| Testing       | JUnit, pytest, automated LLM evaluations |

## What this vertical slice delivers
Upload a document → it is chunked, embedded and stored in pgvector (scoped by an
ACL tag) → ask a question → the backend enforces auth and forwards the user's
**allowed scopes** → the AI service retrieves only permitted chunks and returns a
**cited answer** → the backend persists the conversation and writes an **audit
log** → the frontend renders the answer with numbered citations and feedback.

It runs **end-to-end with zero API keys**: the AI service ships with a
deterministic offline embedder + extractive LLM so retrieval, citations,
permissions, streaming and evaluations are all demonstrable offline. Set
`OPENAI_API_KEY`/`ANTHROPIC_API_KEY` (and provider env vars) to switch to real
models; set `DATABASE_URL` to use pgvector instead of the in-memory store.

## Quick start (Docker Compose)
```bash
docker compose up --build
# Frontend  : http://localhost:3000
# Backend   : http://localhost:8080  (GET /actuator/health)
# AI service: http://localhost:8000  (GET /health)
```

Then mint a dev JWT and paste it into the frontend token box:
```bash
python3 scripts/mint-jwt.py --sub alice --roles employee
# admin (can read every scope + view the audit trail):
python3 scripts/mint-jwt.py --sub root --roles admin
```

## Run services individually
- **AI service** — see [`ai-service/README.md`](ai-service/README.md)
- **Backend** — see [`backend/README.md`](backend/README.md)
- **Frontend** — see [`frontend/README.md`](frontend/README.md)

## Test everything
```bash
# AI service (unit + API + RAG + LLM eval)
cd ai-service && pip install -r requirements-dev.txt && pytest

# Backend (JUnit, uses in-memory H2)
cd backend && mvn test

# Frontend (type check + build)
cd frontend && npm install && npm run typecheck && npm run build
```
CI runs all three on every push/PR (`.github/workflows/ci.yml`).

## Security model
- Stateless **JWT resource server**; production uses a real OIDC issuer
  (`app.jwt-issuer-uri`), local dev uses an HS256 shared secret.
- **Role-based access** (`EMPLOYEE`, `ADMIN`) at URL + method level.
- **Permission-aware RAG**: every chunk carries an ACL `scope`; retrieval is
  filtered to the caller's `roles`/`scopes` claims, so users never see content
  they aren't entitled to — enforced in both the in-memory and pgvector stores.
- **Audit logs** for uploads, queries and feedback.

## Infrastructure
- `docker-compose.yml` — local full stack (Postgres+pgvector, Redis, 3 services).
- `infra/terraform/` — AWS skeleton: RDS PostgreSQL, S3 (documents),
  Secrets Manager, ECR repos, ECS cluster (extend with task defs, or deploy the
  same images to EKS).
- Per-service `Dockerfile`s (multi-stage).

## Observability (opt-in)
- AI service: `OTEL_ENABLED=true` auto-instruments FastAPI; `LANGSMITH_TRACING=true`
  enables LangSmith tracing.
- Backend: Spring Boot Actuator + Micrometer (wire a Datadog/OTel registry).

## Repository layout
```
ai-service/     FastAPI + LangGraph RAG microservice
backend/        Spring Boot API, auth, persistence, orchestration
frontend/       Next.js UI
infra/          Terraform (AWS)
scripts/        Dev helpers (JWT minting)
.github/        CI workflows
docker-compose.yml
```
