#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Torque admisible de un par de engranajes cónicos rectos (mitra 1:1) KG
m = 0,5 mm, z = 20, según Shigley (cap. 15, método AGMA 2003 en unidades SI).

Uso:
    python3 tools/calculo.py          # escribe resultados/ y figuras/

Todas las hipótesis están en DATOS y MATERIALES; cada valor lleva su fuente.
Los metales se evalúan con las ecuaciones de esfuerzo de flexión y de contacto
de Shigley cap. 15. El POM queda fuera del alcance de AGMA y se evalúa con la
ecuación de Lewis (Shigley cap. 14) y con el método KHK para acetal.
"""
import json
import math
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, 'figuras')
RES = os.path.join(ROOT, 'resultados')

# ---------------------------------------------------------------------------
# 1. Datos del caso
# ---------------------------------------------------------------------------
DATOS = {
    'm': 0.5,            # módulo exterior (transversal) m_et, mm — catálogo KG
    'z': 20,             # dientes de piñón y corona (1:1)
    'phi': 20.0,         # ángulo de presión, grados — catálogo KG
    'b_cat': 2.5,        # ancho de cara del catálogo, mm — catálogo KG
    'sigma': 90.0,       # ángulo entre ejes, grados
    'horas_por_mes': 20,
    'anios': 10,         # vida de diseño supuesta (no dada en el pedido)
    'rpm': [0, 0.5, 50, 100],  # «0, 50» se lee también como 0,5 rpm
    'N_estatico': 1e4,   # aplicaciones de par a 0 rpm (arranques/retenciones)
    'T_amb': 40.0,       # °C, extremo superior del rango 30-40 °C
}

# Factores AGMA/Shigley adoptados (cap. 15). Ver informe §5.
FACT = {
    'K_A': 1.00,   # sobrecarga: motor uniforme (BLDC, perfil trapezoidal suave)
                   # y carga uniforme — tabla de factor de sobrecarga, Shigley 15
    'Q_v': 6,      # número de calidad de transmisión (conservador; JIS B1704 3-4)
    'K_mb': 1.25,  # montaje: ningún engranaje entre apoyos (en voladizo)
    'Z_xc': 2.0,   # coronamiento: dientes sin coronar (tallado estándar)
    'Y_beta': 1.0, # curvatura longitudinal: cónico recto
    'R': 0.99,     # confiabilidad
    'S_F': 1.0,    # factor de seguridad a flexión (capacidad nominal AGMA)
    'S_H': 1.0,    # factor de seguridad a picado
    'K_theta': 1.0,# temperatura <= 120 °C
    'Z_W': 1.0,    # relación de durezas: mismo material
    'J': 0.20,     # Y_J, Fig. 15-7 (20 dientes contra 20), lectura ±0,01
    'I': 0.062,    # Z_I, Fig. 15-6 (20 dientes contra 20), lectura ±0,003
}

# ---------------------------------------------------------------------------
# 2. Materiales
# ---------------------------------------------------------------------------
# Referencia: S45C sin tratamiento (KG: 熱処理 —). Dureza JIS G4051 normalizado
# 167–229 HB; se toma 170 HB (extremo bajo). Shigley Fig. 15-13/15-12, grado 1:
#   sigma_Flim = 0,30 HB + 14,48 MPa ; sigma_Hlim = 2,35 HB + 162,89 MPa
HB_REF = 170.0
SFLIM_REF = 0.30 * HB_REF + 14.48
SHLIM_REF = 2.35 * HB_REF + 162.89

MATERIALES = {
    'S45C': {
        'codigo': 'M50S20-1103 / M50S20*1103',
        'nombre': 'Acero S45C (sin tratamiento)',
        'E': 205e3, 'nu': 0.30, 'HB': HB_REF, 'Sy': 345.0,
        'rF': 1.0, 'rH': 1.0,
        'base_F': 'Shigley Fig. 15-13, acero templado total grado 1, 170 HB',
        'base_H': 'Shigley Fig. 15-12, acero templado total grado 1, 170 HB',
        # Catálogo KG, potencia admisible a flexión (W): 10 rpm 0,1; 100 rpm 1,5
        'kg_W': {10: 0.1, 100: 1.5, 200: 3.1, 400: 6.2, 600: 9.3,
                 800: 12.4, 1000: 15.5},
        'kg_base': 'JGMA 403-01 (cálculo)',
        'color': '#2a78d6',
    },
    'SUS304L MIM': {
        'codigo': 'M50SUM20*1103',
        'nombre': 'Inoxidable SUS304L inyectado (MIM)',
        'E': 190e3, 'nu': 0.29, 'HB': 120.0, 'Sy': 175.0,
        # KG, tabla «材質別 強度比較の目安»: MIM = 0,4 × S45C
        'rF': 0.40,
        # Contacto: resistencia hertziana proporcional a la dureza
        'rH': 120.0 / HB_REF,
        'base_F': 'KG: relación de resistencia MIM/S45C = 0,4 (catálogo p. 271)',
        'base_H': 'Dureza: 120 HB / 170 HB = 0,71 × S45C',
        'kg_W': {100: 0.5, 200: 1.1, 400: 2.2, 600: 3.3, 800: 4.4, 1000: 5.6},
        'kg_base': 'ensayo de durabilidad KG (cat. 2020) / JGMA (cat. 2022)',
        'color': '#eb6834',
    },
    'Latón C3604B': {
        'codigo': 'M50B20-1103 / M50B20*1103',
        'nombre': 'Latón de corte libre C3604B',
        'E': 100e3, 'nu': 0.34, 'HB': 100.0, 'Sy': 250.0,
        # Flexión: relación de límites de fatiga. C36000 H02 ≈ 138 MPa a 1e8
        # ciclos (Copper Development Association); S45C: S'e = 0,5·Sut
        # (Shigley ec. 6-8) con Sut = 570 MPa -> 285 MPa. 138/285 = 0,48.
        'rF': 138.0 / 285.0,
        'rH': 100.0 / HB_REF,
        'base_F': 'Fatiga: 138 MPa (C36000 H02) / 285 MPa (S45C) = 0,48',
        'base_H': 'Dureza: 100 HB / 170 HB = 0,59 × S45C',
        'kg_W': None,
        'kg_base': 'KG no publica potencia admisible para m0,5 en latón',
        'color': '#1baf7a',
    },
}

# Cotas inferiores alternativas (para el análisis de sensibilidad del informe)
COTA_BAJA = {
    'SUS304L MIM': {'rH': 0.40, 'motivo': 'aplicar 0,4 de KG también al contacto'},
    'Latón C3604B': {'rH': 207.0 / (2.22 * HB_REF + 200.0),
                     'motivo': 'bronce Sn (Shigley tabla 14-7) / acero 170 HB'},
}

# POM (acetal) inyectado negro M50DM20-1103 — método KHK (Lewis) para Duracon
POM = {
    'codigo': 'M50DM20-1103',
    'y_khk': 0.597,     # KHK tabla 11.5, 20°, z_v = 28,3 -> 28 dientes
    'Y_lewis': 0.353,   # Shigley tabla 14-2, 28 dientes
    # KHK Fig. 11.3, curva m 0,8 (la de menor módulo publicada), kgf/mm²
    'sb_curva': [(1.6e4, 5.65), (1e5, 5.05), (1e6, 4.45), (1e7, 4.0), (1e8, 3.65)],
    'K_T': 0.80,        # KHK Fig. 11.5 a 40 °C
    'K_L': 1.0,         # KHK tabla 11.8: engrase inicial
    'K_M': 0.75,        # KHK tabla 11.9: Duracon contra Duracon
    'C_S': 1.25,        # KHK tabla 11.7: carga uniforme, 24 h/día (20 h seguidas)
    'K_V_khk': 1.40,    # KHK Fig. 11.4 a v ≈ 0 m/s
    # Referencia KG: POM azul M80BP20-1604 (m0,8, b 3,7): 1,20 W a 100 rpm
    'kg_m08': {'m': 0.8, 'z': 20, 'b': 3.7, 'W100': 1.20},
    'color': '#eda100',
}

KGF = 9.80665  # N por kgf


# ---------------------------------------------------------------------------
# 3. Geometría
# ---------------------------------------------------------------------------
def geometria():
    m, z, b = DATOS['m'], DATOS['z'], DATOS['b_cat']
    d = m * z                                    # diámetro primitivo exterior
    delta = math.degrees(math.atan(z / z))       # ángulo de paso, 45°
    Re = d / (2 * math.sin(math.radians(delta)))  # distancia de cono exterior
    b_max = min(0.3 * Re, 10 * m)                # Shigley: F <= A0/3 y 10 m
    b_ef = min(b, b_max)
    dm = d - b * math.sin(math.radians(delta))   # primitivo medio
    zv = z / math.cos(math.radians(delta))       # dientes virtuales
    return {'d': d, 'delta': delta, 'Re': Re, 'b': b, 'b_max': b_max,
            'b_ef': b_ef, 'dm': dm, 'zv': zv, 'da': d + 2 * m *
            math.cos(math.radians(delta)), 'ratio_b_Re': b / Re}


G = geometria()


# ---------------------------------------------------------------------------
# 4. Factores de Shigley cap. 15 (SI)
# ---------------------------------------------------------------------------
def v_et(rpm):
    return math.pi * G['d'] * rpm / 60000.0      # m/s en el diámetro exterior


def K_v(rpm, Qv=None):
    Qv = FACT['Q_v'] if Qv is None else Qv
    B = 0.25 * (12 - Qv) ** (2 / 3)
    A = 50 + 56 * (1 - B)
    return ((A + math.sqrt(200 * v_et(rpm))) / A) ** B


def Y_x(m):
    return 0.5 if m < 1.6 else 0.4867 + 0.008339 * m


def Z_x(b):
    return 0.5 if b < 12.7 else 0.00492 * b + 0.4375


def K_Hb(b, Kmb=None):
    Kmb = FACT['K_mb'] if Kmb is None else Kmb
    return Kmb + 5.6e-6 * b ** 2


def Y_NT(N):
    """Fig. 15-9 (curva general)."""
    if N < 1e3:
        return 2.7
    if N < 3e6:
        return 6.1514 * N ** -0.1192
    return 1.6831 * N ** -0.0323


def Z_NT(N):
    """Fig. 15-8."""
    if N < 1e4:
        return 2.0
    return 3.4822 * N ** -0.0602


def Y_Z(R):
    if R >= 0.99:
        return 0.50 - 0.25 * math.log10(1 - R)
    return 0.70 - 0.15 * math.log10(1 - R)


def Z_E(E, nu):
    return math.sqrt(1 / (math.pi * 2 * (1 - nu ** 2) / E))


def ciclos(rpm):
    if rpm == 0:
        return DATOS['N_estatico']
    horas = DATOS['horas_por_mes'] * 12 * DATOS['anios']
    return rpm * 60 * horas


def ciclos_anios(rpm, anios):
    return rpm * 60 * DATOS['horas_por_mes'] * 12 * anios


# ---------------------------------------------------------------------------
# 5. Torque admisible de un metal
# ---------------------------------------------------------------------------
def torque_metal(mat, rpm, N=None, f=None, rF=None, rH=None, b=None):
    f = dict(FACT, **(f or {}))
    N = ciclos(rpm) if N is None else N
    b = G['b_ef'] if b is None else b
    rF = mat['rF'] if rF is None else rF
    rH = mat['rH'] if rH is None else rH
    m, d = DATOS['m'], G['d']
    Kv = K_v(rpm, f['Q_v'])
    KHb = K_Hb(b, f['K_mb'])
    YZ = Y_Z(f['R'])
    ZZ = math.sqrt(YZ)

    sFlim = SFLIM_REF * rF
    sHlim = SHLIM_REF * rH
    sFP = sFlim * Y_NT(N) / (f['S_F'] * f['K_theta'] * YZ)
    sHP = sHlim * Z_NT(N) * f['Z_W'] / (f['S_H'] * f['K_theta'] * ZZ)

    # Flexión: sigma_F = (W/b)(K_A K_v / m)(Y_x K_Hb / (Y_beta Y_J))
    W_F = sFP * b * m * f['Y_beta'] * f['J'] / (f['K_A'] * Kv * Y_x(m) * KHb)
    # Contacto: sigma_H = Z_E sqrt(W K_A K_v K_Hb Z_x Z_xc / (b d Z_I))
    ZE = Z_E(mat['E'], mat['nu'])
    W_H = (sHP / ZE) ** 2 * b * d * f['I'] / (f['K_A'] * Kv * KHb * Z_x(b)
                                              * f['Z_xc'])
    T_F = W_F * d / 2 / 1000.0   # N·m
    T_H = W_H * d / 2 / 1000.0
    return {
        'rpm': rpm, 'N': N, 'v_et': v_et(rpm), 'K_v': Kv, 'K_Hb': KHb,
        'Y_x': Y_x(m), 'Z_x': Z_x(b), 'Y_NT': Y_NT(N), 'Z_NT': Z_NT(N),
        'Y_Z': YZ, 'Z_Z': ZZ, 'Z_E': ZE, 'sFlim': sFlim, 'sHlim': sHlim,
        'sFP': sFP, 'sHP': sHP, 'W_F': W_F, 'W_H': W_H,
        'T_F': T_F, 'T_H': T_H, 'T_adm': min(T_F, T_H),
        'modo': 'flexión' if T_F <= T_H else 'picado',
        'T_F_alt': 0.70 * T_F,   # carga alternada (dos sentidos): 70 % flexión
    }


def torque_kg(mat, rpm_tab):
    """Torque equivalente de la tabla de potencia KG: T = 9549,7 P / n."""
    if not mat['kg_W']:
        return None
    return {n: 9549.7 * P / 1000.0 / n for n, P in mat['kg_W'].items()}


# ---------------------------------------------------------------------------
# 6. POM
# ---------------------------------------------------------------------------
def sb_pom(N):
    xs = [math.log10(p[0]) for p in POM['sb_curva']]
    ys = [p[1] for p in POM['sb_curva']]
    x = min(max(math.log10(max(N, 1)), xs[0]), xs[-1])
    return float(np.interp(x, xs, ys)) * KGF   # MPa


def torque_pom(rpm, N=None):
    N = ciclos(rpm) if N is None else N
    m, b, d = DATOS['m'], G['b'], G['d']
    fb = (G['Re'] - b) / G['Re']            # reducción cónica (Re - b)/Re
    KV = POM['K_V_khk'] if rpm > 0 else 1.0  # sin crédito de velocidad en estático
    s_adm = sb_pom(N) * KV * POM['K_T'] * POM['K_L'] * POM['K_M'] / POM['C_S']
    F_khk = m * POM['y_khk'] * b * s_adm * fb
    F_lew = m * POM['Y_lewis'] * b * s_adm * fb
    # Calibración con la tabla KG del POM azul m0,8: mismo método, escala
    # geométrica m·b·(Re-b)/Re·d
    k = POM['kg_m08']
    T08 = 9549.7 * k['W100'] / 1000.0 / 100.0
    d08 = k['m'] * k['z']
    Re08 = d08 / (2 * math.sin(math.radians(45)))
    g05 = m * b * fb * d
    g08 = k['m'] * k['b'] * (Re08 - k['b']) / Re08 * d08
    T_kgcal = T08 * g05 / g08
    # La tabla KG se supone referida a 1e7 ciclos (como la tabla de metales,
    # KG5001 p. 18); se corrige por la curva sigma_b(N). En estático no se da
    # el crédito de velocidad K_V que la tabla KG incorpora.
    T_kgcal *= sb_pom(N) / sb_pom(1e7)
    if rpm == 0:
        T_kgcal /= POM['K_V_khk']
    T_khk = F_khk * d / 2 / 1000
    T_lew = F_lew * d / 2 / 1000
    return {'rpm': rpm, 'N': N, 's_b': sb_pom(N), 's_adm': s_adm, 'fb': fb,
            'T_khk': T_khk, 'T_lewis': T_lew, 'T_kgcal': T_kgcal,
            'T_adm': min(T_khk, T_lew, T_kgcal), 'T08_kg': T08}


# ---------------------------------------------------------------------------
# 7. Tornillos prisioneros (verificación del cubo, Shigley tabla 7-4)
# ---------------------------------------------------------------------------
def prisionero():
    F = 85 * 4.44822   # #2 (Ø 2,18 mm, el más cercano por debajo de M2,5): 85 lbf
    D = 3.0            # eje Ø 3 mm
    return {'F': F, 'T_uno': F * D / 2 / 1000, 'n_S': 2.0,
            'T_seguro': F * D / 2 / 1000 / 2.0}


# ---------------------------------------------------------------------------
# 8. Figuras
# ---------------------------------------------------------------------------
TXT = '#0b0b0b'
TXT2 = '#52514e'
GRID = '#e4e3df'
SERIES = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100']


def fmt_rpm(r):
    return f'{r:g}'.replace('.', ',')


def estilo(ax, xlabel=None, ylabel=None):
    ax.set_facecolor('white')
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'):
        ax.spines[s].set_color('#b8b7b1')
    ax.tick_params(colors=TXT2, labelsize=9)
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    if xlabel:
        ax.set_xlabel(xlabel, color=TXT2, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, color=TXT2, fontsize=10)


def guardar(fig, nombre):
    for ext in ('svg', 'png'):
        fig.savefig(os.path.join(FIG, f'{nombre}.{ext}'), dpi=170,
                    bbox_inches='tight', facecolor='white')
    plt.close(fig)


def fig_resumen(res, pom):
    nombres = list(MATERIALES) + ['POM']
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    x = np.arange(len(nombres))
    w = 0.21
    rampa = ['#9ec5f4', '#5598e7', '#256abf', '#0d366b']  # secuencial: más rpm, más oscuro
    for i, rpm in enumerate(DATOS['rpm']):
        vals = [res[n][rpm]['T_adm'] for n in MATERIALES] + [pom[rpm]['T_adm']]
        bars = ax.bar(x + (i - 1.5) * w, vals, w - 0.02, color=rampa[i],
                      label=f'{fmt_rpm(rpm)} rpm', zorder=3)
        for bb, v in zip(bars, vals):
            ax.text(bb.get_x() + bb.get_width() / 2, v + 0.003, f'{v:.3f}',
                    ha='center', va='bottom', fontsize=6.8, color=TXT, rotation=90)
    ax.set_xticks(x, ['S45C', 'SUS304L\nMIM', 'Latón\nC3604B', 'POM\n(inyectado)'])
    estilo(ax, ylabel='Torque admisible por engranaje [N·m]')
    ax.set_ylim(0, 0.27)
    ax.legend(frameon=False, fontsize=9, ncol=4, loc='upper right')
    ax.set_title('Torque admisible (el menor entre flexión y picado)',
                 color=TXT, fontsize=11, loc='left')
    guardar(fig, 'fig_resumen')


def fig_modos(res):
    nombres = list(MATERIALES)
    fig, ax = plt.subplots(figsize=(8.6, 3.9))
    x = np.arange(len(nombres))
    w = 0.26
    tf = [res[n][100]['T_F'] for n in nombres]
    th = [res[n][100]['T_H'] for n in nombres]
    kg = [torque_kg(MATERIALES[n], None) for n in nombres]
    kg = [k[100] if k else 0 for k in kg]
    sets = [('Flexión (Shigley)', tf, SERIES[0]),
            ('Picado (Shigley)', th, SERIES[1]),
            ('Tabla KG a flexión', kg, SERIES[2])]
    for i, (lab, vals, c) in enumerate(sets):
        bars = ax.bar(x + (i - 1) * w, vals, w - 0.02, color=c, label=lab, zorder=3)
        for bb, v in zip(bars, vals):
            ax.text(bb.get_x() + bb.get_width() / 2, v + 0.003,
                    f'{v:.3f}' if v else 'sin dato', ha='center', va='bottom',
                    fontsize=7.5, color=TXT if v else TXT2)
    ax.set_xticks(x, ['S45C', 'SUS304L MIM', 'Latón C3604B'])
    estilo(ax, ylabel='Torque [N·m]')
    ax.set_ylim(0, 0.175)
    ax.legend(frameon=False, fontsize=9, ncol=3, loc='upper right')
    ax.set_title('100 rpm, 10 años: capacidad por modo de falla y valor del catálogo',
                 color=TXT, fontsize=11, loc='left')
    guardar(fig, 'fig_modos')


def fig_rpm(pom):
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    rpms = np.linspace(1, 200, 200)
    for i, (n, mat) in enumerate(MATERIALES.items()):
        t = [torque_metal(mat, r)['T_adm'] for r in rpms]
        ax.plot(rpms, t, color=SERIES[i], lw=2, label=n)
        kg = torque_kg(mat, None)
        if kg:
            pts = [(r, v) for r, v in kg.items() if 10 < r <= 200]
            ax.plot([p[0] for p in pts], [p[1] for p in pts], 'o', ms=8,
                    mfc='white', mec=SERIES[i], mew=2, label=f'{n}: tabla KG')
    t = [torque_pom(r)['T_adm'] for r in rpms]
    ax.plot(rpms, t, color=SERIES[3], lw=2, label='POM')
    for r in (50, 100):
        ax.axvline(r, color='#b8b7b1', lw=1, ls='--', zorder=0)
    estilo(ax, 'Velocidad [rpm]', 'Torque admisible [N·m]')
    ax.set_ylim(0, None)
    ax.legend(frameon=False, fontsize=8.5, ncol=3, loc='upper center',
              bbox_to_anchor=(0.5, -0.16))
    ax.set_title('Torque admisible en función de la velocidad (vida 10 años)',
                 color=TXT, fontsize=11, loc='left')
    guardar(fig, 'fig_rpm')


def fig_vida():
    fig, ax = plt.subplots(figsize=(8.6, 4.0))
    anios = np.linspace(0.5, 30, 120)
    for i, (n, mat) in enumerate(MATERIALES.items()):
        t = [torque_metal(mat, 100, N=ciclos_anios(100, a))['T_adm'] for a in anios]
        ax.plot(anios, t, color=SERIES[i], lw=2, label=n)
    t = [torque_pom(100, N=ciclos_anios(100, a))['T_adm'] for a in anios]
    ax.plot(anios, t, color=SERIES[3], lw=2, label='POM')
    ax.axvline(DATOS['anios'], color='#b8b7b1', lw=1, ls='--')
    ax.text(DATOS['anios'] + 0.3, 0.004, 'vida de diseño supuesta (10 años)',
            color=TXT2, fontsize=8.5, va='bottom')
    estilo(ax, 'Vida de servicio [años] (20 h por mes, 100 rpm)',
           'Torque admisible [N·m]')
    ax.set_ylim(0, None)
    ax.legend(frameon=False, fontsize=9, ncol=4, loc='upper center',
              bbox_to_anchor=(0.5, -0.16))
    ax.set_title('Sensibilidad a la vida supuesta', color=TXT, fontsize=11, loc='left')
    guardar(fig, 'fig_vida')


def fig_ciclos():
    fig, axs = plt.subplots(1, 2, figsize=(8.8, 3.6), sharey=True)
    N = np.logspace(3, 10, 300)
    axs[0].plot(N, [Y_NT(n) for n in N], color=SERIES[0], lw=2)
    axs[1].plot(N, [Z_NT(n) for n in N], color=SERIES[0], lw=2)
    marcas = [(r, ciclos(r)) for r in DATOS['rpm']]
    for ax, fn, tit in ((axs[0], Y_NT, 'Flexión  $K_L$ ($Y_{NT}$), Fig. 15-9'),
                        (axs[1], Z_NT, 'Picado  $C_L$ ($Z_{NT}$), Fig. 15-8')):
        for rpm, n in marcas:
            ax.plot([n], [fn(n)], 'o', ms=8, mfc='white', mec=SERIES[1], mew=2)
            off = (-8, -26) if rpm == 50 else (6, 6)
            ax.annotate(f'{fmt_rpm(rpm)} rpm\n{fn(n):.2f}', (n, fn(n)), xytext=off,
                        textcoords='offset points', fontsize=8, color=TXT,
                        ha='right' if rpm == 50 else 'left')
        ax.set_xscale('log')
        estilo(ax, 'Ciclos de carga $N_L$')
        ax.set_title(tit, color=TXT, fontsize=10, loc='left')
    axs[0].set_ylabel('Factor de ciclos', color=TXT2)
    guardar(fig, 'fig_ciclos')


def fig_sensibilidad():
    mat = MATERIALES['S45C']
    base = torque_metal(mat, 100)['T_adm']
    casos = [
        ('Y_J = J  0,19 / 0,21', {'J': 0.19}, {'J': 0.21}),
        ('Z_I = I  0,059 / 0,065', {'I': 0.059}, {'I': 0.065}),
        ('K_mb  1,25 / 1,00 (entre apoyos)', {'K_mb': 1.25}, {'K_mb': 1.00}),
        ('Z_xc  2,0 / 1,5 (coronado)', {'Z_xc': 2.0}, {'Z_xc': 1.5}),
        ('K_A  1,25 (choque leve) / 1,0', {'K_A': 1.25}, {'K_A': 1.0}),
        ('R  0,999 / 0,99', {'R': 0.999}, {'R': 0.99}),
    ]
    filas = []
    for lab, lo, hi in casos:
        a = torque_metal(mat, 100, f=lo)['T_adm']
        b = torque_metal(mat, 100, f=hi)['T_adm']
        filas.append((lab, min(a, b), max(a, b)))
    # dureza
    t_hb = []
    for hb in (167, 200):
        rF = (0.30 * hb + 14.48) / SFLIM_REF
        rH = (2.35 * hb + 162.89) / SHLIM_REF
        t_hb.append(torque_metal(mat, 100, rF=rF, rH=rH)['T_adm'])
    filas.append(('Dureza  167 / 200 HB', min(t_hb), max(t_hb)))
    tb = torque_metal(mat, 100, b=G['b'])['T_adm']
    filas.append(('Ancho  2,12 (0,3 Re) / 2,5 mm', min(base, tb), max(base, tb)))
    filas.sort(key=lambda r: r[2] - r[1])
    fig, ax = plt.subplots(figsize=(8.6, 3.9))
    for i, (lab, lo, hi) in enumerate(filas):
        ax.barh(i, hi - lo, left=lo, height=0.55, color=SERIES[0], zorder=3)
        ax.text(lo - 0.001, i, f'{lo:.3f}', ha='right', va='center', fontsize=8, color=TXT)
        ax.text(hi + 0.001, i, f'{hi:.3f}', ha='left', va='center', fontsize=8, color=TXT)
    ax.axvline(base, color=TXT, lw=1.2)
    ax.text(base, -0.75, f'  caso base {base:.3f} N·m', fontsize=8.5,
            color=TXT, va='center')
    ax.set_ylim(-1.1, len(filas) - 0.5)
    ax.set_yticks(range(len(filas)), [f[0] for f in filas], fontsize=8.5)
    estilo(ax, 'Torque admisible S45C a 100 rpm [N·m]')
    ax.grid(axis='y', visible=False)
    ax.set_xlim(base * 0.55, base * 1.6)
    ax.set_title('Sensibilidad del resultado a cada hipótesis (S45C, 100 rpm)',
                 color=TXT, fontsize=11, loc='left')
    guardar(fig, 'fig_sensibilidad')


def fig_geometria():
    """Corte axial esquemático del par a 90° con las cotas del catálogo KG."""
    d, Re, b, m = G['d'], G['Re'], G['b'], DATOS['m']
    r = d / 2
    k = (Re - b) / Re
    ha, hf = m, 1.25 * m
    A, rh, rb = 11.0, 4.0, 1.5     # distancia de montaje, radio de cubo y de agujero
    P = np.array([r, r])
    n = np.array([-1.0, 1.0]) / math.sqrt(2)   # hacia la punta (lejos del eje x)
    root_in, tip_in = k * P - n * hf * k, k * P + n * ha * k
    tip_out, root_out = P + n * ha, P - n * hf
    sup = [(root_in[0], rb), tuple(root_in), tuple(tip_in), tuple(tip_out),
           tuple(root_out), (root_out[0], rh), (A, rh), (A, rb)]
    inf = [(x, -y) for x, y in reversed(sup)]

    fig, ax = plt.subplots(figsize=(6.0, 6.0))
    ax.set_aspect('equal')
    ax.axis('off')
    for poly, c, fc in ((sup, SERIES[0], '#cde2fb'), (inf, SERIES[0], '#cde2fb')):
        ax.add_patch(plt.Polygon(poly, closed=True, fc=fc, ec=c, lw=1.2, zorder=2))
        # corona: misma sección reflejada respecto de la diagonal
        ax.add_patch(plt.Polygon([(y, x) for x, y in poly], closed=True,
                                 fc='#fbdccd', ec=SERIES[1], lw=1.2, zorder=2))
    for s_ in (1, -1):
        ax.plot([0, r], [0, s_ * r], color=SERIES[0], lw=0.8, ls=':', zorder=1)
        ax.plot([0, s_ * r], [0, r], color=SERIES[1], lw=0.8, ls=':', zorder=1)
    ax.plot([-1.5, A + 1.5], [0, 0], color=TXT2, lw=0.8, ls='-.')
    ax.plot([0, 0], [-1.5, A + 1.5], color=TXT2, lw=0.8, ls='-.')
    ax.text(A + 1.6, 0, 'eje del piñón', fontsize=8, color=TXT2, va='center')
    ax.text(0, A + 1.8, 'eje de la corona', fontsize=8, color=TXT2, ha='center')
    ax.annotate('', xy=(r, -r - 1.6), xytext=(-r, -r - 1.6),
                arrowprops=dict(arrowstyle='<->', color=TXT, lw=0.8))
    ax.plot([r, r], [-r, -r - 2], color=TXT2, lw=0.5)
    ax.text(0, -r - 2.0, f'd = {d:.0f} mm (primitivo exterior)', fontsize=8.5,
            color=TXT, ha='center', va='top')
    ax.annotate('', xy=(A, -r - 3.6), xytext=(0, -r - 3.6),
                arrowprops=dict(arrowstyle='<->', color=TXT, lw=0.8))
    ax.text(A / 2, -r - 4.0, f'A = {A:.0f} mm (distancia de montaje)', fontsize=8.5,
            color=TXT, ha='center', va='top')
    ax.text(r * 0.42 + 1.1, -r * 0.42 + 1.1, f'Re = {Re:.2f} mm', fontsize=8.5,
            color=TXT, rotation=-45, ha='center', va='center')
    Pl = np.array([-r, r])                 # diente izquierdo de la corona
    nl = np.array([-1.0, -1.0]) / math.sqrt(2)
    ax.annotate(f'b = {b} mm', xy=tuple((Pl + k * Pl) / 2 + nl * 0.6),
                xytext=(-8.5, 3.0), fontsize=8.5, color=TXT,
                arrowprops=dict(arrowstyle='-', color=TXT2, lw=0.6))
    ax.text(-0.5, -0.5, 'O', fontsize=9, color=TXT, ha='right', va='top')
    ax.text(-8.5, -3.2, 'δ₁ = δ₂ = 45°\nΣ = 90°\nm = 0,5 mm, z = 20\nφ = 20°',
            fontsize=8.5, color=TXT, va='top')
    ax.text(A - 2.5, rh + 0.6, 'piñón', fontsize=9, color=SERIES[0], ha='center')
    ax.text(rh + 0.6, A - 2.5, 'corona', fontsize=9, color=SERIES[1], va='center')
    ax.set_xlim(-9, A + 5)
    ax.set_ylim(-r - 5.5, A + 2.5)
    guardar(fig, 'fig_geometria')


# ---------------------------------------------------------------------------
# 9. Principal
# ---------------------------------------------------------------------------
def main():
    os.makedirs(FIG, exist_ok=True)
    os.makedirs(RES, exist_ok=True)
    res = {n: {r: torque_metal(m, r) for r in DATOS['rpm']}
           for n, m in MATERIALES.items()}
    pom = {r: torque_pom(r) for r in DATOS['rpm']}
    cota = {}
    for n, c in COTA_BAJA.items():
        cota[n] = {r: torque_metal(MATERIALES[n], r, rH=c['rH'])['T_adm']
                   for r in DATOS['rpm']}
    salida = {
        'datos': DATOS, 'factores': FACT, 'geometria': G,
        'referencia': {'HB': HB_REF, 'sFlim': SFLIM_REF, 'sHlim': SHLIM_REF},
        'metales': {n: {str(r): v for r, v in d.items()} for n, d in res.items()},
        'kg': {n: torque_kg(m, None) for n, m in MATERIALES.items()},
        'pom': {str(r): v for r, v in pom.items()},
        'cota_baja': {n: {str(r): v for r, v in d.items()} for n, d in cota.items()},
        'prisionero': prisionero(),
        'materiales': {n: {k: v for k, v in m.items() if k != 'color'}
                       for n, m in MATERIALES.items()},
    }
    with open(os.path.join(RES, 'resultados.json'), 'w', encoding='utf-8') as fh:
        json.dump(salida, fh, ensure_ascii=False, indent=1)

    fig_resumen(res, pom)
    fig_modos(res)
    fig_rpm(pom)
    fig_vida()
    fig_ciclos()
    fig_sensibilidad()
    fig_geometria()

    print(f"Geometría: d={G['d']} Re={G['Re']:.3f} b_ef={G['b_ef']:.3f} "
          f"dm={G['dm']:.3f} zv={G['zv']:.2f}")
    print(f"Ref S45C {HB_REF} HB: sFlim={SFLIM_REF:.1f} sHlim={SHLIM_REF:.1f}")
    for n, d in res.items():
        for r, v in d.items():
            print(f"{n:14s} {r:5g} rpm N={v['N']:.2e} Kv={v['K_v']:.4f} "
                  f"YNT={v['Y_NT']:.3f} ZNT={v['Z_NT']:.3f} ZE={v['Z_E']:.1f} "
                  f"sFP={v['sFP']:.1f} sHP={v['sHP']:.1f} TF={v['T_F']:.4f} "
                  f"TH={v['T_H']:.4f} -> {v['T_adm']:.4f} ({v['modo']}) "
                  f"alt={min(v['T_F_alt'], v['T_H']):.4f}")
    for r, v in pom.items():
        print(f"POM {r:5g} rpm N={v['N']:.2e} sb={v['s_b']:.1f} sadm={v['s_adm']:.1f} "
              f"Tkhk={v['T_khk']:.4f} Tlew={v['T_lewis']:.4f} Tkg={v['T_kgcal']:.4f}")
    for n, m in MATERIALES.items():
        print(n, 'KG:', torque_kg(m, None))
    print('cota baja', cota)
    print('prisionero', prisionero())


if __name__ == '__main__':
    main()
