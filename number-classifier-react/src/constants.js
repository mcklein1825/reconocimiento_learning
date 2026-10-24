// src/constants.js
// Única fuente de verdad del tamaño de la cuadrícula.
// Al derivar filas/columnas del MISMO array se elimina la inconsistencia
// entre ROWS y COLS que existía antes (dos constantes independientes).

export const GRID_ROWS = 28;
export const GRID_COLS = 28;

export const PIXEL_OFF = 0;
export const PIXEL_ON = 255;

/** Crea una cuadrícula vacía: GRID_ROWS x GRID_COLS.
 *  La inmutabilidad se aplica en el reducer/hook (nunca se muta en sitio),
 *  no con Object.freeze, que rompería copias y tests. */
export const createEmptyGrid = () =>
  Array.from({ length: GRID_ROWS }, () => Array(GRID_COLS).fill(PIXEL_OFF));

/** Convierte la cuadrícula 2D al arreglo plano de 784 píxeles que espera el backend. */
export const gridToFlatPixels = (grid) => {
  if (!Array.isArray(grid) || grid.length !== GRID_ROWS) {
    throw new Error("Cuadrícula inválida: número de filas inesperado.");
  }
  return grid.flatMap((row) => {
    if (!Array.isArray(row) || row.length !== GRID_COLS) {
      throw new Error("Cuadrícula inválida: número de columnas inesperado.");
    }
    return row;
  });
};

/** ¿La cuadrícula está totalmente vacía? (validación previa al envío) */
export const isGridEmpty = (grid) => !grid.some((row) => row.some((v) => v === PIXEL_ON));
