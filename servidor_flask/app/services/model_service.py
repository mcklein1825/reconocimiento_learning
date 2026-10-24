"""
app/services/model_service.py
Carga del modelo y predicción con timeout.

Diseño:
  - El modelo se carga UNA vez al arrancar el worker (lazy singleton thread-safe).
  - La inferencia corre en un ThreadPoolExecutor con future.result(timeout=...),
    de modo que un modelo lento/cuelgado devuelve 504 en vez de bloquear el
    request indefinidamente.
  - Nota de rendimiento: scikit-learn libera el GIL en sus partes C/Fortran,
    por lo que ejecutar inferencias en threads no serializa del todo. Para CPU
    intensa sostenida, escale con más workers de Gunicorn (ver Dockerfile).
"""

from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from typing import Any

import joblib
import numpy as np

from app.config import Config
from app.logging_config import get_logger

logger = get_logger(__name__)


class ModelLoadError(RuntimeError):
    """El modelo no pudo cargarse (fichero ausente/corrupto/incompatible)."""


class InferenceTimeoutError(RuntimeError):
    """La inferencia excedió el tiempo máximo permitido."""


class ModelService:
    """Wrapper de acceso al clasificador sklearn."""

    def __init__(self, model_path: str | None = None, timeout: float | None = None):
        self._model_path = model_path or Config.MODEL_PATH
        self._timeout = timeout if timeout is not None else Config.INFERENCE_TIMEOUT
        self._model: Any | None = None
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="inference"
        )

    # ---------- carga ----------
    def _load(self) -> Any:
        if self._model is not None:
            return self._model
        with self._lock:
            if self._model is None:  # doble chequeo dentro del lock
                logger.info("Cargando modelo desde %s", self._model_path)
                try:
                    self._model = joblib.load(self._model_path)
                except Exception as exc:  # noqa: BLE001 — frontera de carga
                    logger.exception("Fallo al cargar el modelo")
                    raise ModelLoadError(
                        f"No se pudo cargar el modelo '{self._model_path}'."
                    ) from exc
                logger.info("Modelo cargado correctamente")
        return self._model

    @property
    def loaded(self) -> bool:
        return self._model is not None

    # ---------- inferencia ----------
    def predict(self, image: np.ndarray) -> dict[str, Any]:
        """
        Predice un dígito para `image` con shape (1, N).

        Devuelve: {"prediction": int, "confidence": float | None}
        Lanza: ModelLoadError, InferenceTimeoutError, RuntimeError.
        """
        model = self._load()

        def _run() -> tuple[Any, float | None]:
            pred = model.predict(image)[0]
            confidence: float | None = None
            if hasattr(model, "predict_proba"):
                try:
                    confidence = float(np.max(model.predict_proba(image)[0]))
                except Exception:  # modelos sin probabilidades → degradar suave
                    confidence = None
            return pred, confidence

        future = self._executor.submit(_run)
        try:
            pred, confidence = future.result(timeout=self._timeout)
        except FutureTimeout as exc:
            future.cancel()
            logger.error("Inferencia excedió %.1fs", self._timeout)
            raise InferenceTimeoutError(
                f"La inferencia superó el tiempo máximo ({self._timeout}s)."
            ) from exc
        except Exception as exc:  # noqa: BLE001 — frontera hacia HTTP
            logger.exception("Error durante la inferencia")
            raise RuntimeError("Error interno durante la predicción.") from exc

        return {"prediction": int(pred), "confidence": confidence}


# Singleton usado por las rutas; reemplazable en tests vía app fixture.
_model_service: ModelService | None = None
_service_lock = threading.Lock()


def get_model_service() -> ModelService:
    global _model_service
    if _model_service is None:
        with _service_lock:
            if _model_service is None:
                _model_service = ModelService()
    return _model_service


def set_model_service(service: ModelService | None) -> None:
    """Inyección de dependencias para tests."""
    global _model_service
    _model_service = service
