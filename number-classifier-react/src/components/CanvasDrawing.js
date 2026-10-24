/* eslint-disable */
// src/components/CanvasDrawing.js  (OPCIONAL — versión de alto rendimiento)
//
// Alternativa a la cuadrícula DOM: un solo <canvas> de 280x280 (10px por celda).
// Ventajas vs. 784 <div>:
//   - 1 nodo en el DOM en vez de 784 → sin re-renders por trazo.
//   - Pointer Events unifican mouse/touch/lápiz con un solo handler.
//   - Lectura directa del bitmap → downsample a 28x28 sin estado React por celda.
//
// Uso: <CanvasDrawing onSubmit={(pixels) => predict(pixels)} />
// Nota: requiere babel config para class properties si CRA no lo soporta;
// se puede convertir a hooks fácilmente. NO está montado en App por defecto.

import React from "react";

const CELL = 10;            // px por celda en pantalla
const SIZE = 28 * CELL;     // 280x280

export default class CanvasDrawing extends React.Component {
  state = { hasInk: false };
  ctx = null;
  drawing = false;
  lastPoint = null;

  handlePointerDown = (e) => {
    e.preventDefault();
    this.canvas.setPointerCapture(e.pointerId); // gestos fuera del canvas siguen dentro
    this.drawing = true;
    this.lastPoint = this.getPoint(e);
    this.dot(this.lastPoint);
  };

  handlePointerMove = (e) => {
    if (!this.drawing) return;
    const p = this.getPoint(e);
    this.stroke(this.lastPoint, p);              // interpola: no hay huecos rápidos
    this.lastPoint = p;
  };

  endStroke = () => { this.drawing = false; };

  getPoint(e) {
    const r = this.canvas.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  }

  dot({ x, y }) {
    this.ctx.fillStyle = "#fff";
    this.ctx.beginPath();
    this.ctx.arc(x, y, 5, 0, Math.PI * 2);       // brocha redondeada
    this.ctx.fill();
    if (!this.state.hasInk) this.setState({ hasInk: true });
  }

  stroke(a, b) {
    this.ctx.strokeStyle = "#fff";
    this.ctx.lineWidth = 10;
    this.ctx.lineCap = "round";
    this.ctx.beginPath();
    this.ctx.moveTo(a.x, a.y);
    this.ctx.lineTo(b.x, b.y);
    this.ctx.stroke();
  }

  /** Downsample del bitmap a 784 valores 0/255 listos para el backend. */
  toPixels() {
    const img = this.ctx.getImageData(0, 0, SIZE, SIZE).data;
    const out = new Array(28 * 28);
    for (let row = 0; row < 28; row++) {
      for (let col = 0; col < 28; col++) {
        let acc = 0;
        for (let dy = 0; dy < CELL; dy += 2) {
          for (let dx = 0; dx < CELL; dx += 2) {
            const idx = ((row * CELL + dy) * SIZE + col * CELL + dx) * 4;
            acc += img[idx + 3];                 // canal alpha
          }
        }
        out[row * 28 + col] = acc > 0 ? 255 : 0; // binarización simple
      }
    }
    return out;
  }

  clear = () => {
    this.ctx.fillStyle = "#000";
    this.ctx.fillRect(0, 0, SIZE, SIZE);
    this.setState({ hasInk: false });
  };

  submit = () => {
    if (this.state.hasInk) this.props.onSubmit(this.toPixels());
  };

  render() {
    return (
      <div>
        {/* role=img + aria-label: accesible para lectores de pantalla */}
        <canvas
          ref={(el) => {
            this.canvas = el;
            if (el && !this.ctx) {
              this.ctx = el.getContext("2d");
              this.clear();
            }
          }}
          width={SIZE}
          height={SIZE}
          role="img"
          aria-label="Lienzo para dibujar un dígito del 0 al 9"
          style={{ touchAction: "none", background: "#000" }}
          onPointerDown={this.handlePointerDown}
          onPointerMove={this.handlePointerMove}
          onPointerUp={this.endStroke}
          onPointerCancel={this.endStroke}
        />
        <button type="button" onClick={this.submit} disabled={!this.state.hasInk}>
          ENVIAR
        </button>
        <button type="button" onClick={this.clear}>LIMPIAR</button>
      </div>
    );
  }
}
