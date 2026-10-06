// Tela inicial estilo fliperama:
//   1) o logo cai e quica sobre a floresta em parallax, com a caminhonete da gangue correndo
//      na estrada de terra lá embaixo;
//   2) "PRESSIONE START" pisca (inserir ficha);
//   3) os botões "INICIAR JOGO", "CÓDIGOS" e "SAIR" deslizam para dentro.

import { VIEW_W, VIEW_H } from '../config/constants.js';
import { clamp, easeOutBounce } from '../core/math.js';
import { Parallax } from '../world/Parallax.js';
import { Animator } from '../core/Animator.js';
import { randRange } from '../core/math.js';
import { ButtonMenu } from '../ui/ButtonMenu.js';
import { SelectScene } from './SelectScene.js';
import { GoodbyeScene } from './GoodbyeScene.js';
import { CodeScene } from './CodeScene.js';
import { loadHighScore } from './highscore.js';

const SCROLL = 70;       // velocidade da floresta ao fundo (px/s)
const ROAD_SPEED = 180;  // velocidade da estrada (a caminhonete está "correndo")
const TRUCK_X = 66;      // centro da caminhonete na tela

export class TitleScene {
  /** skipIntro: ao voltar de outras telas, já mostra o menu. */
  constructor(game, { skipIntro = false } = {}) {
    this.game = game;
    this.t = skipIntro ? 2 : 0;
    this.state = skipIntro ? 'menu' : 'press';
    this.parallax = new Parallax(game.assets, 'cenarios/fase1/');
    this.highScore = loadHighScore();
    this.menu = this._mainMenu();
    this.dialog = null;
    this.pending = null; // { at, action } — ação adiada (deixa o botão piscar antes de sair)
    this.truck = new Animator(game.assets, '');
    this.truck.play('veiculos/caminhonete');
    this.dust = [];      // poeira levantada pela caminhonete
    this.dustTimer = 0;
  }

  enter() { this.game.audio.playMusic('audio/musica/titulo'); }

  _mainMenu() {
    return new ButtonMenu(this.game, [
      { label: 'INICIAR JOGO', action: 'start' },
      { label: 'CÓDIGOS', action: 'codes' },
      { label: 'SAIR', action: 'exit' },
    ], { x: VIEW_W / 2, y: 124, spacing: 22 });
  }

  update(dt) {
    this.t += dt;
    this._updateTruck(dt);
    const { input, audio } = this.game;
    if (this.pending && this.t >= this.pending.at) {
      this.pending.action();
      this.pending = null;
    }

    if (this.state === 'press') {
      if (this.t > 0.9 && (input.confirm() || input.pointer?.clicked)) {
        audio.unlock();
        audio.play('audio/sfx/ui_ficha', { pitchVar: 0 });
        this.state = 'menu';
        this.menu = this._mainMenu();
      }
      return;
    }

    if (this.state === 'menu') {
      const chosen = this.menu.update(dt);
      if (chosen?.action === 'start') {
        this.state = 'leaving';
        this.pending = { at: this.t + 0.45, action: () => this.game.transitionTo(() => new SelectScene(this.game), { duration: 0.4 }) };
      } else if (chosen?.action === 'codes') {
        this.state = 'leaving';
        this.pending = { at: this.t + 0.45, action: () => this.game.transitionTo(() => new CodeScene(this.game), { duration: 0.4 }) };
      } else if (chosen?.action === 'exit') {
        this.state = 'confirmExit';
        this.dialog = new ButtonMenu(this.game, [
          { label: 'NÃO', action: 'no' },
          { label: 'SIM', action: 'yes' },
        ], { x: VIEW_W / 2, y: 122, spacing: 24 });
      } else if (input.cancel()) {
        audio.play('audio/sfx/ui_voltar');
        this.state = 'press';
      }
      return;
    }

    if (this.state === 'confirmExit') {
      const chosen = this.dialog.update(dt);
      if (chosen?.action === 'yes') {
        this.state = 'leaving';
        audio.stopMusic(0.6);
        this.pending = { at: this.t + 0.4, action: () => this.game.transitionTo(() => new GoodbyeScene(this.game), { duration: 0.6 }) };
      } else if (chosen?.action === 'no' || (!chosen && input.cancel())) {
        if (!chosen) audio.play('audio/sfx/ui_voltar');
        this.state = 'menu';
        this.dialog = null;
        this.menu.unlock();
      }
    }
  }

  /** Rodas girando, carro balançando e poeira saindo de trás. */
  _updateTruck(dt) {
    this.truck.update(dt * 2.5);
    this.dustTimer -= dt;
    if (this.dustTimer <= 0) {
      this.dustTimer = 0.05;
      this.dust.push({ x: this._truckX() - 34, y: VIEW_H - 8, vx: -ROAD_SPEED * 0.5 - randRange(0, 50), vy: -randRange(5, 30), t: 0, life: randRange(0.4, 0.8) });
    }
    for (const d of this.dust) { d.t += dt; d.x += d.vx * dt; d.y += d.vy * dt; }
    this.dust = this.dust.filter((d) => d.t < d.life);
  }

  /** A caminhonete avança e recua um pouco na tela, como se acelerasse e aliviasse. */
  _truckX() { return TRUCK_X + Math.round(Math.sin(this.game.time * 0.9) * 10); }

  draw(r) {
    const { assets, font, time } = this.game;
    // Floresta passando ao fundo (a "câmera" anda sozinha) e estrada de terra embaixo.
    const camX = time * SCROLL;
    this.parallax.drawBack(r, camX, 12);
    const road = assets.sprite('veiculos/estrada');
    if (road) {
      const off = Math.floor(time * ROAD_SPEED) % road.frameW;
      r.image(road, -off, VIEW_H - 24);
      r.image(road, road.frameW - off, VIEW_H - 24);
    }
    const puff = assets.sprite('efeitos/fumaca_pequena');
    for (const d of this.dust) {
      const k = d.t / d.life;
      r.frame(puff, Math.floor(k * 6), d.x - 8, d.y - 8, { alpha: 1 - k });
    }
    this.truck.draw(r, this._truckX(), VIEW_H - 6);
    this.parallax.drawFront(r, camX, 12);
    r.image(assets.sprite('ui/vinheta'), 0, 0);

    // Logo: cai quicando e depois flutua.
    const logo = assets.sprite('ui/logo');
    if (logo) {
      const p = clamp(this.t / 1.1, 0, 1);
      const drop = (1 - easeOutBounce(p)) * -150;
      const bob = p >= 1 ? Math.round(Math.sin(time * 2) * 2) : 0;
      r.image(logo, Math.round((VIEW_W - logo.frameW) / 2), 10 + drop + bob);
    }

    if (this.state === 'press') {
      if (this.t > 1.1 && Math.floor(time * 2.5) % 2 === 0) {
        font.draw(r, 'PRESSIONE START', VIEW_W / 2, 150, { align: 'center', color: 'amarela', scale: 1 });
      }
      font.draw(r, 'ENTER  /  START  /  TOQUE', VIEW_W / 2, 166, { align: 'center', color: 'cinza' });
    } else {
      this.menu.draw(r);
    }

    font.draw(r, `RECORDE ${String(this.highScore).padStart(6, '0')}`, VIEW_W / 2, VIEW_H - 24, { align: 'center', color: 'ciano' });
    font.draw(r, "© 2026  KANKA'S GANG", VIEW_W / 2, VIEW_H - 12, { align: 'center', color: 'cinza' });

    if (this.state === 'confirmExit' || (this.state === 'leaving' && this.dialog)) {
      r.fade(0.55);
      r.nineSlice(assets.sprite('ui/painel'), VIEW_W / 2 - 90, 92, 180, 84);
      font.draw(r, 'SAIR DO JOGO?', VIEW_W / 2, 104, { align: 'center', color: 'amarela' });
      this.dialog.draw(r);
    }
  }
}
