import json, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from rod import W, H, r
d = json.load(open(sys.argv[1])); out = sys.argv[2]
ext = d['extract']; ret = d['retract']; p = d['pose']
fig, (a, b) = plt.subplots(1, 2, figsize=(13, 4.8), gridspec_kw=dict(width_ratios=[1.35, 1]))
a.add_patch(Rectangle((0, 0), W, H, fill=False, lw=1.5, ec='k'))
a.add_patch(Rectangle((0, H), r * 2, 6, fill=False, lw=1, ec='k', ls='--'))
a.text(2.2, H + 3, 'salida (canal 3.5 mm)', fontsize=8, va='center')
cm = plt.cm.viridis
sel = [s for s in ext if s['ok'] and 50 <= s['L'] <= 63][::3]
for i, s in enumerate(sel):
    X = np.array(s['X']); c = cm(i / max(len(sel) - 1, 1))
    a.plot(X[:, 0], X[:, 1], color=c, lw=2, label=f"L int = {s['L']:.0f} mm  (Rmin {s['Rmin']:.1f})")
    a.plot(X[:, 0], X[:, 1], color=c, lw=3.5 / 0.35 * 0.35 * 8, alpha=0.06)
a.plot(p['x'], p['y'], 's', ms=10, color='C3'); a.annotate('SOLDADURA\n(cable sale hacia abajo)', (p['x'], p['y']),
        (p['x'] - 14, p['y'] - 9), fontsize=8, color='C3', arrowprops=dict(arrowstyle='->', color='C3'))
a.set_aspect('equal'); a.set_xlim(-2, W + 2); a.set_ylim(-2, H + 7)
a.set_title(f"Forma del eje del cable (soldadura x={p['x']} y={p['y']} mm, {p['phi']:.0f}°)", fontsize=10)
a.legend(fontsize=7, loc='lower left'); a.set_xlabel('mm'); a.grid(alpha=.2)
Lr = 63
for s_, lab, m in ((ext, 'extracción', 'o-'), (ret, 'retracción', 'x--')):
    Ls = np.array([s['L'] for s in s_]); R = np.array([s['Rmin'] for s in s_])
    b.plot(Lr - Ls, R, m, label=lab)
b.axhline(14, color='C2', ls=':', label='R mín. recomendado 14')
b.axhline(12.5, color='C3', ls=':', label='R mín. absoluto 12.5')
b.set_xlabel('cable extraído desde el estado guardado (mm)'); b.set_ylabel('radio mínimo en el cable (mm)')
b.set_title('Radio mínimo vs. recorrido', fontsize=10); b.legend(fontsize=8); b.grid(alpha=.3)
fig.tight_layout(); fig.savefig(out, dpi=150)
