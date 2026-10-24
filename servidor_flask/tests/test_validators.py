"""Tests unitarios de la validación estricta del payload."""

import math

import numpy as np
import pytest

from app.validation.validators import ValidationError, validate_payload

KW = dict(expected_size=784, pixel_min=0, pixel_max=255)


def valid_list(value=255):
    return [value] * 784


def test_acepta_arreglo_correcto():
    arr = validate_payload(valid_list(), **KW)
    assert arr.shape == (1, 784)
    assert arr.dtype == np.float64


def test_rechaza_none():
    with pytest.raises(ValidationError, match="cuerpo"):
        validate_payload(None, **KW)


def test_rechaza_dict_objeto_inesperado():
    with pytest.raises(ValidationError, match="objeto"):
        validate_payload({"pixeles": valid_list()}, **KW)


def test_rechaza_string():
    with pytest.raises(ValidationError, match="arreglo JSON"):
        validate_payload("255" * 784, **KW)


def test_rechaza_escalar():
    with pytest.raises(ValidationError, match="arreglo JSON"):
        validate_payload(255, **KW)


def test_rechaza_longitud_incorrecta():
    with pytest.raises(ValidationError, match="784 valores"):
        validate_payload([0] * 783, **KW)


def test_rechaza_matriz_anidada_mal_dimensionada():
    # Una "matriz" 28x28 anidada se rechaza: primero por longitud (28 filas != 784)
    with pytest.raises(ValidationError):
        validate_payload([[0] * 28 for _ in range(28)], **KW)


def test_rechaza_lista_anidada_con_longitud_correcta():
    # 784 elementos pero anidados -> elementos no numéricos
    data = [[0] for _ in range(784)]
    with pytest.raises(ValidationError, match="no numérico"):
        validate_payload(data, **KW)


def test_rechaza_null_interior():
    data = valid_list()
    data[10] = None
    with pytest.raises(ValidationError, match="nulo"):
        validate_payload(data, **KW)


def test_rechaza_nan():
    data = valid_list()
    data[42] = float("nan")
    with pytest.raises(ValidationError, match="NaN"):
        validate_payload(data, **KW)


def test_rechaza_inf():
    data = valid_list()
    data[42] = math.inf
    with pytest.raises(ValidationError, match="NaN/Inf"):
        validate_payload(data, **KW)


def test_rechaza_booleanos():
    data = valid_list()
    data[0] = True
    with pytest.raises(ValidationError, match="booleano"):
        validate_payload(data, **KW)


def test_rechaza_strings_interiores():
    data = valid_list()
    data[7] = "255"
    with pytest.raises(ValidationError, match="no numérico"):
        validate_payload(data, **KW)


def test_rechaza_fuera_de_rango_negativo():
    data = valid_list()
    data[5] = -1
    with pytest.raises(ValidationError, match="rango"):
        validate_payload(data, **KW)


def test_rechaza_fuera_de_rango_alto():
    data = valid_list()
    data[5] = 256
    with pytest.raises(ValidationError, match="rango"):
        validate_payload(data, **KW)


def test_acepta_floats_en_rango():
    data = [float(i % 256) for i in range(784)]
    arr = validate_payload(data, **KW)
    assert arr.max() <= 255
