import { getErrorMessage } from "../utils/errors";

test("prioriza el mensaje del backend", () => {
  const err = { response: { data: { error: "Valor nulo en el índice 3." } } };
  expect(getErrorMessage(err)).toBe("Valor nulo en el índice 3.");
});

test("timeout de axios", () => {
  expect(getErrorMessage({ code: "ECONNABORTED" })).toMatch(/tardó demasiado/i);
});

test("error de red", () => {
  expect(getErrorMessage({ message: "Network Error" })).toMatch(/No hay conexión/i);
});

test("fallback genérico", () => {
  expect(getErrorMessage(null)).toBe("Error desconocido.");
});
