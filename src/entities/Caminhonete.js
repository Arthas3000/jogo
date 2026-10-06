// Caminhonete da gangue.
//   Começo da fase: entra pela esquerda a toda velocidade, freia levantando poeira, o jogador pula da
//   caçamba (GameScene._jumpOut) e ela vai embora.
//   Fim da fase: fica estacionada depois da placa de saída; o jogador corre até ela, pula na caçamba
//   (Player.autoBoard) e ela arranca para fora da tela.
// Não tem colisão: é cenário que anda. Desenhada com o centro inferior em (x, y).

import { Animator } from '../core/Animator.js';
import { spawnSmoke } from './Effects.js';
import { clamp } from '../core/math.js';

const TOP_SPEED = 340;  // px/s
const BRAKE = 520;      // desaceleração ao frear (px/s²)
const ACCEL = 380;      // aceleração ao sair
// Caçamba relativa ao centro inferior (olhando para a direita): de onde o jogador pula / onde ele entra.
const BED = { x0: -50, x1: -6, top: -26 };

export class Caminhonete {
  constructor(scene, x, groundY) {
    this.scene = scene;
    this.x = x;
    this.y = groundY;
    this.vx = 0;
    this.facing = 1;
    this.mode = 'parked'; // parked | arriving | leaving
    this.braking = false;
    this.dustTimer = 0;
    this.removed = false;
    this.anim = new Animator(scene.game.assets, '');
    this.anim.play('veiculos/caminhonete');
  }

  // A câmera segue a caminhonete quando o jogador está dentro dela.
  get centerX() { return this.x; }
  get bottom() { return this.y; }
  get box() { return { x: this.x - 56, y: this.y - 48, w: 112, h: 48 }; }
  get bed() { return { x0: this.x + BED.x0, x1: this.x + BED.x1, top: this.y + BED.top, cx: this.x + (BED.x0 + BED.x1) / 2 }; }
  get parked() { return this.mode === 'parked'; }

  /** Entra a toda velocidade vindo de `fromX` e freia até parar com a caçamba em `bedX`. */
  arrive(bedX, fromX) {
    this.stopX = bedX - (BED.x0 + BED.x1) / 2;
    this.x = fromX;
    this.vx = TOP_SPEED;
    this.mode = 'arriving';
    this.braking = false;
    this.scene.audio.play('audio/sfx/caminhonete_motor');
  }

  leave() {
    if (this.mode === 'leaving') return;
    this.mode = 'leaving';
    this.scene.audio.play('audio/sfx/caminhonete_motor');
  }

  update(dt) {
    const s = this.scene;
    if (this.mode === 'arriving') {
      const dist = this.stopX - this.x;
      const canStop = Math.sqrt(2 * BRAKE * Math.max(0, dist)); // velocidade que ainda dá para frear a tempo
      if (canStop < this.vx && !this.braking) {
        this.braking = true;
        s.audio.play('audio/sfx/caminhonete_freio');
      }
      this.vx = Math.min(TOP_SPEED, canStop);
      if (dist <= 0.5 || this.vx < 6) {
        this.x = this.stopX;
        this.vx = 0;
        this.mode = 'parked';
        this.braking = false;
        s.shake(1.5, 0.15);
        spawnSmoke(s, this.x - 40, this.y - 4, 3, 8);
      }
    } else if (this.mode === 'leaving') {
      this.vx = Math.min(TOP_SPEED, this.vx + ACCEL * dt);
      if (this.x > s.camera.x && !s.camera.isVisible(this.box, 40)) this.removed = true;
    }
    this.x += this.vx * dt;

    // Poeira da roda traseira (muita ao frear) e fumaça do escapamento.
    if (this.vx > 20) {
      this.dustTimer -= dt;
      if (this.dustTimer <= 0) {
        this.dustTimer = this.braking ? 0.025 : 0.06;
        s.spawnEffect('efeitos/poeira_passo', this.x - 30 + (this.braking ? 4 : 0), this.y);
        if (this.braking) s.spawnEffect('efeitos/poeira_passo', this.x + 32, this.y);
        if (Math.random() < 0.35) spawnSmoke(s, this.x - 58, this.y - 12, 1, 2);
      }
      // Rodas giram (e a suspensão balança) na velocidade do carro.
      this.anim.update(dt * clamp(this.vx / 120, 0.3, 2.5));
    }
  }

  draw(r) { this.anim.draw(r, Math.round(this.x), Math.round(this.y)); }
}
