import React from "react";
import { render, screen } from "@testing-library/react";
import PredictionPanel from "../components/PredictionPanel";

test("muestra estado vacío por defecto", () => {
  render(<PredictionPanel loading={false} error={null} result={null} />);
  expect(screen.getByRole("status")).toHaveTextContent(/aún no hay predicción/i);
});

test("muestra loading accesible", () => {
  render(<PredictionPanel loading error={null} result={null} />);
  expect(screen.getByRole("status")).toHaveTextContent(/analizando/i);
});

test("muestra el error normalizado", () => {
  render(<PredictionPanel loading={false} error="Sin conexión" result={null} />);
  expect(screen.getByRole("status")).toHaveTextContent(/sin conexión/i);
});

test("muestra predicción y confianza", () => {
  render(
    <PredictionPanel
      loading={false}
      error={null}
      result={{ prediction: 4, confidence: 0.912 }}
    />
  );
  expect(screen.getByRole("status")).toHaveTextContent("4");
  expect(screen.getByRole("status")).toHaveTextContent(/91\.2%/);
});

test("funciona sin confianza (confidence null)", () => {
  render(
    <PredictionPanel
      loading={false}
      error={null}
      result={{ prediction: 8, confidence: null }}
    />
  );
  expect(screen.getByRole("status")).toHaveTextContent("8");
  expect(screen.getByRole("status")).not.toHaveTextContent(/%/);
});
