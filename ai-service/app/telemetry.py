"""OpenTelemetry / LangSmith wiring.

Instrumentation is optional and guarded so the service runs without the
observability stack installed. When ``OTEL_ENABLED=true`` and the packages are
present, FastAPI requests are auto-instrumented.
"""
from __future__ import annotations

import logging

from .config import Settings

logger = logging.getLogger("knowledge-assistant-ai")


def configure_telemetry(app, settings: Settings) -> None:
    if not settings.otel_enabled:
        return
    try:  # pragma: no cover - depends on optional otel packages
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)
        logger.info("OpenTelemetry instrumentation enabled")
    except Exception as exc:  # pragma: no cover
        logger.warning("OTEL requested but not available: %s", exc)

    if settings.langsmith_enabled:
        logger.info("LangSmith tracing enabled via environment")
