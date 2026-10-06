// Controles na tela para celular/tablet, como um controle de videogame:
// direcional à esquerda, A (pular) e B (atacar) à direita, START (pausa) embaixo no meio.
// Cada botão só aperta/solta uma AÇÃO no Input, como se fosse uma tecla.
// O visual (cores, tamanhos, posições) está no CSS de tools/empacotar.py.

import { MOBILE_QUERY, isRotated } from '../config/constants.js';

const SETAS = { up: '▲', left: '◀', right: '▶', down: '▼' };
const BOTOES = [
  { id: 'botao-a', action: 'jump', label: 'A' },
  { id: 'botao-b', action: 'attack', label: 'B' },
  { id: 'botao-start', action: 'start', label: 'START' },
];
const DEADZONE = 0.12;  // fração do direcional; toque no centro não aperta nada
const DIAGONAL = 0.6;   // menor = diagonais mais fáceis de pegar

function el(parent, { id, className, text } = {}) {
  const e = document.createElement('div');
  if (id) e.id = id;
  if (className) e.className = className;
  if (text) e.textContent = text;
  parent.appendChild(e);
  return e;
}

export function attachTouchControls(input, root) {
  if (!matchMedia(MOBILE_QUERY).matches) return;

  const box = el(root, { id: 'controles' });
  box.addEventListener('contextmenu', (e) => e.preventDefault());

  // Direcional: uma área só, a direção vem da posição do dedo em relação ao centro.
  // Assim dá para deslizar o polegar de ◀ para ▶ (ou para a diagonal) sem levantar.
  const dpad = el(box, { id: 'dpad' });
  const setas = {};
  for (const [action, text] of Object.entries(SETAS)) {
    setas[action] = el(dpad, { className: `seta seta-${action}`, text });
  }
  let finger = null;
  const apply = (dirs) => {
    for (const action of Object.keys(SETAS)) {
      input.setTouch(action, dirs.has(action));
      setas[action].classList.toggle('ativo', dirs.has(action));
    }
  };
  const move = (e) => {
    if (e.pointerId !== finger) return;
    const r = dpad.getBoundingClientRect();
    let dx = e.clientX - (r.left + r.width / 2);
    let dy = e.clientY - (r.top + r.height / 2);
    if (isRotated()) [dx, dy] = [dy, -dx]; // tela girada 90°: converte para o "deitado" do jogo
    const min = r.width * DEADZONE;
    const dirs = new Set();
    if (Math.abs(dx) > min && Math.abs(dx) > Math.abs(dy) * DIAGONAL) dirs.add(dx < 0 ? 'left' : 'right');
    if (Math.abs(dy) > min && Math.abs(dy) > Math.abs(dx) * DIAGONAL) dirs.add(dy < 0 ? 'up' : 'down');
    apply(dirs);
  };
  const release = (e) => {
    if (e.pointerId !== finger) return;
    finger = null;
    apply(new Set());
  };
  dpad.addEventListener('pointerdown', (e) => {
    finger = e.pointerId;
    dpad.setPointerCapture(e.pointerId);
    move(e);
  });
  dpad.addEventListener('pointermove', move);
  dpad.addEventListener('pointerup', release);
  dpad.addEventListener('pointercancel', release);

  for (const { id, action, label } of BOTOES) {
    const b = el(box, { id, className: 'botao', text: label });
    const set = (on) => { input.setTouch(action, on); b.classList.toggle('ativo', on); };
    b.addEventListener('pointerdown', (e) => { b.setPointerCapture(e.pointerId); set(true); });
    b.addEventListener('pointerup', () => set(false));
    b.addEventListener('pointercancel', () => set(false));
  }

  // Ao tocar: tela cheia + trava em paisagem (Android). Onde não dá (iPhone), o CSS gira o jogo.
  window.addEventListener('pointerup', () => {
    if (document.fullscreenElement || !document.documentElement.requestFullscreen) return;
    document.documentElement.requestFullscreen({ navigationUI: 'hide' })
      .then(() => screen.orientation?.lock?.('landscape'))
      .catch(() => {});
  });
}
