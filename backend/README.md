# Backend (Java 21 + Spring Boot + Spring Security)

Main API gateway for the knowledge assistant. Enforces authentication and
**permission-aware** access, persists documents/conversations/audit, and
orchestrates the Python AI service.

## Responsibilities
- **OAuth2/OIDC resource server** (JWT). Falls back to an HS256 shared-secret
  decoder for standalone local dev (`app.jwt-secret`); set `app.jwt-issuer-uri`
  to use a real IdP.
- **Role-based access** via `@EnableMethodSecurity` + URL rules
  (`EMPLOYEE`, `ADMIN`). The user's `roles`/`scopes` JWT claims drive the ACL
  scopes forwarded to the AI service for permission-aware RAG.
- **Persistence** (JPA): documents, conversations, messages, feedback, audit logs.
- **AI orchestration**: `AiServiceClient` (WebClient) calls `/ingest` and `/query`.

## Endpoints
| Method | Path                                  | Role            |
|--------|---------------------------------------|-----------------|
| POST   | `/api/documents`                      | EMPLOYEE/ADMIN  |
| GET    | `/api/documents`                      | EMPLOYEE/ADMIN  |
| POST   | `/api/chat`                           | authenticated   |
| GET    | `/api/chat/{conversationId}/messages` | authenticated   |
| POST   | `/api/feedback`                       | authenticated   |
| GET    | `/api/admin/audit`                    | ADMIN           |

## Run
```bash
mvn spring-boot:run          # needs Postgres + AI service (see docker-compose)
mvn test                     # runs against in-memory H2, no external deps
```

## Local JWT for testing
Generate an HS256 token signed with `app.jwt-secret`, containing
`sub`, `roles` (e.g. `["employee"]`) and optional `scopes`. See the repo root
README for a ready-made snippet.

> Spring AI could replace the WebClient call if you prefer to run RAG inside the
> JVM; here RAG lives in the dedicated Python service so LangGraph and the wider
> Python AI ecosystem are available.
