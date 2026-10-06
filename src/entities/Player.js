// Jogador: movimentação de plataforma com "game feel" moderno.
//
// Técnicas usadas para o controle parecer natural e responsivo:
//  • Aceleração/desaceleração separadas (e mais fortes ao virar) — sem "patinar".
//  • Coyote time: ainda dá pra pular alguns ms depois de sair da beirada.
//  • Jump buffer: apertar pulo um pouco antes de tocar o chão ainda conta.
//  • Pulo variável: soltar o botão cedo corta a subida (pulos curtos e longos).
//  • Gravidade maior na queda + "flutuar" no topo do pulo: arco firme e legível.
//  • Hitstop (congelar alguns ms no impacto) e tremor de tela nos golpes.
//
// A parte específica de cada personagem (como ataca) fica nas subclasses em characters/.
// Pilotando o máquina customizada (this.maquina, ver Maquina.js), corpo, física, ataques e animações
// vêm de config/maquina.js.

import { Entity } from './Entity.js';
import { moveBody, standingOnBridge } from '../world/Physics.js';
import { approach } from '../core/math.js';
import { MAQUINA } from '../config/maquina.js';

let nextAttackId = 1;

export class Player extends Entity {
  constructor(scene, def, x, y) {
    super(scene, { x, y, w: def.body.w, h: def.body.h, sprites: def.sprites });
    this.def = def;
    this.hp = def.maxHp;
    this.state = 'normal'; // normal | attack | hurt | dead | victory | frozen
    this.coyote = 0;
    this.jumpBuffer = 0;
    this.invulnerable = 0;
    this.hurtTimer = 0;
    this.attackCooldown = 0;
    this.attack = null;     // { key, def, id, hits: Map(alvo → tempo), queued }
    this.landTimer = 0;
    this.dropThrough = 0;
    this.wasOnGround = true;
    this.jumping = false;
    this.maquina = null;      // Maquina enquanto pilota a escavadeira
    this.hidden = false;      // dentro da caminhonete (começo/fim da fase)
    this.anim.play('parado');
  }

  /** Parâmetros de movimento atuais (os do personagem ou os da escavadeira). */
  get move() { return this.maquina ? MAQUINA.move : this.def.move; }
  // Gravidade e impulso calculados a partir da altura e do tempo até o topo do pulo.
  get gravity() { const m = this.move; return (2 * m.jumpHeight) / (m.timeToApex * m.timeToApex); }
  get jumpVelocity() { return this.gravity * this.move.timeToApex; }

  get input() { return this.scene.game.input; }
  get alive() { return this.state !== 'dead'; }

  update(dt) {
    const m = this.move;
    const input = this.input;
    this.invulnerable = Math.max(0, this.invulnerable - dt);
    this.attackCooldown = Math.max(0, this.attackCooldown - dt);
    this.dropThrough = Math.max(0, this.dropThrough - dt);
    this.landTimer = Math.max(0, this.landTimer - dt);

    if (this.state === 'dead') return this._updateDead(dt);

    const controllable = this.state === 'normal' || this.state === 'attack';
    const dir = this.state === 'auto' ? this._autoDir() : controllable ? input.axisX() : 0;

    // ── Horizontal ──
    let target = dir * m.maxSpeed;
    if (this.state === 'attack') target *= this.attack.def.moveFactor;
    let rate;
    if (this.onGround) {
      const turning = dir !== 0 && Math.sign(this.vx) === -dir;
      rate = dir === 0 ? m.decel : turning ? m.turnAccel : m.accel;
    } else {
      rate = dir === 0 ? m.airDecel : m.airAccel;
    }
    if (this.state === 'hurt') rate = m.airDecel; // empurrão do dano desliza
    this.vx = approach(this.vx, target, rate * dt);
    if (dir !== 0 && (this.state === 'normal' || this.state === 'auto' || (this.state === 'attack' && !this.onGround))) this.facing = dir;

    // ── Pulo ──
    if (controllable && input.pressed('jump')) this.jumpBuffer = m.jumpBuffer;
    else this.jumpBuffer = Math.max(0, this.jumpBuffer - dt);

    const canJump = this.onGround || this.coyote > 0;
    if (this.jumpBuffer > 0 && canJump && (this.state === 'normal' || this.attack?.def.moveFactor > 0)) {
      if (input.down('down') && this.onGround && standingOnBridge(this, this.scene.level)) {
        this.dropThrough = 0.25; // ↓ + pulo: desce da ponte
      } else {
        this._jump();
      }
      this.jumpBuffer = 0;
    }
    // Pulo variável: soltou cedo, corta a subida.
    if (this.jumping && this.vy < 0 && !input.down('jump') && this.state !== 'auto') {
      this.vy *= m.jumpCut;
      this.jumping = false;
    }

    // ── Gravidade ──
    let g = this.gravity;
    if (this.vy > 0) g *= m.fallMultiplier;
    else if (this.jumping && Math.abs(this.vy) < 50 && input.down('jump')) g *= 0.55; // flutua no topo
    this.vy = Math.min(this.vy + g * dt, m.maxFall);

    // ── Ataque ──
    if (controllable && input.pressed('attack')) {
      if (this.maquina) this.maquina.tryAttack();
      else this._tryAttack();
    }
    if (this.state === 'attack') this._updateAttack(dt);

    // ── Movimento + colisão ──
    this.wasOnGround = this.onGround;
    moveBody(this, this.scene.level, dt);
    if (this.onGround) { this.coyote = m.coyoteTime; this.jumping = false; }
    else this.coyote = Math.max(0, this.coyote - dt);

    if (!this.wasOnGround && this.onGround) this._land();
    this.maquina?.update(dt); // pode acabar o tempo e devolver o jogador ao normal

    if (this.state === 'hurt') {
      this.hurtTimer -= dt;
      if (this.hurtTimer <= 0) this.state = 'normal';
    }

    // Caiu num buraco.
    if (this.top > this.scene.level.height + 32) this.die(true);

    this._pickAnimation();
    this.anim.update(dt);
    this._footsteps();
  }

  /** Som + poeirinha nos quadros em que o pé toca o chão (correndo, ou esteira da máquina). */
  _footsteps() {
    const a = this.anim;
    const running = ['correndo', 'andando', 'carregando_andando'].includes(a.name);
    if (!this.onGround || !running || !a.sprite) return;
    const n = a.sprite.frames;
    if (!a.entered(Math.round(n / 4)) && !a.entered(Math.round((n * 3) / 4))) return;
    if (this.maquina) {
      this.scene.audio.play('audio/sfx/esteira', { minGap: 0.08 });
      this.scene.spawnEffect('efeitos/poeira_passo', this.centerX - this.facing * 20, this.bottom);
      return;
    }
    this.scene.audio.play('audio/sfx/passo', { rate: this.def.heavy ? 0.8 : 1 });
    this.scene.spawnEffect('efeitos/poeira_passo', this.centerX - this.facing * 4, this.bottom);
  }

  /** Voz do personagem (cada um tem seu tom). */
  voice(id, opts = {}) { this.scene.audio.play('audio/sfx/' + id, { rate: this.def.voice ?? 1, ...opts }); }

  _jump() {
    this.vy = -this.jumpVelocity;
    this.jumping = true;
    this.coyote = 0;
    this.onGround = false;
    this.scene.audio.play('audio/sfx/pulo');
    this.scene.spawnEffect('efeitos/poeira_pulo', this.centerX, this.bottom);
    // Ataque no chão interrompido pelo pulo vira estado normal (responsividade > animação).
    if (this.state === 'attack' && this.attack.key !== 'air') this._endAttack();
  }

  _land() {
    this.landTimer = 0.1;
    this.scene.spawnEffect('efeitos/poeira_aterrissagem', this.centerX, this.bottom);
    this.scene.audio.play('audio/sfx/aterrissar', { volume: 0.8 });
    const landShake = this.maquina ? MAQUINA.landShake : this.def.heavy?.landShake;
    if (landShake) this.scene.shake(landShake, 0.12);
    // Ataque aéreo termina ao tocar o chão.
    if (this.state === 'attack' && this.attack.key === 'air') this._endAttack();
  }

  // ───────────────────────────── Ataques ─────────────────────────────

  _tryAttack() {
    const atk = this.attack;
    // Combo: apertou de novo dentro da janela do golpe atual → enfileira o próximo.
    if (this.state === 'attack' && atk.def.next && this.anim.frame >= atk.def.comboFrom) {
      atk.queued = true;
      return;
    }
    if (this.state !== 'normal' || this.attackCooldown > 0) return;
    this.startAttack(this.onGround ? 'ground' : 'air');
  }

  /** Inicia um ataque definido em def.attacks[key]. Subclasses podem estender. */
  startAttack(key) {
    const def = (this.maquina ? this.maquina.tool.attacks : this.def.attacks)[key];
    if (!def) return;
    this.state = 'attack';
    this.attack = { key, def, id: nextAttackId++, hits: new Map(), queued: false };
    this.anim.play(def.anim, { restart: true });
    if (def.sound) this.scene.audio.play('audio/sfx/' + def.sound, { rate: def.soundRate ?? 1 });
    // Grito de ataque de vez em quando (sempre seria cansativo).
    if (!this.maquina && Math.random() < 0.35) this.voice('voz_ataque', { minGap: 0.8 });
  }

  _updateAttack() {
    const { def } = this.attack;
    const frame = this.anim.frame;
    if (this.maquina) this.maquina.onAttackFrame(frame);
    else this.onAttackFrame(frame);

    // Caixas de dano ativas neste quadro.
    const active = def.active?.[frame];
    if (active) {
      const boxes = (Array.isArray(active) ? active : [active]).map((b) => this.worldBox(b));
      this.currentHitboxes = boxes;
      this.scene.meleeHit(this, this.attack, boxes);
    } else {
      this.currentHitboxes = null;
    }

    if (this.anim.finished) {
      if (this.attack.queued && def.next) {
        // Emenda o combo e permite virar para o outro lado entre golpes.
        const dir = this.input.axisX();
        if (dir) this.facing = dir;
        this.startAttack(def.next);
      } else {
        this._endAttack();
      }
    }
  }

  _endAttack() {
    if (this.attack) this.attackCooldown = this.attack.def.cooldown ?? 0;
    this.attack = null;
    this.currentHitboxes = null;
    if (this.state === 'attack') this.state = 'normal';
  }

  /** Gancho por quadro de ataque (o Kanka usa para soltar a ferramenta; o Paulinho, para o impacto). */
  onAttackFrame() {}

  // ───────────────────────────── Dano / morte ─────────────────────────────

  /** Recebe dano. `fromX` = de onde veio o golpe (para empurrar na direção certa). */
  hurt(damage, fromX, knockback = 140) {
    if (this.maquina) return this.maquina.absorb(); // a escavadeira aguenta tudo
    if (this.invulnerable > 0 || !this.alive || ['victory', 'frozen', 'auto'].includes(this.state)) return false;
    this.hp = Math.max(0, this.hp - damage);
    this.scene.audio.play('audio/sfx/jogador_dano');
    this.voice('voz_dano');
    this.scene.hitstop(0.06);
    this.scene.shake(2.5, 0.2);
    if (this.hp <= 0) { this.die(false); return true; }
    const resist = this.def.heavy?.knockbackResist ?? 0;
    const dir = this.centerX < fromX ? -1 : 1;
    this.vx = dir * knockback * (1 - resist);
    this.vy = -170 * (1 - resist * 0.5);
    this.onGround = false;
    this.facing = -dir;
    this._endAttack();
    this.state = 'hurt';
    this.hurtTimer = 0.32;
    this.invulnerable = 1.3;
    return true;
  }

  heal(amount) { this.hp = Math.min(this.def.maxHp, this.hp + amount); }

  die(fell) {
    if (this.state === 'dead') return;
    this.maquina?.discard();
    this._endAttack();
    this.state = 'dead';
    this.hp = 0;
    this.deathTimer = 0;
    this.fell = fell;
    this.vx = 0;
    this.vy = fell ? 0 : -220;
    this.anim.play('morte', { restart: true });
    this.scene.audio.play('audio/sfx/jogador_morte');
    this.voice('voz_morte');
    this.scene.onPlayerDeath();
  }

  _updateDead(dt) {
    this.deathTimer += dt;
    if (!this.fell) {
      this.vy = Math.min(this.vy + this.gravity * dt, 400);
      moveBody(this, this.scene.level, dt);
    }
    this.anim.update(dt);
  }

  /** Congela o jogador (intro da fase, vitória). */
  freeze(state = 'frozen') {
    this._endAttack();
    this.state = state;
    this.vx = 0;
  }
  unfreeze() { if (this.state === 'frozen') this.state = 'normal'; }

  /** Fim de fase: corre sozinho até `targetX` (caçamba da caminhonete) e pula. */
  autoBoard(targetX) {
    this.maquina?.leave();
    this._endAttack();
    this.state = 'auto';
    this.autoTarget = targetX;
    this.autoJumped = false;
  }

  _autoDir() {
    const dx = this.autoTarget - this.centerX;
    if (!this.autoJumped && this.onGround && Math.abs(dx) < 34) {
      this._jump();
      this.autoJumped = true;
    }
    return Math.abs(dx) > 3 ? Math.sign(dx) : 0;
  }

  /** Gira o personagem para a direita e comemora (fim de fase). */
  celebrate() {
    this.maquina?.leave();
    this.freeze('victory');
    this.facing = 1;
  }

  _pickAnimation() {
    if (this.state === 'attack') return; // a animação do ataque manda
    if (this.maquina) return this.maquina.pickAnimation();
    if (this.state === 'victory') {
      // Só comemora depois de pousar.
      if (this.onGround) this.anim.play('vitoria');
      else this.anim.play(this.vy < 0 ? 'pulo' : 'queda');
      if (this.onGround) this.vx = 0;
      return;
    }
    if (this.state === 'hurt') return this.anim.play('dano');
    if (!this.onGround) return this.anim.play(this.vy < 0 ? 'pulo' : 'queda');
    if (this.landTimer > 0 && Math.abs(this.vx) < 20) return this.anim.play('aterrissagem');
    if (Math.abs(this.vx) > 12 && (this.state === 'auto' || (this.state === 'normal' && this.input.axisX() !== 0))) {
      // A corrida anima mais rápido quanto mais rápido o personagem vai.
      return this.anim.play('correndo', { speed: Math.max(0.5, Math.abs(this.vx) / this.def.move.maxSpeed) });
    }
    this.anim.play('parado');
  }

  draw(r) {
    if (this.hidden) return;
    if (this.maquina) return this.maquina.draw(r);
    // Pisca durante a invencibilidade (alterna visível/invisível a cada ~60 ms).
    if (this.invulnerable > 0 && this.state !== 'dead' && Math.floor(this.invulnerable * 16) % 2 === 0) return;
    this.drawSprite(r);
  }
}
