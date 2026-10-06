// Efeitos visuais: animações de uma vez só (poeira, faíscas), partículas com física
// (lascas do sabre, orbes, destroços, folhas, fumaça), explosões e textos de pontuação flutuando.

import { Animator } from '../core/Animator.js';
import { randRange } from '../core/math.js';

/** Toca uma tira de sprites uma vez, com o centro inferior em (x, y), e some. */
export class Effect {
  constructor(scene, spriteId, x, y, { flipX = false } = {}) {
    this.anim = new Animator(scene.game.assets, '');
    this.anim.play(spriteId);
    this.x = x;
    this.y = y;
    this.flipX = flipX;
    this.removed = !this.anim.sprite;
  }
  update(dt) {
    this.anim.update(dt);
    if (this.anim.finished || (this.anim.sprite?.loop && this.anim.time > 1)) this.removed = true;
  }
  draw(r) { this.anim.draw(r, this.x, this.y, { flipX: this.flipX }); }
}

/** Partícula com velocidade, gravidade e tempo de vida (desenhada centralizada). */
export class Particle {
  constructor(scene, spriteId, x, y, { vx = 0, vy = 0, gravity = 0, life = 0.6, fadeOut = true } = {}) {
    this.anim = new Animator(scene.game.assets, '');
    this.anim.play(spriteId);
    Object.assign(this, { x, y, vx, vy, gravity, life, maxLife: life, fadeOut });
    this.removed = !this.anim.sprite;
  }
  update(dt) {
    this.vy += this.gravity * dt;
    this.x += this.vx * dt;
    this.y += this.vy * dt;
    this.life -= dt;
    this.anim.update(dt);
    if (this.life <= 0) this.removed = true;
  }
  draw(r) {
    const s = this.anim.sprite;
    const alpha = this.fadeOut ? Math.min(1, (this.life / this.maxLife) * 3) : 1;
    r.frame(s, this.anim.frame, this.x - s.frameW / 2, this.y - s.frameH / 2, { alpha });
  }
}

/** Texto que sobe e some ("+100"). Usa a fonte pixelada. */
export class ScorePopup {
  constructor(scene, text, x, y, color = 'amarela') {
    Object.assign(this, { scene, text, x, y, color, t: 0 });
    this.removed = false;
  }
  update(dt) {
    this.t += dt;
    this.y -= 28 * dt;
    if (this.t > 0.9) this.removed = true;
  }
  draw(r) {
    const alpha = this.t > 0.6 ? 1 - (this.t - 0.6) / 0.3 : 1;
    this.scene.game.font.draw(r, this.text, this.x - r.offsetX, this.y - r.offsetY, { color: this.color, align: 'center', alpha });
  }
}

/** Explosão de derrota estilo Mega Man: 8 orbes saindo em círculo + 4 mais lentos. */
export function spawnOrbBurst(scene, x, y) {
  const add = (count, speed, offset) => {
    for (let i = 0; i < count; i++) {
      const a = (i / count) * Math.PI * 2 + offset;
      scene.addEffect(new Particle(scene, 'efeitos/explosao_orbe', x, y, {
        vx: Math.cos(a) * speed, vy: Math.sin(a) * speed, life: 0.7, fadeOut: true,
      }));
    }
  };
  add(8, 110, 0);
  add(4, 55, Math.PI / 4);
}

/** Chuva de partículas (destroços, lascas, folhas...) saindo de (x, y). */
export function spawnDebris(scene, spriteId, x, y, count, { speed = 1, up = 1, gravity = 700, life = 0.8 } = {}) {
  for (let i = 0; i < count; i++) {
    scene.addEffect(new Particle(scene, spriteId, x + randRange(-6, 6), y + randRange(-6, 6), {
      vx: randRange(-140, 140) * speed, vy: -randRange(80, 260) * up, gravity, life: randRange(life * 0.6, life),
    }));
  }
}

/** Baforadas de fumaça subindo devagar. */
export function spawnSmoke(scene, x, y, count = 3, spread = 10) {
  for (let i = 0; i < count; i++) {
    scene.addEffect(new Particle(scene, 'efeitos/fumaca_pequena', x + randRange(-spread, spread), y + randRange(-spread / 2, spread / 2), {
      vx: randRange(-12, 12), vy: randRange(-40, -18), life: randRange(0.5, 0.9),
    }));
  }
}

/** Explosão estilo Metal Slug: bola de fogo, destroços voando, fumaça e tremor. */
export function spawnExplosion(scene, x, y, { big = false } = {}) {
  scene.spawnEffect('efeitos/explosao', x, y + 24);
  if (big) {
    scene.spawnEffect('efeitos/explosao', x - 14, y + 30);
    scene.spawnEffect('efeitos/explosao', x + 14, y + 18);
  }
  spawnDebris(scene, 'efeitos/destroco', x, y, big ? 10 : 6);
  spawnSmoke(scene, x, y - 6, big ? 5 : 3);
  scene.audio.play('audio/sfx/explosao', { minGap: 0.05, volume: big ? 1 : 0.8 });
  scene.shake(big ? 4 : 2.5, big ? 0.35 : 0.2);
}
