#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nota 02489-00-MC004 - Selección del actuador del paralelogramo.

Uso (desde esta carpeta):
    python3 calculo.py        # escribe resultados.json y figuras/fig_*.pdf/png

Datos: hojas de datos oficiales en fuentes/ (FAULHABER ediciones 2026-07-28,
maxon 2025, PiezoMotor 2025-2026). La curva par-velocidad del AM1020 se
digitalizó a ojo de la figura «Possible operation areas» de EN_AM1020_FPS.pdf
(error de lectura del orden de ±0,05 mNm).

Calcula:
  1. Par de motor necesario en el husillo 3x0,5 con reductora:
       T_m = F p / (2 pi eta_screw eta_gear i)
     con los rendimientos MÁXIMOS de la hoja (optimista: el par real es mayor).
  2. Velocidad de motor para una velocidad de salida v: n_m = 60 v i / p.
  3. Margen del AM1020 frente a ese par, en la velocidad correspondiente.
  4. Tiempos de carrera.
  5. Alternativa maxon GPX 10 + husillo externo y alternativa de leva.
"""
import json
import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

P = 0.5e-3               # paso del husillo 3x0,5 [m]
ETA_S = 0.35             # rendimiento del husillo, máx. (hoja 10L/06L)
CARRERA = 8.0            # [mm]
F_REQ = 50.0             # [N]

# Hojas de datos FAULHABER (continuous / peak dyn / static / v cont / v peak / L2)
ACT = {
    '06L HL 64:1':    dict(i=64,   eta_g=0.70, Fc=15,  Fp=25,  Fs=80,  vc=1.6,  vp=2.1, diam=6),
    '06L HL 256:1':   dict(i=256,  eta_g=0.60, Fc=20,  Fp=30,  Fs=80,  vc=0.4,  vp=0.5, diam=6),
    '06L HL 1024:1':  dict(i=1024, eta_g=0.55, Fc=25,  Fp=35,  Fs=80,  vc=0.1,  vp=0.1, diam=6),
    '10L SL 64:1':    dict(i=64,   eta_g=0.70, Fc=15,  Fp=30,  Fs=60,  vc=1.6,  vp=2.1, diam=10),
    '10L SL 1024:1':  dict(i=1024, eta_g=0.55, Fc=40,  Fp=50,  Fs=60,  vc=0.1,  vp=0.1, diam=10),
    '10L HL 64:1':    dict(i=64,   eta_g=0.70, Fc=100, Fp=150, Fs=350, vc=1.0,  vp=2.1, diam=10),
    '10L HL 256:1':   dict(i=256,  eta_g=0.60, Fc=150, Fp=200, Fs=350, vc=0.3,  vp=0.5, diam=10),
    '10L HL 1024:1':  dict(i=1024, eta_g=0.55, Fc=200, Fp=250, Fs=350, vc=0.07, vp=0.1, diam=10),
}

# AM1020, curva digitalizada: (min-1, mNm)
AM1020 = {
    '1x Un':   [(0, 1.10), (600, 1.10), (1500, 0.95), (2500, 0.75), (3500, 0.50),
                (4200, 0.33), (4700, 0.12)],
    '2,5x Un': [(0, 1.30), (1500, 1.38), (3000, 1.30), (6000, 1.05), (9000, 0.75),
                (12000, 0.47), (14000, 0.30), (16200, 0.08)],
    '5x Un':   [(0, 1.30), (1500, 1.38), (6000, 1.25), (9000, 1.15), (12000, 1.00),
                (15000, 0.80), (18000, 0.68), (21000, 0.53)],
}
AM1020_HOLD = 1.6        # par de retención a corriente nominal [mNm]
DM0620_HOLD = 0.25       # [mNm]

# Alternativas (hojas de datos)
GPX10 = dict(Tc={1: 0.01, 2: 0.03, 3: 0.10, 4: 0.15, 5: 0.15},   # Nm
             axial_din=5.0)                                        # N
PIEZO = {  # fuerza de bloqueo [N], tamaño L x H x D [mm]
    'LL10': (6.5, (22, 19.3, 10.8)),
    'LT20': (20, (22, 21.8, 10.8)),
    'LT40': (40, (32.1, 24.2, 23.1)),
}
E_LEVA = 4.0e-3          # excentricidad [m]


def par_motor(F, a):
    return F * P / (2 * math.pi * ETA_S * a['eta_g'] * a['i']) * 1e3   # mNm


def rpm_motor(v, a):
    return 60 * v * 1e-3 * a['i'] / P


def am1020(rpm, curva):
    x, y = zip(*AM1020[curva])
    return float(np.interp(rpm, x, y, right=0.0))


def main():
    res = {'actuadores': {}}
    for k, a in ACT.items():
        res['actuadores'][k] = {
            'F_continua_N': a['Fc'], 'margen_vs_50N': round(a['Fc'] / F_REQ, 2),
            'par_motor_50N_mNm': round(par_motor(F_REQ, a), 3),
            'par_motor_Fc_mNm': round(par_motor(a['Fc'], a), 3),
            'rpm_motor_v_cont': round(rpm_motor(a['vc'], a)),
            't_8mm_cont_s': round(CARRERA / a['vc'], 1),
            't_8mm_pico_s': round(CARRERA / a['vp'], 1),
        }

    hl = ACT['10L HL 64:1']
    op = {}
    for nombre, v in (('v_cont_1mm_s', hl['vc']), ('v_pico_2p1mm_s', hl['vp'])):
        n = rpm_motor(v, hl)
        op[nombre] = {'rpm': round(n),
                      'par_disp_2p5x_mNm': round(am1020(n, '2,5x Un'), 2),
                      'par_disp_5x_mNm': round(am1020(n, '5x Un'), 2)}
    op['par_req_50N_mNm'] = round(par_motor(50, hl), 3)
    op['par_req_100N_mNm'] = round(par_motor(100, hl), 3)
    op['F_max_con_par_retencion_N'] = round(
        AM1020_HOLD * 1e-3 * 2 * math.pi * ETA_S * hl['eta_g'] * hl['i'] / P)
    res['am1020_10L_HL_64'] = op
    res['dm0620_06L_HL_64_par_15N_mNm'] = round(par_motor(15, ACT['06L HL 64:1']), 3)
    res['dm0620_par_retencion_mNm'] = DM0620_HOLD

    # maxon: empuje teórico con GPX 10 3 etapas y el mismo husillo
    res['maxon_GPX10_3et'] = {
        'T_cont_Nm': GPX10['Tc'][3],
        'empuje_teorico_N': round(2 * math.pi * ETA_S * GPX10['Tc'][3] / P),
        'carga_axial_admisible_N': GPX10['axial_din'],
    }
    # leva: par máximo en el eje (sin rozamiento) para F_REQ
    res['leva'] = {'e_mm': E_LEVA * 1e3, 'carrera_mm': 2 * E_LEVA * 1e3,
                   'par_max_50N_Nm': round(F_REQ * E_LEVA, 3),
                   'GPX10_T_cont_max_Nm': max(GPX10['Tc'].values())}
    res['piezo'] = {k: {'F_N': f, 'LxHxD_mm': d} for k, (f, d) in PIEZO.items()}

    with open('resultados.json', 'w', encoding='utf-8') as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False)

    figura_curva(hl)
    figura_mapa()
    print(json.dumps({k: res[k] for k in res if k != 'actuadores'}, indent=1, ensure_ascii=False))
    for k, v in res['actuadores'].items():
        print(k, v)


def figura_curva(hl):
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    colores = {'1x Un': '#9CA3AF', '2,5x Un': '#2563EB', '5x Un': '#1E3A8A'}
    for c, pts in AM1020.items():
        x, y = zip(*pts)
        ax.plot(x, y, color=colores[c], lw=2, label=f'AM1020, {c} (hoja)')
    for F, ls in ((50, '--'), (100, '-')):
        ax.axhline(par_motor(F, hl), color='#B91C1C', ls=ls, lw=1.4)
        ax.text(20800, par_motor(F, hl) + 0.03, f'par necesario, {F} N', ha='right',
                va='bottom', color='#B91C1C', fontsize=8)
    for v in (hl['vc'], hl['vp']):
        n = rpm_motor(v, hl)
        ax.axvline(n, color='#374151', lw=0.8, ls=':')
        ax.text(n + 150, 1.45, f'{v:g} mm/s'.replace('.', ','), fontsize=8, color='#374151')
    ax.set_xlim(0, 21000)
    ax.set_ylim(0, 1.6)
    ax.set_xlabel('velocidad del motor [min$^{-1}$]')
    ax.set_ylabel('par [mNm]')
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc='upper right', bbox_to_anchor=(1, 0.9))
    fig.tight_layout()
    for ext in ('pdf', 'png'):
        fig.savefig(f'figuras/fig_par_am1020.{ext}', dpi=200)
    plt.close(fig)


def figura_mapa():
    # (nombre, ancho transversal máx. [mm], fuerza continua o de bloqueo [N], color)
    pts = [('06L HL + DM0620 (64:1)', 6, 15, '#9CA3AF'),
           ('06L HL (1024:1)', 6, 25, '#9CA3AF'),
           ('10L SL (1024:1)', 10, 40, '#9CA3AF'),
           ('10L HL + AM1020 (64:1)', 10, 100, '#B91C1C'),
           ('10L HL (1024:1)', 10, 200, '#6B7280'),
           ('LEGS LL10', 19.3, 6.5, '#2563EB'),
           ('LEGS LT20', 21.8, 20, '#2563EB'),
           ('LEGS LT40', 24.2, 40, '#2563EB')]
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.axvspan(0, 12, ymin=0, ymax=1, color='#FDE68A', alpha=0.35, lw=0)
    ax.axhline(F_REQ, color='#B91C1C', ls='--', lw=1.2)
    ax.text(25.6, F_REQ * 1.07, 'requisito > 50 N', color='#B91C1C', fontsize=8, ha='right')
    ax.text(0.5, 330, 'ancho ≤ 12 mm', fontsize=8, color='#92400E', va='top')
    off = {'06L HL + DM0620 (64:1)': (6, -3), '06L HL (1024:1)': (6, 2),
           '10L SL (1024:1)': (6, -4), '10L HL + AM1020 (64:1)': (6, -4),
           '10L HL (1024:1)': (6, -4), 'LEGS LL10': (-6, 0), 'LEGS LT20': (-6, 0),
           'LEGS LT40': (-6, 0)}
    for n, x, y, c in pts:
        ax.scatter(x, y, s=46, color=c, zorder=3, edgecolor='white', lw=0.8)
        dx, dy = off[n]
        ax.annotate(n, (x, y), xytext=(dx, dy), textcoords='offset points', fontsize=8,
                    ha='left' if dx > 0 else 'right', va='center',
                    fontweight='bold' if 'AM1020' in n else 'normal')
    ax.set_yscale('log')
    ax.set_xlim(0, 26)
    ax.set_ylim(4, 400)
    ax.set_xlabel('ancho transversal máximo [mm]')
    ax.set_ylabel('fuerza continua / de bloqueo [N]')
    ax.grid(alpha=0.3, which='both')
    fig.tight_layout()
    for ext in ('pdf', 'png'):
        fig.savefig(f'figuras/fig_mapa_candidatos.{ext}', dpi=200)
    plt.close(fig)


if __name__ == '__main__':
    main()
