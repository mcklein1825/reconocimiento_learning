// Tests de integración del contenedor App con el servicio API mockeado.

import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App";
import * as api from "./services/api";

jest.spyOn(console, "error").mockImplementation(() => {});

// Pinta una celda simulando un clic completo (down+up) para que el estado
// "dibujando" termine igual que en un navegador real.
const paintCell = async (user, row, col) => {
  const target = screen.getByTestId(`node-${row}-${col}`);
  await user.pointer([
    { keys: "[MouseLeft>]", target },
    { keys: "[/MouseLeft]" },
  ]);
};

beforeEach(() => {
  jest.spyOn(api, "predictDigit").mockReset();
});

afterAll(() => jest.restoreAllMocks());

test("renderiza el título y los controles", () => {
  render(<App />);
  expect(screen.getByText(/Dibuja un número/i)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /enviar/i })).toBeDisabled();
  expect(screen.getByRole("status")).toHaveTextContent(/aún no hay predicción/i);
});

test("habilita ENVIAR tras pintar una celda", async () => {
  const user = userEvent.setup();
  render(<App />);

  await paintCell(user, 10, 10);

  expect(screen.getByRole("button", { name: /enviar/i })).toBeEnabled();
});

test("no envía si la cuadrícula está vacía", async () => {
  const user = userEvent.setup();
  render(<App />);
  // El botón está disabled; pulsarlo no debe llamar a la API
  await user.click(screen.getByRole("button", { name: /enviar/i })).catch(() => {});
  expect(api.predictDigit).not.toHaveBeenCalled();
});

test("muestra loading y luego el resultado con confianza", async () => {
  const user = userEvent.setup();
  let resolvePromise;
  api.predictDigit.mockImplementation(
    () => new Promise((res) => { resolvePromise = res; })
  );

  render(<App />);
  await paintCell(user, 5, 5);
  await user.click(screen.getByRole("button", { name: /enviar/i }));

  const sendButton = screen.getByRole("button", { name: /enviando/i });
  expect(sendButton).toBeDisabled();
  expect(screen.getByRole("status")).toHaveTextContent(/analizando/i);

  resolvePromise({ prediction: 3, confidence: 0.87, model_version: "v1" });
  expect(await screen.findByText("3")).toBeInTheDocument();
  expect(screen.getByRole("status")).toHaveTextContent(/87\.0%/);
});

test("muestra un mensaje de error legible si la API falla", async () => {
  const user = userEvent.setup();
  api.predictDigit.mockRejectedValue({
    response: { data: { error: "Se esperaban 784 valores." }, status: 400 },
  });

  render(<App />);
  await paintCell(user, 1, 1);
  await user.click(screen.getByRole("button", { name: /enviar/i }));

  expect(await screen.findByText(/se esperaban 784 valores/i)).toBeInTheDocument();
});

test("LIMPIAR borra el dibujo, el resultado y deshabilita ENVIAR", async () => {
  const user = userEvent.setup();
  api.predictDigit.mockResolvedValue({ prediction: 9, confidence: 0.5 });

  render(<App />);
  await paintCell(user, 2, 2);
  await user.click(screen.getByRole("button", { name: /enviar/i }));
  expect(await screen.findByText("9")).toBeInTheDocument();

  await user.click(screen.getByRole("button", { name: /limpiar/i }));

  expect(screen.getByRole("button", { name: /enviar/i })).toBeDisabled();
  expect(screen.getByRole("status")).toHaveTextContent(/aún no hay predicción/i);
});
