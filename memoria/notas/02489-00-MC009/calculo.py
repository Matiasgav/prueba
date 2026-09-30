#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometría de ranuras estatóricas en generadores de 20 MW o más (02489-00-MC009).

Qué calcula
    Para cada máquina: paso de ranura en el diámetro interior
    tau_s = pi * D_i / Q_s, relación k_s = b_s / tau_s, diente en el diámetro
    interior b_t = tau_s - b_s y ranuras por polo y fase q = Q_s / (3 P).
    Después arma el rango observado (mínimo y máximo) por tipo, hidro y turbo.
    No se extrapola nada.

De dónde salen los datos
    Máquinas reales publicadas (fuente en cada fila; páginas en fuentes/ cuando
    se pudieron bajar) y, cuando se sumen, las relevadas por Mecanalisis.
    Los diseños teóricos no se cargan: no son máquinas instaladas.

Datos que no entran en algún rango (clave 'excluir')
    - QFSN-600-2YHG: la fuente da «stator slot dimensions 160*70» como
      parámetro de un modelo de elementos finitos, sin rotular. 70 mm no se
      toma como ancho de ranura real.
    - CB 870/300-28: el «radio interior» publicado, 7909,9 mm, da D_i = 15,8 m,
      incompatible con 28 polos a 50 Hz (177 m/s en el diámetro interior) y con
      su diente (115 mm). Se usa su ancho y su Q_s, no su paso.
"""
import json
import math
import pathlib

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

AQUI = pathlib.Path(__file__).resolve().parent

M = [
    # ---------------- HIDRO ----------------
    dict(tipo='hidro', id='H2', maq='Bulbo', pot='34 MW', P=44, Qs=264, Di=5620, bs=28.0, hs=None,
         fuente='Zhen et al., Arch. Electr. Eng. 74 (2025)'),
    dict(tipo='hidro', id='H6', maq='Generador-motor de bombeo', pot='145 MW', P=30, Qs=360, Di=7240,
         bs=24.5, hs=159.5, fuente='Zhang et al., Machines 11 (2023) 901'),
    dict(tipo='hidro', id='H3', maq='Caso 1 (bobinas)', pot='95,5 MVA', P=84, Qs=432, Di=None, bs=24.76,
         hs=None, fuente='Sanosian et al. (Stantec)'),
    dict(tipo='hidro', id='H4', maq='Caso 2 (barras Roebel)', pot='95,5 MVA', P=84, Qs=576, Di=None,
         bs=23.19, hs=None, fuente='Sanosian et al. (Stantec)'),
    dict(tipo='hidro', id='H5', maq='Manic-2', pot='122,6 MVA', P=60, Qs=504, Di=10617.2, bs=23.24,
         hs=159, fuente='Aguiar et al., IECON 2013'),
    dict(tipo='hidro', id='H7', maq='Gezhouba SF150-96/15600', pot='150 MW', P=96, Qs=None, Di=None,
         bs=30.0, hs=None, fuente='Detección de cuñas, Gezhouba'),
    dict(tipo='hidro', id='H8', maq='CB 870/300-28', pot='250 MW', P=28, Qs=348, Di=15819.8, bs=27.9,
         hs=209.9, excluir=('tau', 'ks'), fuente='Carunaiselvane et al., PEDES 2018'),
    dict(tipo='hidro', id='H9', maq='Itaipú', pot='700 MW', P=None, Qs=504, Di=16000, bs=None, hs=None,
         fuente='Descargas parciales en Itaipú'),
    dict(tipo='hidro', id='H10', maq='Hidro 1000 MW', pot='1000 MW', P=54, Qs=810, Di=16300, Di_alt=17500,
         bs=None, hs=None, fuente='Processes 11 (2023) 899'),
    dict(tipo='hidro', id='H11', maq='Hidro 1000 MW', pot='1000 MW', P=56, Qs=696, Di=16580, bs=None,
         hs=None, fuente='Estudio de tiro magnético, 2024'),
    dict(tipo='hidro', id='H1', maq='Westinghouse Canadá (1958)', pot='28 MVA', P=14, Qs=162, Di=None,
         bs=None, hs=None, fuente='Chichkin, Iris 2019'),
    # ---------------- TURBO ----------------
    dict(tipo='turbo', id='T2', maq='QFSN-600-2YHG', pot='667 MVA', P=2, Qs=42, Di=1316, bs=70.0, hs=160,
         excluir=('bs', 'ks', 'hs'), fuente='Jiang et al., Int. J. Rot. Mach. 2021'),
    dict(tipo='turbo', id='T3', maq='Turbo 1000 MW', pot='1000 MW', P=2, Qs=36, Di=1471, bs=None, hs=160,
         fuente='Wang, WSEAS 2015'),
    dict(tipo='turbo', id='T1', maq='Turbo 247 MVA', pot='247 MVA', P=2, Qs=60, Di=None, bs=None, hs=None,
         fuente='Hanic et al., IET EPA 2014'),
    # Máquinas relevadas por Mecanalisis: agregar aquí (tipo, Qs, Di, bs, hs...).
]


def paso(Di, Qs):
    return math.pi * Di / Qs if Di and Qs else None


for m in M:
    m.setdefault('excluir', ())
    m['tau'] = paso(m['Di'], m['Qs'])
    m['tau_alt'] = paso(m.get('Di_alt'), m['Qs'])
    m['ks'] = m['bs'] / m['tau'] if m['bs'] and m['tau'] else None
    m['bt'] = m['tau'] - m['bs'] if m['bs'] and m['tau'] else None
    m['q'] = m['Qs'] / (3 * m['P']) if m['Qs'] and m['P'] else None


def rango(tipo, clave):
    v = []
    for m in M:
        if m['tipo'] != tipo or clave in m['excluir']:
            continue
        if m[clave] is not None:
            v.append(m[clave])
        if clave == 'tau' and m['tau_alt']:
            v.append(m['tau_alt'])
    return [min(v), max(v), len(v)] if v else None


R = {t: {c: rango(t, c) for c in ('bs', 'tau', 'ks', 'Qs', 'hs')} for t in ('hidro', 'turbo')}

# Controles de coherencia de CB 870/300-28 (28 polos, 50 Hz -> 214,3 rpm)
cb = next(m for m in M if m['id'] == 'H8')
rpm = 120 * 50 / cb['P']
control_cb = dict(rpm=rpm, v_Di_15820=math.pi * 15.8198 * rpm / 60,
                  v_Di_7910=math.pi * 7.9099 * rpm / 60,
                  bt_Di_15820=cb['bt'], bt_Di_7910=paso(7909.9, cb['Qs']) - cb['bs'])

(AQUI / 'resultados.json').write_text(
    json.dumps({'maquinas': M, 'rangos': R, 'control_cb': control_cb}, indent=2, ensure_ascii=False),
    encoding='utf-8')

for m in M:
    f = lambda x, d=1: '—' if x is None else f'{x:.{d}f}'
    print(f"{m['id']:4} Qs={m['Qs']} Di={m['Di']} bs={m['bs']} tau={f(m['tau'],2)} "
          f"tau_alt={f(m['tau_alt'],2)} ks={f(m['ks'] and 100*m['ks'])}% bt={f(m['bt'])} q={f(m['q'],3)}")
for t in R:
    print(t, {k: v and [round(v[0], 3), round(v[1], 3), v[2]] for k, v in R[t].items()})
print('CB', {k: round(v, 1) for k, v in control_cb.items()})

# ---------------------------------------------------------------- figura
AZUL, VERDE, TINTA, GRIS = '#2a78d6', '#1baf7a', '#1E2328', '#6B7280'
fig, ax = plt.subplots(figsize=(6.4, 3.0))
for k in (0.2, 0.3, 0.4, 0.5):
    ax.plot([0, 160], [0, 160 * k], color='#DADDE1', lw=0.8, zorder=0)
    x = min(150, 48 / k)
    ax.text(x, x * k + 0.8, f'{int(k*100)} %', color=GRIS, fontsize=7, ha='right', va='bottom')
DESPL = {'H2': (6, 3, 'left'), 'H6': (-6, -2, 'right'), 'H5': (6, -9, 'left')}
puntos = [m for m in M if m['bs'] and m['tau'] and 'ks' not in m['excluir']]
for m in puntos:
    c, mk = (AZUL, 'o') if m['tipo'] == 'hidro' else (VERDE, 's')
    ax.scatter(m['tau'], m['bs'], s=46, marker=mk, color=c, edgecolor='white', linewidth=1.5, zorder=3)
    dx, dy, ha = DESPL.get(m['id'], (6, 4, 'left'))
    ax.annotate(f"{m['id']} ({m['pot']})", (m['tau'], m['bs']), xytext=(dx, dy),
                textcoords='offset points', fontsize=7.5, color=TINTA, ha=ha)
if any(m['tipo'] == 'hidro' for m in puntos):
    ax.scatter([], [], marker='o', color=AZUL, label='Hidrogenerador')
if any(m['tipo'] == 'turbo' for m in puntos):
    ax.scatter([], [], marker='s', color=VERDE, label='Turbogenerador')
ax.set_xlim(40, 160); ax.set_ylim(0, 50)
ax.set_xlabel(r'Paso de ranura en el diámetro interior $\tau_s$ [mm]', color=TINTA, fontsize=9)
ax.set_ylabel(r'Ancho de ranura $b_s$ [mm]', color=TINTA, fontsize=9)
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
for s in ('left', 'bottom'):
    ax.spines[s].set_color(GRIS)
ax.tick_params(colors=GRIS, labelsize=8)
ax.legend(fontsize=7.5, frameon=False, loc='upper left')
fig.tight_layout()
(AQUI / 'figuras').mkdir(exist_ok=True)
fig.savefig(AQUI / 'figuras/bs-vs-paso.pdf')
