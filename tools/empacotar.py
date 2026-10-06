#!/usr/bin/env python3
"""Gera index.html: o jogo inteiro (código + assets) num único arquivo HTML.

Abre com duplo clique, sem servidor. Uso (dentro da pasta jogo/):
    python3 tools/empacotar.py

Rode de novo sempre que mudar código ou assets; a versão anterior vai para backup/.
Só usa a biblioteca padrão do Python.

Como funciona: o navegador bloqueia módulos e fetch em file://, mas aceita data: URLs.
- Cada módulo de src/ vira uma data: URL; um <script type="importmap"> liga o caminho
  'src/...' a ela (os imports relativos são reescritos para esse caminho).
- Cada arquivo de assets/ vira uma data: URL em window.ARQUIVOS, que core/Assets.js usa
  no lugar do caminho normal.
"""

import base64
import json
import mimetypes
import posixpath
import re
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / 'index.html'
BACKUP = RAIZ / 'backup'
MODELO = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<meta name="theme-color" content="#000000">
<title>Kanka's Gang</title>
<style>
/* Posiciona e escala o canvas. A arte do jogo vem toda de assets/; o HTML/CSS só faz os controles de toque. */
html, body {
  margin: 0;
  height: 100%;
  background: #000;
  overflow: hidden;
}
#jogo {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  touch-action: none;
  user-select: none;
  -webkit-user-select: none;
  -webkit-touch-callout: none;
}
/* Celular em pé: gira o jogo 90° para ele ficar sempre deitado.
   Mesma consulta de MOBILE_QUERY/isRotated em src/config/constants.js. */
@media (hover: none) and (pointer: coarse) and (orientation: portrait) {
  #jogo {
    inset: auto;
    top: 0;
    left: 100dvw;
    width: 100dvh;
    height: 100dvw;
    transform: rotate(90deg);
    transform-origin: top left;
  }
}
canvas {
  display: block;
  image-rendering: pixelated;
  image-rendering: crisp-edges;
  outline: none;
  touch-action: none;
}

/* Controles de toque (src/ui/TouchControls.js): só existem em celular/tablet. */
#controles {
  position: absolute;
  inset: 0;
  pointer-events: none;
  font: bold 16px monospace;
  color: #fff;
}
#controles > div {
  position: absolute;
  pointer-events: auto;
  touch-action: none;
}
.botao, .seta {
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  background: rgba(20, 20, 28, 0.5);
  border: 2px solid rgba(248, 120, 8, 0.85);
  color: rgba(255, 255, 255, 0.9);
}
.botao.ativo, .seta.ativo {
  background: rgba(248, 120, 8, 0.6);
}
#dpad {
  left: 20px;
  bottom: 20px;
  width: 138px;
  height: 138px;
}
.seta {
  position: absolute;
  width: 46px;
  height: 46px;
  border-radius: 8px;
}
.seta-up { left: 46px; top: 0; }
.seta-down { left: 46px; bottom: 0; }
.seta-left { left: 0; top: 46px; }
.seta-right { right: 0; top: 46px; }
.botao {
  border-radius: 50%;
  width: 70px;
  height: 70px;
  font-size: 22px;
}
#botao-a { right: 20px; bottom: 64px; }
#botao-b { right: 100px; bottom: 20px; }
#botao-start {
  left: 50%;
  bottom: 10px;
  width: 84px;
  height: 30px;
  margin-left: -42px;
  border-radius: 15px;
  font-size: 13px;
}
</style>
</head>
<body>
<!-- Toda a arte vem de assets/ (ver assets/manifest.json). O HTML só hospeda o canvas. -->
<div id="jogo"><canvas id="tela" width="384" height="216" aria-label="Kanka's Gang"></canvas></div>
<noscript>Ative o JavaScript para jogar.</noscript>
<!--SCRIPTS-->
</body>
</html>
'''

IMPORT = re.compile(r"""(\bfrom\s*|\bimport\s*)(['"])(\.{1,2}/[^'"]+)\2""")


def data_url(dados, mime):
    return f'data:{mime};base64,{base64.b64encode(dados).decode()}'


def modulo(arq):
    """Reescreve imports relativos ('../core/x.js') para o caminho a partir da raiz ('src/core/x.js')."""
    rel = arq.relative_to(RAIZ).as_posix()
    pasta = posixpath.dirname(rel)
    codigo = IMPORT.sub(lambda m: f"{m[1]}'{posixpath.normpath(posixpath.join(pasta, m[3]))}'",
                        arq.read_text(encoding='utf-8'))
    return rel, data_url(codigo.encode('utf-8'), 'text/javascript')


def main():
    imports = dict(modulo(a) for a in sorted((RAIZ / 'src').rglob('*.js')))
    arquivos = {
        a.relative_to(RAIZ / 'assets').as_posix():
            data_url(a.read_bytes(), mimetypes.guess_type(a.name)[0] or 'application/octet-stream')
        for a in sorted((RAIZ / 'assets').rglob('*')) if a.is_file()
    }
    html = MODELO.replace(
        '<!--SCRIPTS-->',
        f'<script>window.ARQUIVOS = {json.dumps(arquivos)};</script>\n'
        f'<script type="importmap">{json.dumps({"imports": imports})}</script>\n'
        '<script type="module">import \'src/main.js\';</script>')
    # A versão anterior vai para backup/, com a data em que foi gerada no nome.
    if SAIDA.exists() and SAIDA.read_text(encoding='utf-8') != html:
        BACKUP.mkdir(exist_ok=True)
        data = datetime.fromtimestamp(SAIDA.stat().st_mtime).strftime('%Y-%m-%d_%H-%M-%S')
        SAIDA.replace(BACKUP / f'{SAIDA.stem}_{data}.html')
        print(f'versão anterior salva em backup/{SAIDA.stem}_{data}.html')
    SAIDA.write_text(html, encoding='utf-8')
    print(f'{SAIDA.name}: {len(imports)} módulos, {len(arquivos)} assets, {SAIDA.stat().st_size / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
