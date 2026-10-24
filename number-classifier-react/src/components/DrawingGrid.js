// src/components/DrawingGrid.js
// Cuadrícula 28x28 accesible con soporte de mouse y touch.
// El estado "dibujando" vive aquí; se termina también si el puntero/dedo
// se levanta fuera del componente (listeners en window).

import React, { useCallback, useEffect, useState } from "react";
import GridNode from "./GridNode";

export default function DrawingGrid({ grid, onPaintCell }) {
  const [isDrawing, setIsDrawing] = useState(false);

  // Terminar el trazo aunque el mouse/dedo se suelte fuera de la cuadrícula
  useEffect(() => {
    const stop = () => setIsDrawing(false);
    window.addEventListener("mouseup", stop);
    window.addEventListener("touchend", stop);
    window.addEventListener("touchcancel", stop);
    return () => {
      window.removeEventListener("mouseup", stop);
      window.removeEventListener("touchend", stop);
      window.removeEventListener("touchcancel", stop);
    };
  }, []);

  const handlePaintStart = useCallback(
    (row, col) => {
      setIsDrawing(true);
      onPaintCell(row, col);
    },
    [onPaintCell]
  );

  const handlePaintMove = useCallback(
    (row, col) => {
      if (isDrawing) onPaintCell(row, col);
    },
    [isDrawing, onPaintCell]
  );

  return (
    <div
      className="grid-top-container"
      role="application"
      aria-label="Cuadrícula de dibujo de 28 por 28. Mantenga presionado y arrastre para pintar un dígito."
      onMouseUp={() => setIsDrawing(false)}
      onMouseLeave={() => setIsDrawing(false)}
      onTouchEnd={() => setIsDrawing(false)}
      style={{ touchAction: "none" }} // el navegador no interfiere con el gesto
    >
      {grid.map((row, rowIndex) => (
        <div className="grid-row" key={`row-${rowIndex}`}>
          {row.map((value, colIndex) => (
            <GridNode
              key={`node-${rowIndex}-${colIndex}`}
              rowIndex={rowIndex}
              colIndex={colIndex}
              active={value === 255}
              onPaintStart={handlePaintStart}
              onPaintMove={handlePaintMove}
            />
          ))}
        </div>
      ))}
    </div>
  );
}
