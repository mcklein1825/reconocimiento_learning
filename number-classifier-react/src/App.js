// src/App.js
// Componente contenedor: orquesta el hook de dibujo y el envío al backend.
// Sin DOM imperativo (nada de getElementById), sin mutación de estado,
// con estados explícitos de loading / error / resultado.

import React, { useCallback, useState } from "react";
import "./App.css";

import useDrawingGrid from "./hooks/useDrawingGrid";
import { predictDigit } from "./services/api";
import { getErrorMessage } from "./utils/errors";
import { gridToFlatPixels } from "./constants";

import DrawingGrid from "./components/DrawingGrid";
import PredictionPanel from "./components/PredictionPanel";

export default function App() {
  const { grid, isEmpty, paintCell, clear } = useDrawingGrid();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleClear = useCallback(() => {
    clear();
    setResult(null);
    setError(null);
  }, [clear]);

  const handleSend = useCallback(async () => {
    // Validación de negocio: no enviar un lienzo vacío
    if (isEmpty || loading) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Contrato de forma validado antes de enviar (filas x columnas consistentes)
      const pixels = gridToFlatPixels(grid);
      const data = await predictDigit(grid);
      setResult(data);
    } catch (err) {
      console.error("Error al enviar el número:", err);
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [grid, isEmpty, loading]);

  return (
    <main className="container">
      <div className="left-container">
        <section className="grid-container" aria-label="Área de dibujo">
          <h1 className="grid-title">Dibuja un número (0 - 9)</h1>

          <DrawingGrid grid={grid} onPaintCell={paintCell} />

          <div className="grid-bottom-container">
            <button
              type="button"
              className="send-button"
              onClick={handleSend}
              disabled={loading || isEmpty}
              aria-disabled={loading || isEmpty}
            >
              {loading ? "ENVIANDO…" : "ENVIAR"}
            </button>

            <button
              type="button"
              className="clear-button"
              onClick={handleClear}
              disabled={loading || isEmpty}
            >
              LIMPIAR
            </button>
          </div>

          {isEmpty && (
            <p className="grid-hint" role="note">
              Dibuja algo en la cuadrícula para habilitar el envío.
            </p>
          )}
        </section>
      </div>

      <PredictionPanel loading={loading} error={error} result={result} />
    </main>
  );
}
