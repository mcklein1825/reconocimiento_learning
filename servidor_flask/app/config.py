"""
app/config.py
Configuración centralizada vía variables de entorno (12-factor).
"""

from __future__ import annotations

import os


def _env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    """Configuración de la API de predicción."""

    # --- Modelo ---
    MODEL_PATH: str = os.environ.get("MODEL_PATH", "digit_classifier.joblib")
    MODEL_VERSION: str = os.environ.get("MODEL_VERSION", "knn-mnist-1.0.0")

    # --- Shape esperado del input ---
    IMAGE_SIZE: int = int(os.environ.get("IMAGE_SIZE", "784"))       # 28x28 aplanado
    PIXEL_MIN: float = float(os.environ.get("PIXEL_MIN", "0"))
    PIXEL_MAX: float = float(os.environ.get("PIXEL_MAX", "255"))

    # --- Seguridad / límites ---
    MAX_CONTENT_LENGTH: int = int(
        os.environ.get("MAX_CONTENT_LENGTH", str(64 * 1024))         # 64 KB por request
    )
    CORS_ORIGINS: list[str] = [
        o.strip()
        for o in os.environ.get(
            "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
        ).split(",")
        if o.strip()
    ]

    # --- Timeout de inferencia (segundos) ---
    INFERENCE_TIMEOUT: float = float(os.environ.get("INFERENCE_TIMEOUT", "5"))

    # --- Observabilidad ---
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    JSON_LOGS: bool = _env_bool("JSON_LOGS", True)

    # --- Debug (NUNCA en producción) ---
    DEBUG: bool = _env_bool("FLASK_DEBUG", False)
