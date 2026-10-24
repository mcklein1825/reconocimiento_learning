// src/components/PredictionPanel.js
// Panel de resultado: maneja los tres estados explícitos (loading / error / éxito).
// aria-live="polite" anuncia cambios a lectores de pantalla sin interrumpir.

import React from "react";

export default function PredictionPanel({ loading, error, result }) {
  let content = "Aún no hay predicción.";

  if (loading) {
    content = (
      <>
        <span className="loader-container-small" aria-hidden="true" />
        Analizando dibujo…
      </>
    );
  } else if (error) {
    content = <span className="prediction-error">⚠️ {error}</span>;
  } else if (result != null) {
    content = (
      <>
        <strong className="prediction-digit">{result.prediction}</strong>
        {typeof result.confidence === "number" && (
          <span className="prediction-confidence">
            {" "}
            ({(result.confidence * 100).toFixed(1)}%)
          </span>
        )}
      </>
    );
  }

  return (
    <div className="right-container">
      <h2 className="grid-title">El número dibujado es:</h2>
      <div className="server-response" role="status" aria-live="polite">
        {content}
      </div>
    </div>
  );
}
