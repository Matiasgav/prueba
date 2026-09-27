"""Plano A3 de la S en el layout del usuario (planta 27/9). Orientacion como en Solid Edge: panel abajo.
z hacia la derecha desde el extremo izquierdo de la placa del conector; x hacia el panel desde la linea del flex
en la placa del conector (x = 0)."""
import json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

D = json.load(open('s_layout.json')); C = 0.1
INK, DIM, PH, HID, FX = '#111', '#1a3fbf', '#555', '#777', '#b5651d'
fig = plt.figure(figsize=(420/25.4, 297/25.4)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 420); ax.set_ylim(0, 297); ax.axis('off')
def view(ox, oy, s, z0, x0): return lambda z, x: (ox + (z - z0)*s, oy - (x - x0)*s)      # x hacia el panel = hacia abajo
def rect(P, z0, z1, x0, x1, fc='none', ec=INK, lw=0.6, ls='-'):
    (a, b), (c, d) = P(z0, x0), P(z1, x1); ax.add_patch(Rectangle((min(a, c), min(b, d)), abs(c - a), abs(d - b), facecolor=fc, edgecolor=ec, lw=lw, ls=ls))
def line(P, p, q, **kw): (a, b), (c, d) = P(*p), P(*q); ax.plot([a, c], [b, d], **kw)
def label(x, y, t, **kw): ax.text(x, y, t, **{**dict(fontsize=6.3, color=INK), **kw})
def dimh(P, za, zb, x, off, t):
    (a, y0), (b, _) = P(za, x), P(zb, x); y = y0 + off
    for xx in (a, b): ax.plot([xx, xx], [y0, y + np.sign(off)*1.2], color=DIM, lw=0.3)
    ax.annotate('', xy=(a, y), xytext=(b, y), arrowprops=dict(arrowstyle='<|-|>', color=DIM, lw=0.4, mutation_scale=5))
    ax.text((a + b)/2, y + 0.7, t, ha='center', va='bottom', fontsize=6, color=DIM)
def dimv(P, xa, xb, z, off, t):
    (x0, ya), (_, yb) = P(z, xa), P(z, xb); xx = x0 + off
    for yy in (ya, yb): ax.plot([x0, xx + np.sign(off)*1.2], [yy, yy], color=DIM, lw=0.3)
    ax.annotate('', xy=(xx, ya), xytext=(xx, yb), arrowprops=dict(arrowstyle='<|-|>', color=DIM, lw=0.4, mutation_scale=5))
    ax.text(xx + (0.7 if off > 0 else -0.7), (ya + yb)/2, t, ha='left' if off > 0 else 'right', va='center', fontsize=6, color=DIM)
def offset_curve(z, x, off):
    dz, dx = np.gradient(z), np.gradient(x); n = np.hypot(dz, dx); return z - dx/n*off, x + dz/n*off
f2 = lambda v: f'{v:.2f}'.replace('.', ',')

# marco y rotulo
ax.add_patch(Rectangle((10, 10), 400, 277, fill=False, lw=0.8, color=INK))
ax.add_patch(Rectangle((250, 10), 160, 38, fill=False, lw=0.6, color=INK))
for yy in (22, 34): ax.plot([250, 410], [yy, yy], color=INK, lw=0.4)
ax.plot([330, 330], [10, 34], color=INK, lw=0.4)
label(254, 40, 'FLEX DEL CONECTOR M12 — S LATERAL', fontsize=10, weight='bold')
label(254, 36, 'Layout del 27/9: conector a la izquierda, pestaña a la derecha · nominal', fontsize=6.8)
label(254, 28, 'Unidades: mm    Escala: indicada', fontsize=6.5); label(254, 24, 'Flex 0,2 · 2 capas · R int. mín. 2,5 · 1 mm recto', fontsize=6.5)
label(254, 15, 'x = 0: línea del flex en la placa del conector', fontsize=6.5)
label(334, 28, 'Plano: FX-M12-S-03   Rev. A', fontsize=6.5); label(334, 24, 'Formato A3', fontsize=6.5); label(334, 15, 'Orientación: panel abajo', fontsize=6.5)

nom = D['seq']['ret_a_nom'][-1]; ret = D['seq']['nom_a_ret'][-1]
NZ, NX = np.array(nom['z']), np.array(nom['x']); RZ, RX = np.array(ret['z']), np.array(ret['x'])
ZC, Z, A = D['ZC'], D['Z'], D['A']; ZT = ZC + Z

# ---------------- PLANTA 4:1 ----------------
S4 = 4.0; P = view(46, 222, S4, -1.0, -14.0)
label(22, 262, 'PLANTA (como en Solid Edge, panel abajo) — ESCALA 4:1', fontsize=8, weight='bold')
# placa del conector nominal y retraida
rect(P, 0, ZC, -0.9, 0.1, fc='#d7ebdc'); label(*P(0.4, 1.9), 'PLACA DEL CONECTOR (nominal)', fontsize=5.8)
rect(P, 0, ZC, -12.9, -11.9, ec=PH, lw=0.5, ls=(0, (6, 2, 1, 2))); label(*P(0.4, -13.4), 'placa del conector retraída (−12)', fontsize=5.5, color=PH)
# pestaña fija
rect(P, ZT, ZT + 14, -A - 0.9, -A + 0.1, fc='#d7ebdc'); label(*P(ZT + 0.5, -A - 1.6), 'PESTAÑA FIJA', fontsize=5.8)
# placa y modulo de camara
rect(P, D['cam_pcb_z0'], 46.0, D['cam_pcb_x'], D['cam_pcb_x'] + 1.0, fc='#d7ebdc'); label(*P(34.5, D['cam_pcb_x'] + 2.4), 'PLACA DE CÁMARA', fontsize=5.8)
rect(P, D['mod_z0'], D['mod_z1'], D['cam_pcb_x'] + 2.12, D['cam_pcb_x'] + 2.12 + 5.05, fc='#d9dce3', ec=HID)
label(*P(D['mod_z0'] + 0.6, D['cam_pcb_x'] + 5.5), 'MÓDULO CÁMARA', fontsize=5.5, color=HID)
# flex nominal (caras) y retraido
zz, xx = NZ, NX
for off in (C, -C):
    a, b = offset_curve(zz, xx, off); q = np.array([P(z, x) for z, x in zip(a, b)]); ax.plot(q[:, 0], q[:, 1], color=FX, lw=0.9)
line(P, (0, 0), (ZC, 0), color=FX, lw=0.5, ls=(0, (2, 1))); line(P, (ZT, -A), (ZT + 14, -A), color=FX, lw=0.5, ls=(0, (2, 1)))
q = np.array([P(z, x) for z, x in zip(RZ, RX)]); ax.plot(q[:, 0], q[:, 1], color=PH, lw=0.5, ls=(0, (6, 2, 1, 2)))
# tangencias y radios
for i, r in enumerate(D['perfil']):
    pz, px = P(r['z0'], r['x0']); ax.plot(pz, px, 'o', ms=1.6, color=INK); ax.text(pz, px + 2.2, 'T' + str(i + 1), fontsize=5.3, ha='center')
    if r['tipo'] == 'Arco':
        mid = np.arctan2(((r['x0'] + r['x1'])/2) - r['cx'], ((r['z0'] + r['z1'])/2) - r['cz'])
        pm = (r['cz'] + r['R']*np.cos(mid), r['cx'] + r['R']*np.sin(mid)); tz, tx = pm[0] + 2.0*np.cos(mid), pm[1] + 2.0*np.sin(mid)
        (a1, b1), (a2, b2) = P(*pm), P(tz, tx)
        ax.annotate('R' + f2(r['R']), xy=(a1, b1), xytext=(a2, b2), fontsize=6, color=DIM, ha='center', arrowprops=dict(arrowstyle='-|>', color=DIM, lw=0.3, mutation_scale=5))
r = D['perfil'][-1]; pz, px = P(r['z1'], r['x1']); ax.plot(pz, px, 'o', ms=1.6, color=INK); ax.text(pz, px + 2.2, 'T' + str(len(D['perfil']) + 1), fontsize=5.3, ha='center')
# cotas como en el boceto del usuario
dimh(P, 0, ZC, -A - 0.9, 26, '16,50'); dimh(P, ZC, ZT, -A - 0.9, 26, f2(Z)); dimh(P, ZT, ZT + 14, -A - 0.9, 26, '14,00')
dimv(P, -A, 0, -0.6, -8, '5,00'); dimv(P, D['cam_pcb_x'], 0, -0.6, -20, '2,50')
dimh(P, ZC, D['mod_z0'], 5.0, -8, '4,66')
dimv(P, -12.0, 0, 47.2, 6, '12,00 carrera')
label(*P(20.0, -9.8), 'juego mínimo del flex a la placa de cámara: ' + f2(min(d['gap'] for d in D['rl'] if abs(d['L'] - D['L']) < 0.26)) + ' (tolerancias)', fontsize=5.8, color=DIM)

# ---------------- DESARROLLO 4:1 ----------------
Lsum = np.cumsum([0] + [r['largo'] for r in D['perfil']])
F = lambda s, y: (262 + s*S4, 120 + y*S4)
label(262, 172, 'DESARROLLO DE LA TIRA — ESCALA 4:1', fontsize=8, weight='bold')
ax.add_patch(Rectangle(F(0, 0), Lsum[-1]*S4, 11*S4, facecolor='#f3dcc0', edgecolor=INK, lw=0.7))
for i, r in enumerate(D['perfil']):
    if r['tipo'] == 'Arco':
        ax.add_patch(Rectangle(F(Lsum[i], 0), r['largo']*S4, 11*S4, facecolor='#e8b98a', edgecolor='none', alpha=.6))
        for s_ in (Lsum[i], Lsum[i + 1]): ax.plot([F(s_, 0)[0]]*2, [F(0, -0.6)[1], F(0, 11.6)[1]], color=INK, lw=0.4, ls=(0, (6, 2, 1, 2)))
        ax.text(*F(Lsum[i] + r['largo']/2, 5.5), f"R{f2(r['R'])}\n{r['barrido']:.0f}°", fontsize=5, ha='center', va='center', rotation=90)
for s_ in Lsum: ax.text(F(s_, 0)[0], F(0, -1.2)[1], f2(s_), fontsize=5, color=DIM, ha='center', rotation=90, va='top')
label(262, 162, 'canto pestaña', fontsize=5.5); label(262 + Lsum[-1]*S4 - 22, 162, 'canto placa conector', fontsize=5.5)
ax.annotate('', xy=F(0, -5)[0:1] + (F(0, -5)[1],), xytext=(F(Lsum[-1], -5)[0], F(0, -5)[1]), arrowprops=dict(arrowstyle='<|-|>', color=DIM, lw=0.4, mutation_scale=5))
ax.text((F(0, 0)[0] + F(Lsum[-1], 0)[0])/2, F(0, -5)[1] + 0.7, f2(Lsum[-1]) + ' ± 0,25 (largo entre cantos rígidos)', ha='center', fontsize=6, color=DIM)
label(F(Lsum[-1], 0)[0] + 3, F(0, 5.5)[1], '11,00 de alto', fontsize=6, color=DIM)

# ---------------- tabla y notas ----------------
label(262, 92, 'PUNTOS DE TANGENCIA (línea media; z, x)', fontsize=6.8, weight='bold'); yy = 88
for i, r in enumerate(D['perfil']):
    t = f"T{i+1}: ({r['z0']:.3f}; {r['x0']:.3f})  {r['tipo'].upper()} "
    t += ('R%.3f %s %.1f°  c(%.3f; %.3f)' % (r['R'], 'antih.' if r['sentido'] == 'antihorario' else 'horario', r['barrido'], r['cz'], r['cx'])) if r['tipo'] == 'Arco' else 'L=%.3f' % r['largo']
    label(262, yy, t.replace('.', ','), fontsize=5.3, family='DejaVu Sans Mono'); yy -= 3.3
r = D['perfil'][-1]; label(262, yy, f"T{len(D['perfil'])+1}: ({r['z1']:.3f}; {r['x1']:.3f})".replace('.', ','), fontsize=5.3, family='DejaVu Sans Mono')
notes = ['NOTAS',
         '1. Posición nominal. Retraído: la placa del conector se desplaza 12,00 hacia atrás (fantasma).',
         '2. Pestaña fija 5,00 detrás de la línea del flex del conector; placa de cámara con su cara trasera 2,50 detrás.',
         '3. El flex sale por la cara delantera de ambas placas, con 1,00 recto antes de doblar.',
         '4. Radios en la línea media; radio interior = R − 0,10. Mínimo en toda la carrera: ' + f2(D['Rmin']) + ' (simulado).',
         '5. Largo ' + f2(D['L']) + ' ± 0,25: R ≥ 2,79 y juego a la placa de cámara ≥ 1,43 con tolerancias (conector ±0,35, carrera 12,5).',
         '6. Con menos de 18,5 el flex apoya en la placa de cámara o se quiebra: no acortar.']
for i, n in enumerate(notes): label(22, 52 - i*4.3, n, fontsize=6.4 if i else 7.5, weight='bold' if i == 0 else 'normal')
for ext in ('pdf', 'png'): fig.savefig(f'planos/S_conector_layout27_plano.{ext}', dpi=200 if ext == 'png' else None)
print('ok')
