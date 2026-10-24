"""
app/routes/health.py
Endpoints de observabilidad:
  GET /health          -> liveness (el proceso responde)
  GET /health/ready    -> readiness (¿podemos servir predicciones?)
  GET /version         -> versión/metadatos del modelo
"""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify

from app.config import Config
from app.services.model_service import get_model_service

bp_health = Blueprint("health", __name__)


@bp_health.get("/health")
def health():
    """Liveness: barato, nunca toca el modelo."""
    return jsonify({"status": "ok", "service": "digit-classifier-api"}), 200


@bp_health.get("/health/ready")
def ready():
    """Readiness: intenta cargar el modelo; devuelve 503 si no está listo."""
    service = get_model_service()
    try:
        if not service.loaded:
            service._load()  # fuerza carga lazy perezosa
        model_loaded = service.loaded
    except Exception:  # noqa: BLE001
        model_loaded = False

    status = 200 if model_loaded else 503
    return jsonify({
        "status": "ready" if model_loaded else "not_ready",
        "model_loaded": model_loaded,
        "model_version": current_app.config.get("MODEL_VERSION", Config.MODEL_VERSION),
    }), status


@bp_health.get("/version")
def version():
    """Metadatos del modelo desplegado (para el frontend / despliegues)."""
    return jsonify({
        "model_version": current_app.config.get("MODEL_VERSION", Config.MODEL_VERSION),
        "model_path": Config.MODEL_PATH,
        "input_shape": [28, 28],
        "flattened_size": Config.IMAGE_SIZE,
        "pixel_range": [Config.PIXEL_MIN, Config.PIXEL_MAX],
    }), 200
