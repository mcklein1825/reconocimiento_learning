"""
app/logging_config.py
Logging estructurado (JSON en producción, texto legible en desarrollo).
Cada request lleva un request_id para correlacionar logs.
"""

from __future__ import annotations

import json
import logging
import sys
import uuid
from contextvars import ContextVar

from flask import g, has_request_context

# Identificador por-request (thread/worker-safe con contextvars)
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class JsonFormatter(logging.Formatter):
    """Formatea cada log como una línea JSON parseable."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        # Campos extra: logger.info(..., extra={"extra": {...}})
        extra = getattr(record, "extra_fields", None)
        if isinstance(extra, dict):
            payload.update(extra)
        return json.dumps(payload, ensure_ascii=False, default=str)


class TextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        rid = request_id_var.get()
        base = f"[{record.levelname}] {record.name} rid={rid} :: {record.getMessage()}"
        if record.exc_info:
            base += "\n" + self.formatException(record.exc_info)
        return base


def configure_logging(level: str = "INFO", json_logs: bool = True) -> None:
    root = logging.getLogger()
    root.setLevel(level.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter() if json_logs else TextFormatter())

    # Evita duplicados si se llama más de una vez (reloader de Flask)
    root.handlers.clear()
    root.addHandler(handler)

    # Silenciar librerías ruidosas
    for noisy in ("numpy", "joblib", "sklearn"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def new_request_id() -> str:
    rid = uuid.uuid4().hex[:12]
    request_id_var.set(rid)
    g.request_id = rid
    return rid
