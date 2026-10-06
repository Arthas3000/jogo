"""Sprites PROVISÓRIOS de veículos: a caminhonete da gangue e a estrada de terra da tela inicial.

Caminhonete (referência: foto da picape da empresa): cabine dupla branca, faixa preta nas portas e
na caçamba com friso vermelho, emblema redondo vermelho no capô, rodas cinza, barro na lataria.
Quadro 112x48 olhando para a direita, pneus na última linha, centro em x = 56. A caçamba fica atrás
(esquerda): é de onde o jogador pula no começo da fase e onde entra no fim (ver src/entities/Caminhonete.js).
"""

import math
import random
from .base import nova, draw, contorno, tira, escurecer, misturar, BRANCO, PRETO, CINZA, CINZA_ESCURO, METAL, \
    METAL_SOMBRA, VERMELHO, VERMELHO_ESCURO, AMARELO, MARROM, MARROM_CLARO, MARROM_ESCURO, VERDE, VERDE_ESCURO

W, H = 112, 48
CHAO = 47
BRANCO_CARRO = (236, 236, 230, 255)
BRANCO_SOMBRA = (190, 190, 186, 255)
VIDRO = (34, 38, 46, 255)
BARRO = (140, 86, 50, 255)


def _roda(d, cx, cy, quadro):
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(22, 22, 26, 255))          # pneu
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=METAL_SOMBRA)               # aro
    for k in range(5):                                                         # raios girando
        a = math.radians(k * 72 + quadro * 18)
        d.line([(cx, cy), (cx + math.cos(a) * 4, cy + math.sin(a) * 4)], fill=METAL)
    d.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=CINZA_ESCURO)
    d.point((cx - 6, cy - 5), fill=(70, 70, 76, 255))                          # brilho da borracha


def caminhonete(quadro):
    img = nova(W, H)
    d = draw(img)
    bob = quadro % 2
    y = lambda v: v + bob  # a carroceria balança 1 px na suspensão; as rodas não

    # Caixas de roda escuras + carroceria branca
    d.polygon([(4, y(22)), (52, y(22)), (54, y(12)), (58, y(8)), (78, y(8)), (88, y(19)), (104, y(22)),
               (109, y(27)), (109, y(37)), (4, y(37))], fill=BRANCO_CARRO)
    d.line([(4, y(22)), (52, y(22))], fill=BRANCO_SOMBRA)                       # borda da caçamba
    d.rectangle([3, y(21), 6, y(36)], fill=BRANCO_SOMBRA)                       # tampa traseira
    d.rectangle([3, y(23), 5, y(27)], fill=VERMELHO)                            # lanterna
    # Vidros da cabine dupla (para-brisa inclinado) e coluna B
    d.polygon([(57, y(11)), (77, y(11)), (86, y(21)), (57, y(21))], fill=VIDRO)
    d.rectangle([70, y(11), 72, y(21)], fill=BRANCO_CARRO)
    d.line([(60, y(13)), (64, y(19))], fill=(90, 100, 116, 255))                # reflexo
    d.line([(74, y(13)), (79, y(19))], fill=(90, 100, 116, 255))
    d.rectangle([85, y(17), 88, y(19)], fill=PRETO)                             # retrovisor
    # Faixa preta com friso vermelho (portas e caçamba), como na foto
    d.rectangle([6, y(27), 100, y(32)], fill=PRETO)
    d.line([(6, y(31)), (104, y(31))], fill=VERMELHO)
    d.polygon([(88, y(22)), (100, y(22)), (104, y(27)), (92, y(27))], fill=PRETO)   # capô preto lateral
    d.ellipse([92, y(20), 97, y(24)], fill=VERMELHO)                            # emblema redondo
    d.point((94, y(22)), fill=PRETO)
    # Frente: farol, grade, para-choque
    d.rectangle([104, y(24), 108, y(26)], fill=(255, 250, 200, 255))
    d.rectangle([105, y(28), 109, y(33)], fill=PRETO)
    for yy in range(28, 33, 2):
        d.line([(106, y(yy)), (108, y(yy))], fill=CINZA_ESCURO)
    d.rectangle([4, y(35), 110, y(37)], fill=(44, 44, 48, 255))                 # saia/para-choques
    # Portas e maçanetas
    for x in (56, 71):
        d.line([(x, y(22)), (x, y(34))], fill=BRANCO_SOMBRA)
        d.rectangle([x + 3, y(24), x + 6, y(24)], fill=CINZA)
    # Barro na parte de baixo
    rnd = random.Random(7)
    for _ in range(26):
        x = rnd.randint(5, 108)
        d.point((x, y(rnd.randint(33, 36))), fill=BARRO if rnd.random() < 0.7 else MARROM_ESCURO)
    # Caixas de roda e rodas
    for cx in (26, 88):
        d.ellipse([cx - 11, y(28), cx + 11, y(50)], fill=(26, 26, 30, 255))
        _roda(d, cx, CHAO - 8, quadro)
    return contorno(img)


def estrada(w=384, h=24):
    """Estrada de terra (emenda horizontal): barro avermelhado de folhas de pinus, sulcos dos pneus e capim."""
    img = nova(w, h)
    d = draw(img)
    base = (150, 84, 46, 255)
    d.rectangle([0, 3, w - 1, h - 1], fill=base)
    rnd = random.Random(11)
    for _ in range(900):                                                       # folhas/cascalho
        x, yy = rnd.randrange(w), rnd.randrange(4, h)
        c = rnd.choice([MARROM_CLARO, MARROM_ESCURO, (176, 100, 52, 255), (120, 66, 38, 255)])
        d.point((x, yy), fill=c)
    for yy in (10, 17):                                                        # sulcos dos pneus
        d.line([(0, yy), (w - 1, yy)], fill=escurecer(base, 0.7))
        d.line([(0, yy + 1), (w - 1, yy + 1)], fill=escurecer(base, 0.82))
    for x in range(0, w, 3):                                                   # capim na borda de cima
        alt = 1 + (x * 7 % 5 == 0) * 2 + (x * 13 % 7 == 0)
        d.line([(x, 3), (x, 3 - alt)], fill=VERDE if x % 2 else VERDE_ESCURO)
    return img


def gerar(nome, n):
    if nome == 'estrada':
        return estrada()
    return tira([caminhonete(i) for i in range(n)])
