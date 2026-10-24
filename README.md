# reconocimiento_learning — Refactor (frontend React + backend Flask)

Aplicación que dibuja un dígito en una cuadrícula 28x28 y lo clasifica con un
modelo scikit-learn servido por Flask.

## Estructura

```
number-classifier-react/          # Frontend React (CRA)
  src/
    App.js                        # Contenedor: orquesta hook + servicio + componentes
    constants.js                  # GRID_ROWS/COLS, createEmptyGrid, gridToFlatPixels…
    components/
      DrawingGrid.js              # Cuadrícula con soporte mouse+touch, accesible
      GridNode.js                 # Celda memoizada (React.memo)
      PredictionPanel.js          # loading / error / resultado con aria-live
      CanvasDrawing.js            # OPCIONAL: versión canvas (Pointer Events)
    hooks/
      useDrawingGrid.js           # Estado inmutable del dibujo (paintCell/clear)
    services/
      api.js                      # axios instance, timeout, POST /predict
    utils/
      errors.js                   # Normalización de errores a mensajes seguros
    __tests__/ + App.test.js      # 22 tests (jest + testing-library)

servidor_flask/                   # Backend Flask refactorizado
  app/
    __init__.py                   # Application factory (CORS, límites, error handlers)
    config.py                     # Config vía env vars
    logging_config.py             # Logging JSON estructurado + request_id
    routes/{predict,health}.py    # Blueprints (/predict, /health, /health/ready, /version)
    services/model_service.py     # Carga singleton + inferencia con timeout
    validation/validators.py      # Validación estricta (NaN/null/rango/tipo/forma)
  tests/                          # 37 tests pytest (unit + integración)
  wsgi.py gunicorn_conf.py Dockerfile requirements.txt SECURITY_CHECKLIST.md
  modelo.py                       # Entrenamiento (sin cambios funcionales)
```

## Ejecutar

```bash
# Backend (desarrollo)
cd servidor_flask && python wsgi.py

# Backend (producción)
gunicorn -c gunicorn_conf.py wsgi:app

# Docker
docker build -t digit-api servidor_flask && docker run -p 8000:8000 digit-api

# Frontend
cd number-classifier-react && npm install && npm start   # http://localhost:3000
```

## Tests

```bash
cd servidor_flask && python -m pytest            # 36 passed
cd number-classifier-react && npm test --watchAll=false   # 22 passed
```

## Notas

- El frontend llama a `POST /predict` (el legacy `POST /` sigue soportado).
- Variables de entorno del backend: `MODEL_PATH`, `MODEL_VERSION`, `CORS_ORIGINS`,
  `MAX_CONTENT_LENGTH`, `INFERENCE_TIMEOUT`, `JSON_LOGS`.
- La versión canvas (`CanvasDrawing.js`) es opcional/documentada: un solo nodo DOM,
  Pointer Events para mouse/touch/lápiz y downsample directo del bitmap.
- El fichero `digit_classifier.joblib` incluido está vacío (0 bytes): vuelve a
  generar el modelo con `python modelo.py` antes de servir predicciones reales.
