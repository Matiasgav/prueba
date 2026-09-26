"""Plano A3 de sujecion (LED A): planta de la zona camara/LED/pestaña, corte A-A por el tornillo del apilado,
corte B-B por el conector de la camara, cadena de tolerancias, lista de piezas y secuencia de montaje.
Coordenadas: x desde la cara interior del panel (negativo hacia atras), z en los 52 mm, y sobre el piso del chasis."""
import numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle

INK, DIM, PH, HID = '#111', '#1a3fbf', '#555', '#777'
PCB, FLEX, CAM, MET, FOAM, CHA = '#d7ebdc', '#f3dcc0', '#c9ccd4', '#cfd3d8', '#f2c4d6', '#e4e7ec'
fig = plt.figure(figsize=(420/25.4, 297/25.4)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 420); ax.set_ylim(0, 297); ax.axis('off')
def view(ox, oy, s, a0, b0): return lambda a, b: (ox + (a - a0)*s, oy + (b - b0)*s)
def rect(P, a0, a1, b0, b1, fc='none', ec=INK, lw=0.6, ls='-', hatch=None):
    (x0, y0), (x1, y1) = P(a0, b0), P(a1, b1)
    ax.add_patch(Rectangle((min(x0, x1), min(y0, y1)), abs(x1 - x0), abs(y1 - y0), facecolor=fc, edgecolor=ec, lw=lw, ls=ls, hatch=hatch))
def line(P, a, b, **kw): (x1, y1), (x2, y2) = P(*a), P(*b); ax.plot([x1, x2], [y1, y2], **kw)
def label(x, y, t, **kw): ax.text(x, y, t, **{**dict(fontsize=6.3, color=INK), **kw})
def lab(P, a, b, t, **kw): label(*P(a, b), t, **kw)
def dim(P, pa, pb, off, text, horiz=True):
    (xa, ya), (xb, yb) = P(*pa), P(*pb)
    if horiz:
        y = ya + off
        for xx, yy in ((xa, ya), (xb, yb)): ax.plot([xx, xx], [yy, y + np.sign(off)*1.2], color=DIM, lw=0.3)
        ax.annotate('', xy=(xa, y), xytext=(xb, y), arrowprops=dict(arrowstyle='<|-|>', color=DIM, lw=0.4, mutation_scale=5))
        ax.text((xa + xb)/2, y + 0.7, text, ha='center', va='bottom', fontsize=6, color=DIM)
    else:
        x = xa + off
        for xx, yy in ((xa, ya), (xb, yb)): ax.plot([xx, x + np.sign(off)*1.2], [yy, yy], color=DIM, lw=0.3)
        ax.annotate('', xy=(x, ya), xytext=(x, yb), arrowprops=dict(arrowstyle='<|-|>', color=DIM, lw=0.4, mutation_scale=5))
        ax.text(x + (0.7 if off > 0 else -0.7), (ya + yb)/2, text, ha='left' if off > 0 else 'right', va='center', fontsize=6, color=DIM)
def callout(P, pt, txt_pt, t):
    (a, b), (c, d) = P(*pt), P(*txt_pt)
    ax.annotate(t, xy=(a, b), xytext=(c, d), fontsize=6, color=INK, arrowprops=dict(arrowstyle='-|>', color=INK, lw=0.3, mutation_scale=5))

# marco y rotulo
ax.add_patch(Rectangle((10, 10), 400, 277, fill=False, lw=0.8, color=INK))
ax.add_patch(Rectangle((250, 10), 160, 38, fill=False, lw=0.6, color=INK))
for yy in (22, 34): ax.plot([250, 410], [yy, yy], color=INK, lw=0.4)
ax.plot([330, 330], [10, 34], color=INK, lw=0.4)
label(254, 40, 'SUJECIÓN CÁMARA · LED · PESTAÑA DE LA S', fontsize=10, weight='bold')
label(254, 36, 'Opción LED A (placa + B2B) · posición nominal', fontsize=7)
label(254, 28, 'Unidades: mm    Escala: indicada en cada vista', fontsize=6.5)
label(254, 24, 'Tornillería métrica M1.6 · FR4 1,0 · flex 0,2', fontsize=6.5)
label(254, 15, 'Coordenadas: x desde el panel, z desde el borde izq.', fontsize=6.5)
label(334, 28, 'Plano: FX-M12-S-02   Rev. A', fontsize=6.5); label(334, 24, 'Formato A3', fontsize=6.5)
label(334, 15, 'Ref.: FX-M12-S-01 (S del conector)', fontsize=6.5)

# ---------------- PLANTA 4:1 (z horizontal, x vertical) ----------------
S4 = 4.0; P = view(24, 150, S4, -1.0, -17.5)
label(24, 247, 'PLANTA DE LA ZONA CÁMARA / LED — ESCALA 4:1', fontsize=8, weight='bold')
line(P, (-1, 0), (33, 0), color=INK, lw=0.9); lab(P, -0.8, 0.4, 'CARA INTERIOR DEL PANEL (x = 0)', fontsize=5.5)
line(P, (0, -17.5), (0, 1.5), color=PH, lw=0.4, ls=(0, (8, 2, 1, 2))); lab(P, 0.2, -17.2, 'z = 0', fontsize=5.5, color=PH)
rect(P, 21.75, 30.25, -5.05, 0, fc=CAM); lab(P, 23.2, -2.6, 'CÁMARA (pegada al panel)', fontsize=5.5)
line(P, (11.25, -5.11), (30.25, -5.11), color='#8a4a12', lw=1.0); lab(P, 17.4, -5.9, 'cola de la cámara', fontsize=5.2, color='#8a4a12')
rect(P, 11.25, 17.25, -5.05, -4.7, fc='#e8e2b8', lw=0.4)
rect(P, 13.2, 15.2, -6.17, -5.17, fc=MET, lw=0.4)
rect(P, 3.6, 16.0, -7.17, -6.17, fc=PCB); lab(P, 3.8, -8.1, 'SECCIÓN DE CÁMARA (fija)', fontsize=5.5)
rect(P, 6.0, 21.5, -4.17, -3.57, fc=PCB); lab(P, 6.2, -3.25, 'PLACA DEL LED 0,6', fontsize=5.5)
rect(P, 6.5, 9.5, -6.17, -4.17, fc=MET, lw=0.4); lab(P, 6.5, -5.45, 'B2B', fontsize=5)
rect(P, 17.8, 20.8, -3.57, -1.07, fc='#fff1a8'); lab(P, 17.9, -2.5, 'LED', fontsize=5.5)
rect(P, 11.5, 17.0, -4.7, -4.17, fc=FOAM, lw=0.4); callout(P, (14.2, -4.43), (13.0, -10.6), 'ESPUMA 0,8→0,5')
rect(P, 20.9, 21.5, -3.57, 0, fc=CHA); callout(P, (21.2, -1.8), (24.0, -12.8), 'NERVIO DEL PANEL\n(apoyo + barrera de luz)')
# tornillo del apilado
rect(P, 9.55, 11.05, -7.97, -7.17, fc='#9aa3ad', lw=0.4); rect(P, 9.9, 10.7, -7.17, -1.47, fc='#b9c0c9', lw=0.4)
rect(P, 9.0, 11.6, -6.17, -4.17, fc='#e9d27a', ec=INK, lw=0.4)
rect(P, 8.6, 12.0, -3.57, 0, fc=CHA, lw=0.4)
callout(P, (10.3, -7.8), (-0.6, -10.6), 'TORNILLO M1.6×6\n+ SEPARADOR 2,0\n+ BUJE EN EL PANEL')
# pestaña de la S con sus guias y arranque de la S
rect(P, 4.0, 16.0, -13.65, -12.65, fc=PCB); lab(P, 4.3, -14.6, 'PESTAÑA FIJA DE LA S', fontsize=5.5)
rect(P, 14.6, 16.0, -16.0, -13.7, fc=CHA, lw=0.4); rect(P, 2.9, 4.3, -16.0, -13.7, fc=CHA, lw=0.4)
callout(P, (15.3, -15.0), (17.5, -16.8), 'POSTES CON RANURA (guía vertical)')
d2 = json.load(open('s2d.json')); f = d2['seq']['ret_a_nom'][-1]
q = np.array([P(z, x) for z, x in zip(f['z'], f['x']) if z <= 33]); ax.plot(q[:, 0], q[:, 1], color='#b5651d', lw=0.9)
lab(P, 25.0, -15.2, 'S del conector (ver FX-M12-S-01)', fontsize=5.2, color='#8a4a12')
# cotas planta
dim(P, (0, -13.65), (10.3, -13.65), -18, '10,30 (eje del tornillo)')
dim(P, (4.0, -16.0), (16.0, -16.0), -15, '12,00 pestaña')
dim(P, (6.0, -3.57), (21.5, -3.57), 26, '15,50 placa del LED')
dim(P, (17.8, 0), (26.0, 0), 8, '8,20 (LED → lente)')
dim(P, (32.0, -7.17), (32.0, -6.17), 5, '1,00', horiz=False)
dim(P, (32.0, -3.57), (32.0, 0), 5, '3,57', horiz=False)
dim(P, (32.0, -6.17), (32.0, -4.17), 16, '2,00 B2B', horiz=False)

# ---------------- CORTE A-A 6:1 (plano z = 10,3; x horizontal, y vertical) ----------------
S6 = 6.0; A = view(24, 34, S6, -9.0, 0.0)
label(24, 118, 'CORTE A-A (por el tornillo, z = 10,30) — ESCALA 6:1', fontsize=8, weight='bold')
line(A, (-9, 0), (1.5, 0), color=INK, lw=0.8); line(A, (-9, 11.9), (1.5, 11.9), color=PH, lw=0.5, ls=(0, (8, 2, 1, 2)))
rect(A, -9, 1.5, 0, 0.25, fc='#f0e0a0', lw=0.3); lab(A, -8.9, -1.2, 'piso · cinta 0,25', fontsize=5.3, color=PH)
lab(A, -8.9, 12.2, 'tapa (11,9)', fontsize=5.3, color=PH)
rect(A, 0, 1.5, -0.5, 12.4, fc=CHA, hatch='///'); lab(A, 0.1, 12.6, 'PANEL', fontsize=5.5)
rect(A, -7.17, -6.17, 0.25, 11.9, fc=PCB); lab(A, -7.15, 12.2, 'sección', fontsize=5.3)
rect(A, -4.17, -3.57, 0.85, 8.25, fc=PCB); lab(A, -3.45, 2.0, 'placa LED', fontsize=5.3)
rect(A, -3.57, 0, 7.85 - 1.7, 7.85 + 1.7, fc=CHA, hatch='///')
rect(A, -6.17, -4.17, 7.85 - 1.3, 7.85 + 1.3, fc='#e9d27a')
rect(A, -7.97, -7.17, 7.85 - 1.5, 7.85 + 1.5, fc='#9aa3ad'); rect(A, -7.17, -1.47, 7.85 - 0.8, 7.85 + 0.8, fc='#b9c0c9', lw=0.4)
rect(A, -6.17, -4.17, 2.25, 6.75, fc=MET, lw=0.4); lab(A, -6.0, 4.3, 'B2B', fontsize=5.3)
callout(A, (-7.6, 9.2), (-8.9, 10.7), 'M1.6×6')
callout(A, (-5.2, 9.0), (-6.6, 13.4), 'separador 2,0')
callout(A, (-1.8, 9.4), (-3.0, 13.4), 'buje del panel')
dim(A, (-7.17, 0.25), (-6.17, 0.25), -9, '1,00'); dim(A, (-6.17, 0.25), (-4.17, 0.25), -9, '2,00')
dim(A, (-4.17, 0.25), (-3.57, 0.25), -17, '0,60'); dim(A, (-3.57, 0.25), (0, 0.25), -9, '3,57')
dim(A, (-7.97, 7.85), (-7.97, 0), -6, '7,85', horiz=False)

# ---------------- CORTE B-B 6:1 (plano z = 14,2 por el conector de la camara) ----------------
Bv = view(118, 34, S6, -9.0, 0.0)
label(118, 118, 'CORTE B-B (por el conector de la cámara, z = 14,20) — ESCALA 6:1', fontsize=8, weight='bold')
line(Bv, (-9, 0), (1.5, 0), color=INK, lw=0.8); line(Bv, (-9, 11.9), (1.5, 11.9), color=PH, lw=0.5, ls=(0, (8, 2, 1, 2)))
rect(Bv, -9, 1.5, 0, 0.25, fc='#f0e0a0', lw=0.3)
rect(Bv, 0, 1.5, -0.5, 12.4, fc=CHA, hatch='///')
rect(Bv, -7.17, -6.17, 0.25, 11.9, fc=PCB)
rect(Bv, -6.17, -5.17, 2.05, 8.05, fc=MET); lab(Bv, -6.1, 5.0, 'AXT', fontsize=5.3)
rect(Bv, -5.17, -5.05, 0.25, 9.85, fc='#e39a4f', lw=0.3)
rect(Bv, -5.05, -4.7, 0.25, 9.85, fc='#e8e2b8', lw=0.4)
rect(Bv, -4.7, -4.17, 1.75, 8.75, fc=FOAM, lw=0.4)
rect(Bv, -4.17, -3.57, 0.85, 8.25, fc=PCB)
callout(Bv, (-5.1, 9.6), (-8.9, 13.4), 'cola de la cámara 0,12 + FR4 0,35')
callout(Bv, (-4.43, 7.0), (-3.2, 10.4), 'espuma 0,8 libre → 0,53')
lab(Bv, -3.4, 4.0, 'la espuma aprieta\nla cola contra\nel AXT', fontsize=5.3)
dim(Bv, (-7.17, 0.25), (-6.17, 0.25), -9, '1,00'); dim(Bv, (-6.17, 0.25), (-5.17, 0.25), -17, '1,00 AXT')
dim(Bv, (-5.17, 0.25), (-4.7, 0.25), -9, '0,47'); dim(Bv, (-4.7, 0.25), (-4.17, 0.25), -25, '0,53')

# ---------------- tolerancias, piezas, montaje ----------------
x0 = 262; y = 244
label(x0, y, 'CADENA DE TOLERANCIAS (hueco para la espuma, z = 14,2)', fontsize=7, weight='bold'); y -= 4.5
for t in ('sección FR4 1,00 ±0,10', 'AXT apareado 1,00 ±0,05', 'cola 0,12 ±0,03 + FR4 0,35 ±0,05',
          'B2B apareado 2,00 ±0,10 (define la placa del LED)', '→ hueco nominal 0,53; rango ≈ 0,25 a 0,80',
          '→ espuma de 0,8 libre: trabaja comprimida entre 0 y 70 %'):
    label(x0, y, t, fontsize=6); y -= 3.6
y -= 2; label(x0, y, 'PIEZAS', fontsize=7, weight='bold'); y -= 4.5
for t in ('1  Tornillo M1.6 × 6, cabeza cilíndrica, del lado de atrás',
          '2  Separador M1.6 de 2,0 (igual a la altura del B2B)',
          '3  Buje en el panel Ø3,4 × 3,57 con inserto o rosca formada',
          '4  Conector B2B apilable, 2,0 apareado (DF40 / SlimStack / A35S)',
          '5  Espuma (Poron o similar) 0,8 × 5,5 × 7, adhesiva a la placa del LED',
          '6  Nervio del panel 0,6 × 7,4: apoyo y barrera de luz',
          '7  Dos postes con ranura de 1,1 para la pestaña de la S',
          '8  Adhesivo cámara-ventana; tuerca del M12 en el panel'):
    label(x0, y, t, fontsize=6); y -= 3.6
y -= 2; label(x0, y, 'SECUENCIA DE MONTAJE', fontsize=7, weight='bold'); y -= 4.5
for t in ('1  Pegar la cámara en la ventana del panel.',
          '2  Bajar el rigid-flex: la pestaña entra en las ranuras de los postes.',
          '3  Llevar el M12 a nominal y apretar su tuerca.',
          '4  Enchufar la cola de la cámara en su AXT.',
          '5  Espuma pegada en la placa del LED; enchufar el B2B.',
          '6  Tornillo M1.6 por detrás de la sección de cámara.',
          '7  Tapa: apoya la pestaña y las placas desde arriba.'):
    label(x0, y, t, fontsize=6); y -= 3.6
for ext in ('pdf', 'png'): fig.savefig(f'planos/sujecion_plano.{ext}', dpi=200 if ext == 'png' else None)
print('ok')
