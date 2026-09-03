"""FastAPI application entrypoint for the Knowledge Assistant AI service."""
from __future__ import annotations

from fastapi import FastAPI

from .config import get_settings
from .routes import health, ingest, query
from .telemetry import configure_telemetry


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Knowledge Assistant AI Service",
        version="0.1.0",
        description="Permission-aware RAG with LangGraph, pgvector and cited outputs.",
    )
    app.include_router(health.router)
    app.include_router(ingest.router)
    app.include_router(query.router)
    configure_telemetry(app, settings)
    return app


app = create_app()
