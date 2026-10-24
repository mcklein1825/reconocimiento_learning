"""Fixtures compartidas: app Flask con un modelo falso inyectado."""

import numpy as np
import pytest

from app import create_app
from app.services.model_service import ModelService, set_model_service


class FakeProbaModel:
    """Modelo stub con predict_proba (pipeline scaler+KNN)."""

    def predict(self, image):
        # predice 7 siempre; el input ya viene validado como ndarray
        assert isinstance(image, np.ndarray) and image.shape[0] == 1
        return np.array([7])

    def predict_proba(self, image):
        probs = np.zeros(10)
        probs[7] = 0.91
        return np.array([probs])


class FakePlainModel:
    """Modelo stub sin predict_proba (degradación suave de confianza)."""

    def predict(self, image):
        return np.array([3])


class HangingModel:
    """Modelo que se cuelga: debe disparar el timeout de inferencia."""

    def predict(self, image):
        import time
        time.sleep(5)
        return np.array([0])


class FakeService(ModelService):
    """ModelService que usa un stub y no toca disco."""

    def __init__(self, model, timeout=None):
        super().__init__(model_path="fake.joblib", timeout=timeout)
        self._model = model


@pytest.fixture()
def client():
    set_model_service(FakeService(FakeProbaModel()))
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c
    set_model_service(None)


@pytest.fixture()
def make_client():
    """Factory para inyectar cualquier stub de modelo en un test."""

    class _ClientFactory:
        def build(self, service):
            set_model_service(service)
            app = create_app()
            app.config.update(TESTING=True)
            return app.test_client()

    return _ClientFactory()
