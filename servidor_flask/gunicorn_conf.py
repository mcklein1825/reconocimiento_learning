"""
gunicorn_conf.py — configuración de Gunicorn para producción.
Uso: gunicorn -c gunicorn_conf.py wsgi:app

Estrategia anti-bloqueo de workers:
  - Workers síncronos (gevent no es necesario: sklearn libera el GIL en C).
  - timeout duro por request + graceful_timeout para drenar.
  - preload NO se usa: joblib+sklearn con fork puede duplicar memoria;
    mejor cargar el modelo por worker (lazy) tras el fork.
"""

import multiprocessing
import os

bind = os.environ.get("BIND", "0.0.0.0:8000")

workers = int(os.environ.get("WEB_CONCURRENCY", min(4, multiprocessing.cpu_count())))
worker_class = "sync"

# Un request colgado no debe matar al worker: que gunicorn lo mate y lo reinicie.
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "10"))
graceful_timeout = 5
keepalive = 2

max_requests = 1000          # reciclaje periódico ante fugas de memoria
max_requests_jitter = 100

accesslog = "-"              # stdout (12-factor: el log lo recoge Docker)
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "info").lower()
proc_name = "digit-classifier-api"
