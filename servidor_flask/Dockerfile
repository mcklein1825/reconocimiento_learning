# syntax=docker/dockerfile:1
# ── Imagen de producción: API de clasificación de dígitos ──────────────
FROM python:3.12-slim AS base

# No correr como root
RUN groupadd -r appuser && useradd -r -g appuser -d /srv/app appuser

WORKDIR /srv/app

# Dependencias del sistema mínimas (nessie: numpy/sklearn traen wheels)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código de la aplicación
COPY app/ ./app/
COPY wsgi.py gunicorn_conf.py ./
# Modelo entrenado (en un setup real se montaría/descargaría en runtime)
COPY digit_classifier.joblib ./

# Permisos mínimos: el código es read-only para appuser
RUN chown -R appuser:appuser /srv/app && chmod -R a-w /srv/app/app /srv/app/*.py

USER appuser

EXPOSE 8000

# Healthcheck contra el endpoint liveness
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; \
r=urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2); \
sys.exit(0 if r.status==200 else 1)"

# timeout < graceful: evita workers zombis; Gunicorn gestiona el pool
CMD ["gunicorn", "-c", "gunicorn_conf.py", "wsgi:app"]
