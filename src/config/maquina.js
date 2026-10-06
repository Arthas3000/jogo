// Máquina customizada: escavadeira florestal escondida numa caixa de madeira gigante (letra X no mapa).
// Ao quebrar a caixa, a ponta da lança vem com uma ferramenta sorteada (garra Gripen ou cabeçote harvester).
// Embarcou, vira uma máquina quase indestrutível por `duration` segundos (como a estrela do Mario).
// Caixas (hitboxes, posições) seguem a convenção de characters.js: relativas aos pés, olhando para a direita.

export const MAQUINA = {
  duration: 20,          // segundos pilotando
  warnTime: 4,           // pisca nos últimos segundos
  exitInvulnerable: 1.5, // invencível logo depois de sair da máquina

  crate: { size: 64, hp: 12, score: 200 },

  // Corpo menor que 48 px de altura: passa onde o jogador passa (3 linhas livres sob blocos).
  body: { w: 48, h: 46 },
  // Pesada: anda devagar, pula só o suficiente para subir degraus de 3 tiles.
  move: {
    maxSpeed: 105, accel: 600, decel: 900, turnAccel: 1200, airAccel: 500, airDecel: 250,
    jumpHeight: 56, timeToApex: 0.4, fallMultiplier: 1.5, jumpCut: 0.5, maxFall: 420,
    coyoteTime: 0.08, jumpBuffer: 0.12,
  },
  landShake: 2.5,

  // Atropelar: qualquer inimigo que encostar na máquina é derrotado.
  contact: { damage: 99, knockback: 300 },

  // Ferramentas da ponta da lança (a máquina é a mesma; muda o que o botão de ataque faz).
  tools: {
    // Garra florestal Gripen: agarra toco / pilha de troncos / árvore e arremessa.
    garra: {
      name: 'GARRA',
      sprites: 'maquina/garra/',
      attacks: {
        // Bate em quem estiver na frente e agarra no quadro grabFrame.
        garra: {
          anim: 'garra', moveFactor: 0.25, damage: 8, hitInterval: 99, knockback: 280, hitstop: 0.07,
          sound: 'maquina_garra', hitSound: 'chave_impacto', cooldown: 0.05, grabFrame: 2,
          active: {
            2: { x: 24, y: -30, w: 32, h: 30 },
            3: { x: 24, y: -26, w: 30, h: 26 },
          },
        },
        // Arremesso do que estiver segurando (solta no quadro releaseFrame).
        arremesso: { anim: 'arremesso', moveFactor: 0.25, cooldown: 0.15, releaseFrame: 2 },
      },
      // Ponta do braço (onde a garra pendura) em cada quadro. Gerado por: cd tools && python -m arte.maquina
      tips: {
        parado: [[34, -38]],
        andando: [[34, -38]],
        garra: [[32, -59], [39, -43], [42, -22], [40, -19], [38, -31], [34, -38]],
        carregando: [[26, -67]],
        carregando_andando: [[26, -67]],
        arremesso: [[19, -78], [31, -68], [50, -44], [43, -34], [34, -38]],
      },
    },
    // Cabeçote harvester: serra quem estiver na frente; corta árvores e pilhas de troncos em toras
    // que saem voando para a frente e tritura tocos.
    cabecote: {
      name: 'CABEÇOTE',
      sprites: 'maquina/cabecote/',
      attacks: {
        corte: {
          anim: 'corte', moveFactor: 0.2, damage: 2, hitInterval: 0.08, knockback: 70, hitstop: 0.02,
          sound: 'sabre_ataque', soundRate: 0.6, hitSound: 'sabre_acerto', hitEffect: 'chips', cooldown: 0.05,
          cutFrame: 2,
          active: {
            2: { x: 24, y: -28, w: 36, h: 28 },
            3: { x: 24, y: -28, w: 36, h: 28 },
            4: { x: 24, y: -28, w: 36, h: 28 },
          },
        },
      },
      // Toras que saem de uma árvore cortada (pilha de troncos: logs - 1).
      cut: { logs: 3, speed: 250, angle: 18, angleStep: 14 },
    },
  },
  // Rosto do operador na janela da cabine: recorte do retrato do HUD (20x20) do personagem escolhido.
  // `at` = canto superior esquerdo relativo aos pés (olhando para a direita); `src` = recorte no retrato.
  operator: { at: { x: 7, y: -44 }, src: { x: 4, y: 3, w: 12, h: 14 } },
  holdDrop: 15, // o objeto fica entre as pinças da garra, um pouco abaixo da ponta do braço

  throw: { speed: 300, angle: 25, inheritVelocity: 0.5 },
  // O que voa. `hit` = caixa de dano em voo; árvores voam de ponta (seguem a trajetória).
  throwables: {
    toco: { sprite: 'maquina/toco', damage: 10, spin: 9, hit: { w: 16, h: 20 } },
    toras: { sprite: 'maquina/toras', damage: 12, spin: 7, hit: { w: 28, h: 22 } },
    tora: { sprite: 'maquina/tora', damage: 8, spin: 12, hit: { w: 22, h: 10 } },
    arvore: { sprite: 'arvore', damage: 20, spin: 0, hit: { w: 90, h: 28 } }, // sprite da pasta da fase
  },
};
