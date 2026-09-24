#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Energia util, sensibilidad y velocidad de impacto a partir de las curvas.

Lee data_curvas.json (salida de digitalizar_curvas.py) y produce:
  - data_resultados.json : tabla de resultados por candidato
  - figuras/*.png        : graficos del informe

Definiciones (x = distancia al tope magnetico, x = 0 es el embolo asentado):
  W_util   = integral de F(x) entre x_imp y x_ini   (trabajo magnetico estatico)
  x_imp    = 0.5 mm: el impacto ocurre antes de que el embolo llegue al tope
  S_0.1    = F(x_imp) * 0.1 mm / W_util: variacion relativa de energia si la
             posicion de la cuna cambia 0.1 mm
  v        = sqrt(2 * eta * W_util / m), eta = fraccion convertida en energia
             cinetica (1 = cota superior estatica)
"""
import json
import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, 'figuras')
X_IMP = 0.5
M_PUNTA = 1.0e-3   # masa de punta de impacto supuesta [kg]

# (clave en json, curva, x_ini [mm], masa movil [g] o None, etiqueta corta)
CANDIDATOS = [
    ('Geeplus 141C', '10% ED', 3.0, 2.5, '141C'),
    ('Takaha CA0422', '24 W (6% ED)', 3.0, None, 'CA0422'),
    ('Geeplus 110C', '10% ED', 2.0, 1.0, '110C'),
    ('Takaha CA0425', '24 W (6% ED)', 3.0, None, 'CA0425'),
    ('Geeplus 144C', '10% ED', 3.5, 3.0, '144C'),
    ('Kendrion BI 13', '7 W (25% ED)', 3.0, 6.0, 'BI 13'),
    ('Ledex B12', '13 W (10% ED)', 3.0, 1.4, 'B12 (10%)'),
    ('Ledex B12', '5.2 W (25% ED)', 2.54, 1.4, 'B12P-255 (25%)'),
    ('MSA 312', '40 W (10% pulso)', 3.0, 7.0, 'MSA 312'),
    ('Transmotec K0420S', '10 W (10% ED)', 3.0, None, 'K0420S'),
    ('Geeplus RD-A420', '11 W (10% ED)', 3.0, 2.0, 'RD-A420'),
]
# Embolo sin dato: acero phi 4 mm x ~20 mm (CA04xx) o phi 3 x ~16 (K0420S)
MASA_ESTIMADA = {'CA0422': 2.0, 'CA0425': 2.2, 'K0420S': 1.0}


def curva(data, modelo, clave):
    p = sorted(data[modelo][clave])
    x = np.array([q[0] for q in p])
    f = np.array([q[1] for q in p])
    # quitar duplicados en x
    x, idx = np.unique(np.round(x, 4), return_index=True)
    return x, f[idx]


def integral(x, f, a, b):
    xs = np.linspace(a, b, 400)
    return float(np.trapezoid(np.interp(xs, x, f), xs))


def main():
    data = json.load(open(os.path.join(ROOT, 'data_curvas.json')))
    res = []
    for modelo, clave, x0, m, et in CANDIDATOS:
        x, f = curva(data, modelo, clave)
        xmin = x.min()
        w_util = integral(x, f, X_IMP, x0)
        w_tope = integral(x, f, max(xmin, 0.0), x0)
        f_imp = float(np.interp(X_IMP, x, f))
        f_ini = float(np.interp(x0, x, f))
        masa = m if m is not None else MASA_ESTIMADA[et]
        mt = masa * 1e-3 + M_PUNTA
        res.append(dict(
            modelo=modelo, curva=clave, etiqueta=et, x_ini=x0,
            x_min_dato=round(float(xmin), 2),
            W_util_mJ=round(w_util, 2), W_hasta_tope_mJ=round(w_tope, 2),
            frac_ultimo_medio_mm=round(1 - w_util / w_tope, 2) if xmin < 0.3 else None,
            F_imp_N=round(f_imp, 2), F_ini_N=round(f_ini, 2),
            relacion_F=round(f_imp / f_ini, 1),
            S_01=round(f_imp * 0.1 / w_util * 100, 1),
            masa_g=masa, masa_estimada=m is None,
            v_max=round((2 * w_util * 1e-3 / mt) ** 0.5, 2),
            v_4mJ=round((2 * 4e-3 / mt) ** 0.5, 2)))
    json.dump(res, open(os.path.join(ROOT, 'data_resultados.json'), 'w'),
              indent=1, ensure_ascii=False)
    for r in res:
        print(f"{r['etiqueta']:16s} W={r['W_util_mJ']:5.2f} mJ (tope {r['W_hasta_tope_mJ']:5.2f})"
              f"  F {r['F_ini_N']:.2f}->{r['F_imp_N']:.2f} N  ratio {r['relacion_F']}"
              f"  S={r['S_01']}%/0.1mm  vmax={r['v_max']} v4={r['v_4mJ']}")
    figuras(data, res)


# ---------------------------------------------------------------- figuras
INK, SEC, MUT, GRID = '#16202b', '#52514e', '#8a8880', '#e4e6ea'
S1, S2 = '#2a78d6', '#eb6834'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                     'axes.edgecolor': MUT, 'axes.labelcolor': SEC,
                     'xtick.color': SEC, 'ytick.color': SEC,
                     'axes.spines.top': False, 'axes.spines.right': False})


def figuras(data, res):
    # 1) pequenos multiplos F-x con la ventana util sombreada
    orden = [r for r in res if r['etiqueta'] != 'B12P-255 (25%)']
    fig, axs = plt.subplots(2, 5, figsize=(11, 4.9), sharex=True)
    for ax, r in zip(axs.flat, orden):
        x, f = curva(data, r['modelo'], r['curva'])
        sel = x <= 5.0
        ax.plot(x[sel], f[sel], color=S1, lw=2)
        xs = np.linspace(X_IMP, r['x_ini'], 100)
        ax.fill_between(xs, 0, np.interp(xs, x, f), color=S1, alpha=0.18, lw=0)
        ax.axvline(X_IMP, color=S2, lw=1.2, ls=(0, (3, 2)))
        ax.set_title(f"{r['etiqueta']}\n{r['curva']}", fontsize=8.5, color=INK, loc='left')
        ax.text(0.97, 0.93, f"{r['W_util_mJ']:.1f} mJ", transform=ax.transAxes,
                ha='right', va='top', fontsize=10, fontweight='bold', color=INK)
        ax.set_ylim(0, max(4.2, min(14, float(np.interp(0.4, x, f)) * 1.15)))
        ax.set_xlim(0, 5)
        ax.grid(color=GRID, lw=0.6)
        ax.set_axisbelow(True)
    for ax in axs[1]:
        ax.set_xlabel('distancia al tope x [mm]')
    for ax in axs[:, 0]:
        ax.set_ylabel('fuerza [N]')
    fig.suptitle('Área útil bajo la curva fuerza–carrera (sombreado: desde la carrera inicial hasta '
                 'x = 0,5 mm, donde se produce el impacto)', fontsize=10, color=INK, x=0.01, ha='left')
    fig.text(0.01, 0.005, 'Fuente: curvas extraídas de las hojas de datos de cada fabricante '
             '(Kendrion: recta entre fuerza inicial y final; MSA: tabla). Línea naranja: punto de impacto.',
             fontsize=7.5, color=MUT)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(os.path.join(FIG, 'fig-curvas.png'), dpi=200)
    plt.close(fig)

    # 2) barras de energia util vs objetivo
    rs = sorted(res, key=lambda r: r['W_util_mJ'])
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    y = np.arange(len(rs))
    ax.set_ylim(-1.1, len(rs) - 0.5)
    ax.axvspan(3, 5, color='#1baf7a', alpha=0.15, lw=0)
    ax.text(4, -0.75, 'objetivo 3–5 mJ', ha='center', va='center', fontsize=8, color=SEC)
    ax.barh(y, [min(r['W_util_mJ'], 12) for r in rs], height=0.62, color=S1,
            edgecolor='white', linewidth=2)
    for i, r in enumerate(rs):
        v = r['W_util_mJ']
        ax.text(min(v, 12) + 0.15, i, f"{v:.1f}" + (' →' if v > 12 else ''),
                va='center', fontsize=8.5, color=INK)
    ax.set_yticks(y, [f"{r['etiqueta']}  ·  {r['curva']}" for r in rs], fontsize=8)
    ax.set_xlim(0, 13.5)
    ax.set_xlabel('trabajo magnético estático entre x_ini y x = 0,5 mm [mJ]')
    ax.grid(axis='x', color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.set_title('Energía disponible sin llegar al tope interno', loc='left', color=INK, fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, 'fig-energia.png'), dpi=200)
    plt.close(fig)

    # 3) forma de la curva: F(x)/F(x_ini) para los cinco primeros
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    sel = [('141C', S1), ('CA0422', S2), ('110C', '#1baf7a')]
    for et, col in sel:
        r = next(q for q in res if q['etiqueta'] == et)
        x, f = curva(data, r['modelo'], r['curva'])
        xs = np.linspace(X_IMP, r['x_ini'], 200)
        ax.plot(xs, np.interp(xs, x, f) / r['F_ini_N'], color=col, lw=2)
        ax.text(X_IMP - 0.05, float(np.interp(X_IMP, x, f)) / r['F_ini_N'], et,
                ha='right', va='center', fontsize=8.5, color=INK)
    ax.axhline(1, color=MUT, lw=0.8)
    ax.set_xlim(0, 3.1)
    ax.set_xlabel('distancia al tope x [mm]')
    ax.set_ylabel('F(x) / F(x_ini)')
    ax.grid(color=GRID, lw=0.6)
    ax.set_title('Qué tan plana es la curva: fuerza relativa a la del inicio de carrera',
                 loc='left', color=INK, fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, 'fig-forma.png'), dpi=200)
    plt.close(fig)


if __name__ == '__main__':
    main()
