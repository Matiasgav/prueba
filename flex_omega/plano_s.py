"""Plano de la S del conector (posicion nominal) en hoja A3: planta 4:1, vista desde atras 4:1,
desarrollo del flex 4:1, detalle de la salida 10:1, tabla de coordenadas, notas y rotulo.
Convencion: el flex va por la cara delantera (hacia el panel) de la pestaña fija y de la placa del conector."""
import json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc, Polygon, Circle

D = json.load(open('s2d.json'))
C = 0.1                                  # medio espesor del flex
B = 6.65                                 # cuerpo del conector detras del panel (nominal)
XFC = -B                                 # cara delantera de la placa del conector (nominal)
XFT = XFC - 6.0                          # cara delantera de la pestaña fija
XLC, XLT = XFC - C, XFT - C              # linea media del flex en cada placa
SH = XLT - D['XT']                       # corrimiento respecto de la simulacion (flex en el plano medio)
Z0 = 16.0; Z1 = Z0 + D['Z']; ZT = f"{D['Z']:.2f}".replace('.', ',')
Y0, H = 0.25, 11.9                       # cinta y techo
YF0, YF1 = Y0 + 0.35, Y0 + 11.35         # tira de flex de 11 mm
ROWS = [dict(r, x0=r['x0'] + SH, x1=r['x1'] + SH, **({'cx': r['cx'] + SH} if r['tipo'] == 'Arco' else {})) for r in D['perfil']]
nom = D['seq']['ret_a_nom'][-1]; ret = D['seq']['nom_a_ret'][-1]
NZ, NX = np.array(nom['z']), np.array(nom['x']) + SH
RZ, RX = np.array(ret['z']), np.array(ret['x']) + SH

fig = plt.figure(figsize=(420/25.4, 297/25.4)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 420); ax.set_ylim(0, 297); ax.axis('off')
INK, THIN, PH, DIM, HID = '#111', 0.35, '#555', '#1a3fbf', '#777'
TXT = dict(fontsize=7, family='DejaVu Sans', color=INK)

def view(ox, oy, s, z0, x0):
    return lambda z, x: (ox + (z - z0)*s, oy + (x - x0)*s)

def poly(P, pts, **kw):
    q = [P(*p) for p in pts]; ax.add_patch(Polygon(q, closed=kw.pop('closed', True), fill=kw.pop('fill', False), **kw))

def line(P, a, b, **kw):
    (x1, y1), (x2, y2) = P(*a), P(*b); ax.plot([x1, x2], [y1, y2], **kw)

def rect(P, z0, z1, x0, x1, **kw):
    poly(P, [(z0, x0), (z1, x0), (z1, x1), (z0, x1)], **kw)

def dim_h(P, za, zb, x, off, text, ext_from=None):
    """Cota horizontal (en z) a la altura de modelo x, desplazada off mm de papel."""
    (xa, ya), (xb, yb) = P(za, x), P(zb, x); y = ya + off
    for xx, yy in ((xa, ya), (xb, yb)):
        y0 = P(0, ext_from)[1] if ext_from is not None else yy
        ax.plot([xx, xx], [y0 + np.sign(off)*1, y + np.sign(off)*1.5], color=DIM, lw=0.3)
    ax.annotate('', xy=(xa, y), xytext=(xb, y), arrowprops=dict(arrowstyle='<|-|>', color=DIM, lw=0.4, mutation_scale=6))
    ax.text((xa + xb)/2, y + 0.8, text, ha='center', va='bottom', fontsize=6.5, color=DIM)

def dim_v(P, xa, xb, z, off, text, side='right'):
    (za_, ya), (zb_, yb) = P(z, xa), P(z, xb); xx = za_ + off
    for yy in (ya, yb): ax.plot([za_ + np.sign(off)*1, xx + np.sign(off)*1.5], [yy, yy], color=DIM, lw=0.3)
    ax.annotate('', xy=(xx, ya), xytext=(xx, yb), arrowprops=dict(arrowstyle='<|-|>', color=DIM, lw=0.4, mutation_scale=6))
    ax.text(xx + (0.8 if side == 'right' else -0.8), (ya + yb)/2, text, ha='left' if side == 'right' else 'right', va='center', fontsize=6.5, color=DIM, rotation=0)

def label(x, y, t, **kw): ax.text(x, y, t, **{**TXT, **kw})

# ---------------- hoja, marco y rotulo ----------------
ax.add_patch(Rectangle((10, 10), 400, 277, fill=False, lw=0.8, color=INK))
tb = (250, 10, 160, 38); ax.add_patch(Rectangle(tb[:2], tb[2], tb[3], fill=False, lw=0.6, color=INK))
for yy in (22, 34): ax.plot([250, 410], [yy, yy], color=INK, lw=0.4)
ax.plot([330, 330], [10, 34], color=INK, lw=0.4)
label(254, 40, 'FLEX DEL CONECTOR M12 — S LATERAL', fontsize=10, weight='bold')
label(254, 36, 'Rigid-flex · posición nominal · flex de canto, 11 mm de alto', fontsize=7)
label(254, 28, 'Unidades: mm    Escala: indicada en cada vista', fontsize=6.5)
label(254, 24, 'Flex: poliimida 2 capas, 0,2 mm · R int. mín. 3,0', fontsize=6.5)
label(254, 15, 'Material rígido: FR4 1,0 mm', fontsize=6.5)
label(334, 28, 'Plano: FX-M12-S-01   Rev. A', fontsize=6.5)
label(334, 24, 'Formato A3', fontsize=6.5)
label(334, 15, 'Proyección: vistas alineadas en z', fontsize=6.5)

# ---------------- PLANTA 4:1 ----------------
S4 = 4.0; P = view(22, 142, S4, -1.0, -22.5)
label(22, 250, 'PLANTA (vista de arriba) — ESCALA 4:1', fontsize=8, weight='bold')
# panel, limites de 52, borde de mainboard
line(P, (-1, 0), (54, 0), color=INK, lw=0.9); label(*P(-0.8, 0.5), 'CARA INTERIOR DEL PANEL (x = 0)', fontsize=6)
for zz in (0, 52): line(P, (zz, -22.5), (zz, 1.5), color=PH, lw=0.4, ls=(0, (8, 2, 1, 2)))
line(P, (Z0, -20.5), (52, -20.5), color=PH, lw=0.5, ls=(0, (4, 2))); label(*P(16.3, -20.2), 'borde de la mainboard en x ≤ −20,50', fontsize=5.5, color=PH)
# camara (referencia)
rect(P, 21.75, 30.25, -5.05, 0, edgecolor=HID, lw=0.4, ls=(0, (3, 2)))
line(P, (11.25, -5.11), (30.25, -5.11), color=HID, lw=0.4, ls=(0, (3, 2))); label(*P(22.3, -2.8), 'cámara (ref.)', fontsize=5.5, color=HID)
# pestaña fija
rect(P, 4.0, Z0, XFT - 1.0, XFT, edgecolor=INK, lw=0.7, fill=True, facecolor='#d7ebdc')
label(*P(4.3, XFT - 2.4), 'PESTAÑA FIJA (FR4 1,0)', fontsize=6)
# placa del conector nominal + cuerpo M12 + rosca
rect(P, Z1, 52.0, XFC - 1.0, XFC, edgecolor=INK, lw=0.7, fill=True, facecolor='#d7ebdc')
rect(P, 38.0, 50.0, XFC, 0, edgecolor=INK, lw=0.5)
rect(P, 38.0, 50.0, 0, 1.5, edgecolor=HID, lw=0.4, ls=(0, (3, 2)))
label(*P(38.4, -3.4), 'M12 (cuerpo detrás del panel)', fontsize=5.5)
label(*P(33.0, XFC - 2.9), 'PLACA DEL CONECTOR (nominal)', fontsize=6)
# placa del conector retraida (fantasma)
rect(P, Z1, 52.0, XFC - 13.0, XFC - 12.0, edgecolor=PH, lw=0.5, ls=(0, (6, 2, 1, 2)))
label(*P(33.0, XFC - 11.7), 'placa del conector retraída (−12,00)', fontsize=5.5, color=PH)
# flex nominal: dos caras
def offset_curve(z, x, off):
    dz, dx = np.gradient(z), np.gradient(x); n = np.hypot(dz, dx); return z - dx/n*off, x + dz/n*off
zz = np.concatenate([[Z0 - 0.0], NZ[1:-1], [Z1]]); xx = np.concatenate([[XLT], NX[1:-1], [XLC]])
for off in (C, -C):
    a, b = offset_curve(zz, xx, off); q = np.array([P(z, x) for z, x in zip(a, b)]); ax.plot(q[:, 0], q[:, 1], color='#b5651d', lw=0.8)
# flex dentro de las placas (capa delantera)
for (za, zb, xl) in ((4.0, Z0, XLT), (Z1, 52.0, XLC)):
    line(P, (za, xl), (zb, xl), color='#b5651d', lw=0.5, ls=(0, (2, 1)))
# flex retraido fantasma
q = np.array([P(z, x) for z, x in zip(RZ, RX)]); ax.plot(q[:, 0], q[:, 1], color=PH, lw=0.5, ls=(0, (6, 2, 1, 2)))
# centros y radios
for i, r in enumerate(ROWS):
    if r['tipo'] != 'Arco': continue
    cz, cx = r['cz'], r['cx']
    if r['R'] < 10:
        pz, px = P(cz, cx); ax.plot([pz - 2, pz + 2], [px, px], color=DIM, lw=0.3); ax.plot([pz, pz], [px - 2, px + 2], color=DIM, lw=0.3)
    mid = np.arctan2(((r['x0'] + r['x1'])/2) - cx, ((r['z0'] + r['z1'])/2) - cz)
    pm = (cz + r['R']*np.cos(mid), cx + r['R']*np.sin(mid))
    tz, tx = pm[0] + 2.2*np.cos(mid), pm[1] + 2.2*np.sin(mid)
    if r['R'] > 10: tz, tx = pm[0], pm[1] + 2.5
    (a1, b1), (a2, b2) = P(*pm), P(tz, tx)
    ax.annotate(f"R{r['R']:.2f}".replace('.', ','), xy=(a1, b1), xytext=(a2, b2), fontsize=6.5, color=DIM,
                arrowprops=dict(arrowstyle='-|>', color=DIM, lw=0.3, mutation_scale=5), ha='center')
# puntos de tangencia numerados
for i, r in enumerate(ROWS):
    pz, px = P(r['z0'], r['x0']); ax.plot(pz, px, 'o', ms=1.6, color=INK)
    ax.text(pz, px - 3.2, 'T' + str(i + 1), fontsize=5.5, ha='center', color=INK)
pz, px = P(ROWS[-1]['z1'], ROWS[-1]['x1']); ax.plot(pz, px, 'o', ms=1.6, color=INK); ax.text(pz, px - 3.2, 'T' + str(len(ROWS) + 1), fontsize=5.5, ha='center')
# cotas
dim_h(P, 0, 52, 0, 14, '52,00 (ancho disponible)')
dim_h(P, 0, Z0, XFT - 1.0, -22, '16,00')
dim_h(P, Z0, Z1, XFT - 1.0, -22, ZT + ' (separación entre cantos)')
dim_h(P, Z1, 52, 0, 5, f'{52 - Z1:.2f}'.replace('.', ','))
dim_v(P, XFC, 0, 52.2, 3, '6,65')
dim_v(P, XFT, XFC, 3.0, -14, '6,00', side='left')
dim_v(P, XFC - 12, XFC, 52.2, 11, '12,00\ncarrera')
dim_v(P, XFT, 0, -0.5, -8, '12,65', side='left')

# ---------------- VISTA DESDE ATRAS 4:1 (alineada en z) ----------------
V = view(22, 62, S4, -1.0, 0.0)
label(22, 118, 'VISTA DESDE ATRÁS (mirando hacia el panel) — ESCALA 4:1', fontsize=8, weight='bold')
line(V, (-1, 0), (54, 0), color=INK, lw=0.8); line(V, (-1, Y0), (54, Y0), color=PH, lw=0.3)
line(V, (-1, H), (54, H), color=PH, lw=0.5, ls=(0, (8, 2, 1, 2))); label(*V(-0.8, H + 0.4), 'techo del chasis (11,9)', fontsize=5.5, color=PH)
label(*V(-0.8, -1.2), 'piso · cinta 0,25', fontsize=5.5, color=PH)
# pestaña: con muesca abajo por donde entra el flex desde la mainboard
poly(V, [(4, Y0 + 4.2), (15, Y0 + 4.2), (15, Y0), (Z0, Y0), (Z0, H), (4, H)], edgecolor=INK, lw=0.7, fill=True, facecolor='#d7ebdc')
rect(V, 4.5, 14.5, Y0, Y0 + 4.2, edgecolor='#b5651d', lw=0.5, ls=(0, (2, 1)))
label(*V(4.6, Y0 + 1.6), 'entra el flex de la mainboard (dobla R3)', fontsize=5, color='#b5651d')
# tira de flex entre cantos
rect(V, Z0, Z1, YF0, YF1, edgecolor='#b5651d', lw=0.8, fill=True, facecolor='#f3dcc0')
label(*V(19.5, 6.0), 'FLEX DE CANTO', fontsize=6, color='#8a4a12')
# placa del conector y M12
rect(V, Z1, 52, Y0, H, edgecolor=INK, lw=0.7, fill=True, facecolor='#d7ebdc')
cz, cy = V(44.0, (Y0 + H)/2); ax.add_patch(Circle((cz, cy), 6*S4, fill=False, color=HID, lw=0.4, ls=(0, (3, 2))))
label(*V(41.2, (Y0 + H)/2 - 0.3), 'M12 Ø12', fontsize=5.5, color=HID)
dim_v(V, YF0, YF1, Z0 + 0.2, -8, '11,00', side='left')
dim_v(V, 0, Y0 + 0.35, 13.0, -3, '0,60', side='left')
dim_v(V, 0, H, 53.0, 6, '11,90')
dim_h(V, Z0, Z1, 0, -8, ZT)

# ---------------- DESARROLLO DEL FLEX 4:1 ----------------
Lsum = np.cumsum([0] + [r['largo'] for r in ROWS])
F = view(262, 190, S4, 0.0, 0.0)
label(262, 250, 'DESARROLLO DE LA TIRA (plano) — ESCALA 4:1', fontsize=8, weight='bold')
rect(F, 0, Lsum[-1], 0, 11.0, edgecolor=INK, lw=0.7, fill=True, facecolor='#f3dcc0')
for i, r in enumerate(ROWS):
    if r['tipo'] == 'Arco':
        ax.add_patch(Rectangle(F(Lsum[i], 0), r['largo']*S4, 11*S4, fill=True, facecolor='#e8b98a', edgecolor='none', alpha=.6))
        for s_ in (Lsum[i], Lsum[i + 1]): line(F, (s_, -0.6), (s_, 11.6), color=INK, lw=0.4, ls=(0, (6, 2, 1, 2)))
        hacia = 'hacia el panel' if r['sentido'] == 'antihorario' else 'hacia atrás'
        label(*F(Lsum[i] + r['largo']/2, 5.5), f"R{r['R']:.2f}\n{r['barrido']:.1f}°\n{hacia}".replace('.', ','), fontsize=5.3, ha='center', va='center', rotation=90)
label(*F(-0.2, 11.8), 'canto pestaña', fontsize=5.5); label(*F(Lsum[-1] - 4.5, 11.8), 'canto placa conector', fontsize=5.5)
for i in range(len(Lsum)):
    line(F, (Lsum[i], 0), (Lsum[i], -1.2), color=DIM, lw=0.3)
    ax.text(*F(Lsum[i], -2.6), f"{Lsum[i]:.2f}".replace('.', ','), fontsize=5.3, color=DIM, ha='center', rotation=90, va='top')
dim_h(F, 0, Lsum[-1], 0, -26, f"{Lsum[-1]:.2f} ± 0,25 (largo entre cantos rígidos)".replace('.', ','))
dim_v(F, 0, 11, Lsum[-1], 5, '11,00')

# ---------------- DETALLE A 10:1: salida en la placa del conector ----------------
S10 = 10.0; E = view(262, 86, S10, 28.5, -8.9)
label(262, 128, 'DETALLE A — SALIDA EN LA PLACA DEL CONECTOR — ESCALA 10:1', fontsize=8, weight='bold')
rect(E, Z1, 36.0, XFC - 1.0, XFC, edgecolor=INK, lw=0.7, fill=True, facecolor='#d7ebdc')
rect(E, Z1, 36.0, XFC - 0.2, XFC, edgecolor='#b5651d', lw=0.5, fill=True, facecolor='#f3dcc0')
for off in (C, -C):
    a_, b_ = offset_curve(zz, xx, off); m = (a_ > 28.6) & (a_ <= Z1)
    q = np.array([E(z, x) for z, x in zip(a_[m], b_[m])]); ax.plot(q[:, 0], q[:, 1], color='#b5651d', lw=0.9)
line(E, (Z1 - 1.0, XLC - 0.6), (Z1 - 1.0, XLC + 0.6), color=INK, lw=0.4, ls=(0, (6, 2, 1, 2)))
label(*E(33.2, XFC - 0.7), 'FR4 1,00', fontsize=6)
label(*E(32.4, XFC + 0.35), 'capa de flex en la cara delantera', fontsize=6, color='#8a4a12')
label(*E(28.6, XFC + 0.9), '→ hacia el panel', fontsize=6, color=INK)
label(*E(29.1, XLC - 0.9), 'inicio del doblez', fontsize=5.5, color=INK)
dim_h(E, Z1 - 1.0, Z1, XFC - 1.0, -8, '1,00 recto')
dim_v(E, XFC - 1.0, XFC, 36.0, 5, '1,00')
dim_v(E, XFC - 0.2, XFC, 36.0, 15, '0,20')

# ---------------- tabla de coordenadas y notas ----------------
label(262, 76, 'PUNTOS DE TANGENCIA (línea media, coordenadas z; x desde borde izq. y panel)', fontsize=6.5, weight='bold')
yy = 72
for i, r in enumerate(ROWS):
    t = f"T{i+1}: ({r['z0']:.3f}; {r['x0']:.3f})   {r['tipo'].upper()} {('R%.3f %s %.2f°' % (r['R'], 'antih.' if r['sentido']=='antihorario' else 'horario', r['barrido'])) if r['tipo']=='Arco' else 'L=%.3f' % r['largo']}"
    if r['tipo'] == 'Arco': t += f"   centro ({r['cz']:.3f}; {r['cx']:.3f})"
    label(262, yy, t.replace('.', ','), fontsize=5.6, family='DejaVu Sans Mono'); yy -= 3.4
r = ROWS[-1]; label(262, yy, f"T{len(ROWS)+1}: ({r['z1']:.3f}; {r['x1']:.3f})".replace('.', ','), fontsize=5.6, family='DejaVu Sans Mono')
notes = ['NOTAS', '1. Posición nominal. Retraído: la placa del conector se desplaza 12,00 hacia atrás (fantasma).',
         '2. La cara delantera de la pestaña fija queda 6,00 detrás de la cara delantera de la placa del conector.',
         '3. El flex sale por la cara delantera de ambas placas, con 1,00 recto antes de doblar.',
         '4. Radios de la tabla en la línea media; radio interior = R − 0,10. Mínimo en carrera: 3,10 (simulado).',
         '5. Desarrollo 17,75 ± 0,25 verificado con cuerpo M12 de 6,30 a 7,00 y carrera de 12,5.',
         '6. Sin pared: la S no pasa de x = −6,2 (≥ 0,9 del flex de la cámara).',
         '7. Pestaña fija: su canto de salida (z 16,00) queda 15,50 a la izquierda del canto de la placa del conector (z 31,50).']
yy = 118
for i, n in enumerate(notes): label(22, 50 - i*4.2, n, fontsize=6.5 if i else 7.5, weight='bold' if i == 0 else 'normal')
for ext in ('pdf', 'svg', 'png'):
    fig.savefig(f'planos/S_conector_plano.{ext}', dpi=200 if ext == 'png' else None)
print('ok', SH, XFT, XFC)
