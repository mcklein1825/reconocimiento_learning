// src/services/api.js
// Capa de acceso al backend: único lugar que conoce URLs, timeouts y forma del payload.

import axios from "axios";
import { GRID_ROWS, GRID_COLS } from "../constants";

export const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://localhost:5000";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // no dejar el request colgado indefinidamente
  headers: { "Content-Type": "application/json" },
});

/**
 * Envía la cuadrícula 2D como arreglo plano de 784 píxeles.
 * @param {number[][]} grid - Cuadrícula GRID_ROWS x GRID_COLS con valores 0/255.
 * @returns {Promise<{prediction:number, confidence:number|null, model_version:string}>}
 */
export async function predictDigit(grid) {
  // Contrato explícito: filas x columnas correctas ANTES de salir por red
  if (
    !Array.isArray(grid) ||
    grid.length !== GRID_ROWS ||
    grid.some((row) => !Array.isArray(row) || row.length !== GRID_COLS)
  ) {
    throw new Error("Cuadrícula con dimensiones inválidas.");
  }

  const pixels = grid.flat();
  const { data } = await client.post("/predict", pixels);
  return data;
}

/** Consulta de salud del backend (usable para mostrar banner de offline). */
export async function checkHealth() {
  const { data } = await client.get("/health");
  return data;
}

export default client;
