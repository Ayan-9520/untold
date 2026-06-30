"""OpenTelemetry tracing and Prometheus metrics."""

from __future__ import annotations

import logging
import os

from app.core.config import Settings

logger = logging.getLogger("untold.telemetry")
_otel_configured = False


def setup_telemetry(app, settings: Settings) -> None:
    global _otel_configured
    if settings.metrics_enabled:
        _setup_prometheus(app)
    if settings.otel_enabled:
        _setup_opentelemetry(app, settings)
    _otel_configured = True


def _setup_prometheus(app) -> None:
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        Instrumentator(
            should_group_status_codes=True,
            should_ignore_untemplated=True,
            excluded_handlers=["/metrics", "/health", "/ready", "/live"],
        ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
        logger.info("Prometheus metrics enabled at /metrics")
    except Exception as exc:
        logger.warning("Prometheus instrumentation failed: %s", exc)


def _setup_opentelemetry(app, settings: Settings) -> None:
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        endpoint = settings.otel_exporter_otlp_endpoint.rstrip("/")
        if not endpoint.endswith("/v1/traces"):
            endpoint = f"{endpoint}/v1/traces"

        resource = Resource.create(
            {
                "service.name": settings.otel_service_name,
                "service.version": settings.app_version,
                "deployment.environment": settings.environment,
            }
        )
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
        trace.set_tracer_provider(provider)

        FastAPIInstrumentor.instrument_app(app, excluded_urls="/health,/ready,/live,/metrics")
        SQLAlchemyInstrumentor().instrument()
        logger.info("OpenTelemetry tracing enabled -> %s", endpoint)
    except Exception as exc:
        logger.warning("OpenTelemetry setup failed: %s", exc)


def configure_logging(settings: Settings) -> None:
    level = logging.DEBUG if settings.debug else logging.INFO
    if settings.is_production or os.getenv("LOG_FORMAT") == "json":
        fmt = '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
    else:
        fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    logging.basicConfig(level=level, format=fmt)
    if settings.otel_enabled and os.getenv("OTEL_LOGS_EXPORTER"):
        try:
            from opentelemetry.instrumentation.logging import LoggingInstrumentor

            LoggingInstrumentor().instrument(set_logging_format=True)
        except Exception:
            pass
