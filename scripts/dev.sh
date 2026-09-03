#!/usr/bin/env bash
#
# Launch the full local stack (AI service + backend + frontend) with one command.
#
#   ./scripts/dev.sh
#
# - AI service : http://localhost:8000  (FastAPI, offline RAG by default)
# - Backend    : http://localhost:8080  (Spring Boot, in-memory H2 "local" profile)
# - Frontend   : http://localhost:3000  (Next.js)
#
# Press Ctrl+C to stop all three. Set OPENAI_API_KEY / ANTHROPIC_API_KEY (and
# LLM_PROVIDER/EMBEDDING_PROVIDER) to use real models instead of the offline
# fallback.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Prefer a locally-vendored Node (installed under .tools) if present.
if [ -d "$ROOT/.tools" ]; then
  NODE_BIN="$(find "$ROOT/.tools" -maxdepth 2 -type d -name bin 2>/dev/null | head -1 || true)"
  if [ -n "${NODE_BIN:-}" ]; then
    export PATH="$NODE_BIN:$PATH"
  fi
fi

command -v python3 >/dev/null || { echo "python3 is required"; exit 1; }
command -v mvn >/dev/null      || { echo "maven (mvn) is required"; exit 1; }
command -v node >/dev/null     || { echo "node is required (install Node 20+, or vendor it under .tools/)"; exit 1; }

PIDS=()
cleanup() {
  echo ""
  echo "Shutting down..."
  for pid in "${PIDS[@]:-}"; do
    if [ -n "${pid:-}" ] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "==> [1/3] AI service (FastAPI) on :8000"
(
  cd "$ROOT/ai-service"
  if [ ! -d .venv ]; then
    python3 -m venv .venv
    ./.venv/bin/pip install -q --upgrade pip
    ./.venv/bin/pip install -q -r requirements.txt
  fi
  exec ./.venv/bin/uvicorn app.main:app --port 8000 --log-level warning
) &
PIDS+=($!)

echo "==> [2/3] Backend (Spring Boot, H2) on :8080"
(
  cd "$ROOT/backend"
  exec env SPRING_PROFILES_ACTIVE=local AI_SERVICE_BASE_URL=http://localhost:8000 \
    mvn -q -B spring-boot:run
) &
PIDS+=($!)

echo "==> [3/3] Frontend (Next.js) on :3000"
(
  cd "$ROOT/frontend"
  if [ ! -d node_modules ]; then
    npm install
  fi
  exec env NEXT_PUBLIC_BACKEND_URL=http://localhost:8080 npm run dev
) &
PIDS+=($!)

sleep 2
echo ""
echo "-----------------------------------------------------------------"
echo " Frontend : http://localhost:3000"
echo " Backend  : http://localhost:8080/actuator/health"
echo " AI       : http://localhost:8000/health"
echo ""
echo " Get a JWT to paste into the UI:"
echo "   python3 scripts/mint-jwt.py --sub alice --roles employee"
echo "   python3 scripts/mint-jwt.py --sub root  --roles admin"
echo ""
echo " Press Ctrl+C to stop everything."
echo "-----------------------------------------------------------------"

wait
