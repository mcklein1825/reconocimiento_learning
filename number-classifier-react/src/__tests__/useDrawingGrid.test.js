// Tests del hook: estado inmutable garantizado.

import { renderHook, act } from "@testing-library/react";
import useDrawingGrid from "../hooks/useDrawingGrid";
import { PIXEL_ON } from "../constants";

test("paintCell crea referencias nuevas (inmutabilidad)", () => {
  const { result } = renderHook(() => useDrawingGrid());
  const before = result.current.grid;

  act(() => result.current.paintCell(4, 7));

  const after = result.current.grid;
  expect(after).not.toBe(before);            // array nuevo
  expect(after[4]).not.toBe(before[4]);      // solo la fila pintada es nueva
  expect(after[5]).toBe(before[5]);          // las demás comparten referencia
  expect(after[4][7]).toBe(PIXEL_ON);
  expect(before[4][7]).toBe(0);              // el estado anterior NO se mutó
});

test("pintar dos veces la misma celda es idempotente", () => {
  const { result } = renderHook(() => useDrawingGrid());
  act(() => result.current.paintCell(1, 1));
  const first = result.current.grid;
  act(() => result.current.paintCell(1, 1));
  expect(result.current.grid).toBe(first);   // sin re-render innecesario
});

test("isEmpty pasa a false al pintar y clear() reinicia todo", () => {
  const { result } = renderHook(() => useDrawingGrid());
  expect(result.current.isEmpty).toBe(true);
  act(() => result.current.paintCell(0, 0));
  expect(result.current.isEmpty).toBe(false);
  act(() => result.current.clear());
  expect(result.current.isEmpty).toBe(true);
  expect(result.current.grid.flat().some((v) => v === PIXEL_ON)).toBe(false);
});
