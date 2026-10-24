"""
app/validation/validators.py
Validación estricta del payload: protege contra NaN, null, bools, strings,
objetos inesperados, longitudes incorrectas y valores fuera de rango.

Lanza ValidationError con un mensaje claro (seguro para el cliente).
"""

from __future__ import annotations

import math

import numpy as np


class ValidationError(ValueError):
    """Error de validación con código HTTP 422/400 asociado."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def validate_payload(payload: object, *, expected_size: int,
                     pixel_min: float, pixel_max: float) -> np.ndarray:
    """
    Valida el JSON recibido y devuelve un ndarray (1, expected_size) float64.

    Reglas estrictas:
      - El body debe ser una LISTA (no dict, no scalar, no null).
      - Longitud exacta == expected_size.
      - Cada elemento debe ser int o float REAL (los bool se rechazan:
        en Python `True` es instancia de int y podría colarse).
      - Prohibido None, NaN, Inf.
      - Cada valor dentro de [pixel_min, pixel_max].
    """
    # 1) Tipo contenedor: solo listas. Dicts, strings, números y None se rechazan.
    if payload is None:
        raise ValidationError("El cuerpo de la petición es obligatorio.")
    if isinstance(payload, dict):
        raise ValidationError(
            "Se esperaba un arreglo JSON de píxeles, se recibió un objeto."
        )
    if not isinstance(payload, list):
        raise ValidationError(
            f"Se esperaba un arreglo JSON, se recibió '{type(payload).__name__}'."
        )

    # 2) Tamaño exacto
    if len(payload) != expected_size:
        raise ValidationError(
            f"Se esperaban {expected_size} valores, se recibieron {len(payload)}."
        )

    # 3) Validación elemento a elemento (rápida y con mensajes útiles)
    for i, v in enumerate(payload):
        # bool antes que int: bool ES subtipo de int en Python
        if isinstance(v, bool):
            raise ValidationError(f"Valor no numérico en el índice {i}: booleano.")
        if v is None:
            raise ValidationError(f"Valor nulo (null) en el índice {i}.")
        if not isinstance(v, (int, float)):
            raise ValidationError(
                f"Valor no numérico en el índice {i}: '{type(v).__name__}'."
            )
        # float('nan') / float('inf') pasan isinstance(float) → hay que filtrarlos
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            raise ValidationError(f"Valor no finito (NaN/Inf) en el índice {i}.")

    # 4) Rango: vectorizado con numpy (más rápido que un bucle python)
    arr = np.asarray(payload, dtype=np.float64)
    # Última red de seguridad ante NaN introducidos por coerción implícita
    if not np.all(np.isfinite(arr)):
        raise ValidationError("El arreglo contiene valores NaN o infinitos.")
    if arr.min() < pixel_min or arr.max() > pixel_max:
        raise ValidationError(
            f"Todos los píxeles deben estar en el rango [{pixel_min}, {pixel_max}]."
        )

    return arr.reshape(1, expected_size)
