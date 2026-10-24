// src/hooks/useDrawingGrid.js
// Lógica de dominio de la cuadrícula: pintar, limpiar y estado derivado.
// Estado 100% inmutable: cada pintura produce filas/columnas nuevas (nunca mutación).

import { useCallback, useMemo, useState } from "react";
import {
  createEmptyGrid,
  isGridEmpty,
  PIXEL_ON,
} from "../constants";

export default function useDrawingGrid() {
  const [grid, setGrid] = useState(createEmptyGrid);

  // Se deriva del estado en lugar de duplicarlo en un segundo useState
  // (antes existía `emptyGrid` que podía desincronizarse de `grid`).
  const isEmpty = useMemo(() => isGridEmpty(grid), [grid]);

  /** Pinta una celda de forma inmutable. No-op si ya estaba pintada. */
  const paintCell = useCallback((rowIndex, colIndex) => {
    setGrid((prev) => {
      if (!prev[rowIndex] || prev[rowIndex][colIndex] === PIXEL_ON) {
        return prev; // sin cambios → React no re-renderiza
      }
      // Copia solo la fila afectada; el resto comparte referencias (barato)
      const nextRow = [...prev[rowIndex]];
      nextRow[colIndex] = PIXEL_ON;
      const next = [...prev];
      next[rowIndex] = nextRow;
      return next;
    });
  }, []);

  const clear = useCallback(() => setGrid(createEmptyGrid()), []);

  return { grid, isEmpty, paintCell, clear };
}
