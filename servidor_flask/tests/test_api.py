"""Tests de integración de la API (modelo stub inyectado)."""

import json

VALID = [0] * 784
VALID[350] = 255


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_ready(client):
    r = client.get("/health/ready")
    assert r.status_code == 200
    body = r.get_json()
    assert body["model_loaded"] is True


def test_version(client):
    r = client.get("/version")
    assert r.status_code == 200
    body = r.get_json()
    assert body["input_shape"] == [28, 28]
    assert body["flattened_size"] == 784
    assert "model_version" in body


def test_predict_ok(client):
    r = client.post("/predict", json=VALID)
    assert r.status_code == 200
    body = r.get_json()
    assert body["prediction"] == 7
    assert 0.0 <= body["confidence"] <= 1.0
    assert "model_version" in body


def test_predict_legacy_route_root(client):
    r = client.post("/", json=VALID)
    assert r.status_code == 200
    assert r.get_json()["prediction"] == 7


def test_rechaza_sin_content_type(client):
    r = client.post("/predict", data=json.dumps(VALID),
                    content_type="text/plain")
    assert r.status_code == 415


def test_rechaza_json_malformado(client):
    r = client.post("/predict", data="{no-es-json", content_type="application/json")
    assert r.status_code == 400
    assert "error" in r.get_json()


def test_rechaza_tamano_incorrecto(client):
    r = client.post("/predict", json=[0] * 100)
    assert r.status_code == 400
    assert "784" in r.get_json()["error"]


def test_rechaza_nan(client):
    data = [float("nan")] * 784
    r = client.post("/predict", json=data)
    assert r.status_code == 400
    assert "NaN" in r.get_json()["error"]


def test_rechaza_nulls(client):
    data = [None] * 784
    r = client.post("/predict", json=data)
    assert r.status_code == 400


def test_rechaza_objeto_en_lugar_de_arreglo(client):
    r = client.post("/predict", json={"grid": VALID})
    assert r.status_code == 400


def test_rechaza_fuera_de_rango(client):
    data = [999] * 784
    r = client.post("/predict", json=data)
    assert r.status_code == 400
    assert "rango" in r.get_json()["error"]


def test_rechaza_body_demasiado_grande(client):
    # MAX_CONTENT_LENGTH = 64KB; un arreglo gigante debe dar 413
    huge = [0] * 200_000
    r = client.post("/predict", json=huge)
    assert r.status_code == 413


def test_timeout_de_inferencia_devuelve_504(make_client):
    from tests.conftest import FakeService, HangingModel

    service = FakeService(HangingModel(), timeout=0.2)
    c = make_client.build(service)
    r = c.post("/predict", json=VALID)
    assert r.status_code == 504
    assert "inferencia" in r.get_json()["error"].lower()


def test_modelo_sin_proba_degrada_confianza_a_none(make_client):
    from tests.conftest import FakeService, FakePlainModel

    c = make_client.build(FakeService(FakePlainModel()))
    r = c.post("/predict", json=VALID)
    assert r.status_code == 200
    body = r.get_json()
    assert body["prediction"] == 3
    assert body["confidence"] is None


def test_modelo_no_disponible_devuelve_503(make_client):
    from app.services.model_service import ModelService

    bad = ModelService(model_path="/ruta/inexistente/model.joblib")
    c = make_client.build(bad)
    r = c.post("/predict", json=VALID)
    assert r.status_code == 503


def test_cors_deniega_origen_desconocido(client):
    r = client.options("/predict", headers={
        "Origin": "http://evil.example.com",
        "Access-Control-Request-Method": "POST",
    })
    acao = r.headers.get("Access-Control-Allow-Origin")
    assert acao is None or "evil.example.com" not in (acao or "")


def test_cors_permite_origen_configurado(client):
    r = client.post("/predict", json=VALID,
                    headers={"Origin": "http://localhost:3000"})
    assert r.headers.get("Access-Control-Allow-Origin") == "http://localhost:3000"


def test_headers_de_seguridad(client):
    r = client.get("/health")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"


def test_404_devuelve_json(client):
    r = client.get("/no-existe")
    assert r.status_code == 404
    assert r.is_json
