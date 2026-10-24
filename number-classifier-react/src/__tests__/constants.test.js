// Tests unitarios de utilidades puras de la cuadrícula.

import {
  createEmptyGrid,
  gridToFlatPixels,
  isGridEmpty,
  GRID_ROWS,
  GRID_COLS,
  PIXEL_ON,
} from "../constants";

test("createEmptyGrid produce 28 filas de 28 columnas en cero", () => {
  const grid = createEmptyGrid();
  expect(grid).toHaveLength(GRID_ROWS);
  grid.forEach((row) => expect(row).toHaveLength(GRID_COLS));
  expect(grid.flat().every((v) => v === 0)).toBe(true);
});

test("gridToFlatPixels devuelve 784 valores y preserva el orden fila a fila", () => {
  const grid = createEmptyGrid();
  grid[0][0] = PIXEL_ON;
  grid[1][0] = PIXEL_ON;
  const flat = gridToFlatPixels(grid);
  expect(flat).toHaveLength(GRID_ROWS * GRID_COLS);
  expect(flat[0]).toBe(PIXEL_ON);
  expect(flat[GRID_COLS]).toBe(PIXEL_ON); // inicio de la fila 1
});

test("gridToFlatPixels rechaza matrices mal dimensionadas", () => {
  expect(() => gridToFlatPixels([[1, 2]])).toThrow(/filas/);
  const bad = createEmptyGrid();
  bad[3] = [1, 2]; // fila con ancho incorrecto
  expect(() => gridToFlatPixels(bad)).toThrow(/columnas/);
});

test("isGridEmpty detecta dibujos", () => {
  const grid = createEmptyGrid();
  expect(isGridEmpty(grid)).toBe(true);
  grid[14][14] = PIXEL_ON;
  expect(isGridEmpty(grid)).toBe(false);
});
