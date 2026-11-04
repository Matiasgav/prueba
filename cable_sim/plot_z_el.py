import json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from rod import W, H, r, D
from z_elastica import VENT
d = [s for s in json.load(open('z_el.json')) if s['ok']]
L0 = 192.4                                    # guardado: primer estado con R >= 8.5
cA, cB, c2 = '#1f6fb2', '#e07b00', '#7b3fa0'
fig = plt.figure(figsize=(15, 8.2))
sel = [192.4, 172.4, 152.4, 134.4, 122.4, 120.4]
for i, Lt in enumerate(sel):
    s = min(d, key=lambda q: abs(q['L'] - Lt)); X = np.array(s['X']); ss = np.array(s['s']); mid = s['mid']
    ax = fig.add_axes([0.01 + (i % 3) * 0.33, 0.55 - (i // 3) * 0.29, 0.32, 0.26])
    ax.add_patch(Rectangle((-8, -3), W + 11, H + 6, color='#d5d8dc'))
    ax.add_patch(Rectangle((0, 0), W, H, fc='w', ec='k')); ax.add_patch(Rectangle((-8, H - D), 8, D, color='w'))
    for m, c in ((ss < mid - VENT, cA), ((ss >= mid - VENT) & (ss <= mid + VENT), c2), (ss > mid + VENT, cB)):
        ax.plot(X[m, 0], X[m, 1], color=c, lw=D * 2.3, alpha=.35, solid_capstyle='round'); ax.plot(X[m, 0], X[m, 1], color=c, lw=1.2)
    ax.plot([-8, X[-1, 0]], [X[-1, 1]] * 2, color=cB, lw=1.2)
    ax.add_patch(Rectangle((0.2, 0.2), 5, 3.1, fc='#bdbdbd', ec='k', lw=.6, zorder=6))
    ax.set_xlim(-8, W + 3); ax.set_ylim(-3, H + 3); ax.set_aspect('equal'); ax.axis('off')
    e = L0 - s['L']
    ax.set_title(f"{e:.0f} mm extraídos  ·  R = {min(s['R']):.1f} mm", fontsize=10, color='#c62828' if e >= 70 else 'k')
b = fig.add_axes([0.08, 0.06, 0.86, 0.17])
e = np.array([L0 - s['L'] for s in d]); R = np.array([s['R'] for s in d])
for k, lab, c in ((0, 'lazo derecho piso 1', cA), (1, 'lazo izquierdo (cambio de piso)', c2), (2, 'lazo derecho piso 2', cB)):
    b.plot(e, R[:, k], 'o-', ms=3, color=c, label=lab)
b.axvspan(0, 70, color='#2e7d32', alpha=.08, label='70 mm requeridos')
b.axhline(8.5, ls=':', color='k', lw=.8)
b.set_xlim(-10, 78); b.set_ylim(4, 11); b.set_xlabel('cable extraído (mm)'); b.set_ylabel('R mín. (mm)')
b.grid(alpha=.3); b.legend(fontsize=8, ncol=4, loc='lower center')
fig.suptitle('Elástica del cable en Z (dos pisos): azul = piso 1, violeta = cambio de piso, naranja = piso 2', fontsize=12)
fig.savefig('z_elastica.png', dpi=140)
