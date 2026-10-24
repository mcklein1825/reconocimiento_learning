"""
wsgi.py — entry point para Gunicorn:  gunicorn -c gunicorn_conf.py wsgi:app
Desarrollo: python wsgi.py  (levanta el dev server de Flask)
"""

import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Solo desarrollo; en producción manda Gunicorn
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true",
    )
