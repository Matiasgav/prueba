import json, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from rod import W, H, r
d = json.load(open(sys.argv[1])); out = sys.argv[2]; Lmin, Lmax = float(sys.argv[3]), float(sys.argv[4])
p = d['pose']; ret = d['retract']; ext = d['extract']
fig, (a, b) = plt.subplots(1, 2, figsize=(13, 4.8), gridspec_kw=dict(width_ratios=[1.35, 1]))
a.add_patch(Rectangle((0, 0), W, H, fill=False, lw=1.5, ec='k'))
a.add_patch(Rectangle((-7, H - 2 * r), 7, 2 * r, fill=False, lw=1, ec='k', ls='--'))
a.text(-6.5, H + 1, 'salida', fontsize=8)
cm = plt.cm.viridis
Ls = np.linspace(Lmin, Lmax, 6)
for i, Lt in enumerate(Ls):
    s = min((s for s in ext if s['ok']), key=lambda s: abs(s['L'] - Lt))
    X = np.array(s['X']); c = cm(i / 5)
    a.plot(X[:, 0], X[:, 1], color=c, lw=2,
           label=f"extraído {Lmax - s['L']:4.1f} mm  (L int {s['L']:.0f}, Rmin {s['Rmin']:.1f})")
    a.plot(X[:, 0], X[:, 1], color=c, lw=15, alpha=0.05, solid_capstyle='round')
a.plot(p['x'], p['y'], 's', ms=10, color='C3')
a.annotate('SOLDADURA\n(cable sale hacia la derecha)', (p['x'], p['y']), (p['x'] + 6, p['y'] + 7),
           fontsize=8, color='C3', arrowprops=dict(arrowstyle='->', color='C3'))
a.set_aspect('equal'); a.set_xlim(-8, W + 2); a.set_ylim(-2, H + 3)
a.set_title('Lazo rodante: forma del eje del cable a lo largo de la carrera', fontsize=10)
a.legend(fontsize=7, loc='center right', bbox_to_anchor=(1.0, 0.45)); a.set_xlabel('mm'); a.grid(alpha=.2)
for s_, lab, m in ((ext, 'extracción', '-'), (ret, 'retracción', '--')):
    q = [s for s in s_ if s['ok']]
    b.plot([Lmax - s['L'] for s in q], [s['Rmin'] for s in q], m, label=lab)
b.axvspan(0, 60, color='C2', alpha=0.08, label='60 mm requeridos')
b.set_xlim(-3, Lmax - 27); b.set_ylim(0, 12)
b.set_xlabel('cable extraído (mm)'); b.set_ylabel('radio mínimo en el cable (mm)')
b.set_title('Radio mínimo vs. carrera', fontsize=10); b.legend(fontsize=8); b.grid(alpha=.3)
fig.tight_layout(); fig.savefig(out, dpi=150)
