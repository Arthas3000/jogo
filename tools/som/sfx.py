"""Efeitos sonoros sintetizados (menus finais + jogo provisório)."""

import numpy as np
from . import sintetizador as s


def _env(x, tau):
    return x * s.decaimento(len(x), tau)


def _seq(*partes):
    return np.concatenate(partes)


def ui_mover():
    return _env(s.pulso(1320, 0.05, 0.5), 0.03)


def ui_confirmar():
    return _seq(*[_env(s.pulso(f, 0.05, 0.25), 0.05) for f in (660, 990, 1320)], _env(s.pulso(1760, 0.12, 0.25), 0.05))


def ui_voltar():
    return _env(s.pulso(660, 0.12, 0.5, f_fim=330), 0.06)


def ui_ficha():
    # O clássico "plim-plim" de moeda: B5 curto e E6 longo.
    return _seq(_env(s.pulso(988, 0.07, 0.5), 0.2), _env(s.pulso(1319, 0.45, 0.5), 0.15))


def ui_tique():
    return _env(s.pulso(1600, 0.035, 0.5), 0.01)


def ui_pronto():
    acorde = sum(s.pulso(s.freq(m), 0.7, 0.25) for m in (s.midi('A3'), s.midi('E4'), s.midi('A4'), s.midi('C#5')))
    subida = s.pulso(220, 0.7, 0.5, f_fim=880) * 0.4
    estouro = s.ruido(0.7, 9000) * s.decaimento(int(0.7 * s.SR), 0.08)
    return _env(acorde * 0.4 + subida + estouro, 0.25)


def ui_anuncio():
    n = int(0.5 * s.SR)
    vento = s.passa_baixa(s.ruido(0.5, s.SR), 3000) * np.sin(np.linspace(0, np.pi, n)) * 1.5
    return vento + _env(s.pulso(220, 0.5, 0.25, f_fim=660), 0.25) * 0.5


def pulo():
    return _env(s.pulso(280, 0.13, 0.5, f_fim=720), 0.08)


def aterrissar():
    return _env(s.passa_baixa(s.ruido(0.08, 3000), 900), 0.03) * 1.5


def sabre_ataque():
    # Motosserra: serra grave com modulação de amplitude rápida + ruído.
    dur = 0.32
    n = int(dur * s.SR)
    t = s.tempo(n)
    motor = s.serra(95, dur, f_fim=150) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 38 * t)))
    corrente = s.passa_baixa(s.ruido(dur, 8000), 2500) * 0.6
    return (motor + corrente) * s.adsr(n, 0.01, 0.05, 0.8, 0.08)


def sabre_acerto():
    dur = 0.16
    n = int(dur * s.SR)
    t = s.tempo(n)
    return _env(s.serra(240, dur) * (np.sin(2 * np.pi * 60 * t) > 0) + s.ruido(dur, 12000) * 0.7, 0.08)


def arremesso():
    n = int(0.16 * s.SR)
    return s.passa_baixa(s.ruido(0.16, s.SR), 2500) * np.sin(np.linspace(0, np.pi, n)) * 1.6


def ferramenta_quica():
    dur = 0.2
    return _env(sum(s.seno(f, dur) * a for f, a in ((2350, 0.6), (3720, 0.4), (5130, 0.3))), 0.05)


def ferramenta_acerto():
    return _env(s.seno(700, 0.14, 180), 0.06) * 1.2 + _env(s.ruido(0.14, 6000), 0.015)


def chave_giro():
    n = int(0.3 * s.SR)
    return s.passa_baixa(s.ruido(0.3, s.SR), 900) * np.sin(np.linspace(0, np.pi, n)) ** 2 * 2.5


def chave_impacto():
    dur = 0.45
    return _env(s.seno(130, dur, 38), 0.18) * 1.3 + _env(s.passa_baixa(s.ruido(dur, 5000), 1200), 0.08) * 1.2


def inimigo_dano():
    return _env(s.pulso(420, 0.09, 0.5, f_fim=180), 0.05) + _env(s.ruido(0.09, 8000), 0.02) * 0.5


def inimigo_morte():
    # Explosão estilo Mega Man: ruído grave decaindo + arpejo descendente.
    ruido = _env(s.ruido(0.6, 2500), 0.18)
    arpejo = _seq(*[_env(s.pulso(f, 0.05, 0.5), 0.04) for f in (880, 660, 440, 330, 220)])
    arpejo = np.pad(arpejo, (0, len(ruido) - len(arpejo)))
    return ruido + arpejo * 0.5


def inimigo_alerta():
    return _seq(_env(s.pulso(1000, 0.05, 0.25), 0.04), _env(s.pulso(1500, 0.08, 0.25), 0.05))


def inimigo_golpe():
    n = int(0.2 * s.SR)
    return s.passa_baixa(s.ruido(0.2, s.SR), 1500) * np.sin(np.linspace(0, np.pi, n)) * 2


def lata_arremesso():
    n = int(0.15 * s.SR)
    chocalho = s.ruido(0.15, 600) * (np.sin(np.linspace(0, 40, n)) > 0.6) * 0.4
    return s.passa_baixa(s.ruido(0.15, s.SR), 2000) * np.sin(np.linspace(0, np.pi, n)) + chocalho


def lata_respingo():
    return _env(s.passa_baixa(s.ruido(0.3, 4000), 700), 0.1) * 2 + _env(s.seno(200, 0.3, 80), 0.06)


def jogador_dano():
    return _seq(*[_env(s.pulso(f, 0.05, 0.5), 0.04) for f in (500, 380, 500, 300)])


def jogador_morte():
    descida = _env(s.pulso(880, 1.0, 0.5, f_fim=80), 0.5)
    return descida * 0.7 + _env(s.ruido(1.0, 3000), 0.3) * 0.5


def item():
    return _seq(*[_env(s.pulso(s.freq(m), 0.06, 0.25), 0.08) for m in (72, 76, 79, 84)], _env(s.pulso(s.freq(88), 0.2, 0.25), 0.08))


def checkpoint():
    notas = _seq(*[_env(s.pulso(s.freq(m), 0.08, 0.5), 0.1) for m in (67, 72, 76, 79, 84)])
    brilho = _env(s.seno(2637, len(notas) / s.SR), 0.2) * 0.3
    return notas + brilho


# ── máquina customizada ──
def caixa_acerto():
    # "Toc" de madeira oca: seno grave curto + estalo de ruído.
    return _env(s.seno(180, 0.18, 110), 0.05) + _env(s.passa_baixa(s.ruido(0.18, 6000, 11), 1800), 0.02) * 0.8


def caixa_quebra():
    estalos = sum(np.roll(_env(s.passa_baixa(s.ruido(0.6, 8000, k), 2500), 0.03), int(k * 0.045 * s.SR)) for k in range(6))
    return estalos + _env(s.seno(140, 0.6, 50), 0.12) * 0.8


def maquina_ligar():
    # Motor diesel pegando (pulsos graves acelerando) + fanfarra curta de poder.
    n = int(0.9 * s.SR)
    ronco = s.pulso(45, 0.9, 0.3, f_fim=110) * (0.5 + 0.5 * np.sin(np.cumsum(np.linspace(20, 60, n)) / s.SR * 2 * np.pi))
    fanfarra = _seq(*[_env(s.pulso(s.freq(m), 0.09, 0.25), 0.15) for m in (60, 64, 67)], _env(s.pulso(s.freq(72), 0.63, 0.25), 0.3))
    fanfarra = np.pad(fanfarra, (0, max(0, n - len(fanfarra))))[:n]
    return s.passa_baixa(ronco, 900) * 0.8 + fanfarra * 0.5


def maquina_garra():
    # Hidráulico chiando + "clanc" metálico da garra fechando.
    n = int(0.35 * s.SR)
    chiado = s.passa_baixa(s.ruido(0.35, s.SR, 5), 3000) * np.sin(np.linspace(0, np.pi, n)) * 0.5
    clanc = np.zeros(n)
    k = int(0.22 * s.SR)
    clanc[k:] = _env(s.pulso(420, 0.13, 0.5) + s.pulso(633, 0.13, 0.5), 0.04)[:n - k] * 0.6
    return chiado + clanc


def maquina_pegar():
    return _env(s.seno(90, 0.3, 50), 0.1) + _env(s.passa_baixa(s.ruido(0.3, 3000, 8), 1200), 0.08)


def maquina_desligar():
    return _env(s.pulso(110, 0.8, 0.3, f_fim=35), 0.4) * 0.8 + _env(s.ruido(0.8, 2000, 4), 0.3) * 0.3


def maquina_impacto():
    return _env(s.seno(70, 0.5, 30), 0.15) * 1.2 + _env(s.passa_baixa(s.ruido(0.5, 5000, 6), 1500), 0.1)


# ── Passos, vozes e explosões ──
def passo():
    # Bota na terra: baque grave curto + "crec" de folhas/cascalho.
    return _env(s.seno(110, 0.09, 60), 0.025) + _env(s.passa_baixa(s.ruido(0.09, 9000, 21), 2200), 0.015) * 0.7


def esteira():
    # Esteira de aço da escavadeira: dois "clacs" metálicos + ronco.
    clac = _env(s.pulso(300, 0.05, 0.5) + s.ruido(0.05, 7000, 22) * 0.6, 0.012)
    pausa = np.zeros(int(0.03 * s.SR))
    batidas = np.concatenate([clac, pausa, clac * 0.7, pausa])
    return batidas + _env(s.pulso(55, len(batidas) / s.SR, 0.3), 0.08)[:len(batidas)] * 0.5


def _ressonador(x, f, banda):
    """Passa-banda de 2 polos: imita uma formante da voz humana."""
    r = np.exp(-np.pi * banda / s.SR)
    c = 2 * r * np.cos(2 * np.pi * f / s.SR)
    y = np.empty_like(x)
    y1 = y2 = 0.0
    for i, v in enumerate(x):
        y0 = v + c * y1 - r * r * y2
        y[i] = y0
        y2, y1 = y1, y0
    return y * (1 - r)


# Formantes (F1, F2, F3 em Hz) das vogais usadas nos gritos.
VOGAIS = {'a': (750, 1200, 2500), 'e': (500, 1800, 2500), 'u': (350, 800, 2300)}


def _voz(f0, f0_fim, dur, vogal, ataque=0.01, soltura=0.08, vibrato=0.0, sopro=0.15):
    """Voz sintetizada de fliperama: pulso glotal (serra) + sopro passando pelas formantes, em 6 bits."""
    n = int(dur * s.SR)
    t = s.tempo(n)
    f = np.geomspace(f0, f0_fim, n) * (1 + vibrato * np.sin(2 * np.pi * 7 * t))
    fonte = (np.cumsum(f) / s.SR % 1.0) * 2 - 1 + s.ruido(dur, s.SR, 31)[:n] * sopro
    voz = sum(_ressonador(fonte, fr, 90 + fr * 0.08) * g for fr, g in zip(VOGAIS[vogal], (1.0, 0.6, 0.25)))
    voz = voz * s.adsr(n, ataque, 0.05, 0.8, soltura)
    voz = voz / (np.max(np.abs(voz)) or 1)
    return np.round(voz * 32) / 32  # 6 bits: soa "digitalizado", como as vozes de fliperama


def voz_ataque():
    return _voz(190, 150, 0.16, 'a', soltura=0.05)                     # "Rá!"


def voz_dano():
    return _voz(230, 140, 0.22, 'u', sopro=0.3)                        # "Uh!"


def voz_morte():
    return _voz(260, 90, 0.9, 'a', ataque=0.02, soltura=0.4, vibrato=0.04, sopro=0.25)   # "Aaaargh..."


def inimigo_grito():
    # O grito clássico de soldado derrotado no Metal Slug: agudo e caindo.
    return np.concatenate([_voz(340, 300, 0.08, 'e'), _voz(420, 160, 0.5, 'a', soltura=0.25, vibrato=0.05, sopro=0.3)])


def explosao():
    n = int(1.1 * s.SR)
    estrondo = s.passa_baixa(s.ruido(1.1, 6000, 41), 900)[:n] * s.decaimento(n, 0.28) * 1.6
    baque = s.seno(90, 1.1, 28)[:n] * s.decaimento(n, 0.18)
    estalos = s.ruido(1.1, 2500, 42)[:n] * s.decaimento(n, 0.05) * 0.6
    return estrondo + baque + estalos


# ── Caminhonete ──
def caminhonete_motor():
    # Motor acelerando forte e passando (giro sobe, depois some).
    n = int(1.4 * s.SR)
    ronco = s.pulso(55, 1.4, 0.35, f_fim=150) * 0.7 + s.serra(110, 1.4, f_fim=300) * 0.3
    ronco = s.passa_baixa(ronco, 1400) * (0.6 + 0.4 * np.sin(np.linspace(0, 60, n)))
    env = np.minimum(1, np.linspace(0, 6, n)) * np.linspace(1, 0.15, n)
    return ronco * env + s.ruido(1.4, 3000, 51)[:n] * env * 0.15


def caminhonete_freio():
    # Pneus derrapando na terra: chiado + guincho do freio.
    n = int(0.7 * s.SR)
    chiado = s.passa_baixa(s.ruido(0.7, s.SR, 52), 3500)[:n]
    guincho = s.pulso(1150, 0.7, 0.5, vibrato=0.03)[:n] * 0.25
    return (chiado + guincho) * s.adsr(n, 0.01, 0.1, 0.8, 0.25)


SFX = {nome: fn for nome, fn in globals().items() if callable(fn) and not nome.startswith('_') and nome not in ('np', 's')}


def gerar(nome):
    x = SFX[nome]()
    fade = min(len(x), int(0.005 * s.SR))
    x[-fade:] *= np.linspace(1, 0, fade)  # sem estalo no fim
    m = np.max(np.abs(x)) or 1
    return x / m * 0.9
