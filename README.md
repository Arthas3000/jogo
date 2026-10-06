# Kanka's Gang

Plataforma 2D side-scroller em pixel art (estética 16-bit inspirada em Mega Man, menus de fliperama no estilo Metal Slug).
JavaScript puro (ES modules) + Canvas 2D — **sem dependências** e sem etapa de build.

- **Personagens:** Samurai Jeff (corpo a corpo, Sabre da Oregon), Kanka (à distância, ferramentas em parábola), Paulinho (pesado, Chave de Engenheiro).
- **Fase 1:** Floresta de Pinus — só mecânicos **LogMax** (correm atrás e batem).
- **Fase 2:** Floresta de Eucalipto — só mecânicos **Ponssee** (mantêm distância e arremessam latas de óleo).
- **Toda a arte e todo o som vêm de arquivos em `assets/`.** O código só posiciona, espelha e gira imagens. A lista completa de assets, com tamanhos e quadros, está em **[ASSETS.md](ASSETS.md)**.

## Como rodar

O jogo roda **offline**: abra o `index.html` com duplo clique. Ele tem código e assets embutidos num arquivo só (dá para mandar para outra pessoa).

Depois de mudar código ou assets, gere a nova versão:

```bash
python3 tools/empacotar.py
```

A versão anterior é guardada automaticamente em `backup/index_<data>.html` (também abre com duplo clique). A antiga versão que precisava de servidor está em `backup/versao_servidor/`.

No GitHub Pages fica em `https://<usuário>.github.io/<repositório>/jogo/`.

Parâmetros úteis na URL: `?debug` (mostra hitboxes e caixas de colisão) · `?fase=2` (começa na fase 2).

## Controles

| Ação | Teclado | Controle | Celular (botões na tela) |
|---|---|---|---|
| Andar | ← → ou A D | Direcional / analógico | Direcional ◀ ▶ |
| Pular (segure para pular mais alto) | Z, Espaço ou J | A / ✕ | A |
| Atacar | X ou K | X / □ ou B / ○ | B |
| Mirar o arremesso (Kanka) | ↑ arco alto · ↓ no ar = rasante | Direcional | Direcional ▲ ▼ |
| Descer da ponte de tronco | ↓ + pulo | ↓ + A | ▼ + A |
| Pausa | Enter ou Esc | Start | START |
| Ligar/desligar som | M | — | — |

**No celular/tablet** aparecem na tela um direcional e os botões A, B e START. O jogo fica sempre deitado: no Android ele entra em tela cheia e trava na horizontal no primeiro toque; no iPhone (que não deixa travar), se o aparelho estiver em pé o jogo é girado 90° — é só virar o celular.

Menus também funcionam com mouse/toque (passar por cima seleciona, clicar confirma).

## Códigos de fase

Ao chegar numa fase, o código dela aparece na faixa de entrada, na tela de resultado (código da próxima fase) e no "CONTINUAR?". Na tela inicial, **CÓDIGOS** → digite o código para começar direto naquela fase (o último código alcançado já vem preenchido). Fase 2: `EUC4`. Os códigos ficam em `src/config/phases.js`.

## Caminhonete e máquina customizada

- **Caminhonete da gangue:** no começo da fase ela entra a toda velocidade, freia e o jogador pula da caçamba; no fim, ele corre até ela, pula na caçamba e ela vai embora. Também aparece correndo na estrada de terra da tela inicial.
- **Máquina customizada:** na fase 1 há uma caixa de madeira gigante (`X` no mapa). Quebre-a para liberar uma escavadeira florestal; encoste nela para pilotar por 20 s (pisca quando está acabando). Ela atropela inimigos, aguenta qualquer golpe e vem com uma ferramenta sorteada na ponta da lança:
  - **Garra Gripen:** ataque agarra toco, pilha de troncos ou árvore; ataque de novo arremessa.
  - **Cabeçote harvester:** ataque serra quem estiver na frente, tritura tocos e corta árvores/troncos em toras que saem voando.
  - O operador na cabine tem o rosto do personagem escolhido.

## Estrutura

```
jogo/
├── index.html            O JOGO: gerado por tools/empacotar.py (não edite à mão)
├── backup/               versões anteriores do index.html
├── assets/
│   └── manifest.json     FONTE ÚNICA DE VERDADE dos assets (tamanho, quadros, fps, loop)
├── src/
│   ├── main.js           inicialização
│   ├── config/           todos os números de jogabilidade (edite aqui para ajustar o "feeling")
│   │   ├── constants.js  resolução, tile, regras de fliperama
│   │   ├── characters.js personagens: física, hitboxes por quadro, arremessos
│   │   ├── enemies.js    inimigos: vida, velocidade, alcance de visão, ataques
│   │   └── phases.js     ordem das fases e camadas de parallax
│   ├── core/             motor: loop de passo fixo, entrada, áudio, assets, câmera, animação, fonte
│   ├── world/            Level (mapa ASCII + autotile), Physics (colisão AABB), Parallax, levels/
│   ├── entities/         Player (+ characters/), enemies/, projéteis, itens, efeitos
│   ├── scenes/           Boot → Title → Select → Game → Continue / Ending
│   └── ui/               ButtonMenu (menus), Hud
└── tools/
    ├── empacotar.py      gera o index.html (código + assets num arquivo só)
    └── gerar_assets.py   gera placeholders/menus/sons e escreve ASSETS.md
```

### Loop principal
`core/Game.js` roda a simulação em **passo fixo de 60 Hz** (acumulador), independente da taxa do monitor — o pulo tem a mesma altura em 60 Hz ou 144 Hz. O desenho acontece uma vez por quadro do navegador. A troca de cenas usa fade.

### Física e "game feel"
- `world/Physics.js`: colisão AABB contra a grade de tiles, resolvendo X e depois Y (método clássico de plataforma). Tiles sólidos e **pontes atravessáveis por baixo** (one-way).
- `entities/Player.js`: aceleração/desaceleração separadas, curva mais forte ao virar, **coyote time**, **jump buffer**, **pulo variável** (soltar o botão corta a subida), gravidade maior na queda, "flutuar" no topo do pulo, **hitstop** e tremor de tela nos golpes.
- A altura do pulo é definida em pixels e tempo até o topo (`jumpHeight`, `timeToApex`); o código calcula gravidade e impulso exatos.

### Projéteis do Kanka (`entities/ToolProjectile.js`)
Velocidade inicial decomposta a partir de ângulo e força (`aim` em `characters.js`) + gravidade constante → trajetória parabólica real. Cada ferramenta tem peso próprio (`gravityScale`), gira no ar, herda parte da velocidade do Kanka e quica uma vez no chão perdendo energia. As latas do Ponssee fazem o inverso: resolvem a equação do movimento para **cair onde o jogador vai estar**.

### Hitboxes
Definidas por **quadro de animação** em `config/characters.js` / `config/enemies.js`, relativas aos pés do personagem olhando para a direita (o código espelha). Quando você trocar os sprites (por exemplo, o Sabre da Oregon a partir da sua imagem de referência), abra com `?debug` e ajuste os retângulos vermelhos até cobrirem a lâmina nos quadros de golpe.

## Trocando a arte e o som

1. Veja em **ASSETS.md** o nome, o tamanho e o número de quadros de cada arquivo.
2. Salve seu PNG/WAV **com o mesmo nome** por cima do placeholder.
3. Mudou a quantidade de quadros ou o FPS? Edite `assets/manifest.json` (e rode `python3 tools/gerar_assets.py --tabela` para atualizar a tabela).

O gerador **nunca sobrescreve** arquivos existentes, a menos que você peça (`--forcar`). Para recriar algo específico:
`python3 tools/gerar_assets.py --forcar audio/musica/titulo.wav`. Requer Python 3 com Pillow e numpy.

## Criando ou editando fases

As fases são texto em `src/world/levels/`. Cada fase é uma lista de **trechos** de 15 linhas colados lado a lado — dá para reordenar, duplicar ou criar trechos novos. Legenda:

| Letra | Significado | Letra | Significado |
|---|---|---|---|
| `#` | chão (grama automática no topo) | `P` | início do jogador |
| `B` | bloco de pular | `E` | inimigo da fase |
| `=` | ponte de tronco (atravessável por baixo) | `M` | marmita (recupera vida) |
| `L` | troncos empilhados | `K` | checkpoint |
| `T` | toco de árvore | `F` | fim da fase |
| `t a s r c p` | decorações: árvore, arbusto, samambaia, pedra, cogumelo, placa | `.` | vazio |
| `X` | caixa da máquina customizada (4×4 tiles; o X é o canto inferior esquerdo) | | |

Regras de medida (para todos os personagens conseguirem passar): o jogador tem 34 px de altura, então blocos sobre um caminho precisam de **3 linhas livres** embaixo; o Paulinho pula ~50 px de altura e ~55 px de distância — degraus de até 2 tiles e buracos de até 2–3 tiles.

Para adicionar uma fase 3: crie `levels/fase3.js`, a pasta `assets/cenarios/fase3/` (mesmos arquivos da fase 1), as entradas no `manifest.json` e uma linha em `config/phases.js`.
