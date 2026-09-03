# Frontend (Next.js + React + TypeScript)

Web UI for the knowledge assistant: upload documents and chat with **cited,
permission-aware** answers.

## Features
- Document upload with ACL **scope** selection (public / admin / hr-confidential)
- Chat panel rendering the answer plus numbered **citations** (source + snippet + score)
- Thumbs up/down **feedback** per answer
- JWT bearer auth (paste a token; persisted in `localStorage`)

## Run
```bash
npm install
cp .env.local.example .env.local   # point NEXT_PUBLIC_BACKEND_URL at the backend
npm run dev                        # http://localhost:3000
```

## Type-check
```bash
npm run typecheck
```

Set `NEXT_PUBLIC_BACKEND_URL` to the Spring Boot backend (default
`http://localhost:8080`).
