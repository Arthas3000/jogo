// Máquina customizada: a caixa de madeira gigante, a escavadeira florestal que sai dela e o
// "modo piloto" do jogador. A ferramenta da ponta da lança é sorteada ao quebrar a caixa:
//   garra     (Gripen) agarra toco / pilha de troncos / árvore e arremessa;
//   cabecote  (harvester) serra inimigos, corta árvores e troncos em toras que saem voando, tritura tocos.
//
//   Crate            caixa 4x4 tiles, sólida; recebe golpes/ferramentas como um inimigo e, quebrada,
//                    solta a escavadeira.
//   ParkedExcavator  escavadeira parada. Encostou nela → embarca. Depois que o tempo acaba, a
//                    máquina desligada fica piscando um pouco e some.
//   Maquina          estado do jogador enquanto pilota (player.maquina): invencível, atropela inimigos
//                    e usa a ferramenta sorteada.
//   ThrownObject     toco / toras / tora / árvore voando: atravessa inimigos e se despedaça no chão.
//
// O Player continua sendo o mesmo objeto (câmera, HUD, inimigos e itens não mudam nada): ao embarcar,
// só trocam o corpo, a física (config/maquina.js), as animações e o que o botão de ataque faz.

import { Animator } from '../core/Animator.js';
import { TILE } from '../config/constants.js';
import { MAQUINA } from '../config/maquina.js';
import { SOLID, TILE_INDEX } from '../world/Level.js';
import { PROJECTILE_GRAVITY } from './ToolProjectile.js';
import { Particle, ScorePopup, spawnDebris, spawnSmoke } from './Effects.js';
import { randRange } from '../core/math.js';

const GRABS = [
  { kind: 'toco', tiles: [TILE_INDEX.STUMP_TOP, TILE_INDEX.STUMP] },
  { kind: 'toras', tiles: [TILE_INDEX.LOGS] },
];

/** Lascas de madeira voando. */
function splinters(scene, x, y, count, power = 1) {
  for (let i = 0; i < count; i++) {
    scene.addEffect(new Particle(scene, 'efeitos/serragem', x + randRange(-8, 8), y + randRange(-8, 8), {
      vx: randRange(-150, 150) * power, vy: randRange(-260, -60) * power, gravity: 700, life: randRange(0.4, 0.8),
    }));
  }
}

/** Folhas caindo devagar (árvore arrancada/cortada). */
function leaves(scene, x, y, count) {
  spawnDebris(scene, 'efeitos/folha', x, y, count, { speed: 0.5, up: 0.4, gravity: 120, life: 1.6 });
}

/** Árvore (decoração) cuja base do tronco encosta na caixa. */
function treeAt(scene, box) {
  return scene.decorations.find((d) => d.name === 'arvore' && scene.overlaps(box, { x: d.x - 10, y: d.y - 40, w: 20, h: 40 }));
}

/** Troca o tamanho do corpo mantendo os pés no mesmo lugar. */
function resize(body, { w, h }) {
  const cx = body.centerX, bottom = body.bottom;
  body.w = w;
  body.h = h;
  body.x = cx - w / 2;
  body.y = bottom - h;
}

// ───────────────────────────── Caixa gigante ─────────────────────────────

export class Crate {
  /** (col, row) = célula do canto inferior esquerdo (onde está o X no mapa). */
  constructor(scene, col, row) {
    this.scene = scene;
    const n = MAQUINA.crate.size / TILE;
    this.cells = [];
    for (let dy = 0; dy < n; dy++) for (let dx = 0; dx < n; dx++) this.cells.push([col + dx, row - dy]);
    for (const [cx, cy] of this.cells) scene.level.setCell(cx, cy, SOLID);
    this.w = this.h = MAQUINA.crate.size;
    this.x = col * TILE;
    this.y = (row + 1) * TILE - this.h;
    this.hp = MAQUINA.crate.hp;
    this.sprite = scene.game.assets.sprite('maquina/caixa');
    this.shakeTimer = 0;
    this.active = true;   // alvo válido para golpes e projéteis (como um inimigo)
    this.dying = false;
    this.removed = false;
  }

  get box() { return { x: this.x, y: this.y, w: this.w, h: this.h }; }
  get centerX() { return this.x + this.w / 2; }
  get centerY() { return this.y + this.h / 2; }

  takeHit(damage, fromX) {
    if (this.removed) return false;
    this.hp -= damage;
    this.shakeTimer = 0.15;
    this.scene.audio.play('audio/sfx/caixa_acerto', { minGap: 0.05 });
    splinters(this.scene, fromX < this.centerX ? this.x : this.x + this.w, this.centerY, 2, 0.6);
    if (this.hp <= 0) this._break();
    return true;
  }

  _break() {
    const s = this.scene;
    this.removed = true;
    for (const [cx, cy] of this.cells) s.level.setCell(cx, cy, 0);
    s.audio.play('audio/sfx/caixa_quebra');
    s.shake(4, 0.3);
    s.hitstop(0.08);
    splinters(s, this.centerX, this.centerY, 18, 1.3);
    s.spawnEffect('efeitos/fumaca', this.centerX - 16, this.y + this.h);
    s.spawnEffect('efeitos/fumaca', this.centerX + 16, this.y + this.h);
    s.addScore(MAQUINA.crate.score, this.centerX, this.y - 6);
    const tool = Math.random() < 0.5 ? 'garra' : 'cabecote'; // sorteio da ferramenta
    s.items.push(new ParkedExcavator(s, this.centerX, this.y + this.h, { tool }));
  }

  update(dt) { this.shakeTimer = Math.max(0, this.shakeTimer - dt); }

  draw(r) {
    const frame = this.hp > MAQUINA.crate.hp * 2 / 3 ? 0 : this.hp > MAQUINA.crate.hp / 3 ? 1 : 2;
    const dx = this.shakeTimer > 0 ? Math.round(Math.sin(this.shakeTimer * 90) * 2) : 0;
    r.frame(this.sprite, frame, this.x + dx, this.y);
  }
}

// ───────────────────────────── Escavadeira parada ─────────────────────────────

export class ParkedExcavator {
  /** `off`: já foi usada (desligada) — pisca e some, não dá para embarcar de novo. */
  constructor(scene, x, groundY, { tool, off = false, facing = 1 } = {}) {
    this.scene = scene;
    this.tool = tool;
    this.anim = new Animator(scene.game.assets, MAQUINA.tools[tool].sprites);
    this.anim.play('desligada');
    this.x = x;
    this.groundY = groundY;
    this.y = groundY;
    this.vy = off ? 0 : -170; // pula para fora da caixa
    this.off = off;
    this.facing = facing;
    this.t = 0;
    this.removed = false;
  }

  get box() { return { x: this.x - MAQUINA.body.w / 2, y: this.y - MAQUINA.body.h, w: MAQUINA.body.w, h: MAQUINA.body.h }; }

  update(dt) {
    this.t += dt;
    this.vy += PROJECTILE_GRAVITY * dt;
    this.y = Math.min(this.groundY, this.y + this.vy * dt);
    if (this.off) {
      if (this.t > 1.5) {
        this.removed = true;
        this.scene.spawnEffect('efeitos/fumaca', this.x, this.groundY);
      }
      return;
    }
    const p = this.scene.player;
    const ready = p.alive && !p.maquina && (p.state === 'normal' || p.state === 'attack');
    if (this.t > 0.5 && this.y >= this.groundY && ready && this.scene.overlaps(this.box, p.box)) {
      this.removed = true;
      Maquina.board(p, this);
    }
  }

  draw(r) {
    if (this.off && Math.floor(this.t * 12) % 2 === 0) return;
    this.anim.draw(r, this.x, Math.round(this.y), { flipX: this.facing < 0 });
    if (!this.off && this.t > 0.5) {
      // "!" balançando sobre a cabine: "suba aqui".
      const s = this.scene.game.assets.sprite('efeitos/alerta');
      if (s) r.frame(s, Math.floor(this.t * 8), this.x - 8, this.y - 72 + Math.round(Math.sin(this.t * 6) * 2));
    }
  }
}

// ───────────────────────────── Pilotando ─────────────────────────────

export class Maquina {
  static board(player, parked) {
    const s = player.scene;
    const m = new Maquina(player, parked.tool);
    player._endAttack();
    player.maquina = m;
    m.ownAnim = player.anim;
    player.anim = m.anim;
    resize(player, MAQUINA.body);
    player.x = parked.x - player.w / 2; // senta na máquina, onde ela está
    player.y = parked.y - player.h;
    player.vx = 0;
    player.facing = parked.facing;
    player.invulnerable = 0;
    player.state = 'normal';
    s.audio.play('audio/sfx/maquina_ligar', { pitchVar: 0 });
    s.shake(3, 0.3);
    s.addEffect(new ScorePopup(s, `MÁQUINA: ${m.tool.name}!`, player.centerX, player.top - 10, 'ciano'));
  }

  constructor(player, toolId) {
    this.player = player;
    this.toolId = toolId;
    this.tool = MAQUINA.tools[toolId];
    this.time = MAQUINA.duration;
    this.held = null; // garra: 'toco' | 'toras' | 'arvore'
    this.smokeTimer = 0;
    this.anim = new Animator(player.scene.game.assets, this.tool.sprites);
    this.anim.play('parado');
  }

  get scene() { return this.player.scene; }

  update(dt) {
    const p = this.player, s = this.scene;
    this.time -= dt;
    // Atropela quem estiver no caminho.
    for (const e of s.enemies) {
      if (!e.active || e.dying || e.removed || !s.overlaps(p.box, e.box)) continue;
      e.takeHit(MAQUINA.contact.damage, p.centerX, MAQUINA.contact.knockback);
      s.hitstop(0.05);
      s.shake(2, 0.12);
      s.audio.play('audio/sfx/chave_impacto', { minGap: 0.05 });
      s.spawnEffect('efeitos/faisca_acerto', e.centerX, e.centerY + 16);
    }
    // Fumaça do escapamento (mais forte andando).
    this.smokeTimer -= dt;
    if (this.smokeTimer <= 0) {
      this.smokeTimer = Math.abs(p.vx) > 20 ? 0.18 : 0.4;
      spawnSmoke(s, p.centerX - p.facing * 18, p.bottom - 52, 1, 2);
    }
    if (this.time <= 0) this.leave();
  }

  /** Golpe/oil can/encostão de inimigo: a máquina aguenta tudo (só faísca). */
  absorb() {
    const p = this.player;
    this.scene.audio.play('audio/sfx/ferramenta_quica', { minGap: 0.25 });
    this.scene.spawnEffect('efeitos/faisca_metal', p.centerX + randRange(-12, 12), p.centerY);
    return true;
  }

  tryAttack() {
    const p = this.player;
    if (p.state !== 'normal' || p.attackCooldown > 0) return;
    if (this.toolId === 'cabecote') p.startAttack('corte');
    else p.startAttack(this.held ? 'arremesso' : 'garra');
  }

  onAttackFrame() {
    const p = this.player, { key, def } = p.attack;
    if (key === 'garra' && !this.held && p.anim.entered(def.grabFrame)) this._grab(p.worldBox(def.active[def.grabFrame]));
    if (key === 'arremesso' && this.held && p.anim.entered(def.releaseFrame)) this._throw();
    if (key === 'corte') {
      if (p.anim.entered(def.cutFrame)) this._cut(p.worldBox(def.active[def.cutFrame]));
      if (def.active[p.anim.frame]) spawnDebris(this.scene, 'efeitos/serragem', p.centerX + p.facing * 44, p.bottom - 4, 1, { speed: 0.5 });
    }
  }

  /** Cabeçote: tritura toco; corta pilha de troncos e árvores em toras que voam para a frente. */
  _cut(box) {
    const s = this.scene, x = box.x + box.w / 2, y = box.y + box.h;
    if (s.level.removeTiles(box, GRABS[0].tiles)) {
      spawnDebris(s, 'efeitos/serragem', x, y - 10, 18, { speed: 1.1 });
      s.audio.play('audio/sfx/sabre_acerto', { rate: 0.7 });
      s.shake(2, 0.15);
      return;
    }
    if (s.level.removeTiles(box, GRABS[1].tiles)) return this._ejectLogs(x, y - 18, this.tool.cut.logs - 1);
    const tree = treeAt(s, box);
    if (tree) {
      s.decorations.splice(s.decorations.indexOf(tree), 1);
      leaves(s, tree.x, tree.y - 120, 14);
      this._ejectLogs(tree.x, y - 20, this.tool.cut.logs);
    }
  }

  _ejectLogs(x, y, count) {
    const s = this.scene, p = this.player, c = this.tool.cut;
    for (let i = 0; i < count; i++) {
      const rad = ((c.angle + i * c.angleStep) * Math.PI) / 180;
      const speed = c.speed * (0.85 + i * 0.15);
      s.addPlayerProjectile(new ThrownObject(s, 'tora', x, y - i * 6, Math.cos(rad) * speed * p.facing, -Math.sin(rad) * speed, p.facing));
    }
    spawnDebris(s, 'efeitos/serragem', x, y, 12, { speed: 1 });
    s.audio.play('audio/sfx/maquina_pegar');
    s.audio.play('audio/sfx/arremesso', { rate: 0.8 });
    s.shake(2.5, 0.2);
  }

  _grab(box) {
    const s = this.scene;
    let kind = null;
    for (const g of GRABS) {
      if (s.level.removeTiles(box, g.tiles)) { kind = g.kind; break; }
    }
    if (!kind) {
      // Árvore: agarra pela base do tronco e arranca.
      const tree = treeAt(s, box);
      if (tree) {
        s.decorations.splice(s.decorations.indexOf(tree), 1);
        leaves(s, tree.x, tree.y - 120, 10);
        kind = 'arvore';
      }
    }
    if (!kind) return;
    this.held = kind;
    s.audio.play('audio/sfx/maquina_pegar');
    s.shake(2, 0.15);
    s.spawnEffect('efeitos/poeira_aterrissagem', box.x + box.w / 2, box.y + box.h);
    splinters(s, box.x + box.w / 2, box.y + box.h - 8, 6, 0.7);
  }

  /** Centro do objeto na garra (coordenadas do mundo), seguindo o quadro atual da animação. */
  _holdPoint() {
    const p = this.player;
    const tips = this.tool.tips[p.anim.name] ?? this.tool.tips.carregando;
    const [x, y] = tips[Math.min(p.anim.frame, tips.length - 1)];
    const b = p.worldBox({ x, y: y + MAQUINA.holdDrop, w: 0, h: 0 });
    return { x: b.x, y: b.y };
  }

  _throw(speedScale = 1) {
    const p = this.player, t = MAQUINA.throw;
    const at = this._holdPoint();
    const rad = (t.angle * Math.PI) / 180;
    const vx = (Math.cos(rad) * t.speed * p.facing + p.vx * t.inheritVelocity) * speedScale;
    const vy = -Math.sin(rad) * t.speed * speedScale;
    this.scene.addPlayerProjectile(new ThrownObject(this.scene, this.held, at.x, at.y, vx, vy, p.facing));
    this.scene.audio.play('audio/sfx/arremesso', { rate: 0.6 });
    this.held = null;
  }

  /** Tempo acabou (ou fim de fase): desliga a máquina e o jogador pula para fora. */
  leave() {
    const p = this.player, s = this.scene;
    if (this.held) this._throw(0.2); // solta o que estava segurando
    this.discard();
    s.items.push(new ParkedExcavator(s, p.centerX, p.bottom, { tool: this.toolId, off: true, facing: p.facing }));
    s.audio.play('audio/sfx/maquina_desligar');
    s.spawnEffect('efeitos/fumaca', p.centerX, p.bottom - 24);
    p.invulnerable = MAQUINA.exitInvulnerable;
    p.vy = -p.jumpVelocity * 0.8;
    p.onGround = false;
  }

  /** Volta o jogador ao normal sem deixar máquina para trás (usado ao morrer). */
  discard() {
    const p = this.player;
    p._endAttack();
    p.maquina = null;
    p.anim = this.ownAnim;
    resize(p, p.def.body);
    if (p.state !== 'dead') p.state = 'normal';
  }

  pickAnimation() {
    const p = this.player;
    const moving = p.onGround && Math.abs(p.vx) > 12 && p.input.axisX() !== 0;
    if (this.held) p.anim.play(moving ? 'carregando_andando' : 'carregando');
    else p.anim.play(moving ? 'andando' : 'parado');
  }

  draw(r) {
    const p = this.player;
    // Pisca nos últimos segundos, avisando que vai acabar.
    const alpha = this.time < MAQUINA.warnTime && Math.floor(this.time * 8) % 2 === 0 ? 0.4 : 1;
    if (this.held) {
      const s = this.scene.game.assets.sprite(heldSprite(this.scene, this.held));
      const at = this._holdPoint();
      const rotation = this.held === 'arvore' ? (Math.PI / 2) * p.facing : 0; // árvore deitada, copa para a frente
      if (s) r.frame(s, 0, at.x - s.frameW / 2, at.y - s.frameH / 2, { rotation, flipX: p.facing < 0, alpha });
    }
    p.drawSprite(r, { alpha });
    this._drawOperator(r, alpha);
  }

  /** O operador na cabine tem o rosto do personagem escolhido (retrato do HUD). */
  _drawOperator(r, alpha) {
    const p = this.player, o = MAQUINA.operator;
    const face = this.scene.game.assets.sprite(p.def.hudPortrait);
    if (!face) return;
    const bob = p.anim.frame % 2; // a cabine treme 1 px com o motor ligado
    const at = p.worldBox({ x: o.at.x, y: o.at.y + bob, w: o.src.w, h: o.src.h });
    r.crop(face, o.src.x, o.src.y, o.src.w, o.src.h, at.x, at.y, alpha);
  }
}

function heldSprite(scene, kind) {
  const sprite = MAQUINA.throwables[kind].sprite;
  return kind === 'arvore' ? scene.phase.folder + sprite : sprite;
}

// ───────────────────────────── Objeto arremessado ─────────────────────────────

export class ThrownObject {
  constructor(scene, kind, x, y, vx, vy, facing) {
    this.scene = scene;
    this.cfg = MAQUINA.throwables[kind];
    this.sprite = scene.game.assets.sprite(heldSprite(scene, kind));
    Object.assign(this, { x, y, vx, vy, facing });
    this.rotation = kind === 'arvore' ? (Math.PI / 2) * facing : 0;
    this.hits = new Set();
    this.removed = false;
  }

  get box() {
    const { w, h } = this.cfg.hit;
    return { x: this.x - w / 2, y: this.y - h / 2, w, h };
  }

  update(dt) {
    const s = this.scene, level = s.level;
    this.vy += PROJECTILE_GRAVITY * dt;
    this.x += this.vx * dt;
    this.y += this.vy * dt;
    // Toco e toras giram; a árvore voa de ponta, seguindo a trajetória (como uma lança).
    this.rotation = this.cfg.spin ? this.rotation + this.cfg.spin * this.facing * dt : Math.atan2(this.vy, this.vx) + Math.PI / 2;

    // Atravessa os inimigos, acertando cada um uma vez.
    for (const e of s.enemies) {
      if (!e.active || e.dying || e.removed || this.hits.has(e) || !s.overlaps(this.box, e.box)) continue;
      this.hits.add(e);
      e.takeHit(this.cfg.damage, this.x - Math.sign(this.vx) * 20, 260);
      s.hitstop(0.05);
      s.audio.play('audio/sfx/ferramenta_acerto');
      s.spawnEffect('efeitos/faisca_acerto', e.centerX, e.centerY + 16);
    }

    const { w, h } = this.cfg.hit;
    if (level.isSolidAt(this.x, this.y + h / 2) || level.isSolidAt(this.x + Math.sign(this.vx) * w / 2, this.y)) return this._shatter();
    if (this.y > level.height + 32) this.removed = true;
  }

  _shatter() {
    const s = this.scene;
    this.removed = true;
    s.audio.play('audio/sfx/maquina_impacto');
    s.shake(3, 0.2);
    splinters(s, this.x, this.y, 12, 1);
    if (this.cfg === MAQUINA.throwables.arvore) leaves(s, this.x, this.y - 10, 12);
    s.spawnEffect('efeitos/poeira_aterrissagem', this.x, this.y + this.cfg.hit.h / 2);
    s.spawnEffect('efeitos/fumaca', this.x, this.y + this.cfg.hit.h / 2);
  }

  draw(r) {
    const sp = this.sprite;
    if (sp) r.frame(sp, 0, this.x - sp.frameW / 2, this.y - sp.frameH / 2, { rotation: this.rotation, flipX: this.facing < 0 && !!this.cfg.spin });
  }
}
