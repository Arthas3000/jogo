"""Sprites PROVISÓRIOS de personagens e inimigos (64x64, olhando para a direita, pés na última linha).

Cada quadro é montado como um "boneco articulado": pernas, tronco, cabeça (cabelo/barba de cada
personagem), braços em um ângulo e a arma presa na mão. As poses foram pensadas para coincidir
com as hitboxes de src/config/characters.js — use-as como referência de proporção e timing
ao desenhar a arte definitiva.
"""

import math
from PIL import Image
from .base import (nova, draw, contorno, tira, escurecer, misturar, CONTORNO, PELE, PELE_SOMBRA, CABELO_PRETO, CABELO_CASTANHO,
                   CABELO_RUIVO, VERMELHO, VERMELHO_ESCURO, BRANCO, CINZA_ESCURO, CINZA, CINZA_CLARO, PRETO,
                   AZUL, AZUL_ESCURO, AZUL_CLARO, VERDE, VERDE_ESCURO, MARROM, MARROM_ESCURO, LARANJA,
                   LARANJA_ESCURO, AMARELO, AMARELO_ESCURO, METAL, METAL_SOMBRA, METAL_BRILHO,
                   UNIFORME, UNIFORME_SOMBRA, UNIFORME_CALCA)

W = H = 64
CX = 32
CHAO = 63

# ── Aparência de cada personagem ───────────────────────────────────────────
# A gangue do Kanka usa o mesmo uniforme: preto com gola e faixa no peito laranja.
UNIFORME_GANGUE = dict(camisa=UNIFORME, camisa_sombra=UNIFORME_SOMBRA, calca=UNIFORME_CALCA, gola=LARANJA,
                       faixa=LARANJA, cinto=LARANJA_ESCURO, bota=PRETO)

TIPOS = {
    'samurai_jeff': dict(UNIFORME_GANGUE, cabelo='coque', barba='cheia', cor_cabelo=CABELO_PRETO,
                         arma='sabre', descanso=60, largura=5),
    'kanka': dict(UNIFORME_GANGUE, cabelo='curto', barba='curta', cor_cabelo=CABELO_CASTANHO,
                  arma=None, descanso=None, largura=5),
    'paulinho': dict(UNIFORME_GANGUE, cabelo='topete', barba='cheia', cor_cabelo=CABELO_RUIVO,
                     arma='chave', descanso=-125, largura=6, barriga=True),
    'logmax': dict(cabelo='capacete', cor_capacete=CINZA_CLARO, barba='bigode', cor_cabelo=CABELO_PRETO,
                   camisa=LARANJA, camisa_sombra=LARANJA_ESCURO, gola=None, calca=LARANJA_ESCURO,
                   macacao=LARANJA, bota=PRETO, cinto=None, arma='marreta', descanso=70, largura=6),
    'ponssee': dict(cabelo='capacete', cor_capacete=AMARELO, barba='curta', cor_cabelo=CABELO_CASTANHO,
                    camisa=AMARELO, camisa_sombra=AMARELO_ESCURO, gola=None, calca=CINZA_ESCURO,
                    macacao=AMARELO, faixa=PRETO, bota=PRETO, cinto=None, arma=None, descanso=None, largura=6),
}


def _ponto(x, y, ang, comp):
    r = math.radians(ang)
    return x + math.cos(r) * comp, y + math.sin(r) * comp


def _retangulo_girado(d, x, y, ang, comp, larg, cor, inicio=0):
    """Retângulo que sai de (x, y) na direção `ang` (graus; 0 = frente, 90 = baixo)."""
    r = math.radians(ang)
    ux, uy = math.cos(r), math.sin(r)
    nx, ny = -uy * larg / 2, ux * larg / 2
    x0, y0 = x + ux * inicio, y + uy * inicio
    x1, y1 = x + ux * (inicio + comp), y + uy * (inicio + comp)
    d.polygon([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], fill=cor)


def _arma(img, d, tipo, hx, hy, ang, quadro):
    """Desenha a arma presa na mão (hx, hy) apontando para `ang`."""
    if tipo == 'sabre':
        # Sabre de motosserra: cabo curto + barra longa com a corrente nas bordas.
        _retangulo_girado(d, hx, hy, ang, 5, 3, LARANJA, inicio=-2)
        _retangulo_girado(d, hx, hy, ang, 23, 5, METAL, inicio=3)
        tx, ty = _ponto(hx, hy, ang, 26)
        d.ellipse([tx - 2.5, ty - 2.5, tx + 2.5, ty + 2.5], fill=METAL)
        _retangulo_girado(d, hx, hy, ang, 21, 1, METAL_SOMBRA, inicio=5)
        r = math.radians(ang)
        nx, ny = -math.sin(r), math.cos(r)
        p = img.load()
        for k in range(4 + (quadro % 2), 27, 2):  # dentes da corrente andam a cada quadro
            for lado in (-3, 3):
                px, py = _ponto(hx, hy, ang, k)
                px, py = int(round(px + nx * lado)), int(round(py + ny * lado))
                if 0 <= px < W and 0 <= py < H:
                    p[px, py] = CINZA_ESCURO
    elif tipo == 'chave':
        # Chave de engenheiro gigante: cabo grosso + cabeça com mandíbula.
        _retangulo_girado(d, hx, hy, ang, 16, 4, METAL, inicio=-3)
        cx, cy = _ponto(hx, hy, ang, 16)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=METAL)
        bx, by = _ponto(hx, hy, ang, 19)
        d.ellipse([bx - 2.5, by - 2.5, bx + 2.5, by + 2.5], fill=(0, 0, 0, 0))
        _retangulo_girado(d, hx, hy, ang, 12, 1, METAL_SOMBRA, inicio=-1)
    elif tipo == 'marreta':
        _retangulo_girado(d, hx, hy, ang, 14, 3, MARROM, inicio=-2)
        cx, cy = _ponto(hx, hy, ang, 13)
        _retangulo_girado(d, cx, cy, ang + 90, 10, 6, CINZA, inicio=-5)
    elif tipo == 'ferramenta':
        _retangulo_girado(d, hx, hy, ang, 7, 2, METAL, inicio=-1)
        cx, cy = _ponto(hx, hy, ang, 7)
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=METAL)
    elif tipo == 'lata':
        d.rectangle([hx - 3, hy - 5, hx + 3, hy + 3], fill=VERMELHO)
        d.rectangle([hx - 3, hy - 2, hx + 3, hy - 1], fill=AMARELO)
        d.rectangle([hx - 1, hy - 7, hx + 1, hy - 6], fill=CINZA)


def _clarear(cor, t=0.3):
    return misturar(cor, BRANCO, t)


def _capsula(d, a, b, r0, r1, cor, borda=None):
    """Membro arredondado de `a` até `b` (raio r0 → r1): coxa, canela, braço, antebraço.
    Com `borda`, desenha antes um contorno próprio (separa o membro do corpo atrás dele)."""
    if borda:
        _capsula(d, a, b, r0 + 1, r1 + 1, borda)
    (x0, y0), (x1, y1) = a, b
    comp = math.hypot(x1 - x0, y1 - y0) or 1
    nx, ny = -(y1 - y0) / comp, (x1 - x0) / comp
    d.polygon([(x0 + nx * r0, y0 + ny * r0), (x1 + nx * r1, y1 + ny * r1),
               (x1 - nx * r1, y1 - ny * r1), (x0 - nx * r0, y0 - ny * r0)], fill=cor)
    d.ellipse([x0 - r0, y0 - r0, x0 + r0, y0 + r0], fill=cor)
    d.ellipse([x1 - r1, y1 - r1, x1 + r1, y1 + r1], fill=cor)


def _junta(a, b, dobra, frente=1.0):
    """Ponto da articulação (joelho/cotovelo) entre a e b, deslocado `dobra` px para o lado da dobra."""
    (x0, y0), (x1, y1) = a, b
    comp = math.hypot(x1 - x0, y1 - y0) or 1
    nx, ny = -(y1 - y0) / comp, (x1 - x0) / comp
    return (x0 + x1) / 2 + nx * dobra * frente, (y0 + y1) / 2 + ny * dobra * frente


def _perna(d, quadril, pe, cor, bota, frente):
    """Coxa + canela com o joelho dobrado para a frente e bota de bico arredondado."""
    joelho = _junta(quadril, pe, 2.2, -1)  # o joelho aponta para a frente (direita)
    if joelho[0] < max(quadril[0], pe[0]):
        joelho = (max(quadril[0], pe[0]) + 1.5, joelho[1])
    borda = CONTORNO if frente else None
    _capsula(d, quadril, joelho, 4.0, 3.2, cor, borda)                                   # coxa larga (calça cargo)
    _capsula(d, joelho, (pe[0], pe[1] - 2), 3.2, 3.0, cor, borda)                       # calça "estufada" na bota
    if frente:
        d.line([(quadril[0] + 3, quadril[1] + 1), (joelho[0] + 2.5, joelho[1])], fill=_clarear(cor, 0.2))   # luz
        bx, by = _junta(quadril, joelho, 0.5)
        d.rectangle([bx - 2, by - 1, bx + 1, by + 2], fill=escurecer(cor, 0.78))       # bolso lateral
        d.line([(joelho[0] - 2, joelho[1] + 1), (joelho[0] + 1, joelho[1] + 2)], fill=escurecer(cor, 0.72))  # dobra
    fx, fy = pe
    if borda:
        d.rounded_rectangle([fx - 4, fy - 4, fx + 7, fy + 2], radius=2, fill=CONTORNO)
    d.rounded_rectangle([fx - 3, fy - 3, fx + 6, fy + 1], radius=2, fill=bota)          # bota robusta
    d.line([(fx - 3, fy + 1), (fx + 6, fy + 1)], fill=escurecer(bota, 0.5))              # sola grossa
    d.line([(fx - 2, fy - 2), (fx + 1, fy - 2)], fill=_clarear(bota, 0.15))             # cano
    if frente:
        d.point((fx + 4, fy - 1), fill=_clarear(bota, 0.35))                            # brilho do couro


def _braco(d, ombro, mao, manga, pele, frente):
    """Braço forte: manga do uniforme e antebraço musculoso de fora (estilo Metal Slug)."""
    cotovelo = _junta(ombro, mao, 1.4)
    borda = CONTORNO if frente else None
    _capsula(d, cotovelo, mao, 2.8, 2.2, pele, borda)                                    # antebraço
    _capsula(d, ombro, cotovelo, 3.3, 2.8, manga, borda)                                 # braço com manga
    if frente:
        d.line([(cotovelo[0], cotovelo[1] + 1), (mao[0] - 1, mao[1] + 1)], fill=PELE_SOMBRA)    # músculo do antebraço
        bx, by = _junta(ombro, cotovelo, 1.2, -1)
        d.point((bx, by), fill=_clarear(manga, 0.3))                                   # brilho no bíceps


def boneco(tipo, pose, quadro=0):
    """Renderiza um quadro 64x64 de perfil no formato do Marco (Metal Slug), com anatomia arredondada e
    contorno definido (lembrando Street Fighter): postura curvada, cabeça grande, braço forte com
    antebraço de fora, calça cargo larga e botas robustas; cabeça de perfil, tronco com peito e costas, membros
    com joelho/cotovelo dobrados, 3 tons por material e contorno próprio no braço e na perna da frente.
    `pose` é um dict com os parâmetros (ver poses()). A mão fica a 10 px do ombro, como as hitboxes esperam."""
    t = TIPOS[tipo]
    img = nova(W, H)
    d = draw(img)
    bob = pose.get('bob', 0)
    lean = pose.get('lean', 0)
    agacha = pose.get('agacha', 0)
    lw = t['largura']
    camisa, sombra, luz = t['camisa'], t['camisa_sombra'], _clarear(t['camisa'], 0.22)

    quadril_y = CHAO - 14 + agacha
    ombro_topo = quadril_y - 11 + bob
    ox = CX + lean
    ombro_y = ombro_topo + 2
    curva = 2  # postura curvada para a frente (os ombros passam do quadril)

    # ── Braço de trás (mais escuro, atrás de tudo) ──
    ombro_tras = (ox - 1 + curva, ombro_y)
    ang_tras = pose.get('braco_tras', 100)
    mao_tras = _ponto(*ombro_tras, ang_tras, 10)
    _braco(d, ombro_tras, mao_tras, escurecer(camisa, 0.65), PELE_SOMBRA, False)
    d.ellipse([mao_tras[0] - 2.5, mao_tras[1] - 2.5, mao_tras[0] + 2, mao_tras[1] + 2], fill=PELE_SOMBRA)

    # ── Perna de trás ──
    pt = pose.get('pe_tras', (-3, 0))
    _perna(d, (CX - 1 + lean / 2, quadril_y), (CX + pt[0], CHAO - pt[1] - 2),
           escurecer(t['calca'], 0.72), escurecer(t['bota'], 0.8), False)

    # ── Tronco de perfil: costas curvas atrás, peito para a frente ──
    frente_x = ox + lw - 1
    tronco = [(ox - lw + 1 + curva, ombro_topo + 1), (ox + curva, ombro_topo - 1), (frente_x + curva, ombro_topo),
              (frente_x + 2 + curva, ombro_topo + 4), (frente_x + 1, quadril_y - 4), (frente_x, quadril_y),
              (ox - lw + 1, quadril_y), (ox - lw - 1, quadril_y - 5), (ox - lw + curva - 1, ombro_topo + 3)]
    d.polygon(tronco, fill=camisa)
    d.polygon([(ox - lw + 1 + curva, ombro_topo + 1), (ox - lw + 3 + curva, ombro_topo + 1), (ox - lw + 3, quadril_y),
               (ox - lw + 1, quadril_y), (ox - lw - 1, quadril_y - 5), (ox - lw + curva - 1, ombro_topo + 3)], fill=sombra)  # costas
    d.line([(frente_x, ombro_topo + 1), (frente_x + 1, ombro_topo + 4)], fill=luz)                  # peito
    d.arc([ox - 1, ombro_topo + 2, frente_x + 1, ombro_topo + 8], 20, 120, fill=escurecer(camisa, 0.8))  # peitoral
    if t.get('macacao'):
        d.polygon([(ox - lw + 1, ombro_topo + 5), (frente_x + 1, ombro_topo + 5), (frente_x + 1, quadril_y - 4),
                   (frente_x, quadril_y), (ox - lw + 2, quadril_y), (ox - lw + 1, quadril_y - 5)], fill=t['macacao'])
        d.line([(ox + 2, ombro_topo), (ox + 2, ombro_topo + 5)], fill=t['macacao'], width=2)        # alça
    if t.get('faixa'):
        d.line([(ox - lw + 1, ombro_topo + 6), (frente_x + 1, ombro_topo + 6)], fill=t['faixa'], width=2)
    if t.get('barriga'):
        d.ellipse([ox - 1, ombro_topo + 3, frente_x + 5, quadril_y + 1], fill=camisa)
        d.arc([ox - 1, ombro_topo + 3, frente_x + 5, quadril_y + 1], 300, 60, fill=luz)
        d.arc([ox - 1, ombro_topo + 3, frente_x + 5, quadril_y + 1], 60, 120, fill=escurecer(camisa, 0.75))
    if t.get('gola'):
        d.polygon([(ox + 1, ombro_topo - 1), (frente_x, ombro_topo), (ox + 3, ombro_topo + 4)], fill=t['gola'])
    if t.get('cinto'):
        cinto_x = frente_x + (4 if t.get('barriga') else 1)
        d.line([(ox - lw + 1, quadril_y - 1), (cinto_x, quadril_y - 1)], fill=t['cinto'], width=2)
        d.point((frente_x - 1, quadril_y - 1), fill=METAL)                                      # fivela

    # ── Perna da frente (contorno próprio) ──
    pf = pose.get('pe_frente', (3, 0))
    _perna(d, (CX + 1 + lean / 2, quadril_y), (CX + pf[0], CHAO - pf[1] - 2), t['calca'], t['bota'], True)

    # ── Cabeça de perfil: crânio, mandíbula, nariz, olho, orelha ──
    hx = ox + 1 + curva
    topo = ombro_topo - 11
    d.rectangle([hx - 2, topo + 8, hx + 1, ombro_topo + 1], fill=PELE_SOMBRA)                   # pescoço grosso
    d.ellipse([hx - 6, topo - 1, hx + 5, topo + 9], fill=PELE)                                # crânio grande
    d.polygon([(hx - 3, topo + 6), (hx + 5, topo + 5), (hx + 6, topo + 9), (hx + 5, topo + 11),
               (hx - 1, topo + 11)], fill=PELE)                                               # queixo quadrado
    d.polygon([(hx + 4, topo + 2), (hx + 7, topo + 5), (hx + 5, topo + 6)], fill=PELE)        # nariz marcado
    d.point((hx + 6, topo + 5), fill=PELE_SOMBRA)
    d.arc([hx - 6, topo - 1, hx + 5, topo + 9], 110, 200, fill=PELE_SOMBRA)                   # sombra da nuca
    d.line([(hx - 1, topo + 11), (hx + 4, topo + 11)], fill=PELE_SOMBRA)                      # sombra do queixo
    d.point((hx + 2, topo + 3), fill=BRANCO)                                                  # olho
    d.point((hx + 3, topo + 3), fill=PRETO)
    d.ellipse([hx - 3, topo + 4, hx - 1, topo + 7], fill=PELE_SOMBRA)                         # orelha
    d.line([(hx + 3, topo + 8), (hx + 4, topo + 8)], fill=VERMELHO_ESCURO)                    # boca
    cc = t['cor_cabelo']
    d.line([(hx, topo + 2), (hx + 4, topo + 1)], fill=cc, width=2)                            # sobrancelha brava
    cab = t['cabelo']
    if cab == 'capacete':
        cap = t['cor_capacete']
        d.chord([hx - 7, topo - 4, hx + 6, topo + 7], 180, 360, fill=cap)
        d.line([(hx - 7, topo + 1), (hx + 8, topo + 1)], fill=escurecer(cap, 0.7), width=2)    # aba
        d.arc([hx - 6, topo - 3, hx + 3, topo + 4], 200, 280, fill=_clarear(cap, 0.45))        # brilho
        d.rectangle([hx - 6, topo + 3, hx - 4, topo + 6], fill=cc)
    else:
        d.chord([hx - 7, topo - 3, hx + 5, topo + 6], 160, 360, fill=cc)                       # cabelo
        d.rectangle([hx - 7, topo + 1, hx - 3, topo + 6], fill=cc)                             # nuca
        for k in range(3):                                                                    # mechas espetadas
            d.polygon([(hx - 5 + k * 3, topo - 2), (hx - 3 + k * 3, topo - 5), (hx - 1 + k * 3, topo - 2)], fill=cc)
        d.arc([hx - 6, topo - 2, hx + 3, topo + 5], 210, 290, fill=_clarear(cc, 0.3))          # brilho
        if cab == 'coque':     # coque samurai + hachimaki laranja na testa
            d.ellipse([hx - 7, topo - 7, hx - 2, topo - 2], fill=cc)
            d.line([(hx - 7, topo + 1), (hx + 5, topo)], fill=LARANJA, width=2)
            d.polygon([(hx - 7, topo + 1), (hx - 11, topo + 4), (hx - 9, topo + 5)], fill=LARANJA)   # pontas da faixa
        elif cab == 'topete':  # topete pontudo para a frente
            d.polygon([(hx - 2, topo - 2), (hx + 8, topo - 6), (hx + 4, topo + 1)], fill=cc)
        elif cab == 'curto':
            d.line([(hx - 3, topo - 1), (hx + 2, topo - 1)], fill=cc)
    barba = t['barba']
    if barba == 'cheia':
        d.polygon([(hx - 2, topo + 6), (hx + 6, topo + 7), (hx + 5, topo + 12), (hx - 1, topo + 12)], fill=cc)
        d.line([(hx + 2, topo + 6), (hx + 6, topo + 6)], fill=cc)                              # bigode
        d.point((hx + 2, topo + 9), fill=_clarear(cc, 0.2))
    elif barba == 'curta':
        d.polygon([(hx - 1, topo + 9), (hx + 5, topo + 9), (hx + 4, topo + 12), (hx - 1, topo + 12)], fill=cc)
        d.line([(hx + 3, topo + 7), (hx + 5, topo + 7)], fill=cc)
    elif barba == 'bigode':
        d.line([(hx + 2, topo + 7), (hx + 5, topo + 7)], fill=cc, width=2)

    # ── Braço da frente (contorno próprio) + punho + arma ──
    ombro = (ox + 1 + curva, ombro_y)
    ang = pose.get('braco', 80)
    mao = _ponto(*ombro, ang, 10)
    arma = pose.get('arma', t['arma'])
    ang_arma = pose.get('ang_arma', ang)
    _braco(d, ombro, mao, camisa, PELE, True)
    d.ellipse([ombro[0] - 3.5, ombro[1] - 3.5, ombro[0] + 3.5, ombro[1] + 2.5], fill=camisa)    # ombro (deltoide)
    d.arc([ombro[0] - 3.5, ombro[1] - 3.5, ombro[0] + 3.5, ombro[1] + 2.5], 200, 320, fill=luz)
    if arma:
        _arma(img, d, arma, mao[0], mao[1], ang_arma, quadro)
    mx, my = mao
    d.ellipse([mx - 3, my - 3, mx + 2.5, my + 2.5], fill=CONTORNO)                             # punho grande
    d.ellipse([mx - 2.2, my - 2.2, mx + 1.8, my + 1.8], fill=PELE)
    d.point((mx + 1, my - 1), fill=PELE_SOMBRA)

    img = contorno(img)
    rot = pose.get('rot', 0)
    if rot:
        # Gira em torno dos pés (para quedas/morte) e reposiciona no chão.
        img = img.rotate(-rot, resample=Image.NEAREST, center=(CX, CHAO - 4))
        if abs(rot) >= 60:
            caixa = img.getbbox()
            if caixa:
                desl = CHAO - caixa[3]
                deslocada = nova(W, H)
                deslocada.paste(img, (0, desl), img)
                img = deslocada
    return img


# ── Poses ──────────────────────────────────────────────────────────────────

def _correndo(n, amplitude=5, pesado=False):
    quadros = []
    for i in range(n):
        p = i / n * math.tau
        s, c = math.sin(p), math.cos(p)
        quadros.append(dict(
            pe_frente=(round(amplitude * s), round(max(0, c) * 3)),
            pe_tras=(round(-amplitude * s), round(max(0, -c) * 3)),
            bob=-1 if abs(s) > 0.7 else 0, lean=1 if not pesado else 0,
            braco=round(80 - 45 * s), braco_tras=round(95 + 45 * s)))
    return quadros


def _arma_descanso(tipo):
    return TIPOS[tipo]['descanso']


def poses(tipo, anim, n):
    descanso = _arma_descanso(tipo)
    base_braco = descanso if descanso is not None else 80
    pesado = tipo == 'paulinho'

    if anim == 'parado':
        return [dict(bob=b, braco=base_braco, braco_tras=100) for b in (0, 0, 1, 1)][:n]
    if anim in ('correndo', 'andando'):
        lista = _correndo(n, amplitude=4 if anim == 'andando' else 5, pesado=pesado)
        if descanso is not None:
            for q in lista:
                q['braco'] = descanso + (q['braco'] - 80) // 4
        return lista
    if anim == 'pulo':
        return [dict(pe_frente=(4, 6), pe_tras=(-3, 2), braco=-30 if descanso is None else descanso - 20, braco_tras=-60 + k * 10, bob=-1) for k in range(n)]
    if anim == 'queda':
        return [dict(pe_frente=(3, 1 + k), pe_tras=(-4, 3), braco=-10 + k * 10 if descanso is None else descanso, braco_tras=-30) for k in range(n)]
    if anim == 'aterrissagem':
        return [dict(agacha=a, pe_frente=(4, 0), pe_tras=(-4, 0), braco=base_braco + 10, braco_tras=110) for a in (3, 1)][:n]
    if anim == 'dano':
        return [dict(lean=-2, bob=-1, braco=-70, braco_tras=-120, rot=-8 - 4 * k, pe_frente=(5, 1), pe_tras=(-2, 0)) for k in range(n)]
    if anim == 'morte':
        rots = [-10, -30, -55, -80, -90, -90]
        return [dict(lean=-2, braco=-80, braco_tras=-120, rot=r, pe_frente=(5, 1), pe_tras=(-2, 0)) for r in rots][:n]
    if anim == 'vitoria':
        if tipo == 'kanka':
            return [dict(braco=-90 + k % 2 * 10, ang_arma=-90, arma='ferramenta', braco_tras=100, bob=-(k % 2)) for k in range(n)]
        return [dict(braco=-80 - k % 2 * 10, ang_arma=-95 - k % 2 * 10, braco_tras=110, bob=-(k % 2), pe_frente=(5, 0), pe_tras=(-5, 0)) for k in range(n)]
    if anim == 'alerta':
        return [dict(braco=-60, braco_tras=-110, bob=-2, pe_frente=(3, 2), pe_tras=(-3, 2)), dict(braco=-40, braco_tras=-100, bob=-1)][:n]

    # ── Ataques ──
    postura = dict(pe_frente=(5, 0), pe_tras=(-5, 0))
    no_ar = dict(pe_frente=(4, 6), pe_tras=(-3, 3))
    if tipo == 'samurai_jeff':
        angs = {'ataque': [-130, -60, 0, 45, 70, 80], 'ataque_2': [80, 45, 0, -60, -100, -110],
                'ataque_ar': [-90, -45, 30, 135, 200]}[anim]
        extra = no_ar if anim == 'ataque_ar' else postura
        return [dict(braco=a if a < 150 else a - 360, braco_tras=110, lean=2 if 1 <= i <= 3 else 0, **extra) for i, a in enumerate(angs)][:n]
    if tipo == 'paulinho':
        angs = {'ataque': [-100, -130, -150, -160, 20, 50, 60, 40], 'ataque_ar': [-120, -150, -40, 40, 60, 50]}[anim]
        extra = no_ar if anim == 'ataque_ar' else postura
        return [dict(braco=a, braco_tras=110, agacha=2 if anim == 'ataque' and i in (4, 5) else 0,
                     lean=2 if i in (4, 5) else -1 if i in (2, 3) else 0, **extra) for i, a in enumerate(angs)][:n]
    if tipo == 'kanka':  # arremesso / arremesso_ar
        extra = no_ar if anim == 'arremesso_ar' else postura
        seq = [dict(braco=-130, arma='ferramenta', ang_arma=-130), dict(braco=-20, arma=None), dict(braco=0, arma=None), dict(braco=40, arma=None)]
        return [dict(braco_tras=110, lean=1 if i else -1, **extra, **q) for i, q in enumerate(seq)][:n]
    if tipo == 'logmax':  # ataque
        angs = [-110, -140, -20, 40, 70, 80]
        return [dict(braco=a, braco_tras=110, lean=2 if i in (2, 3) else 0, **postura) for i, a in enumerate(angs)][:n]
    if tipo == 'ponssee':  # arremesso (a lata sai no quadro 2)
        seq = [dict(braco=-100, arma='lata'), dict(braco=-150, arma='lata'), dict(braco=-30, arma=None),
               dict(braco=10, arma=None), dict(braco=60, arma=None)]
        return [dict(braco_tras=110, **postura, **q) for q in seq][:n]
    raise ValueError(f'pose desconhecida: {tipo}/{anim}')


def gerar(tipo, anim, n):
    lista = poses(tipo, anim, n)
    while len(lista) < n:
        lista.append(lista[-1])
    return tira([boneco(tipo, p, i) for i, p in enumerate(lista)])
