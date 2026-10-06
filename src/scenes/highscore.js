// Recorde e último código de fase salvos no navegador (opcional: se o armazenamento estiver
// bloqueado, só não salva).

const KEY = 'furia-na-floresta:recorde';
const CODE_KEY = 'kankas-gang:codigo';

export function loadHighScore() {
  try { return parseInt(localStorage.getItem(KEY), 10) || 0; } catch { return 0; }
}

export function saveHighScore(score) {
  try {
    if (score > loadHighScore()) localStorage.setItem(KEY, String(score));
  } catch { /* armazenamento indisponível */ }
}

/** Último código de fase alcançado (a tela de códigos já começa preenchida com ele). */
export function loadCode() {
  try { return localStorage.getItem(CODE_KEY) || ''; } catch { return ''; }
}

export function saveCode(code) {
  try { localStorage.setItem(CODE_KEY, code); } catch { /* armazenamento indisponível */ }
}
