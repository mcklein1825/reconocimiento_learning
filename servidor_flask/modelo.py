"""
modelo.py
Entrena un clasificador de dígitos (0-9) con MNIST y lo guarda con joblib.
Ejecutar UNA sola vez:  python modelo.py
"""

import numpy as np
import joblib
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# ──────────────────────────────────────────────
# PASO 1: Descargar MNIST (70,000 imágenes 28x28)
# ──────────────────────────────────────────────
print("Descargando dataset MNIST...")
mnist = fetch_openml("mnist_784", version=1, as_frame=False, parser="auto")
X, y = mnist.data, mnist.target.astype(int)
print(f"✅ Dataset cargado: {X.shape[0]} imágenes, {X.shape[1]} píxeles")

# ──────────────────────────────────────────────
# PASO 2: Separar entrenamiento / prueba
# ──────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"Entrenamiento: {X_train.shape[0]} | Prueba: {X_test.shape[0]}")

# ──────────────────────────────────────────────
# PASO 3: Crear pipeline (escalar + KNN)
# ──────────────────────────────────────────────
modelo = Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsClassifier(n_neighbors=5, weights="distance"))
])

# ──────────────────────────────────────────────
# PASO 4: Entrenar
# ──────────────────────────────────────────────
print("Entrenando modelo...")
modelo.fit(X_train, y_train)
print("Entrenamiento terminado")

# ──────────────────────────────────────────────
# PASO 5: Evaluar
# ──────────────────────────────────────────────
y_pred = modelo.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\nPrecisión en test: {acc:.4f} ({acc*100:.2f}%)")
print("\nReporte de clasificación:")
print(classification_report(y_test, y_pred, digits=4))

# ──────────────────────────────────────────────
# PASO 6: Guardar con joblib
# ──────────────────────────────────────────────
archivo = "digit_classifier.joblib"
joblib.dump(modelo, archivo)
print(f"\nModelo guardado en: {archivo}")