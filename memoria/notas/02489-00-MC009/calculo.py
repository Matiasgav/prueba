#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometría de ranuras estatóricas en generadores de 20 MW o más (02489-00-MC009).

Qué calcula
    Para cada máquina de la base: paso de ranura en el diámetro interior
    tau_s = pi * D_i / Q_s, relación k_s = b_s / tau_s, ancho de diente en el
    diámetro interior b_t = tau_s - b_s, y ranuras por polo y fase q = Q_s / (3 P).
    Después arma los rangos por tipo (hidro / turbo) y por nivel de evidencia.

De dónde salen los datos
    Todos los valores son los publicados en cada fuente, copiados tal cual
    (los PDF leídos están en fuentes/). Se clasifican así:

    A  Máquina real (o tipo real) con la fuente primaria leída en esta nota.
    B  Máquina real, pero la fuente no pudo abrirse (ResearchGate, IEEE, Scribd
       bloqueados). El dato viene del material de partida o del resumen de un
       buscador; NO está verificado contra el texto original.
    D  Diseño propuesto o modelo de cálculo, no una máquina instalada. Se lista
       aparte y NO entra en los rangos comprobados.

    No se extrapola nada: los rangos son mínimo y máximo de lo publicado.

Qué se interpreta (marcado en 'nota')
    - QFSN-600-2YHG: la fuente da «stator slot dimensions 160*70» sin decir cuál
      es el ancho. Se toma 70 mm como ancho porque 160 mm supera el paso.
    - CB 870/300-28: el material de partida da «radio interior 7909,9 mm». Con
      ese radio (D_i = 15 820 mm) la velocidad periférica sería 177 m/s; con
      7909,9 mm como diámetro, 89 m/s. Se calculan las dos y se excluye de los
      rangos de paso y k_s hasta ver el paper.
    - Hidro 1000 MW (Processes 2023): la tabla da D_i = 17 500 mm y
      D_e = 16 300 mm (interior mayor que exterior). Se calculan las dos.
"""
import json
import math
import pathlib

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

AQUI = pathlib.Path(__file__).resolve().parent

# tipo, id, máquina, potencia, P (polos), Qs, Di [mm], bs [mm], hs [mm], rpm, nivel, fuente, nota
M = [
    # ---------------- HIDRO ----------------
    dict(tipo='hidro', id='H1', maq='Bulbo (tubular), no identificada', pot='34 MW', P=44, Qs=264,
         Di=5620, bs=28.0, hs=None, rpm=None, nivel='A',
         fuente='Zhen et al., Arch. Electr. Eng. 74 (2025), tabla 2', nota='q = 2 (dato)'),
    dict(tipo='hidro', id='H2', maq='Generador-motor de bombeo, no identificado', pot='145/170 MW', P=30,
         Qs=360, Di=7240, bs=24.5, hs=159.5, rpm=200, nivel='A',
         fuente='Zhang et al., Machines 11 (2023) 901, tabla 1',
         nota='«based on the real machine»; ensayo de calentamiento en la central'),
    dict(tipo='hidro', id='H3', maq='Caso 1, no identificada (bobinas)', pot='95,5 MVA', P=84, Qs=432,
         Di=None, bs=24.76, hs=None, rpm=None, nivel='A',
         fuente='Sanosian et al. (Stantec/Altair), caso 1',
         nota='q = 1 5/7; P deducido de Qs y q'),
    dict(tipo='hidro', id='H4', maq='Caso 2, no identificada (barras Roebel)', pot='95,5 MVA', P=84, Qs=576,
         Di=None, bs=23.19, hs=None, rpm=None, nivel='A',
         fuente='Sanosian et al. (Stantec/Altair), caso 2',
         nota='q = 2 2/7; P deducido de Qs y q'),
    dict(tipo='hidro', id='H5', maq='Hidro 1000 MW, no identificada', pot='1000 MW', P=54, Qs=810,
         Di=17500, Di_alt=16300, bs=None, hs=None, rpm=None, nivel='A',
         fuente='Processes 11 (2023) 899, tabla 1',
         nota='tabla con D_i > D_e: se dan los dos pasos'),
    dict(tipo='hidro', id='H6', maq='Westinghouse Canadá (1958)', pot='28 MVA', P=14, Qs=162,
         Di=None, bs=None, hs=None, rpm=514, nivel='A',
         fuente='Chichkin, Iris Rotating Machine Conf. 2019, lám. 17',
         nota='presentado como ejemplo de cálculo con datos de placa'),
    dict(tipo='hidro', id='H7', maq='Manic-2 (Hydro-Québec)', pot='122,6 MVA', P=60, Qs=504,
         Di=10617.2, bs=23.24, hs=159, rpm=120, nivel='B',
         fuente='Aguiar, Merkhouf, Al-Haddad, IECON 2013',
         nota='P, Qs y MVA confirmados por buscador; D_i, b_s, h_s solo del material de partida'),
    dict(tipo='hidro', id='H8', maq='CB 870/300-28 (India)', pot='250 MW', P=28, Qs=348,
         Di=15819.8, Di_alt=7909.9, bs=27.9, hs=209.9, rpm=None, nivel='B',
         fuente='Carunaiselvane et al., PEDES 2018',
         nota='P y Qs confirmados por buscador; D_i dudoso (ver texto)'),
    dict(tipo='hidro', id='H9', maq='Gezhouba SF150-96/15600', pot='150 MW', P=96, Qs=None,
         Di=None, bs=30.0, hs=None, rpm=None, nivel='B',
         fuente='ResearchGate 369359836 (cuñas de ranura)',
         nota='b_s confirmado solo por resumen de buscador'),
    dict(tipo='hidro', id='H10', maq='Itaipú', pot='700 MW', P=None, Qs=504,
         Di=16000, bs=None, hs=None, rpm=None, nivel='B',
         fuente='Presentación DP Itaipú (Scribd)', nota='D_i «aprox. 16 m»; 66/78 polos (50/60 Hz)'),
    dict(tipo='hidro', id='H11', maq='Hidro 1000 MW, no identificada', pot='1000 MW', P=56, Qs=696,
         Di=16580, bs=None, hs=None, rpm=None, nivel='B',
         fuente='ResearchGate 384860410 (2024)', nota='solo material de partida'),
    # ---------------- TURBO ----------------
    dict(tipo='turbo', id='T1', maq='QFSN-600-2YHG', pot='667 MVA', P=2, Qs=42,
         Di=1316, bs=70.0, hs=160, rpm=3000, nivel='A',
         fuente='Jiang et al., Int. J. Rotating Mach. 2021, 5554914, tabla 1',
         nota='«stator slot dimensions 160*70»: se interpreta b_s = 70 mm; parámetros de modelo FEM'),
    dict(tipo='turbo', id='T2', maq='Turbo 1000 MW, no identificado', pot='1000 MW', P=2, Qs=36,
         Di=1471, bs=None, hs=160, rpm=None, nivel='A',
         fuente='Wang, WSEAS Trans. Appl. Theor. Mech. 2015, §3.3',
         nota='h_s = 160 mm coincide con (1791 - 1471)/2'),
    dict(tipo='turbo', id='T3', maq='Turbo 247 MVA, no identificado', pot='247 MVA', P=2, Qs=60,
         Di=None, bs=None, hs=None, rpm=3000, nivel='B',
         fuente='Hanic et al., IET EPA 2014', nota='solo material de partida'),
    # ---------------- DISEÑOS (no entran en los rangos) ----------------
    dict(tipo='turbo', id='D1', maq='Diseño 250 MW aire', pot='250 MW', P=2, Qs=72,
         Di=1200 + 2 * 50, bs=27.0, hs=261, rpm=3000, nivel='D',
         fuente='Minko y Shevchenko 2018, tabla 1', nota='D_i = rotor + 2 entrehierro'),
    dict(tipo='turbo', id='D2', maq='Diseño 250 MW H2', pot='250 MW', P=2, Qs=60,
         Di=1075 + 2 * 100, bs=38.6, hs=250, rpm=3000, nivel='D',
         fuente='Minko y Shevchenko 2018, tabla 1', nota='D_i = rotor + 2 entrehierro'),
    dict(tipo='turbo', id='D3', maq='Diseño 250 MW H2/agua', pot='250 MW', P=2, Qs=30,
         Di=1120 + 2 * 77.5, bs=50.8, hs=183, rpm=3000, nivel='D',
         fuente='Minko y Shevchenko 2018, tabla 1', nota='D_i = rotor + 2 entrehierro'),
    dict(tipo='turbo', id='D4', maq='Modelo 30 MVA', pot='30 MVA', P=None, Qs=None,
         Di=None, bs=24.0, hs=None, rpm=None, nivel='D', ks_dato=0.15,
         fuente='High Voltage 2026, hve2.70118', nota='b_s = 0,15 tau_s impuesto; fuente no abierta'),
]


def paso(Di, Qs):
    return math.pi * Di / Qs if Di and Qs else None


for m in M:
    m['tau'] = paso(m['Di'], m['Qs'])
    m['tau_alt'] = paso(m.get('Di_alt'), m['Qs'])
    m['ks'] = m['bs'] / m['tau'] if m['bs'] and m['tau'] else m.get('ks_dato')
    m['ks_alt'] = m['bs'] / m['tau_alt'] if m['bs'] and m['tau_alt'] else None
    m['bt'] = m['tau'] - m['bs'] if m['bs'] and m['tau'] else None
    m['q'] = m['Qs'] / (3 * m['P']) if m['Qs'] and m['P'] else None
    if m['rpm'] and m['Di']:
        m['v_bore'] = math.pi * m['Di'] / 1000 * m['rpm'] / 60
        m['v_bore_alt'] = (math.pi * m['Di_alt'] / 1000 * m['rpm'] / 60) if m.get('Di_alt') else None

# CB 870/300-28: 28 polos a 50 Hz -> 214,3 rpm (la fuente es de India, 50 Hz)
cb = next(m for m in M if m['id'] == 'H8')
cb['rpm_calc'] = 120 * 50 / cb['P']
cb['v_bore'] = math.pi * cb['Di'] / 1000 * cb['rpm_calc'] / 60
cb['v_bore_alt'] = math.pi * cb['Di_alt'] / 1000 * cb['rpm_calc'] / 60


def rango(tipo, clave, niveles, excluir=()):
    v = [m[clave] for m in M if m['tipo'] == tipo and m['nivel'] in niveles
         and m[clave] is not None and m['id'] not in excluir]
    for m in M:  # valores alternativos (D_i ambiguo) cuentan en el rango de paso
        if m['tipo'] == tipo and m['nivel'] in niveles and m['id'] not in excluir \
                and clave == 'tau' and m.get('tau_alt'):
            v.append(m['tau_alt'])
    return [min(v), max(v), len(v)] if v else None


R = {}
for tipo in ('hidro', 'turbo'):
    R[tipo] = {
        'bs_A': rango(tipo, 'bs', 'A'),
        'bs_AB': rango(tipo, 'bs', 'AB'),
        'tau_A': rango(tipo, 'tau', 'A'),
        'tau_AB': rango(tipo, 'tau', 'AB', excluir=('H8',)),
        'ks_A': rango(tipo, 'ks', 'A'),
        'ks_AB': rango(tipo, 'ks', 'AB', excluir=('H8',)),
        'Qs_A': rango(tipo, 'Qs', 'A'),
        'Qs_AB': rango(tipo, 'Qs', 'AB'),
        'hs_A': rango(tipo, 'hs', 'A'),
        'hs_AB': rango(tipo, 'hs', 'AB'),
    }

salida = {'maquinas': M, 'rangos': R}
(AQUI / 'resultados.json').write_text(json.dumps(salida, indent=2, ensure_ascii=False), encoding='utf-8')

# ---------------------------------------------------------------- consola
for m in M:
    f = lambda x, d=1: '—' if x is None else f'{x:.{d}f}'
    print(f"{m['id']:4} {m['nivel']} Qs={m['Qs']} Di={m['Di']} bs={m['bs']} tau={f(m['tau'],2)}"
          f" tau_alt={f(m['tau_alt'],2)} ks={f(m['ks'] and 100*m['ks'])}% ks_alt={f(m['ks_alt'] and 100*m['ks_alt'])}%"
          f" bt={f(m['bt'])} q={f(m['q'],3)} v={f(m.get('v_bore'))} v_alt={f(m.get('v_bore_alt'))}")
print(json.dumps(R, indent=1))

# ---------------------------------------------------------------- figura
AZUL, VERDE, TINTA, GRIS = '#2a78d6', '#1baf7a', '#1E2328', '#6B7280'
fig, ax = plt.subplots(figsize=(6.4, 4.0))
for k in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7):
    ax.plot([0, 160], [0, 160 * k], color='#DADDE1', lw=0.8, zorder=0)
    x = min(158, 78 / k)
    ax.text(x, x * k + 1.0, f'{int(k*100)} %', color=GRIS, fontsize=7, ha='right', va='bottom')
puntos = [m for m in M if m['nivel'] in 'AB' and m['bs'] and m['tau']]
for m in puntos:
    c = AZUL if m['tipo'] == 'hidro' else VERDE
    mk = 'o' if m['tipo'] == 'hidro' else 's'
    lleno = m['nivel'] == 'A'
    ax.scatter(m['tau'], m['bs'], s=46, marker=mk, color=c if lleno else 'white',
               edgecolor=c, linewidth=2, zorder=3)
    if m.get('tau_alt'):
        ax.scatter(m['tau_alt'], m['bs'], s=46, marker=mk, color='white', edgecolor=c,
                   linewidth=2, zorder=3)
        ax.plot([m['tau_alt'], m['tau']], [m['bs'], m['bs']], color=c, lw=1, ls=':', zorder=2)
etiquetas = [(66.88, 28.0, -1.5, 2.0, 'right', '34 MW'), (63.18, 24.5, -1.5, 0.6, 'right', '145 MW'),
             (66.18, 23.24, 1.5, -4.2, 'left', 'Manic-2'),
             (71.41, 27.9, 1.5, 2.0, 'left', r'CB 870/300-28, $D_i$ = 7,91 m'),
             (142.81, 27.9, 0, 2.6, 'center', r'ídem, $D_i$ = 15,8 m'),
             (98.44, 70.0, 0, 2.6, 'center', 'QFSN-600-2YHG')]
for x, y, dx, dy, ha, t in etiquetas:
    ax.text(x + dx, y + dy, t, fontsize=7.5, color=TINTA, ha=ha)
ax.scatter([], [], marker='o', color=AZUL, label='Hidro, fuente leída')
ax.scatter([], [], marker='o', color='white', edgecolor=AZUL, linewidth=2, label='Hidro, fuente no abierta')
ax.scatter([], [], marker='s', color=VERDE, label='Turbo, fuente leída')
ax.set_xlim(40, 160); ax.set_ylim(0, 80)
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
print('figura ok')
