// src/components/GridNode.js
// Una celda de la cuadrícula. React.memo evita re-renderizar las 783 celdas
// que no cambiaron cuando se pinta una.

import React from "react";

const GridNode = React.memo(function GridNode({
  rowIndex,
  colIndex,
  active,
  onPaintStart,
  onPaintMove,
}) {
  return (
    <div
      role="presentation"
      data-testid={`node-${rowIndex}-${colIndex}`}
      className={active ? "node-active" : "node-inactive"}
      onMouseDown={(e) => {
        e.preventDefault();
        onPaintStart(rowIndex, colIndex);
      }}
      onMouseEnter={() => onPaintMove(rowIndex, colIndex)}
      onTouchStart={(e) => {
        // Sin preventDefault aquí para permitir scroll fuera de la cuadrícula;
        // el gesto de dibujo lo captura el contenedor con touch-action: none.
        onPaintStart(rowIndex, colIndex);
      }}
      onTouchMove={(e) => {
        // En touch, `elementFromPoint` identifica la celda real bajo el dedo,
        // porque los eventos targetean al elemento donde empezó el gesto.
        const touch = e.touches[0];
        if (!touch) return;
        const el = document.elementFromPoint(touch.clientX, touch.clientY);
        const testId = el?.getAttribute?.("data-testid");
        if (testId) {
          const match = /^node-(\d+)-(\d+)$/.exec(testId);
          if (match) onPaintMove(Number(match[1]), Number(match[2]));
        }
      }}
    />
  );
});

export default GridNode;
