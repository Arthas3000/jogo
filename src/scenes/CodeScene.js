// Tela de CÓDIGOS: digite o código mostrado ao chegar numa fase para começar o jogo direto nela.
// ↑ ↓ trocam o caractere, ← → mudam de casa, START/A confirma, B volta.
// No teclado dá para digitar direto (Backspace apaga, Esc volta); no toque, tocar numa casa a seleciona/avança.
// Já começa preenchida com o último código alcançado (salvo no navegador).

import { VIEW_W, VIEW_H } from '../config/constants.js';
import { PHASES, phaseByCode } from '../config/phases.js';
import { clamp, easeOutCubic } from '../core/math.js';
import { loadCode, saveCode } from './highscore.js';
import { SelectScene } from './SelectScene.js';
import { TitleScene } from './TitleScene.js';

const CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
const LEN = 4;
const SLOT_W = 28;
const SLOT_H = 32;
const SLOT_GAP = 8;
const SLOT_Y = 84;

export class CodeScene {
  constructor(game) {
    this.game = game;
    const saved = loadCode().toUpperCase();
    this.code = Array.from({ length: LEN }, (_, i) => (CHARS.includes(saved[i]) ? saved[i] : 'A'));
    this.pos = 0;
    this.t = 0;
    this.state = 'editing'; // editing | ok | leaving
    this.message = null;    // { text, color, at }
    const total = LEN * SLOT_W + (LEN - 1) * SLOT_GAP;
    this.slotX = Array.from({ length: LEN }, (_, i) => Math.round((VIEW_W - total) / 2 + i * (SLOT_W + SLOT_GAP)));
    this._onKey = (e) => this._typed(e);
  }

  enter() {
    this.game.audio.playMusic('audio/musica/selecao');
    // Captura antes do Input: letras como Z/X/A/D digitam em vez de pular/atacar/andar.
    window.addEventListener('keydown', this._onKey, true);
  }

  exit() { window.removeEventListener('keydown', this._onKey, true); }

  /** Teclado físico: letras/números entram direto; Backspace apaga para trás; Esc volta. */
  _typed(e) {
    if (this.state !== 'editing') return;
    const ch = e.key.length === 1 ? e.key.toUpperCase() : '';
    if (ch && CHARS.includes(ch)) {
      this.code[this.pos] = ch;
      this.pos = Math.min(LEN - 1, this.pos + 1);
      this.game.audio.play('audio/sfx/ui_mover');
    } else if (e.key === 'Backspace') {
      this.pos = Math.max(0, this.pos - 1);
      this.game.audio.play('audio/sfx/ui_voltar');
    } else if (e.key === 'Escape') {
      this._leave();
    } else {
      return; // setas, Enter, espaço: seguem para o Input normalmente
    }
    e.preventDefault();
    e.stopImmediatePropagation();
  }

  _cycle(step) {
    const i = CHARS.indexOf(this.code[this.pos]);
    this.code[this.pos] = CHARS[(i + step + CHARS.length) % CHARS.length];
    this.game.audio.play('audio/sfx/ui_mover');
  }

  update(dt) {
    this.t += dt;
    const { input, audio } = this.game;
    if (this.state === 'ok' && this.t - this.message.at > 1.3) {
      this.state = 'leaving';
      this.game.transitionTo(() => new SelectScene(this.game, { phaseIndex: this.phaseIndex }), { duration: 0.4 });
    }
    if (this.state !== 'editing' || this.t < 0.3) return;

    if (input.pressed('up')) this._cycle(1);
    if (input.pressed('down')) this._cycle(-1);
    if (input.pressed('left')) this.pos = (this.pos - 1 + LEN) % LEN;
    if (input.pressed('right')) this.pos = (this.pos + 1) % LEN;

    const p = input.pointer;
    if (p?.clicked) {
      const hit = this.slotX.findIndex((x) => p.x >= x && p.x < x + SLOT_W && p.y >= SLOT_Y && p.y < SLOT_Y + SLOT_H);
      if (hit === this.pos) this._cycle(1);
      else if (hit >= 0) this.pos = hit;
      else if (p.y > SLOT_Y + SLOT_H + 20 && p.y < SLOT_Y + SLOT_H + 44) return this._submit();
    }

    if (input.pressed('start') || input.pressed('jump')) return this._submit();
    if (input.pressed('attack') || input.pressed('back')) return this._leave(); // B do controle/tela
  }

  _submit() {
    const code = this.code.join('');
    const index = phaseByCode(code);
    const { audio } = this.game;
    if (index < 0) {
      audio.play('audio/sfx/ui_voltar', { pitchVar: 0 });
      this.message = { text: 'CÓDIGO INVÁLIDO', color: 'vermelha', at: this.t };
      return;
    }
    audio.play('audio/sfx/ui_pronto', { pitchVar: 0 });
    saveCode(code);
    this.phaseIndex = index;
    this.state = 'ok';
    this.message = { text: `${PHASES[index].title} LIBERADA!`, color: 'amarela', at: this.t };
  }

  _leave() {
    this.game.audio.play('audio/sfx/ui_voltar');
    this.state = 'leaving';
    this.game.transitionTo(() => new TitleScene(this.game, { skipIntro: true }), { duration: 0.4 });
  }

  draw(r) {
    const { assets, font, time } = this.game;
    r.image(assets.sprite('ui/selecao_fundo'), 0, 0);
    const titleY = Math.round(14 - (1 - easeOutCubic(clamp(this.t / 0.4, 0, 1))) * 40);
    font.draw(r, 'CÓDIGOS', VIEW_W / 2, titleY, { align: 'center', color: 'metal', scale: 2 });
    font.draw(r, 'DIGITE O CÓDIGO DA FASE', VIEW_W / 2, 52, { align: 'center', color: 'branca' });
    font.draw(r, 'QUE VOCÊ ALCANÇOU', VIEW_W / 2, 63, { align: 'center', color: 'branca' });

    // Casa recusada treme; casa atual pisca.
    const msg = this.message;
    const shake = msg?.color === 'vermelha' && this.t - msg.at < 0.3 ? Math.round(Math.sin(this.t * 80) * 3) : 0;
    const panel = assets.sprite('ui/painel');
    this.code.forEach((ch, i) => {
      const x = this.slotX[i] + shake;
      r.nineSlice(panel, x, SLOT_Y, SLOT_W, SLOT_H);
      const selected = i === this.pos && this.state === 'editing';
      font.draw(r, ch, x + SLOT_W / 2, SLOT_Y + 9, { align: 'center', color: selected ? 'amarela' : 'branca', scale: 2 });
      if (selected && Math.floor(time * 3) % 2 === 0) font.draw(r, '_', x + SLOT_W / 2, SLOT_Y + SLOT_H + 2, { align: 'center', color: 'amarela', scale: 2 });
    });

    font.draw(r, 'CONFIRMAR', VIEW_W / 2, SLOT_Y + SLOT_H + 28, { align: 'center', color: this.state === 'editing' ? 'ciano' : 'cinza' });
    if (msg && (msg.color === 'amarela' || this.t - msg.at < 2)) {
      font.draw(r, msg.text, VIEW_W / 2, SLOT_Y + SLOT_H + 46, { align: 'center', color: msg.color, scale: msg.color === 'amarela' ? 2 : 1 });
    }
    font.draw(r, 'CIMA/BAIXO: LETRA   < >: CASA   START: OK   B: VOLTAR', VIEW_W / 2, VIEW_H - 13, { align: 'center', color: 'cinza' });
  }
}
