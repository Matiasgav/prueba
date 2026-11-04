"""Esquema: cable plegado en Z en dos capas (3 lazos rodantes).
El perfil de cada lazo es el de la simulación del lazo simple (R ≈ 8,8 mm)."""
import json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from rod import W, H, r, D

d = json.load(open('rl_a.json'))
X = np.array(min((s for s in d['extract'] if s['ok']), key=lambda s: abs(s['L'] - 61))['X'])
tip = X[:, 0].max()
T = X[X[:, 0] > tip - 9.3] - [tip, 0]          # lazo relativo a su punta (abre a la izquierda)
WL = -T[:, 0].min()                              # largo del tramo tomado
Y0, Y1 = r, H - r; XL = r; XR = W - r


def path(t1, t2, t3):
    """t1, t3: punta lazos derechos; t2: punta lazo izquierdo."""
    l1 = T + [t1, 0]; l3 = T + [t3, 0]
    l2 = np.c_[-T[:, 0] + t2, Y1 + Y0 - T[:, 1]][::-1]   # espejado: abre a la derecha, de arriba a abajo
    l2 = l2[::-1]
    A = np.vstack([[XL, Y0], l1[l1[:, 1] < H / 2][:: 1] if False else l1, ])
    capaA = np.vstack([[XL, Y0], l1, l2[l2[:, 1] > H / 2]])
    capaB = np.vstack([l2[l2[:, 1] <= H / 2], l3, [-6, Y1]])
    return capaA, capaB

fig, axs = plt.subplots(1, 3, figsize=(15, 4.6), gridspec_kw=dict(width_ratios=[1, 1, .42]))
for ax, (t1, t2, t3), tit in ((axs[0], (XR, XL, XR), 'Guardado (0 mm extraídos)'),
                              (axs[1], (XL + 2 * 9.3 + 0.6, XL, XL + 2 * 9.3 + 0.6), 'Extraído al máximo (~80 mm)')):
    ax.add_patch(Rectangle((-8, -3), W + 11, H + 6, color='#d5d8dc'))
    ax.add_patch(Rectangle((0, 0), W, H, fc='w', ec='k'))
    ax.add_patch(Rectangle((-8, H - D), 8, D, color='w'))
    ax.add_patch(Rectangle((0.2, 0.2), 5, 3.1, fc='#bdbdbd', ec='k', lw=.8, zorder=6))
    A, B = path(t1, t2, t3)
    for P, c, lab in ((A, '#1f6fb2', 'capa A (contra la PCB)'), (B, '#e07b00', 'capa B (contra la tapa)')):
        ax.plot(P[:, 0], P[:, 1], color=c, lw=D * 5.6, alpha=.35, solid_capstyle='round')
        ax.plot(P[:, 0], P[:, 1], color=c, lw=1.4, label=lab)
    ax.text(2.7, 1.75, 'sold.', fontsize=7, ha='center', va='center', zorder=7)
    ax.text(-7.5, H - D - 2, 'salida ←\n(capa B)', fontsize=8)
    for t, nm, dx in ((t1, '1', -6), (t2, '2', 4), (t3, '3', -6)):
        ax.text(t + dx, H / 2 + (1.5 if nm != '3' else -2.5), nm, fontsize=11, fontweight='bold',
                color='#1f6fb2' if nm == '1' else ('#e07b00' if nm == '3' else 'k'))
    ax.text(XL + 1.2, H / 2, 'cambio\nde capa', fontsize=6.5, va='center')
    ax.set_xlim(-8, W + 3); ax.set_ylim(-3, H + 3); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(tit, fontsize=10)
axs[0].legend(loc='lower center', bbox_to_anchor=(.5, -.16), ncol=2, fontsize=8, frameon=False)
axs[1].text(W / 2, -2.2, 'los lazos 1 y 3 se superponen en esta vista: van en capas distintas', fontsize=7.5, ha='center')
# corte en profundidad
b = axs[2]; DEP = 2.5 * D
b.add_patch(Rectangle((-1.5, -1.5), DEP + 3, H + 3, color='#d5d8dc'))
b.add_patch(Rectangle((0, 0), DEP, H, fc='w', ec='k'))
b.add_patch(Rectangle((0, 0), .8, H, color='#2e7d32', alpha=.5))
for z, y, c in ((r + .8, Y0, '#1f6fb2'), (r + .8, Y1, '#1f6fb2'), (DEP - r, Y0, '#e07b00'), (DEP - r, Y1, '#e07b00')):
    b.add_patch(Circle((z, y), r, fc=c, ec='k', alpha=.8))
b.plot([r + .8, DEP - r], [Y1, Y0], ':', color='k')
b.text(DEP / 2, H / 2 + 1, 'lazo 2\ncambia\nde capa', fontsize=7.5, ha='center')
b.text(.4, -1.2, 'PCB', fontsize=7, color='#1b5e20')
b.text(DEP / 2, H + 1.5, 'Corte: 8,75 mm = 2 capas', fontsize=9, ha='center')
b.set_xlim(-2, DEP + 2); b.set_ylim(-2, H + 3); b.set_aspect('equal'); b.axis('off')
fig.tight_layout(); fig.savefig('dibujo_Z_70mm.png', dpi=160)
