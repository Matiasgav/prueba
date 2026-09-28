#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Actuación de un paralelogramo elevador con tornillo de avance y biela de empuje.

Uso:
    python3 tools/paralelogramo.py      # escribe figuras/ y resultados.json

Geometría (pivote inferior de la biela en el origen, viga horizontal):
  * biela del paralelogramo de largo L, ángulo theta desde la horizontal;
  * punto de enganche A sobre esa biela a distancia a del pivote;
  * tuerca N sobre la viga, del lado del motor, a una altura -e bajo el pivote;
  * biela de empuje N-A de largo c, trabajando a compresión para subir.
La placa sube h = L sen(theta) y se mantiene paralela.

TODOS los valores de DATOS son supuestos de ejemplo: reemplazarlos por los reales.
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

DATOS = {
    'W': 10.0,        # N, peso sobre la placa (1 kg), supuesto
    'L': 100.0,       # mm, largo de las bielas del paralelogramo, supuesto
    'a': 25.0,        # mm, enganche de la biela de empuje desde el pivote
    'c': 60.0,        # mm, largo de la biela de empuje
    'e': 8.0,         # mm, altura del eje del tornillo bajo el pivote
    'th_min': 15.0,   # grados, placa abajo
    'th_max': 65.0,   # grados, placa arriba
    'n_motor': 6000,  # rpm del motor para el tiempo de subida
}
TORNILLOS = [  # nombre, paso [mm], rendimiento, autobloqueante
    ('Tr6×1 trapezoidal', 1.0, 0.30, True),
    ('M4×0,7 métrica', 0.7, 0.25, True),
    ('Bolas 6×1', 1.0, 0.90, False),
]

TXT, TXT2, GRID = '#0b0b0b', '#52514e', '#e4e3df'
SERIES = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9})


def estilo(ax, xl=None, yl=None, titulo=None):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'):
        ax.spines[s].set_color('#b8b7b1')
    ax.tick_params(colors=TXT2, labelsize=8.5)
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    if xl:
        ax.set_xlabel(xl, color=TXT2)
    if yl:
        ax.set_ylabel(yl, color=TXT2)
    if titulo:
        ax.set_title(titulo, loc='left', color=TXT, fontsize=10)


def guardar(fig, nombre):
    for ext in ('png', 'pdf'):
        fig.savefig(os.path.join(FIG, f'{nombre}.{ext}'), dpi=180, bbox_inches='tight',
                    facecolor='white')
    plt.close(fig)


# ---------------------------------------------------------------------------
# Cinemática y estática
# ---------------------------------------------------------------------------
def x_tuerca(th, d=DATOS):
    """Posición de la tuerca (mm) para el ángulo th (rad)."""
    a, c, e = d['a'], d['c'], d['e']
    return a * np.cos(th) + np.sqrt(c ** 2 - (a * np.sin(th) + e) ** 2)


def angulo_transmision(th, d=DATOS):
    """Ángulo entre la biela de empuje y la biela del paralelogramo (grados).
    90° es ideal; cerca de 0° o 180° hay punto muerto."""
    psi = np.arcsin((d['a'] * np.sin(th) + d['e']) / d['c'])
    return np.degrees(th + psi)


def estatica(d=DATOS, W=None):
    W = d['W'] if W is None else W
    th = np.radians(np.linspace(d['th_min'], d['th_max'], 400))
    h = d['L'] * np.sin(th)                       # mm
    T_piv = W * d['L'] * np.cos(th) / 1000        # N·m (trabajos virtuales)
    x = x_tuerca(th, d)
    dxdth = np.gradient(x, th)                    # mm/rad (negativo: la tuerca avanza al subir)
    F = W * d['L'] * np.cos(th) / np.abs(dxdth)   # N, fuerza axial en la tuerca
    return {'th': np.degrees(th), 'h': h, 'T_piv': T_piv, 'x': x, 'F': F,
            'mu': angulo_transmision(th, d), 'dxdth': dxdth}


def torque_motor(F, paso, eta):
    return F * paso / (2 * math.pi * eta) / 1000  # N·m


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------
def fig_esquema(d=DATOS):
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    ax.set_aspect('equal')
    ax.axis('off')
    L, a, c, e = d['L'], d['a'], d['c'], d['e']
    sep = 70.0
    for th_deg, alpha, ls in ((d['th_min'], 0.35, '--'), (40.0, 1.0, '-')):
        th = math.radians(th_deg)
        P1, P2 = np.array([0, 0]), np.array([sep, 0])
        Q1 = P1 + L * np.array([math.cos(th), math.sin(th)])
        Q2 = P2 + L * np.array([math.cos(th), math.sin(th)])
        ax.plot(*zip(P1, Q1), color=SERIES[0], lw=3, alpha=alpha, ls=ls)
        ax.plot(*zip(P2, Q2), color=SERIES[0], lw=3, alpha=alpha, ls=ls)
        ax.plot([Q1[0] - 10, Q2[0] + 30], [Q1[1], Q2[1]], color='#1a7f4b', lw=5, alpha=alpha,
                solid_capstyle='butt')
        A = P2 + a * np.array([math.cos(th), math.sin(th)])
        N = np.array([sep + float(x_tuerca(th, d)), -e])
        ax.plot(*zip(A, N), color=SERIES[1], lw=2.5, alpha=alpha, ls=ls)
        ax.add_patch(plt.Rectangle((N[0] - 6, -e - 4), 12, 8, color=SERIES[1], alpha=alpha))
    ax.add_patch(plt.Rectangle((-30, -e - 8), 260, 16, fc='#e9e8e4', ec='#b8b7b1', zorder=0))
    ax.plot([-25, 225], [-e, -e], color=TXT2, lw=1, ls='-.')
    ax.add_patch(plt.Rectangle((230, -e - 9), 26, 18, color='#333333'))
    ax.text(243, -e - 14, 'motor', ha='center', va='top', fontsize=8)
    ax.text(150, -e - 14, 'tornillo dentro de la viga', ha='center', va='top', fontsize=8,
            color=TXT2)
    ax.text(60, 95, 'placa (sube paralela)', fontsize=8, color='#1a7f4b')
    ax.text(10, 45, 'bielas del paralelogramo, L', fontsize=8, color=SERIES[0], rotation=38)
    ax.text(sep + 40, 8, 'biela de empuje c\n(compresión al subir)', fontsize=8, color=SERIES[1])
    ax.text(sep + 55, -e + 7, 'tuerca', fontsize=8, color=SERIES[1])
    ax.text(-28, 100, 'Línea llena: 40°. Línea cortada: posición baja.', fontsize=7.5,
            color=TXT2)
    ax.set_xlim(-35, 260)
    ax.set_ylim(-30, 110)
    guardar(fig, '01_esquema')


def fig_torque_pivote(d=DATOS):
    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    for i, W in enumerate((5, 10, 20)):
        s = estatica(d, W)
        ax.plot(s['th'], s['T_piv'], color=SERIES[i], lw=2, label=f'W = {W} N')
    estilo(ax, 'Ángulo de las bielas θ [°]', 'Torque en el pivote [N·m]',
           'Torque necesario en el pivote: T = W·L·cos θ (máximo con la placa abajo)')
    ax.axvspan(d['th_min'], d['th_min'] + 5, color='#fdf3e6', zorder=0)
    ax.text(d['th_min'] + 0.5, ax.get_ylim()[1] * 0.92, 'placa\nabajo', fontsize=8, color=TXT2,
            va='top')
    ax.legend(frameon=False, fontsize=8)
    guardar(fig, '02_torque_pivote')


def fig_fuerza_tuerca(d=DATOS):
    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    for i, a in enumerate((15, 25, 40)):
        dd = dict(d, a=a)
        s = estatica(dd)
        ax.plot(s['h'], s['F'], color=SERIES[i], lw=2, label=f'enganche a = {a} mm')
    estilo(ax, 'Altura de la placa h = L sen θ [mm]', 'Fuerza axial en la tuerca [N]',
           f'Fuerza en el tornillo (W = {d["W"]:g} N): más enganche, menos fuerza pero más carrera')
    ax.set_ylim(0, None)
    ax.legend(frameon=False, fontsize=8)
    guardar(fig, '03_fuerza_tuerca')


def fig_transmision(d=DATOS):
    fig, ax = plt.subplots(figsize=(7.6, 3.2))
    for i, e in enumerate((0, 8, 20)):
        dd = dict(d, e=e)
        s = estatica(dd)
        ax.plot(s['th'], s['mu'], color=SERIES[i], lw=2, label=f'e = {e} mm')
    ax.axhspan(0, 20, color='#fbe4e4', zorder=0)
    ax.axhspan(160, 180, color='#fbe4e4', zorder=0)
    ax.axhline(90, color=TXT2, lw=0.8, ls=':')
    ax.text(d['th_min'] + 0.5, 12, 'zona de punto muerto (< 20°)', fontsize=8, color='#a33')
    ax.text(d['th_max'] - 0.5, 92, 'ideal 90°', fontsize=8, color=TXT2, ha='right')
    estilo(ax, 'Ángulo de las bielas θ [°]', 'Ángulo de transmisión [°]',
           'Ángulo entre la biela de empuje y la del paralelogramo')
    ax.set_ylim(0, 180)
    ax.legend(frameon=False, fontsize=8, loc='lower right')
    guardar(fig, '04_angulo_transmision')


def fig_torque_motor(d=DATOS):
    s = estatica(d)
    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    for i, (nom, p, eta, auto) in enumerate(TORNILLOS):
        tm = torque_motor(s['F'], p, eta) * 1000
        ax.plot(s['h'], tm, color=SERIES[i], lw=2,
                label=f'{nom} (η = {eta:.2f}, {"autobloqueante" if auto else "NO autobloqueante"})')
    estilo(ax, 'Altura de la placa h [mm]', 'Torque en el motor [mN·m]',
           f'Torque del motor para subir W = {d["W"]:g} N, sin reductor')
    ax.set_ylim(0, None)
    ax.legend(frameon=False, fontsize=7.5)
    guardar(fig, '05_torque_motor')


def fig_resorte(d=DATOS):
    s = estatica(d)
    th = np.radians(s['th'])
    T = s['T_piv']
    # Resorte de torsión lineal T_r = k (th0 - th): ajuste por mínimos cuadrados
    A = np.vstack([np.ones_like(th), -th]).T
    coef, *_ = np.linalg.lstsq(A, T, rcond=None)
    Tr = A @ coef
    k = coef[1]
    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    ax.plot(s['th'], T * 1000, color=SERIES[0], lw=2, label='Sin resorte')
    ax.plot(s['th'], Tr * 1000, color=SERIES[2], lw=1.5, ls='--', label='Aporte del resorte')
    ax.plot(s['th'], (T - Tr) * 1000, color=SERIES[1], lw=2, label='Con resorte (neto)')
    ax.axhline(0, color=TXT2, lw=0.8)
    estilo(ax, 'Ángulo de las bielas θ [°]', 'Torque en el pivote [mN·m]',
           f'Compensación con resorte de torsión (k ≈ {k * 1000 / math.degrees(1):.1f} mN·m/°)')
    ax.legend(frameon=False, fontsize=8)
    guardar(fig, '06_resorte')
    return {'k_Nm_por_rad': float(k), 'T_max_sin': float(T.max()),
            'T_max_con': float(np.abs(T - Tr).max())}


def fig_tiempo(d=DATOS):
    s = estatica(d)
    carrera = float(abs(s['x'][-1] - s['x'][0]))
    fig, ax = plt.subplots(figsize=(7.6, 3.2))
    n = np.linspace(1000, 12000, 200)
    for i, (nom, p, eta, auto) in enumerate(TORNILLOS[:2]):
        t = carrera / (p * n / 60)
        ax.plot(n, t, color=SERIES[i], lw=2, label=f'{nom}')
    estilo(ax, 'Velocidad del motor [rpm]', 'Tiempo de subida [s]',
           f'Tiempo de subida completa (carrera de la tuerca {carrera:.1f} mm), sin reductor')
    ax.set_ylim(0, None)
    ax.legend(frameon=False, fontsize=8)
    guardar(fig, '07_tiempo')
    return carrera


def main():
    os.makedirs(FIG, exist_ok=True)
    fig_esquema()
    fig_torque_pivote()
    fig_fuerza_tuerca()
    fig_transmision()
    fig_torque_motor()
    res = fig_resorte()
    carrera = fig_tiempo()
    s = estatica()
    out = {
        'datos': DATOS,
        'T_pivote_max_Nm': float(s['T_piv'].max()),
        'F_tuerca_max_N': float(s['F'].max()),
        'mu_min_grados': float(s['mu'].min()),
        'mu_max_grados': float(s['mu'].max()),
        'carrera_tuerca_mm': carrera,
        'altura_mm': [float(s['h'][0]), float(s['h'][-1])],
        'torque_motor_max_mNm': {nom: float(torque_motor(s['F'], p, eta).max() * 1000)
                                 for nom, p, eta, _ in TORNILLOS},
        'resorte': res,
    }
    with open(os.path.join(ROOT, 'resultados.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
