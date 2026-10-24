"""
servidor.py
Servidor Flask que recibe un arreglo de 784 píxeles (28x28)
y devuelve el dígito predicho (0-9).
Ejecutar:  python servidor.py
"""

import numpy as np
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS

# ──────────────────────────────────────────────
# Cargar modelo entrenado
# ──────────────────────────────────────────────
MODELO_PATH = "digit_classifier.joblib"
modelo = joblib.load(MODELO_PATH)
print(f"✅ Modelo cargado desde {MODELO_PATH}")

# ──────────────────────────────────────────────
# Crear app Flask
# ──────────────────────────────────────────────
app = Flask(__name__)

# Permitir peticiones desde el frontend React (localhost:3000)
CORS(app, resources={r"/*": {"origins": "*"}})

# ──────────────────────────────────────────────
# Ruta principal: recibe el dibujo y predice
# ──────────────────────────────────────────────
@app.route("/", methods=["POST"])
def predecir():
    try:
        # El frontend envía un arreglo JSON de 784 enteros (0 o 255)
        datos = request.get_json(force=True)

        # Validar tamaño
        if len(datos) != 784:
            return jsonify({"error": f"Se esperaban 784 valores, se recibieron {len(datos)}"}), 400

        # Convertir a numpy array (fila de 784)
        imagen = np.array(datos, dtype=np.float64).reshape(1, 784)

        # Predecir
        prediccion = modelo.predict(imagen)[0]

        # Obtener probabilidades (si el modelo lo soporta)
        try:
            probabilidades = modelo.predict_proba(imagen)[0]
            confianza = float(np.max(probabilidades))
        except Exception:
            confianza = None

        print(f"🔢 Predicción: {prediccion} (confianza: {confianza:.2%})" if confianza else f"🔢 Predicción: {prediccion}")

        return jsonify(int(prediccion))

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────
# Ruta de salud (opcional, para verificar que está vivo)
# ──────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def salud():
    return jsonify({"status": "ok", "modelo": MODELO_PATH})


# ──────────────────────────────────────────────
# Iniciar servidor
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Servidor corriendo en http://localhost:5000")
