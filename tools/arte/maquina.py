"""Sprites PROVISÓRIOS da máquina customizada: a caixa de madeira gigante, a escavadeira florestal e
as duas ferramentas da ponta da lança (sorteadas ao quebrar a caixa).

Referência da máquina (foto): lança curva e braço amarelos (ponta do braço preta), corpo e cabine
pretos, capô do motor amarelo atrás com guarda-corpo, faróis brancos, esteiras pretas.
Ferramentas:
  garra     garra florestal Gripen: cabeçote preto + pinças amarelas curvas (agarra e arremessa);
  cabecote  cabeçote harvester: chassi vermelho, tampa preta, rolos pretos com cravos, facas
            amarelas e o sabre de corte embaixo (corta árvores em toras, tritura tocos).

A máquina é montada como um braço articulado (lança + braço + ferramenta pendurada); cada quadro
é só um conjunto de ângulos (POSES). Quadro 144x80, olhando para a direita, esteiras na última
linha, centro em x = 72. Rode `python -m arte.maquina` (dentro de tools/) para ver onde fica a
ponta do braço em cada quadro — esses números vão para src/config/maquina.js (toolTips).
"""

import math
from .base import (nova, draw, contorno, tira, escurecer, misturar, BRANCO, LARANJA, CINZA, CINZA_ESCURO,
                   METAL, METAL_SOMBRA, METAL_BRILHO, MARROM, MARROM_CLARO, MARROM_ESCURO, PRETO, UNIFORME)

W, H = 144, 80
CX, CHAO = 72, 79
LANCA, BRACO = 40, 26

AMARELO_MAQ = (244, 184, 16, 255)
AMARELO_SOMBRA = (190, 132, 8, 255)
AMARELO_LUZ = (255, 222, 96, 255)
PRETO_MAQ = (30, 30, 36, 255)
PRETO_LUZ = (58, 58, 68, 255)
VIDRO = (36, 44, 58, 255)
VERMELHO_MAQ = (216, 28, 24, 255)
VERMELHO_SOMBRA = (150, 16, 16, 255)

# (ângulo da lança, ângulo do braço, abertura/serra 0..1). 0 = frente, -90 = cima.
POSES = {
    'garra': {
        'desligada': [(-45, 85, 0.6)],
        'parado': [(-55, 55, 0.5)] * 2,
        'andando': [(-55, 55, 0.5)] * 4,
        'garra': [(-75, 15, 1), (-55, 40, 1), (-28, 65, 1), (-25, 72, 0), (-42, 62, 0.2), (-55, 55, 0.5)],
        'carregando': [(-85, 0, 0)] * 2,
        'carregando_andando': [(-85, 0, 0)] * 4,
        'arremesso': [(-92, -25, 0), (-78, -5, 0), (-42, 22, 1), (-42, 48, 1), (-55, 55, 0.5)],
    },
    'cabecote': {
        'desligada': [(-45, 85, 0)],
        'parado': [(-55, 55, 0)] * 2,
        'andando': [(-55, 55, 0)] * 4,
        'corte': [(-68, 30, 0), (-45, 55, 0.3), (-25, 75, 1), (-25, 75, 1), (-25, 75, 1), (-50, 58, 0.2)],
    },
}


def _ponto(x, y, ang, comp):
    r = math.radians(ang)
    return x + math.cos(r) * comp, y + math.sin(r) * comp


def _barra(d, a, b, larg, cor):
    (x0, y0), (x1, y1) = a, b
    comp = math.hypot(x1 - x0, y1 - y0) or 1
    nx, ny = -(y1 - y0) / comp * larg / 2, (x1 - x0) / comp * larg / 2
    d.polygon([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], fill=cor)


def _linha(d, pts, larg, cor):
    for a, b in zip(pts, pts[1:]):
        _barra(d, a, b, larg, cor)


def _pivo(bob):
    return CX - 4, CHAO - 12 + bob - 16


def braco(a1, a2, bob=0):
    """Pontos do braço articulado: pivô, cotovelo da lança curva e ponta do braço."""
    piv = _pivo(bob)
    meio = _ponto(*piv, a1 - 10, LANCA * 0.55)       # lança "banana": dobra no meio
    cot = _ponto(*meio, a1 + 14, LANCA * 0.45)
    pon = _ponto(*cot, a2, BRACO)
    return piv, meio, cot, pon


def ponta(a1, a2, bob=0):
    """Ponta do braço (onde a ferramenta pendura), relativa aos pés."""
    pon = braco(a1, a2, bob)[3]
    return pon[0] - CX, pon[1] - CHAO


# ───────────────────────────── Máquina ─────────────────────────────

def _esteiras(d, i, andando):
    d.rounded_rectangle([CX - 31, CHAO - 12, CX + 31, CHAO], radius=6, fill=(22, 22, 26, 255))
    d.rounded_rectangle([CX - 27, CHAO - 9, CX + 27, CHAO - 3], radius=3, fill=PRETO_LUZ)
    d.ellipse([CX - 30, CHAO - 11, CX - 20, CHAO - 1], fill=CINZA_ESCURO)          # roda motriz
    d.ellipse([CX + 21, CHAO - 10, CX + 29, CHAO - 2], fill=CINZA_ESCURO)          # roda guia
    for k in range(5):
        x = CX - 14 + k * 7
        d.ellipse([x - 2, CHAO - 7, x + 2, CHAO - 3], fill=METAL_SOMBRA)
    fase = (i * 2) % 4 if andando else 0                                         # sapatas andando
    for x in range(CX - 28 + fase, CX + 29, 4):
        d.point((x, CHAO - 12), fill=CINZA)
        d.point((x, CHAO), fill=CINZA)
    for x, y in ((CX - 18, CHAO - 2), (CX + 4, CHAO - 1), (CX + 15, CHAO - 2)):   # barro
        d.point((x, y), fill=MARROM)


def _corpo(d, y0, ligada, i):
    # Base giratória preta + contrapeso.
    d.rectangle([CX - 34, y0 - 14, CX + 22, y0], fill=PRETO_MAQ)
    d.line([(CX - 34, y0 - 14), (CX + 22, y0 - 14)], fill=PRETO_LUZ)
    # Capô do motor amarelo (traseira) com grade e sombra.
    d.rectangle([CX - 33, y0 - 22, CX - 12, y0 - 5], fill=AMARELO_MAQ)
    d.line([(CX - 33, y0 - 22), (CX - 12, y0 - 22)], fill=AMARELO_LUZ)
    d.rectangle([CX - 33, y0 - 8, CX - 12, y0 - 5], fill=AMARELO_SOMBRA)
    for x in range(CX - 30, CX - 15, 3):
        d.line([(x, y0 - 19), (x, y0 - 11)], fill=AMARELO_SOMBRA)
    # Guarda-corpo preto sobre o motor + escapamento.
    for x in (CX - 31, CX - 23, CX - 15):
        d.line([(x, y0 - 23), (x, y0 - 31)], fill=PRETO)
    d.line([(CX - 32, y0 - 31), (CX - 13, y0 - 31)], fill=PRETO)
    d.rectangle([CX - 20, y0 - 30, CX - 18, y0 - 22], fill=METAL_SOMBRA)
    if ligada:
        r = 2 + (i % 2)
        d.ellipse([CX - 21 - r, y0 - 35 - r * 2, CX - 17 + r, y0 - 34], fill=(140, 140, 150, 255))
    # Painel da frente (pé da lança) com dois faróis e logo laranja da gangue.
    d.rectangle([CX - 11, y0 - 30, CX + 1, y0 - 4], fill=PRETO_MAQ)
    d.line([(CX - 11, y0 - 30), (CX - 11, y0 - 4)], fill=PRETO_LUZ)
    for yy in (y0 - 26, y0 - 21):
        d.ellipse([CX - 8, yy, CX - 5, yy + 3], fill=BRANCO)
    d.rectangle([CX - 9, y0 - 12, CX - 3, y0 - 11], fill=LARANJA)
    # Cabine preta, vidro escuro com reflexo, barra de faróis no teto.
    d.rectangle([CX + 2, y0 - 36, CX + 22, y0 - 4], fill=PRETO_MAQ)
    d.rectangle([CX + 5, y0 - 33, CX + 20, y0 - 15], fill=VIDRO)
    d.line([(CX + 7, y0 - 31), (CX + 12, y0 - 24)], fill=(110, 130, 150, 255))
    d.line([(CX + 9, y0 - 31), (CX + 13, y0 - 26)], fill=(80, 96, 116, 255))
    # O operador não é desenhado aqui: o jogo põe o rosto do personagem escolhido na janela
    # (MAQUINA.operator em src/config/maquina.js aponta para este vidro: x 5..20, y0-33..y0-15).
    for x in (CX + 5, CX + 10, CX + 15):
        d.rectangle([x, y0 - 38, x + 2, y0 - 37], fill=BRANCO)
    d.line([(CX + 2, y0 - 36), (CX + 22, y0 - 36)], fill=PRETO_LUZ)
    for x in range(CX + 4, CX + 22, 4):                                         # rebites
        d.point((x, y0 - 6), fill=PRETO_LUZ)


def _lanca(d, a1, a2, bob):
    piv, meio, cot, pon = braco(a1, a2, bob)
    y0 = CHAO - 12 + bob
    _barra(d, (CX - 2, y0 - 6), _ponto(*piv, a1 - 10, LANCA * 0.45), 3, CINZA)     # pistão da lança
    _linha(d, [piv, meio, cot], 8, AMARELO_MAQ)
    _linha(d, [piv, meio, cot], 2, AMARELO_SOMBRA)
    _barra(d, meio, cot, 2, AMARELO_LUZ)
    _barra(d, _ponto(*meio, a1 + 14, 4), cot, 2, PRETO)                         # pistão do braço por cima
    meio_braco = _ponto(*cot, a2, BRACO * 0.6)
    _barra(d, cot, meio_braco, 6, AMARELO_MAQ)                                  # braço amarelo...
    _barra(d, meio_braco, pon, 6, PRETO_MAQ)                                    # ...com a ponta preta
    _barra(d, _ponto(*cot, a2 + 90, 3), _ponto(*pon, a2 + 90, 3), 1, AMARELO_LUZ)  # mangueira amarela
    for p in (piv, cot):
        d.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=PRETO)
        d.point(p, fill=METAL)
    return pon


def _garra(d, gx, gy, abre):
    gx, gy = round(gx), round(gy)
    """Garra Gripen: rotor + cabeçote preto + dois pares de pinças amarelas curvas."""
    d.rectangle([gx - 2, gy, gx + 2, gy + 3], fill=METAL_SOMBRA)                # rotor
    d.polygon([(gx - 5, gy + 3), (gx + 5, gy + 3), (gx + 8, gy + 8), (gx - 8, gy + 8)], fill=PRETO_MAQ)
    d.point((gx - 1, gy + 5), fill=AMARELO_MAQ)                                 # logo
    d.point((gx + 1, gy + 5), fill=BRANCO)
    abertura = 3 + abre * 6
    for lado, cor, dx in ((-1, AMARELO_SOMBRA, 1), (1, AMARELO_SOMBRA, -1), (-1, AMARELO_MAQ, 0), (1, AMARELO_MAQ, 0)):
        x0 = gx + lado * 6 + dx
        pts = [(x0, gy + 7), (x0 + lado * abertura * 0.6, gy + 12), (x0 + lado * abertura * 0.5, gy + 17),
               (gx + lado * (abertura * 0.5 - 1) + dx, gy + 21), (gx + lado * abertura * 0.2 + dx, gy + 22)]
        _linha(d, pts, 3, cor)
    for lado in (-1, 1):
        d.point((gx + lado * 6, gy + 7), fill=METAL_BRILHO)                     # pinos


def _cabecote(d, gx, gy, serra, i):
    gx, gy = round(gx), round(gy)
    """Cabeçote harvester: arco vermelho, tampa preta, rolos com cravos, facas amarelas e sabre."""
    d.rectangle([gx - 2, gy, gx + 2, gy + 2], fill=METAL_SOMBRA)
    d.polygon([(gx - 6, gy + 2), (gx + 6, gy + 2), (gx + 8, gy + 7), (gx - 8, gy + 7)], fill=VERMELHO_MAQ)  # arco
    d.rectangle([gx - 9, gy + 7, gx + 9, gy + 11], fill=PRETO_MAQ)              # tampa preta
    d.line([(gx - 8, gy + 8), (gx + 2, gy + 8)], fill=VERMELHO_MAQ)             # faixa "always ahead"
    d.rectangle([gx - 10, gy + 11, gx + 10, gy + 16], fill=VERMELHO_MAQ)        # chassi
    d.line([(gx - 10, gy + 16), (gx + 10, gy + 16)], fill=VERMELHO_SOMBRA)
    for x in (gx - 7, gx + 6):
        d.point((x, gy + 13), fill=METAL)                                       # parafusos
    for x0 in (gx - 12, gx + 6):                                                # rolos com cravos
        d.rectangle([x0, gy + 15, x0 + 6, gy + 22], fill=(16, 16, 20, 255))
        for k in range(3):
            yy = gy + 16 + ((k * 2 + i) % 6)
            d.point((x0 + 1 + k * 2, yy), fill=CINZA)
    for lado in (-1, 1):                                                        # facas amarelas
        _linha(d, [(gx + lado * 2, gy + 16), (gx + lado * 4, gy + 20), (gx + lado * 2, gy + 24)], 2, AMARELO_MAQ)
    # Sabre de corte embaixo: recolhido = toco curto; cortando = barra comprida com corrente correndo.
    comp = 4 + serra * 16
    d.rectangle([gx - 2, gy + 23, gx + comp, gy + 25], fill=METAL)
    d.ellipse([gx + comp - 2, gy + 22, gx + comp + 2, gy + 26], fill=METAL)
    for x in range(gx - 1 + (i % 2), round(gx + comp), 2):
        d.point((x, gy + 22), fill=CINZA_ESCURO)
        d.point((x, gy + 26), fill=CINZA_ESCURO)


def maquina(ferramenta, anim, i):
    a1, a2, abre = POSES[ferramenta][anim][i]
    ligada = anim != 'desligada'
    bob = (i % 2) if ligada else 0
    img = nova(W, H)
    d = draw(img)
    _esteiras(d, i, 'andando' in anim)
    y0 = CHAO - 12 + bob
    _corpo(d, y0, ligada, i)
    gx, gy = _lanca(d, a1, a2, bob)
    if ferramenta == 'garra':
        _garra(d, gx, gy, abre)
    else:
        _cabecote(d, gx, gy, abre, i)
    return contorno(img)


# ───────────────────────────── Caixa e objetos ─────────────────────────────

def caixa(dano):
    """Caixa de madeira 64x64 com ripas, travessa em X, cantoneiras e veios. `dano` 0..2 = rachaduras."""
    img = nova(64, 64)
    d = draw(img)
    d.rectangle([0, 0, 63, 63], fill=MARROM)
    for y in range(4, 60, 8):                          # ripas com veio da madeira
        d.line([(4, y), (59, y)], fill=MARROM_ESCURO)
        d.line([(4, y + 1), (59, y + 1)], fill=MARROM_CLARO)
        for x in range(8 + (y * 7) % 11, 58, 13):
            d.line([(x, y + 3), (x + 4, y + 3)], fill=escurecer(MARROM, 0.85))
    for x0, y0, x1, y1 in ((0, 0, 63, 5), (0, 58, 63, 63), (0, 0, 5, 63), (58, 0, 63, 63)):
        d.rectangle([x0, y0, x1, y1], fill=MARROM_CLARO)
    _barra(d, (6, 6), (57, 57), 6, MARROM_CLARO)
    _barra(d, (57, 6), (6, 57), 6, MARROM_CLARO)
    _barra(d, (6, 6), (57, 57), 2, MARROM_ESCURO)
    for cx, cy in ((0, 0), (52, 0), (0, 52), (52, 52)):  # cantoneiras de metal com rebite
        d.rectangle([cx, cy, cx + 11, cy + 11], fill=METAL_SOMBRA)
        d.point((cx + 5, cy + 5), fill=METAL_BRILHO)
    d.rectangle([20, 26, 43, 37], fill=MARROM_ESCURO)    # etiqueta "KG" (Kanka's Gang)
    d.rectangle([22, 28, 41, 35], fill=LARANJA)
    d.line([(25, 29), (25, 34)], fill=UNIFORME)                                 # K
    d.line([(29, 29), (26, 31), (29, 34)], fill=UNIFORME)
    d.line([(38, 29), (34, 29), (33, 30), (33, 33), (34, 34), (38, 34), (38, 32), (36, 32)], fill=UNIFORME)  # G
    rachas = [[(10, 20), (18, 26), (14, 34)], [(44, 8), (40, 18), (48, 24)], [(30, 44), (36, 50), (28, 56)],
              [(50, 36), (56, 44)], [(8, 46), (16, 52)]]
    for linha in rachas[:dano * 3 - (1 if dano == 2 else 0)]:
        d.line(linha, fill=CINZA_ESCURO, width=2)
    if dano == 2:
        d.polygon([(44, 40), (52, 44), (46, 50)], fill=(0, 0, 0, 0))   # lasca arrancada
    return contorno(img)


def toco():
    img = nova(16, 24)
    d = draw(img)
    d.rectangle([3, 4, 12, 19], fill=MARROM)
    d.line([(5, 6), (5, 18)], fill=MARROM_ESCURO)
    d.line([(10, 8), (10, 17)], fill=MARROM_CLARO)
    d.ellipse([3, 1, 12, 6], fill=MARROM_CLARO)
    d.ellipse([6, 3, 9, 4], fill=MARROM)
    for x0, x1 in ((3, 0), (7, 6), (12, 15)):          # raízes com terra
        d.line([(x0, 19), (x1, 23)], fill=MARROM_ESCURO, width=2)
    return contorno(img)


def toras():
    """Feixe de 3 toras vistas pela ponta (como os troncos empilhados do cenário)."""
    img = nova(32, 24)
    d = draw(img)
    for cx, cy in ((9, 17), (22, 17), (15, 7)):
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=MARROM)
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=MARROM_CLARO)
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(232, 196, 140, 255))
        d.point((cx, cy), fill=MARROM)
    return contorno(img)


def tora():
    """Uma tora cortada pelo cabeçote (vista de lado, ponta clara)."""
    img = nova(24, 10)
    d = draw(img)
    d.rectangle([1, 1, 20, 8], fill=MARROM)
    d.line([(2, 3), (19, 3)], fill=MARROM_CLARO)
    d.line([(4, 6), (12, 6)], fill=MARROM_ESCURO)
    d.ellipse([17, 1, 23, 8], fill=(232, 196, 140, 255))
    d.point((20, 4), fill=MARROM)
    return contorno(img)


def gerar(caminho, nome, n):
    """caminho = partes do arquivo depois de 'maquina/' (ex.: ['garra', 'parado.png'])."""
    if nome == 'caixa':
        return tira([caixa(k) for k in range(n)])
    if nome in ('toco', 'toras', 'tora'):
        return globals()[nome]()
    ferramenta = caminho[0]
    return tira([maquina(ferramenta, nome, i) for i in range(n)])


if __name__ == '__main__':
    for ferramenta, anims in POSES.items():
        for anim, poses in anims.items():
            print(ferramenta, anim, [list(round(v) for v in ponta(a1, a2)) for a1, a2, _ in poses])
