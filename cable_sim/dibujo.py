"""Esquema de la solución: vista frontal (simulada) + corte en profundidad."""
import json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch
from rod import W, H, r, D

d = json.load(open('rl_a.json')); ext = [s for s in d['extract'] if s['ok']]
st = lambda L: np.array(min(ext, key=lambda s: abs(s['L'] - L))['X'])
DEP = 2.5 * D
fig = plt.figure(figsize=(14, 7.2))
a = fig.add_axes([0.03, 0.1, 0.64, 0.82]); b = fig.add_axes([0.71, 0.18, 0.27, 0.64])

# ---------- vista frontal ----------
gris = '#c9ccd1'
a.add_patch(Rectangle((-14, -6), 14, H + 14, color=gris))           # pared izq.
a.add_patch(Rectangle((W, -6), 6, H + 14, color=gris))              # pared der.
a.add_patch(Rectangle((-14, -6), W + 20, 6, color=gris))            # fondo
a.add_patch(Rectangle((3.5, H), W - 3.5, 8, color='#3b4bd1', alpha=.85))   # placa azul
a.text(W / 2 + 2, H + 2.5, 'PCB superior (placa azul)', color='w', ha='center', fontsize=9)
a.add_patch(Rectangle((-14, H), 17.5, 8, color=gris))
a.add_patch(Rectangle((-14, H - 2 * r - .25), 14, 2 * r + .5, color='w'))  # canal de salida
a.add_patch(Rectangle((0, 0), W, H, fill=False, lw=1.2, ec='k'))
a.add_patch(Rectangle((0.3, 0.3), W - .6, 1.0, color='#2e7d32', alpha=.5))  # PCB del cable
a.text(W - 1, 0.8, 'PCB del cable', fontsize=7, ha='right', va='center', color='#1b5e20')

for L, c, lw, ls, lab in ((91, '#e07b00', 1, '-', 'guardado (0 mm extraídos)'),
                          (61, '#7a7a7a', 1, '--', '30 mm extraídos'),
                          (31, '#c62828', 1, '-', '60 mm extraídos')):
    X = st(L)
    tail = np.array([[X[-1, 0], X[-1, 1]], [-14, X[-1, 1]]]) if L != 31 else None
    extra = 60 - (91 - L)
    Xo = np.vstack([X, [[X[-1, 0] - 14 + 0 * extra, X[-1, 1]]]])
    a.plot(Xo[:, 0], Xo[:, 1], color=c, lw=D * 7.2, alpha=.25 if ls == '--' else .45,
           solid_capstyle='round', solid_joinstyle='round')
    a.plot(Xo[:, 0], Xo[:, 1], color=c, lw=1.4, ls=ls, label=lab)

# radio en la punta
X = st(61); i = np.argmax(X[:, 0]); cx = X[i, 0] - 8.8
a.add_patch(Circle((cx, X[i, 1]), 8.8, fill=False, ls=':', ec='k', lw=.8))
a.annotate('R ≈ 8,8 mm\n(punta del lazo)', (cx + 8.8 * .7, X[i, 1] + 8.8 * .7), (cx + 14, X[i, 1] + 6),
           fontsize=8, arrowprops=dict(arrowstyle='->', lw=.8))
# avance
a.add_patch(FancyArrowPatch((39, 12), (12.5, 12), arrowstyle='-|>', mutation_scale=14, color='#c62828', lw=1.2))
a.text(26, 13, 'al extraer, el lazo rueda a la izquierda\n(1 mm de lazo por cada 2 mm de cable)',
       ha='center', fontsize=8, color='#c62828')
# soldadura
a.add_patch(Rectangle((0.2, 0.2), 5, 3.1, fc='#bdbdbd', ec='k', lw=.8, zorder=5))
a.text(2.7, 1.75, 'sold.', fontsize=7, ha='center', va='center', zorder=6)
a.annotate('SOLDADURA\nesquina inf. izq.\ncable sale →', (0.5, 2.5), (-13.5, 9), fontsize=8,
           color='#c62828', arrowprops=dict(arrowstyle='->', color='#c62828'))
a.annotate('SALIDA ←', (-1, H - r), (-13, H - 9), fontsize=9, fontweight='bold',
           arrowprops=dict(arrowstyle='->'))
# variante: soldadura corrida 5 mm
a.add_patch(Rectangle((-5, 0.2), 5, 3.1, fc='none', ec='#1565c0', ls='--', lw=1))
a.add_patch(Rectangle((-14, -0.0), 14, 3.5, fc='w', ec='#1565c0', ls='--', lw=.8, alpha=.0))
a.annotate('variante 70 mm:\nsoldadura 5 mm\nmás a la izq.\n(si hay hueco)',
           (-4, 1.75), (-13.5, 1.0), fontsize=7, color='#1565c0',
           arrowprops=dict(arrowstyle='->', color='#1565c0'))
# cotas
def cota(ax, p, q, txt, off=(0, 0), rot=0):
    ax.annotate('', p, q, arrowprops=dict(arrowstyle='<->', lw=.8))
    ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], txt, fontsize=8, ha='center', rotation=rot)
cota(a, (0, -3.5), (W, -3.5), '42,62', (0, .4))
cota(a, (W + 3, 0), (W + 3, H), '24,57', (1.4, 0), 90)
a.text(W / 2, H + 6.6, 'Cable guardado: 91 mm entre soldadura y salida  ·  carrera 60 mm  ·  Ø 3,5 mm',
       ha='center', fontsize=8, color='w')
a.set_xlim(-14, W + 6); a.set_ylim(-6, H + 8); a.set_aspect('equal'); a.axis('off')
a.legend(loc='upper center', bbox_to_anchor=(0.5, 0.02), fontsize=8, ncol=3, frameon=False)
a.set_title('Vista frontal — lazo rodante (formas de la simulación)', fontsize=11)

# ---------- corte A-A (profundidad) ----------
b.add_patch(Rectangle((-2, -2), DEP + 4, H + 4, color=gris))
b.add_patch(Rectangle((0, 0), DEP, H, color='w', ec='k', lw=1))
b.add_patch(Rectangle((0, 0), .8, H, color='#2e7d32', alpha=.5))
for y, z, lab in ((r, r, 'rama inferior\n(contra el fondo)'), (H - r, DEP - r, 'rama superior\n(contra la tapa)')):
    b.add_patch(Circle((z, y), r, fc='#e07b00', ec='k', alpha=.8))
    b.text(DEP + 2.6, y, lab, fontsize=8, va='center')
b.plot([r, DEP - r], [r, H - r], ':', color='k', lw=.8)
b.text(DEP / 2 + .3, H / 2, 'plano del lazo\ninclinado\n≈ 21,7 mm\n→ R ≈ 9,1', fontsize=7.5, ha='left', va='center',
       rotation=0)
cota(b, (0, -1.2), (DEP, -1.2), '8,75 (2,5 Ø)', (0, -1.6))
b.set_xlim(-2.5, DEP + 9); b.set_ylim(-4, H + 2); b.set_aspect('equal'); b.axis('off')
b.set_title('Corte A-A (profundidad)', fontsize=11)
fig.savefig('dibujo_solucion.png', dpi=170)
