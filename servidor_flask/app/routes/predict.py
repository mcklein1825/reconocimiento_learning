"""
app/routes/predict.py
Blueprint de predicción: POST /predict  (y alias legacy POST /).

Flujo: parse JSON -> validar -> inferir con timeout -> responder.
Los errores se mapean a códigos HTTP correctos sin filtrar stack traces.
"""

from __future__ import annotations

import time

from flask import Blueprint, current_app, jsonify, request

from app.config import Config
from app.logging_config import get_logger
from app.services.model_service import (
    InferenceTimeoutError,
    ModelLoadError,
    get_model_service,
)
from app.validation.validators import ValidationError, validate_payload

logger = get_logger(__name__)

bp_predict = Blueprint("predict", __name__)


def _error(message: str, status: int):
    return jsonify({"error": message, "status": status}), status


@bp_predict.post("/predict")
@bp_predict.post("/")  # compatibilidad con el frontend legado
def predict():
    started = time.perf_counter()

    # 0) Límite de tamaño defensivo (los test clients no aplican MAX_CONTENT_LENGTH;
    #    en producción lo corta también el servidor WSGI/Gunicorn)
    declared = request.content_length
    if declared is not None and declared > current_app.config["MAX_CONTENT_LENGTH"]:
        logger.warning("Content-Length %s excede el máximo permitido", declared)
        return _error(
            f"Cuerpo demasiado grande (máx. {current_app.config['MAX_CONTENT_LENGTH']} bytes).",
            413,
        )

    # 1) Content-Type y parseo estricto (sin force=True para no tragar basura)
    if not request.is_json:
        logger.warning("Request sin Content-Type application/json")
        return _error("Content-Type debe ser application/json.", 415)

    try:
        payload = request.get_json(silent=False)
    except Exception:  # noqa: BLE001 — JSON malformado
        logger.warning("Body con JSON inválido")
        return _error("El cuerpo no es JSON válido.", 400)

    # 2) Validación estricta del arreglo de píxeles
    try:
        image = validate_payload(
            payload,
            expected_size=Config.IMAGE_SIZE,
            pixel_min=Config.PIXEL_MIN,
            pixel_max=Config.PIXEL_MAX,
        )
    except ValidationError as exc:
        logger.warning("Payload rechazado: %s", exc.message)
        return _error(exc.message, exc.status_code)

    # 3) Inferencia con timeout
    try:
        result = get_model_service().predict(image)
    except InferenceTimeoutError:
        return _error("Tiempo de inferencia excedido. Intente de nuevo.", 504)
    except ModelLoadError:
        logger.error("Modelo no disponible")
        return _error("El modelo no está disponible en este momento.", 503)
    except RuntimeError:
        return _error("Error interno durante la predicción.", 500)

    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    painted = int((image[0] > 0).sum())
    logger.info(
        "Predicción realizada",
        extra={"extra_fields": {
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "painted_pixels": painted,
            "elapsed_ms": elapsed_ms,
        }},
    )

    return jsonify({
        "prediction": result["prediction"],
        "confidence": result["confidence"],
        "model_version": current_app.config.get("MODEL_VERSION", Config.MODEL_VERSION),
        "elapsed_ms": elapsed_ms,
    })
