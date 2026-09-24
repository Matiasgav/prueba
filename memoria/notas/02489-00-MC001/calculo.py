#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nota 02489-00-MC001 - Torque admisible de engranajes cónicos a 90° para
la rueda de un carro, según Shigley (cap. 15, método AGMA en unidades SI).

Uso (desde esta carpeta):
    python3 calculo.py        # escribe resultados.json y figuras/

Caso de carga (rueda de carro):
  * torque en ambos sentidos (marcha adelante/atrás, aceleración y frenado)
    -> flexión alternada: 70 % de la resistencia a flexión (Shigley cap. 15);
  * servicio normal con torque bajo durante toda la vida (T_normal);
  * picos ocasionales de 10 s al torque admisible (T_pico);
  * los dos regímenes se combinan con la regla de Miner, 50 % de daño cada uno.

Diseños: KG M50S20 (S45C), KG M50B20 (latón), KG M50S25 (S45C),
RS PRO 521-5780 (m0,8 z16) y mitra a medida m0,6 z21 de SCM415 carburizado.
"""
import json
import math
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(ROOT, 'figuras')
RES = ROOT

# ---------------------------------------------------------------------------
# 1. Datos del caso
# ---------------------------------------------------------------------------
DATOS = {
    'horas_por_mes': 20,     # 20 h seguidas, una vez por mes
    'anios': 10,             # vida de diseño supuesta
    'rpm': [0, 0.5, 50, 100],
    'rpm_normal': [0.5, 50, 100],   # a 0 rpm no hay servicio continuo
    't_pico': 10.0,          # s, duración de cada pico
    'picos_por_hora': 1.0,   # picos por hora de uso (supuesto)
    'fraccion_miner': 0.5,   # fracción del daño asignada a cada régimen
    'T_amb': 40.0,
}
HORAS_VIDA = DATOS['horas_por_mes'] * 12 * DATOS['anios']
N_PICOS = DATOS['picos_por_hora'] * HORAS_VIDA

FACT = {
    'K_A': 1.00,    # BLDC con perfil trapezoidal suave, carga suave (pedido)
    'Q_v': 6,       # conservador frente a JIS B1704 grados 3-4
    'K_mb': 1.25,   # ningún engranaje entre apoyos
    'Z_xc': 2.0,    # dientes no coronados
    'Y_beta': 1.0,  # dientes rectos
    'R': 0.95,      # confiabilidad pedida
    'S_F': 1.0, 'S_H': 1.0,
    'K_theta': 1.0, 'Z_W': 1.0,
    'alternada': 0.70,  # flexión con carga en ambos sentidos
}

# ---------------------------------------------------------------------------
# 2. Engranajes (geometría) y materiales
# ---------------------------------------------------------------------------
# J (Y_J) e I (Z_I): Shigley Figs. 15-7 y 15-6. 25/25: Ejemplo 15-1 del libro.
ENGRANAJES = {
    'KG m0,5 z20': {'m': 0.5, 'z': 20, 'b': 2.5, 'J': 0.200, 'I': 0.062,
                    'fuente': 'KG M50S20 (catálogo)'},
    'KG m0,5 z25': {'m': 0.5, 'z': 25, 'b': 3.0, 'J': 0.216, 'I': 0.065,
                    'fuente': 'KG M50S25 (catálogo)'},
    'm0,8 z16': {'m': 0.8, 'z': 16, 'b': None, 'J': 0.185, 'I': 0.058,
                 'fuente': 'RS PRO 521-5780 (acero, stock)'},
    # módulo normalizado 0,6 (DIN 780 serie 1); J e I de 20/20 (conservador)
    'm0,6 z21': {'m': 0.6, 'z': 21, 'b': None, 'J': 0.200, 'I': 0.062,
                 'fuente': 'a medida'},
}


def geometria(g):
    m, z = g['m'], g['z']
    d = m * z
    delta = 45.0
    Re = d / (2 * math.sin(math.radians(delta)))
    b_max = min(0.3 * Re, 10 * m)
    b = g['b'] if g['b'] else b_max
    return {'m': m, 'z': z, 'd': d, 'delta': delta, 'Re': Re, 'b': b,
            'b_max': b_max, 'b_ef': min(b, b_max),
            'dm': d - b * math.sin(math.radians(delta)),
            'zv': z / math.cos(math.radians(delta)),
            'da': d + 2 * m * math.cos(math.radians(delta)),
            'ratio_b_Re': b / Re, 'J': g['J'], 'I': g['I']}


BASE = geometria(ENGRANAJES['KG m0,5 z20'])

HB_REF = 170.0
SFLIM_REF = 0.30 * HB_REF + 14.48      # Shigley Fig. 15-13, grado 1
SHLIM_REF = 2.35 * HB_REF + 162.89     # Shigley Fig. 15-12, grado 1

MATERIALES = {
    'S45C': {
        'codigo': 'M50S20-1103', 'E': 205e3, 'nu': 0.30, 'HB': HB_REF, 'Sy': 345.0,
        'sFlim': SFLIM_REF, 'sHlim': SHLIM_REF,
        'base_F': 'Shigley Fig. 15-13, grado 1, 170 HB',
        'base_H': 'Shigley Fig. 15-12, grado 1, 170 HB',
        'kg_W': {100: 1.5, 200: 3.1, 400: 6.2, 600: 9.3, 800: 12.4, 1000: 15.5},
    },
    'Latón C3604B': {
        'codigo': 'M50B20-1103', 'E': 100e3, 'nu': 0.34, 'HB': 100.0, 'Sy': 250.0,
        'sFlim': 138.0 / 285.0 * SFLIM_REF, 'sHlim': 100.0 / HB_REF * SHLIM_REF,
        'base_F': 'fatiga 138/285 MPa × S45C',
        'base_H': 'dureza 100/170 × S45C',
        'kg_W': None,
    },
    # Solo para alternativas a medida: Shigley, acero carburizado grado 1
    'SCM415 carburizado': {
        'codigo': 'a medida', 'E': 205e3, 'nu': 0.30, 'HB': 600.0, 'Sy': 800.0,
        'sFlim': 206.8, 'sHlim': 1379.0,
        'base_F': 'Shigley, carburizado grado 1 (30 kpsi), 58-62 HRC',
        'base_H': 'Shigley, carburizado grado 1 (200 kpsi)',
        'kg_W': None,
    },
}

COTA_BAJA = {  # hipótesis más pesimista para el picado del latón (no tabulado)
    'Latón C3604B': 207.0 / (2.22 * HB_REF + 200.0) * SHLIM_REF,
}

KGF = 9.80665


# ---------------------------------------------------------------------------
# 3. Factores de Shigley cap. 15 (SI)
# ---------------------------------------------------------------------------
def v_et(g, rpm):
    return math.pi * g['d'] * rpm / 60000.0


def K_v(g, rpm, Qv):
    B = 0.25 * (12 - Qv) ** (2 / 3)
    A = 50 + 56 * (1 - B)
    return ((A + math.sqrt(200 * v_et(g, rpm))) / A) ** B


def Y_x(m):
    return 0.5 if m < 1.6 else 0.4867 + 0.008339 * m


def Z_x(b):
    return 0.5 if b < 12.7 else 0.00492 * b + 0.4375


def K_Hb(b, Kmb):
    return Kmb + 5.6e-6 * b ** 2


def Y_NT(N):
    if N < 1e3:
        return 2.7
    if N < 3e6:
        return 6.1514 * N ** -0.1192
    return 1.6831 * N ** -0.0323


def Z_NT(N):
    if N < 1e4:
        return 2.0
    return 3.4822 * N ** -0.0602


def Y_Z(R):
    if R >= 0.99:
        return 0.50 - 0.25 * math.log10(1 - R)
    return 0.70 - 0.15 * math.log10(1 - R)


def Z_E(E, nu):
    return math.sqrt(1 / (math.pi * 2 * (1 - nu ** 2) / E))


# ---------------------------------------------------------------------------
# 4. Ciclos de cada régimen
# ---------------------------------------------------------------------------
def ciclos_normal(rpm, anios=None):
    anios = DATOS['anios'] if anios is None else anios
    return rpm * 60 * DATOS['horas_por_mes'] * 12 * anios


def ciclos_pico(rpm, picos=None):
    """Ciclos por diente debidos a los picos. Con menos de una vuelta por pico
    (0 y 0,5 rpm) se supone que el mismo diente carga en cada pico."""
    picos = N_PICOS if picos is None else picos
    vueltas = rpm * DATOS['t_pico'] / 60.0
    return picos * max(1.0, vueltas)


def N_eval(n):
    """Miner: cada régimen consume la fracción asignada del daño, así que se
    evalúa la resistencia a n / fracción ciclos."""
    return n / DATOS['fraccion_miner']


# ---------------------------------------------------------------------------
# 5. Capacidad de un par metálico
# ---------------------------------------------------------------------------
def capacidad(g, mat, rpm, N, f=None, sHlim=None, alternada=True):
    f = dict(FACT, **(f or {}))
    m, d, b = g['m'], g['d'], g['b_ef']
    Kv = K_v(g, rpm, f['Q_v'])
    KHb = K_Hb(b, f['K_mb'])
    YZ = Y_Z(f['R'])
    ZZ = math.sqrt(YZ)
    sFlim = mat['sFlim'] * (f['alternada'] if alternada else 1.0)
    sHlim = mat['sHlim'] if sHlim is None else sHlim
    sFP = sFlim * Y_NT(N) / (f['S_F'] * f['K_theta'] * YZ)
    sHP = sHlim * Z_NT(N) * f['Z_W'] / (f['S_H'] * f['K_theta'] * ZZ)
    W_F = sFP * b * m * f['Y_beta'] * g['J'] / (f['K_A'] * Kv * Y_x(m) * KHb)
    ZE = Z_E(mat['E'], mat['nu'])
    W_H = (sHP / ZE) ** 2 * b * d * g['I'] / (f['K_A'] * Kv * KHb * Z_x(b) * f['Z_xc'])
    T_F, T_H = W_F * d / 2000.0, W_H * d / 2000.0
    # Verificación de fluencia a flexión en picos: el admisible no puede
    # superar S_y (estado límite estático).
    return {'rpm': rpm, 'N': N, 'v_et': v_et(g, rpm), 'K_v': Kv, 'K_Hb': KHb,
            'Y_NT': Y_NT(N), 'Z_NT': Z_NT(N), 'Y_Z': YZ, 'Z_Z': ZZ, 'Z_E': ZE,
            'sFlim': sFlim, 'sHlim': sHlim, 'sFP': sFP, 'sHP': sHP,
            'fluencia_ok': sFP < mat['Sy'],
            'W_F': W_F, 'W_H': W_H, 'T_F': T_F, 'T_H': T_H,
            'T_adm': min(T_F, T_H), 'modo': 'flexión' if T_F <= T_H else 'picado'}


def regimenes(g, mat, **kw):
    out = {'normal': {}, 'pico': {}}
    for r in DATOS['rpm_normal']:
        out['normal'][r] = capacidad(g, mat, r, N_eval(ciclos_normal(r)), **kw)
    for r in DATOS['rpm']:
        out['pico'][r] = capacidad(g, mat, r, N_eval(ciclos_pico(r)), **kw)
    return out


def torque_kg(mat):
    if not mat['kg_W']:
        return None
    return {n: 9549.7 * P / 1000.0 / n for n, P in mat['kg_W'].items()}


# ---------------------------------------------------------------------------
# 7. Fijación al eje (Shigley tabla 7-4)
# ---------------------------------------------------------------------------
def prisionero(D=3.0, lbf=85):
    """Shigley tabla 7-4: n.º 2 (bajo M2,5) 85 lbf; n.º 4 (bajo M3) 160 lbf."""
    F = lbf * 4.44822
    return {'F': F, 'D': D, 'T_uno': F * D / 2000, 'n_S': 2.0,
            'T_seguro': F * D / 2000 / 2.0}


# ---------------------------------------------------------------------------
# 8. Diseños analizados (todos con d_a <= 14 mm, 1:1, 90°)
# ---------------------------------------------------------------------------
DISENOS = [
    # clave, engranaje, material, etiqueta corta, descripción
    ('M50S20', 'KG m0,5 z20', 'S45C', 'KG M50S20', 'KG M50S20, S45C (stock, referencia)'),
    ('M50B20', 'KG m0,5 z20', 'Latón C3604B', 'KG M50B20', 'KG M50B20, latón C3604B (stock)'),
    ('M50S25', 'KG m0,5 z25', 'S45C', 'KG M50S25', 'KG M50S25, S45C (stock)'),
    ('RS', 'm0,8 z16', 'S45C', 'RS PRO 521-5780', 'RS PRO 521-5780, m0,8 z16, S45C (stock)'),
    ('CARB', 'm0,6 z21', 'SCM415 carburizado', 'A medida carburizada',
     'A medida m0,6 z21, SCM415 carburizado 58-62 HRC'),
]
CLAVES = [d[0] for d in DISENOS]
INFO = {d[0]: {'eng': d[1], 'mat': d[2], 'corto': d[3], 'desc': d[4]} for d in DISENOS}
GEO = {k: geometria(ENGRANAJES[INFO[k]['eng']]) for k in CLAVES}


def calcular_disenos(**kw):
    return {k: regimenes(GEO[k], MATERIALES[INFO[k]['mat']], **kw) for k in CLAVES}


# ---------------------------------------------------------------------------
# 9. Figuras
# ---------------------------------------------------------------------------
TXT, TXT2, GRID = '#0b0b0b', '#52514e', '#e4e3df'
SERIES = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100']
RAMPA = ['#9ec5f4', '#5598e7', '#256abf', '#0d366b']
# Latin Modern, como el texto de la nota (si no está instalada, DejaVu Serif)
_LM = '/usr/share/texmf/fonts/opentype/public/lm/lmroman10-regular.otf'
if os.path.exists(_LM):
    from matplotlib import font_manager
    font_manager.fontManager.addfont(_LM)
    font_manager.fontManager.addfont(_LM.replace('regular', 'bold'))
plt.rcParams.update({'font.family': 'serif',
                     'font.serif': ['Latin Modern Roman', 'DejaVu Serif'],
                     'mathtext.fontset': 'cm', 'font.size': 9,
                     'pdf.fonttype': 3})


def fmt_rpm(r):
    return f'{r:g}'.replace('.', ',')


def estilo(ax, xlabel=None, ylabel=None):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'):
        ax.spines[s].set_color('#b8b7b1')
    ax.tick_params(colors=TXT2, labelsize=8.5)
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    if xlabel:
        ax.set_xlabel(xlabel, color=TXT2)
    if ylabel:
        ax.set_ylabel(ylabel, color=TXT2)


def _coma(v, _pos):
    return f'{v:g}'.replace('.', ',')


def guardar(fig, nombre):
    from matplotlib.ticker import FuncFormatter, ScalarFormatter
    for ax in fig.axes:  # decimales con coma en ejes lineales
        for eje, escala in ((ax.xaxis, ax.get_xscale()), (ax.yaxis, ax.get_yscale())):
            if escala == 'linear' and type(eje.get_major_formatter()) is ScalarFormatter:
                eje.set_major_formatter(FuncFormatter(_coma))
    for ext in ('pdf', 'png'):
        fig.savefig(os.path.join(FIG, f'{nombre}.{ext}'), dpi=200,
                    bbox_inches='tight', facecolor='white')
    plt.close(fig)


def barras(ax, grupos, series, colores, etiquetas, fmt='{:.3f}'):
    x = np.arange(len(grupos))
    k = len(series)
    w = 0.8 / k
    for i, (vals, c, lab) in enumerate(zip(series, colores, etiquetas)):
        bars = ax.bar(x + (i - (k - 1) / 2) * w, vals, w * 0.92, color=c,
                      label=lab, zorder=3)
        for bb, v in zip(bars, vals):
            if v is None or np.isnan(v):
                continue
            ax.text(bb.get_x() + bb.get_width() / 2, v, ' ' + fmt.format(v).replace('.', ','),
                    ha='center', va='bottom', fontsize=6.8, color=TXT, rotation=90)
    ax.set_xticks(x, grupos)


SERIES5 = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4']


def fig_resumen(res):
    grupos = ['KG M50S20\nS45C', 'KG M50B20\nlatón', 'KG M50S25\nS45C',
              'RS PRO\n521-5780', 'A medida\ncarburizada']
    fig, axs = plt.subplots(2, 1, figsize=(9.2, 6.4), sharex=True)
    rn = DATOS['rpm_normal']
    barras(axs[0], grupos, [[res[k]['normal'][r]['T_adm'] for k in CLAVES] for r in rn],
           RAMPA[1:], [f'{fmt_rpm(r)} rpm' for r in rn])
    axs[0].set_title('Torque normal admisible (toda la vida)', loc='left', color=TXT, fontsize=10)
    barras(axs[1], grupos, [[res[k]['pico'][r]['T_adm'] for k in CLAVES] for r in DATOS['rpm']],
           RAMPA, [f'{fmt_rpm(r)} rpm' for r in DATOS['rpm']])
    axs[1].set_title('Torque de pico admisible (10 s, ocasional)', loc='left', color=TXT, fontsize=10)
    for ax in axs:
        estilo(ax, ylabel='Torque [N·m]')
        ax.legend(frameon=False, fontsize=7.5, ncol=4, loc='upper left')
    axs[0].set_ylim(0, max(res['CARB']['normal'][0.5]['T_adm'], 0.1) * 1.3)
    axs[1].set_ylim(0, res['CARB']['pico'][0]['T_adm'] * 1.3)
    fig.tight_layout()
    guardar(fig, 'fig_resumen')


def fig_modos(res):
    grupos = [INFO[k]['corto'] for k in CLAVES]
    tf = [res[k]['normal'][100]['T_F'] for k in CLAVES]
    th = [res[k]['normal'][100]['T_H'] for k in CLAVES]
    fig, ax = plt.subplots(figsize=(9.0, 3.4))
    barras(ax, grupos, [tf, th], SERIES[:2], ['Flexión alternada', 'Picado'])
    estilo(ax, ylabel='Torque [N·m]')
    ax.set_yscale('log')
    ax.set_ylim(0.02, 3)
    ax.legend(frameon=False, fontsize=8, ncol=2, loc='upper left')
    ax.tick_params(axis='x', labelsize=8)
    guardar(fig, 'fig_modos')


def fig_rpm():
    fig, axs = plt.subplots(1, 2, figsize=(9.2, 3.6))
    rpms = np.linspace(0.5, 200, 240)
    for i, k in enumerate(CLAVES):
        g, mat = GEO[k], MATERIALES[INFO[k]['mat']]
        tn = [capacidad(g, mat, r, N_eval(ciclos_normal(r)))['T_adm'] for r in rpms]
        tp = [capacidad(g, mat, r, N_eval(ciclos_pico(r)))['T_adm'] for r in rpms]
        axs[0].plot(rpms, tn, color=SERIES5[i], lw=1.8, label=INFO[k]['corto'])
        axs[1].plot(rpms, tp, color=SERIES5[i], lw=1.8, label=INFO[k]['corto'])
    axs[0].set_title('Torque normal', loc='left', color=TXT, fontsize=10)
    axs[1].set_title('Torque de pico (10 s)', loc='left', color=TXT, fontsize=10)
    for ax in axs:
        estilo(ax, 'Velocidad de la rueda [rpm]', 'Torque admisible [N·m]')
        ax.set_ylim(0, None)
    axs[1].legend(frameon=False, fontsize=7.5, loc='upper right')
    fig.tight_layout()
    guardar(fig, 'fig_rpm')


def fig_picos():
    fig, ax = plt.subplots(figsize=(8.6, 3.4))
    ph = np.logspace(-1, 2, 80)
    for i, k in enumerate(CLAVES):
        g, mat = GEO[k], MATERIALES[INFO[k]['mat']]
        t = [capacidad(g, mat, 100, N_eval(ciclos_pico(100, p * HORAS_VIDA)))['T_adm'] for p in ph]
        ax.plot(ph, t, color=SERIES5[i], lw=1.8, label=INFO[k]['corto'])
    ax.axvline(DATOS['picos_por_hora'], color='#b8b7b1', lw=1, ls='--')
    ax.text(DATOS['picos_por_hora'] * 1.08, 0.02, 'supuesto: 1 pico por hora',
            color=TXT2, fontsize=8)
    ax.set_xscale('log')
    estilo(ax, 'Picos de 10 s por hora de uso', 'Pico admisible a 100 rpm [N·m]')
    ax.set_ylim(0, None)
    ax.legend(frameon=False, fontsize=7.5, ncol=3, loc='upper right')
    guardar(fig, 'fig_picos')


def fig_ciclos():
    fig, axs = plt.subplots(1, 2, figsize=(9.0, 3.4), sharey=True)
    N = np.logspace(2, 10, 300)
    axs[0].plot(N, [Y_NT(n) for n in N], color=SERIES[0], lw=1.8)
    axs[1].plot(N, [Z_NT(n) for n in N], color=SERIES[0], lw=1.8)
    pts = [('normal 100 rpm', N_eval(ciclos_normal(100)), SERIES[1]),
           ('pico 100 rpm', N_eval(ciclos_pico(100)), SERIES[2]),
           ('pico 0 rpm', N_eval(ciclos_pico(0)), SERIES[3])]
    for ax, fn, tit in ((axs[0], Y_NT, r'Flexión  $Y_{NT}$ (Fig. 15-9)'),
                        (axs[1], Z_NT, r'Picado  $Z_{NT}$ (Fig. 15-8)')):
        for lab, n, c in pts:
            ax.plot([n], [fn(n)], 'o', ms=7, mfc='white', mec=c, mew=2, label=lab)
            ax.annotate(f'{fn(n):.2f}'.replace('.', ','), (n, fn(n)), xytext=(6, 4),
                        textcoords='offset points', fontsize=8, color=TXT)
        ax.set_xscale('log')
        estilo(ax, r'Ciclos de carga $N_L$')
        ax.set_title(tit, color=TXT, fontsize=10, loc='left')
    axs[0].set_ylabel('Factor de ciclos', color=TXT2)
    axs[1].legend(frameon=False, fontsize=8, loc='upper right')
    guardar(fig, 'fig_ciclos')


def fig_sensibilidad():
    mat = MATERIALES['S45C']
    N = N_eval(ciclos_normal(100))

    def T(**f):
        return capacidad(BASE, mat, 100, N, f=f)['T_adm']
    base = T()
    casos = [
        (r'$Z_{xc}$ 2,0 / 1,5 (coronado)', T(Z_xc=2.0), T(Z_xc=1.5)),
        (r'$K_{mb}$ 1,25 / 1,00 (entre apoyos)', T(K_mb=1.25), T(K_mb=1.0)),
        (r'$K_A$ 1,25 (choques de rueda) / 1,0', T(K_A=1.25), T(K_A=1.0)),
        (r'$R$ 0,99 / 0,95', T(R=0.99), T(R=0.95)),
        (r'$R$ 0,95 / 0,90', T(R=0.95), T(R=0.90)),
        (r'$Z_I$ 0,059 / 0,065', T(I=0.059) if False else None, None),
    ]
    # I y J viven en la geometría
    gI1, gI2 = dict(BASE, I=0.059), dict(BASE, I=0.065)
    casos[-1] = (r'$Z_I$ 0,059 / 0,065', capacidad(gI1, mat, 100, N)['T_adm'],
                 capacidad(gI2, mat, 100, N)['T_adm'])
    gJ1, gJ2 = dict(BASE, J=0.19), dict(BASE, J=0.21)
    casos.append((r'$Y_J$ 0,19 / 0,21', capacidad(gJ1, mat, 100, N)['T_adm'],
                  capacidad(gJ2, mat, 100, N)['T_adm']))
    t_hb = []
    for hb in (167, 200):
        m2 = dict(mat, sFlim=0.30 * hb + 14.48, sHlim=2.35 * hb + 162.89)
        t_hb.append(capacidad(BASE, m2, 100, N)['T_adm'])
    casos.append(('Dureza 167 / 200 HB', min(t_hb), max(t_hb)))
    gb = dict(BASE, b_ef=BASE['b'])
    casos.append(('Ancho 2,12 / 2,5 mm', base, capacidad(gb, mat, 100, N)['T_adm']))
    filas = sorted([(l, min(a, b), max(a, b)) for l, a, b in casos], key=lambda r: r[2] - r[1])
    fig, ax = plt.subplots(figsize=(8.4, 3.6))
    for i, (lab, lo, hi) in enumerate(filas):
        ax.barh(i, max(hi - lo, 1e-4), left=lo, height=0.55, color=SERIES[0], zorder=3)
        ax.text(lo, i, f'{lo:.3f} '.replace('.', ','), ha='right', va='center', fontsize=7.5)
        ax.text(hi, i, f' {hi:.3f}'.replace('.', ','), ha='left', va='center', fontsize=7.5)
    ax.axvline(base, color=TXT, lw=1.1)
    ax.text(base, -0.9, f'  caso base {base:.3f} N·m'.replace('.', ','), fontsize=8, va='center')
    ax.set_ylim(-1.3, len(filas) - 0.4)
    ax.set_yticks(range(len(filas)), [f[0] for f in filas], fontsize=8)
    estilo(ax, 'Torque normal admisible S45C a 100 rpm [N·m]')
    ax.grid(axis='y', visible=False)
    ax.set_xlim(base * 0.5, base * 1.55)
    guardar(fig, 'fig_sensibilidad')


def fig_geometria():
    g = BASE
    d, Re, b, m = g['d'], g['Re'], g['b'], g['m']
    r = d / 2
    k = (Re - b) / Re
    ha, hf = m, 1.25 * m
    A, rh, rb = 11.0, 4.0, 1.5
    P = np.array([r, r])
    n = np.array([-1.0, 1.0]) / math.sqrt(2)
    root_in, tip_in = k * P - n * hf * k, k * P + n * ha * k
    tip_out, root_out = P + n * ha, P - n * hf
    sup = [(root_in[0], rb), tuple(root_in), tuple(tip_in), tuple(tip_out),
           tuple(root_out), (root_out[0], rh), (A, rh), (A, rb)]
    inf = [(x, -y) for x, y in reversed(sup)]
    fig, ax = plt.subplots(figsize=(5.2, 5.2))
    ax.set_aspect('equal')
    ax.axis('off')
    for poly in (sup, inf):
        ax.add_patch(plt.Polygon(poly, closed=True, fc='#cde2fb', ec=SERIES[0], lw=1.1, zorder=2))
        ax.add_patch(plt.Polygon([(y, x) for x, y in poly], closed=True, fc='#fbdccd',
                                 ec=SERIES[1], lw=1.1, zorder=2))
    for s_ in (1, -1):
        ax.plot([0, r], [0, s_ * r], color=SERIES[0], lw=0.7, ls=':')
        ax.plot([0, s_ * r], [0, r], color=SERIES[1], lw=0.7, ls=':')
    ax.plot([-1.5, A + 1.5], [0, 0], color=TXT2, lw=0.7, ls='-.')
    ax.plot([0, 0], [-1.5, A + 1.5], color=TXT2, lw=0.7, ls='-.')
    ax.text(A + 1.6, 0, 'eje del piñón', fontsize=7.5, color=TXT2, va='center')
    ax.text(0, A + 1.8, 'eje de la corona', fontsize=7.5, color=TXT2, ha='center')
    ax.annotate('', xy=(r, -r - 1.6), xytext=(-r, -r - 1.6),
                arrowprops=dict(arrowstyle='<->', color=TXT, lw=0.7))
    ax.text(0, -r - 2.0, r'$d_e = 10$ mm', fontsize=8, ha='center', va='top')
    ax.annotate('', xy=(A, -r - 3.6), xytext=(0, -r - 3.6),
                arrowprops=dict(arrowstyle='<->', color=TXT, lw=0.7))
    ax.text(A / 2, -r - 4.0, r'$A = 11$ mm', fontsize=8, ha='center', va='top')
    ax.text(r * 0.42 + 1.1, -r * 0.42 + 1.1, f'$R_e = {Re:.2f}$ mm'.replace('.', '{,}'),
            fontsize=8, rotation=-45, ha='center', va='center')
    Pl = np.array([-r, r])
    nl = np.array([-1.0, -1.0]) / math.sqrt(2)
    ax.annotate(r'$b = 2{,}5$ mm', xy=tuple((Pl + k * Pl) / 2 + nl * 0.6),
                xytext=(-8.5, 3.0), fontsize=8,
                arrowprops=dict(arrowstyle='-', color=TXT2, lw=0.6))
    ax.text(-0.5, -0.5, 'O', fontsize=8, ha='right', va='top')
    ax.text(-8.5, -3.2, '$\\delta_1=\\delta_2=45°$\n$\\Sigma=90°$\n$m=0{,}5$ mm, $z=20$',
            fontsize=8, va='top')
    ax.text(A - 2.5, rh + 0.6, 'piñón', fontsize=8.5, color=SERIES[0], ha='center')
    ax.text(rh + 0.6, A - 2.5, 'corona', fontsize=8.5, color=SERIES[1], va='center')
    ax.set_xlim(-9, A + 5)
    ax.set_ylim(-r - 5.5, A + 2.5)
    guardar(fig, 'fig_geometria')


# ---------------------------------------------------------------------------
# 10. Principal
# ---------------------------------------------------------------------------
def main():
    os.makedirs(FIG, exist_ok=True)
    os.makedirs(RES, exist_ok=True)
    res = calcular_disenos()
    cota = {r: capacidad(BASE, MATERIALES['Latón C3604B'], r, N_eval(ciclos_normal(r)),
                         sHlim=COTA_BAJA['Latón C3604B'])['T_adm'] for r in DATOS['rpm_normal']}
    js = lambda d: {str(k): v for k, v in d.items()}  # noqa: E731
    salida = {
        'datos': DATOS, 'factores': FACT, 'horas_vida': HORAS_VIDA, 'n_picos': N_PICOS,
        'referencia': {'HB': HB_REF, 'sFlim': SFLIM_REF, 'sHlim': SHLIM_REF},
        'disenos': {k: dict(INFO[k], geo=GEO[k],
                            normal=js(res[k]['normal']), pico=js(res[k]['pico']))
                    for k in CLAVES},
        'cota_laton': js(cota),
        # Tablas KG a flexión (W): M50S20 1,5 W y M50S25 2,5 W a 100 rpm
        'kg': {'M50S20': 9549.7 * 1.5e-3 / 100, 'M50S25': 9549.7 * 2.5e-3 / 100},
        'prisionero': {'M2,5 en eje 3': prisionero(3.0, 85),
                       'M3 en eje 4': prisionero(4.0, 160)},
        'materiales': MATERIALES,
        'Y_Z': Y_Z(FACT['R']),
    }
    with open(os.path.join(RES, 'resultados.json'), 'w', encoding='utf-8') as fh:
        json.dump(salida, fh, ensure_ascii=False, indent=1)
    fig_resumen(res)
    fig_modos(res)
    fig_rpm()
    fig_picos()
    fig_ciclos()
    fig_sensibilidad()
    fig_geometria()

    print(f'Y_Z={Y_Z(FACT["R"]):.4f} picos={N_PICOS:.0f}')
    for k in CLAVES:
        g = GEO[k]
        print(f"== {INFO[k]['desc']}  d={g['d']} da={g['da']:.2f} Re={g['Re']:.2f} b_ef={g['b_ef']:.2f}")
        for reg in ('normal', 'pico'):
            for r, v in res[k][reg].items():
                print(f"   {reg:6s} {r:5g} N={v['N']:.2e} TF={v['T_F']:.4f} TH={v['T_H']:.4f}"
                      f" -> {v['T_adm']:.4f} {v['modo']} sFP={v['sFP']:.0f} ok={v['fluencia_ok']}")
    print(prisionero(3.0, 85), prisionero(4.0, 160))


if __name__ == '__main__':
    main()
