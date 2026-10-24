"""
app/__init__.py
Application factory: config, logging, CORS seguro, límites y handlers de error.
"""

from __future__ import annotations

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge

from app.config import Config
from app.logging_config import configure_logging, get_logger, new_request_id


def create_app(config: type[Config] | None = None) -> Flask:
    cfg = config or Config
    configure_logging(cfg.LOG_LEVEL, cfg.JSON_LOGS)
    logger = get_logger(__name__)

    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = cfg.MAX_CONTENT_LENGTH
    app.config["MODEL_VERSION"] = cfg.MODEL_VERSION
    app.config["MODEL_PATH"] = cfg.MODEL_PATH

    # --- CORS: solo orígenes explícitos (nada de "*") ---
    CORS(
        app,
        resources={r"/predict": {"origins": cfg.CORS_ORIGINS},
                   r"/health": {"origins": cfg.CORS_ORIGINS},
                   r"/health/ready": {"origins": cfg.CORS_ORIGINS},
                   r"/version": {"origins": cfg.CORS_ORIGINS}},
        methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
        supports_credentials=False,
        max_age=86400,
    )

    # --- Request ID + log por request ---
    @app.before_request
    def _assign_request_id():
        new_request_id()

    @app.after_request
    def _log_request(response):
        logger.info(
            "%s %s -> %s",
            request.method,
            request.path,
            response.status_code,
            extra={"extra_fields": {
                "path": request.path,
                "method": request.method,
                "status": response.status_code,
                "remote_addr": request.remote_addr,
            }},
        )
        # Headers de seguridad básica
        response.headers["Server"] = "digit-api"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    # --- Blueprints ---
    from app.routes.health import bp_health
    from app.routes.predict import bp_predict

    app.register_blueprint(bp_health)
    app.register_blueprint(bp_predict)

    # --- Handlers de error globales (nunca filtrar stack traces al cliente) ---
    @app.errorhandler(RequestEntityTooLarge)
    def _too_large(_e):
        logger.warning("Body excede MAX_CONTENT_LENGTH")
        return jsonify({
            "error": f"Cuerpo demasiado grande (máx. {cfg.MAX_CONTENT_LENGTH} bytes).",
            "status": 413,
        }), 413

    @app.errorhandler(404)
    def _not_found(_e):
        return jsonify({"error": "Recurso no encontrado.", "status": 404}), 404

    @app.errorhandler(405)
    def _bad_method(_e):
        return jsonify({"error": "Método no permitido.", "status": 405}), 405

    @app.errorhandler(Exception)
    def _unhandled(e):
        logger.exception("Error no manejado: %s", e)
        return jsonify({"error": "Error interno del servidor.", "status": 500}), 500

    logger.info("App creada | modelo=%s version=%s", cfg.MODEL_PATH, cfg.MODEL_VERSION)
    return app
