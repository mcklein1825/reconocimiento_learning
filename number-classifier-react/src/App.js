// librerías
import { useState, useEffect } from "react";
import axios from "axios";

// estilos
import "./App.css";

const ROWS = 28;
const COLS = 28;

// Crear cuadrícula vacía
// 0 = nodo inactivo
// 255 = nodo activo
const createEmptyGrid = () =>
  Array.from({ length: ROWS }, () => Array(COLS).fill(0));

export default function App() {
  // Cuadrícula 28 x 28
  const [grid, setGrid] = useState(createEmptyGrid);

  // Saber si el usuario está dibujando
  const [isUserDrawing, setIsUserDrawing] = useState(false);

  // Saber si la cuadrícula está vacía
  const [emptyGrid, setEmptyGrid] = useState(true);

  // Resultado devuelto por el servidor
  const [resultNum, setResultNum] = useState(null);

  // Estado de carga mientras envía al servidor
  const [loading, setLoading] = useState(false);

  // Si el usuario suelta el mouse fuera de la app, dejamos de dibujar
  useEffect(() => {
    const stopDrawing = () => setIsUserDrawing(false);

    window.addEventListener("mouseup", stopDrawing);

    return () => {
      window.removeEventListener("mouseup", stopDrawing);
    };
  }, []);

  const startDrawing = () => {
    setIsUserDrawing(true);
  };

  const stopDrawing = () => {
    setIsUserDrawing(false);
  };

  const paintNode = (rowIndex, colIndex, force = false) => {
    // Solo pinta si el usuario está dibujando
    // force = true se usa para pintar el primer clic
    if (!force && !isUserDrawing) return;

    if (emptyGrid) {
      setEmptyGrid(false);
    }

    setGrid((previousGrid) => {
      // Si ya está pintado, no hacemos nada
      if (previousGrid[rowIndex][colIndex] === 255) {
        return previousGrid;
      }

      // Copia inmutable de la cuadrícula
      const newGrid = previousGrid.map((row) => [...row]);

      // Pintar nodo seleccionado
      newGrid[rowIndex][colIndex] = 255;

      return newGrid;
    });
  };

  const clearGrid = () => {
    setGrid(createEmptyGrid());
    setEmptyGrid(true);
    setResultNum(null);
  };

  const sendNumber = async () => {
    // Enviar solo si el usuario dibujó algo
    if (emptyGrid) return;

    setLoading(true);

    // Convertir matriz 28x28 en arreglo de 784 valores
    const numArr = grid.flat();

    try {
      // Enviar arreglo al servidor Flask
      const response = await axios.post("http://localhost:5000/", numArr);

      setResultNum(response.data);
    } catch (error) {
      console.error("Error al enviar el número:", error);
      setResultNum("Error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="left-container">
        <div className="grid-container">
          <h1 className="grid-title">Dibuja un número (0 - 9)</h1>

          <div
            className="grid-top-container"
            onMouseUp={stopDrawing}
            onMouseLeave={stopDrawing}
          >
            {grid.map((row, rowIndex) => (
              <div className="grid-row" key={`row-${rowIndex}`}>
                {row.map((value, colIndex) => (
                  <div
                    key={`node-${rowIndex}-${colIndex}`}
                    className={
                      value === 255 ? "node-active" : "node-inactive"
                    }
                    onMouseDown={(event) => {
                      event.preventDefault();
                      startDrawing();
                      paintNode(rowIndex, colIndex, true);
                    }}
                    onMouseEnter={() => {
                      paintNode(rowIndex, colIndex, false);
                    }}
                  />
                ))}
              </div>
            ))}
          </div>

          <div className="grid-bottom-container">
            <button
              className="send-button"
              onClick={sendNumber}
              disabled={loading || emptyGrid}
            >
              ENVIAR
            </button>

            <button
              className="clear-button"
              onClick={clearGrid}
              disabled={loading}
            >
              LIMPIAR
            </button>
          </div>
        </div>
      </div>

      <div className="right-container">
        <h1 className="grid-title">El número dibujado es:</h1>

        <div className="server-response">
          {loading ? (
            <div className="loader-container-small" />
          ) : (
            resultNum
          )}
        </div>
      </div>
    </div>
  );
}