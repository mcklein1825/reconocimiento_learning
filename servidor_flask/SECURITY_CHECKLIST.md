# Checklist de seguridad — API de clasificación de dígitos (Flask)

## Validación de entrada
- [x] Solo se acepta `Content-Type: application/json` (415 en caso contrario).
- [x] JSON malformado → 400 sin stack trace.
- [x] Payload debe ser **lista** de exactamente 784 números (rechaza dict, string, escalar, null).
- [x] Rechazo explícito de `null`, booleanos y strings dentro del arreglo.
- [x] Rechazo de `NaN` e `Inf` (doble filtro: por elemento y con `np.isfinite`).
- [x] Rango de píxeles validado `[0, 255]` vectorizado.
- [x] Matrices anidadas/mal dimensionadas rechazadas (longitud o tipo de elemento).

## Límites y disponibilidad
- [x] `MAX_CONTENT_LENGTH = 64 KB` (413 para bodies gigantes) + chequeo defensivo de `Content-Length`.
- [x] Timeout de inferencia (`INFERENCE_TIMEOUT`, default 5 s) → 504 sin bloquear el worker.
- [x] Modelo ausente/corrupto → 503 (degradación controlada, no crash).
- [x] Gunicorn: `timeout` duro, `graceful_timeout`, reciclaje con `max_requests` (anti-fugas).

## CORS y headers
- [x] CORS con allowlist explícita (`CORS_ORIGINS`), **sin wildcard `*`**.
- [x] Sin `supports_credentials` (la API es anónima; evita CSRF cross-origin con cookies).
- [x] Headers: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy`.
- [x] `Server` header ofuscado.

## Errores y logging
- [x] Handlers globales 404/405/413/500 devuelven JSON sin detalles internos.
- [x] Mensajes de error al cliente sin stack traces ni rutas absolutas.
- [x] Logging estructurado JSON con `request_id` por petición (correlación).
- [x] Logs a stdout (12-factor); Docker/K8s los recoge y rota.

## Despliegue
- [x] Dockerfile: usuario no-root, `PYTHONUNBUFFERED`, permisos read-only, HEALTHCHECK.
- [x] `.dockerignore` excluye tests, .env y entrenamiento.
- [x] Config vía variables de entorno (`MODEL_PATH`, `CORS_ORIGINS`, etc.).
- [x] Debug desactivado por defecto; nunca usar el server de Flask en producción.

## Recomendaciones adicionales (no incluidas)
- [ ] Rate limiting (`flask-limiter` + Redis) si la API es pública.
- [ ] TLS termination en reverse proxy (nginx/traefik) + HSTS.
- [ ] Escaneo de imagen (trivy/snyk) y pines de versiones en CI.
- [ ] Validar integridad del joblib (hash/firma) antes de cargarlo.
- [ ] Auditar dependencias periódicamente (`pip-audit`).
