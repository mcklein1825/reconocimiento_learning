// src/utils/errors.js
// Normaliza errores de axios / dominio en un mensaje seguro para el usuario.

export function getErrorMessage(error) {
  if (!error) return "Error desconocido.";

  // Respuesta del backend con { error: "..." } validado
  const serverMessage = error?.response?.data?.error;
  if (typeof serverMessage === "string" && serverMessage.trim()) {
    return serverMessage;
  }

  if (error?.code === "ECONNABORTED") {
    return "El servidor tardó demasiado en responder. Intente de nuevo.";
  }
  if (error?.message === "Network Error" || !error?.response) {
    return "No hay conexión con el servidor. Verifique que Flask esté corriendo.";
  }
  if (error?.status === 503) {
    return "El modelo no está disponible en este momento.";
  }
  if (error?.status === 504) {
    return "La inferencia superó el tiempo máximo. Intente de nuevo.";
  }

  return error?.message || "Ocurrió un error inesperado.";
}
