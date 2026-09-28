"""02489-00-MC006 · Forma y largo del flex del conector M12.
Genera las figuras y resultados.json de la nota a partir de:
  - flex_omega/s_layout.json: modelo final (elástica) con el layout del 27/9, calculado por flex_omega/s_layout.py;
  - geom_simple.json: geometría simplificada para dibujar (3 arcos R 3,5), calculada por geom_simple.py;
  - capturas/*.jpg: capturas de las páginas 2D y del visor 3D de alternativas (flex_omega/*.html).
Planta como en Solid Edge: panel abajo; z hacia la derecha, x hacia el panel (hacia abajo en la figura).
Uso: python3 calculo.py  (desde cualquier carpeta)"""
import json, os, sys, io
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__)); FLEX = os.path.join(AQUI, '..', '..', '..', 'flex_omega')
OUT = os.path.join(AQUI, 'figuras'); os.makedirs(OUT, exist_ok=True)
CAP = os.path.join(AQUI, 'capturas')
D = json.load(open(os.path.join(FLEX, 's_layout.json'))); G = json.load(open(os.path.join(AQUI, 'geom_simple.json')))
Z, L, A, ZC = D['Z'], D['L'], D['A'], D['ZC']; ZT = ZC + Z
YO, Z0C, M0, M1 = D['cam_pcb_x'], D['cam_pcb_z0'], D['mod_z0'], D['mod_z1']

# paleta del informe (misma que tools/make_figures.py, validada)
INK, SEC, MUT, GRID = '#16202b', '#52514e', '#8a8880', '#e4e6ea'
S1, S2, CRIT = '#2a78d6', '#eb6834', '#d03b3b'
RAMP = ['#9ec5f4', '#6da7ec', '#3987e5', '#256abf', '#184f95', '#0d366b']
PCB, PCBE, KAP, MOD = '#cfe8d5', '#2f7a47', '#c8781e', '#d9dce3'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8, 'text.color': INK, 'axes.edgecolor': MUT,
                     'axes.labelcolor': SEC, 'xtick.color': SEC, 'ytick.color': SEC, 'svg.fonttype': 'path'})
f2 = lambda v: f'{v:.2f}'.replace('.', ',')
f1 = lambda v: f'{v:.1f}'.replace('.', ',')

def save(fig, name, dpi=150, exts=('pdf', 'png')):
    for ext in exts:
        fig.savefig(f'{OUT}/{name}.{ext}', dpi=dpi, bbox_inches='tight', pad_inches=0.04)
    plt.close(fig)

# ------------------------------------------------------------------ geometria simplificada (coords absolutas)
def to_abs(zr, yr): return ZC + Z - zr, yr - A
R, t1, t2, t3 = G['R'], np.radians(G['t1']), np.radians(G['t2']), np.radians(G['t3'])
segs = [('Recta', 0, 1.0), ('Arco', -1, t1), ('Recta', 0, G['s1']), ('Arco', 1, t2), ('Recta', 0, G['s2']), ('Arco', -1, t3), ('Recta', 0, 1.0)]
p, th, tang, arcs = np.zeros(2), 0.0, [np.zeros(2)], []
for tipo, sg, v in segs:
    if tipo == 'Recta': q = p + v*np.array([np.cos(th), np.sin(th)])
    else:
        c = p + sg*R*np.array([-np.sin(th), np.cos(th)])
        th2 = th + sg*v; q = c + sg*R*np.array([np.sin(th2), -np.cos(th2)])
        arcs.append(dict(c=c, p0=p.copy(), p1=q.copy(), sg=sg, ang=np.degrees(v))); th = th2
    tang.append(q.copy()); p = q
TP = [to_abs(*t) for t in tang]
PAN0 = YO + 1.0 + 1.12 + 5.05
json.dump(dict(tangentes=[[round(a, 3), round(b, 3)] for a, b in TP],
               centros=[[round(v, 3) for v in to_abs(*a['c'])] for a in arcs]), open(os.path.join(AQUI, 'geom_simple_tangentes.json'), 'w'))
PS = np.array([to_abs(*q) for q in G['puntos']])
nom = D['seq']['ret_a_nom'][-1]; NZ, NX = np.array(nom['z']), np.array(nom['x'])

def board(ax, z0, z1, x0, x1, lab=None, ls='-', fc=PCB, ec=PCBE, lpos=None, **kw):
    ax.add_patch(Rectangle((z0, x0), z1 - z0, x1 - x0, fc=fc, ec=ec, lw=0.8, ls=ls, zorder=2))
    if lab: ax.text(*(lpos or ((z0 + z1)/2, x1 + 0.5)), lab, ha='center', va='top', fontsize=7, color=SEC, **kw)

def scene(ax, ghost=True, labels=True):
    board(ax, 0, ZC, -0.9, 0.1, 'placa del conector M12' if labels else None)
    board(ax, ZT, ZT + 8, -A - 0.9, -A + 0.1, 'pestaña fija (mainboard)' if labels else None, lpos=(ZT + 4, -A - 1.1))
    board(ax, Z0C, 40, YO, YO + 1.0, 'placa de cámara' if labels else None, lpos=(36.5, YO - 0.3))
    board(ax, M0, M1, YO + 1.0 + 1.12, YO + 1.0 + 1.12 + 5.05, 'módulo cámara' if labels else None, fc=MOD, ec=MUT,
          lpos=((M0 + M1)/2, YO + 5.2))
    if ghost:
        board(ax, 0, ZC, -12.9, -11.9, 'conector retraído (−12)' if labels else None, ls=(0, (4, 2)), fc='none', ec=MUT,
              lpos=(ZC/2, -12.9 - 0.3))
    ax.set_aspect('equal'); ax.invert_yaxis(); ax.axis('off')

def dimh(ax, za, zb, x, t, tick=0.5):
    ax.annotate('', xy=(za, x), xytext=(zb, x), arrowprops=dict(arrowstyle='<|-|>', color=S1, lw=0.6, mutation_scale=7, shrinkA=0, shrinkB=0))
    ax.text((za + zb)/2, x - 0.35, t, ha='center', va='bottom', fontsize=7.5, color=S1)

def dimv(ax, xa, xb, z, t, side=1):
    ax.annotate('', xy=(z, xa), xytext=(z, xb), arrowprops=dict(arrowstyle='<|-|>', color=S1, lw=0.6, mutation_scale=7, shrinkA=0, shrinkB=0))
    ax.text(z + 0.35*side, (xa + xb)/2, t, ha='left' if side > 0 else 'right', va='center', fontsize=7.5, color=S1)

def ext(ax, pts, **kw):
    for (a, b), (c, d) in pts: ax.plot([a, c], [b, d], color=S1, lw=0.35, **kw)

# ------------------------------------------------------------------ 1. problema
fig, ax = plt.subplots(figsize=(7.2, 4.1)); scene(ax, labels=False)
ax.plot(NZ, NX, color=KAP, lw=2.2, solid_capstyle='butt', zorder=3)
ret = D['seq']['nom_a_ret'][-1]; ax.plot(ret['z'], ret['x'], color=KAP, lw=1.0, ls=(0, (4, 2)), alpha=.8, zorder=3)
ax.text(ZC/2, 0.5, 'placa del conector M12 (nominal)', ha='center', va='top', fontsize=7, color=SEC)
ax.text(ZC/2, -13.3, 'placa del conector retraída', ha='center', va='bottom', fontsize=7, color=MUT)
ax.text(40, -6.2, 'pestaña fija (mainboard)', ha='right', va='bottom', fontsize=7, color=SEC)
ax.text(40, -1.2, 'placa de cámara', ha='right', va='top', fontsize=7, color=SEC)
ax.text((M0 + M1)/2, 2.3, 'módulo\ncámara', ha='center', va='center', fontsize=7, color=SEC)
ax.annotate('', xy=(8, -11.4), xytext=(8, -0.9), arrowprops=dict(arrowstyle='-|>', color=CRIT, lw=1.2, mutation_scale=10))
ax.text(8.5, -6.2, 'retrae 12 mm\npara el montaje', color=CRIT, fontsize=7.5, va='center')
PAN = YO + 1.0 + 1.12 + 5.05
ax.plot([-1.5, 41], [PAN, PAN], color=INK, lw=1.4); ax.text(-1.5, PAN + 0.4, 'panel frontal (M12 y ventana de cámara)', fontsize=7, va='top', color=INK)
ax.annotate('flex nominal', xy=(19.0, -0.75), xytext=(12.5, 2.6), fontsize=7.5, color=KAP, ha='center', va='center',
            arrowprops=dict(arrowstyle='-', color=KAP, lw=0.5))
ax.text(22.5, -11.3, 'flex retraído', color=KAP, fontsize=7.5, ha='left')
dimh(ax, ZC, ZT, -14.6, 'Z = separación entre cantos (la medida a minimizar)')
ext(ax, [((ZC, -12.9), (ZC, -14.8)), ((ZT, -A - 0.9), (ZT, -14.8))])
ax.set_xlim(-2, 41); ax.set_ylim(PAN + 1.6, -16.2)
save(fig, 'fig_problema')

# ------------------------------------------------------------------ 2. geometria para dibujar
fig, ax = plt.subplots(figsize=(7.4, 4.4)); scene(ax, ghost=False, labels=False)
ax.text(13.3, 0.5, 'placa del conector', ha='center', va='top', fontsize=7, color=SEC)
ax.text(40, -6.2, 'pestaña fija', ha='right', va='bottom', fontsize=7, color=SEC)
ax.text(40, -1.2, 'placa de cámara', ha='right', va='top', fontsize=7, color=SEC)
ax.text((M0 + M1)/2, 2.3, 'módulo cámara', ha='center', va='center', fontsize=7, color=SEC)
ax.plot([ZC, 44.2], [0, 0], color=S1, lw=0.4, ls=(0, (1, 2)), zorder=1)
ax.plot(NZ, NX, color=MUT, lw=0.9, ls=(0, (3, 2)), zorder=3)
ax.plot(PS[:, 0], PS[:, 1], color=KAP, lw=2.4, solid_capstyle='butt', zorder=4)
off = {0: (0, 0.85), 1: (0, 0.85), 2: (0, 0.85), 3: (0, -0.8), 4: (-0.7, 0), 5: (-0.7, 0), 6: (0, -0.8), 7: (0, -0.8)}
for i, (a, b) in enumerate(TP):
    ax.plot(a, b, 'o', ms=3.2, color=INK, zorder=5); dz, dx = off[i]
    ax.text(a + dz, b + dx, f'T{i+1}', fontsize=7, ha='right' if dz < 0 else 'center', va='center', color=INK, zorder=5)
lab = [('R 3,5 · 21,5°', (31.6, -8.3)), ('R 3,5 · 83,5°', (21.4, -8.6)), ('R 3,5 · 62,0°', (18.8, 1.6))]
for a, (t, xy) in zip(arcs, lab):
    sg = a['sg']; c = np.array(a['c'])
    v0 = a['p0'] - c; ang0 = np.arctan2(v0[1], v0[0]); am = ang0 + sg*np.radians(a['ang'])/2
    m = to_abs(*(c + R*np.array([np.cos(am), np.sin(am)])))
    ax.annotate(t, xy=m, xytext=xy, fontsize=7.5, color=S1, ha='center', va='center',
                arrowprops=dict(arrowstyle='-', color=S1, lw=0.4, shrinkA=2, shrinkB=1))
m = (np.array(TP[2]) + np.array(TP[3]))/2; ax.text(m[0], m[1] + 0.7, 's1 = 3,39', fontsize=7, color=SEC, ha='center', va='top')
m = (np.array(TP[4]) + np.array(TP[5]))/2; ax.text(m[0] + 0.5, m[1] + 0.2, 's2 = 3,41', fontsize=7, color=SEC, ha='left', va='center')
dimh(ax, ZC, ZT, -10.2, '15,50'); ext(ax, [((ZC, -0.9), (ZC, -10.4)), ((ZT, -A - 0.9), (ZT, -10.4))])
dimv(ax, YO, 0, 41.6, '2,50'); ext(ax, [((40, YO), (41.8, YO))])
dimv(ax, -A, 0, 43.8, '5,00'); ext(ax, [((40, -A), (44.0, -A))])
dimh(ax, ZC, M0, 5.6, '4,66'); ext(ax, [((ZC, 0.1), (ZC, 5.8)), ((M0, PAN0), (M0, 5.8))])
ax.text(44.2, 0.5, 'x = 0', fontsize=6.5, color=S1, ha='right', va='top')
ax.plot([11.4, 13.0], [3.0, 3.0], color=KAP, lw=2.4); ax.text(13.3, 3.0, 'geometría para dibujar', fontsize=7, va='center', color=INK)
ax.plot([11.4, 13.0], [4.2, 4.2], color=MUT, lw=0.9, ls=(0, (3, 2))); ax.text(13.3, 4.2, 'forma simulada', fontsize=7, va='center', color=INK)
ax.set_xlim(11, 45.5); ax.set_ylim(6.6, -11.4)
save(fig, 'fig_geometria')

# ------------------------------------------------------------------ 3. carrera
fr = D['seq']['nom_a_ret']; idx = [0, 10, 20, 30, 40, 50, 60]; col = ['#b9d6f7'] + RAMP
fig, ax = plt.subplots(figsize=(7.2, 3.9)); scene(ax, ghost=False, labels=False)
ax.text(40, -6.2, 'pestaña fija', ha='right', va='bottom', fontsize=7, color=SEC)
ax.text(40, -1.2, 'placa de cámara', ha='right', va='top', fontsize=7, color=SEC)
ax.text((M0 + M1)/2, 2.3, 'módulo cámara', ha='center', va='center', fontsize=7, color=SEC)
for j, i in enumerate(idx[::-1]):
    f = fr[i]; c = col[idx.index(i)]
    ax.plot(f['z'], f['x'], color=c, lw=1.5, zorder=3 + j)
    ax.add_patch(Rectangle((0, -f['ret'] - 0.9), ZC, 1.0, fc='none', ec=c, lw=0.6, zorder=2))
    ax.text(-0.4, -f['ret'] - 0.4, f"{f['ret']:.0f}", fontsize=7, ha='right', va='center', color=SEC)
ax.text(-0.4, -14.2, 'retracción\n(mm)', fontsize=7, ha='right', va='center', color=SEC)
ax.set_xlim(-4, 41); ax.set_ylim(5.0, -15.2)
save(fig, 'fig_carrera')

# ------------------------------------------------------------------ 4. robustez (small multiples, un eje cada uno)
rl = D['rl']; Ls = [r['L'] for r in rl]
fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.5), gridspec_kw=dict(wspace=0.42))
def base(a, title):
    a.set_title(title, fontsize=8, loc='left', color=INK, pad=6)
    for s in ('top', 'right'): a.spines[s].set_visible(False)
    a.grid(axis='y', color=GRID, lw=0.6); a.set_axisbelow(True); a.tick_params(labelsize=7, length=2)
a = axs[0]; rr = [f['ret'] for f in fr]; RR = [f['R'] for f in fr]
base(a, 'R interior vs. retracción\n(L = 19,0, cotas nominales)')
a.plot(rr, RR, color=S1, lw=2); a.axhline(2.5, color=CRIT, lw=1, ls=(0, (4, 2))); a.text(12, 2.53, 'mín. 2,5', color=CRIT, fontsize=7, ha='right', va='bottom')
a.set_xlabel('retracción (mm)', fontsize=7); a.set_ylim(2, 4.2); a.set_xticks([0, 4, 8, 12])
a = axs[1]; base(a, 'R interior peor caso\nvs. largo del flex')
a.plot(Ls, [r['R'] for r in rl], color=S1, lw=2, marker='o', ms=4)
a.axhline(2.5, color=CRIT, lw=1, ls=(0, (4, 2))); a.axvspan(18.75, 19.25, color=S1, alpha=.10, lw=0)
a.text(19.0, 3.12, '19,0 ± 0,25', fontsize=7, ha='center', color=S1)
a.annotate('se tensa y\nse quiebra', xy=(18.25, 1.77), xytext=(18.55, 1.9), fontsize=6.8, color=CRIT, arrowprops=dict(arrowstyle='-', color=CRIT, lw=0.5))
a.set_xlabel('largo entre cantos (mm)', fontsize=7); a.set_ylim(1.5, 3.3)
a = axs[2]; base(a, 'Juego a la placa de cámara\npeor caso vs. largo del flex')
a.plot(Ls, [r['gap'] for r in rl], color=S1, lw=2, marker='o', ms=4)
a.axhline(0.3, color=CRIT, lw=1, ls=(0, (4, 2))); a.axvspan(18.75, 19.25, color=S1, alpha=.10, lw=0)
a.text(20, 0.36, 'mín. 0,3 (apoya)', color=CRIT, fontsize=7, ha='right', va='bottom')
a.set_xlabel('largo entre cantos (mm)', fontsize=7); a.set_ylim(0, 2.7)
save(fig, 'fig_robustez')

# ------------------------------------------------------------------ 5. galerias de alternativas
def gallery(name, items, ncol=2, w=7.4):
    n = len(items); nr = (n + ncol - 1)//ncol
    ims = []
    for f, *_ in items:
        im = Image.open(f'{CAP}/{f}.jpg').convert('RGB'); s = 640/im.size[0]
        ims.append(im.resize((640, int(im.size[1]*s)), Image.LANCZOS))
    h = max(i.size[1] for i in ims)/640*w/ncol
    fig = plt.figure(figsize=(w, nr*(h + 0.62)))
    for k, (im, (f, t, v, ok)) in enumerate(zip(ims, items)):
        r, c = divmod(k, ncol)
        x0 = c/ncol; y0 = 1 - (r + 1)/nr
        ax = fig.add_axes([x0 + 0.008, y0 + 0.5/(nr*(h + 0.62)) + 0.004, 1/ncol - 0.016, h/(nr*(h + 0.62)) - 0.008])
        ax.imshow(np.asarray(im)); ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values(): s.set_color(GRID)
        yt = y0 + 0.47/(nr*(h + 0.62))
        mark = {'si': ('✔', '#0c7a0c'), 'no': ('✘', CRIT), 'parcial': ('◐', '#b07c00')}[ok]
        fig.text(x0 + 0.012, yt, mark[0], color=mark[1], fontsize=9, va='top', weight='bold')
        fig.text(x0 + 0.04, yt, t, fontsize=8, weight='bold', va='top', color=INK)
        fig.text(x0 + 0.04, yt - 0.2/(nr*(h + 0.62)), v, fontsize=7.2, va='top', color=SEC)
    save(fig, name, dpi=150, exts=('jpg',))

gallery('fig_galeria_1', [
    ('2d_colgada', 'Omega libre, conector colgando', 'W = 32 mm · R 3,4 · ocupa demasiado', 'no'),
    ('2d_tu_dibujo', 'Omega del primer boceto', 'W = 26,4 mm · R 2,7 · sigue ancho', 'no'),
    ('2d_piso', 'Conector en el piso, flex hacia arriba', 'W = 24 mm · R 3,7 · mejora, no alcanza', 'no'),
    ('2d_s_centrada', 'S lateral en el plano de las placas', 'Z = 15,5 · R 3 · punto de partida elegido', 'si')])
gallery('fig_galeria_2', [
    ('3d_piso', 'Placa en el piso (3D)', 'arco de R 3: el mismo ancho que en 2D (≈ 24)', 'no'),
    ('3d_u_rodante', 'U rodante', 'pide un canal de 7,6 mm libre', 'no'),
    ('3d_s_lateral', 'S lateral de canto', 'la más compacta: base de la solución', 'si'),
    ('3d_interfaz_camara', 'Interfaz fija + cámara + S doble', 'dos flex en una pieza: no fabricable en PCBWay', 'no'),
    ('3d_camara_horizontal', 'Cámara con imagen horizontal', 'dobla demasiado el flex de la cámara', 'no'),
    ('3d_camara_centrada', 'Cámara centrada, flex recto', 'imagen a 90°, flex de cámara sin doblar', 'si')])
gallery('fig_galeria_3', [
    ('3d_pared_lateral', 'Pared lateral para la cámara', 'boceto del usuario: sube y se extiende en los 52 mm', 'si'),
    ('3d_led_a', 'LED A: placa LED + conector B2B', 'elegida: LED delante del flex de cámara, a la altura del lente', 'si'),
    ('3d_led_b', 'LED B: isla rigid-flex', 'segundo brazo de flex: no fabricable así', 'no'),
    ('3d_led_c', 'LED C: placa en el panel + FFC', 'suma cable y conectores', 'no')])
R = dict(L=D['L'], tol_L=0.25, Z=Z, A=A, carrera=D['travel'], Rint_min_carrera=D['Rmin'],
         juego_min_nominal_cotas=D['gapmin'], peor_caso_por_largo=D['rl'],
         Rint_peor_tolerancia=min(r['R'] for r in D['rl'] if abs(r['L'] - D['L']) <= 0.25 + 1e-9),
         juego_peor_tolerancia=min(r['gap'] for r in D['rl'] if abs(r['L'] - D['L']) <= 0.25 + 1e-9),
         dibujo=dict(R=G['R'], Rint=G['Rint'], ang=[G['t1'], G['t2'], G['t3']], rectas=[1.0, G['s1'], G['s2'], 1.0],
                     largo=G['largo'], desvio_max=G['desvio'], juego_placa=G['gap_placa'],
                     tangentes=[[round(a, 3), round(b, 3)] for a, b in TP]),
         perfil_exacto=D['perfil'])
json.dump(R, open(os.path.join(AQUI, 'resultados.json'), 'w'), indent=1, ensure_ascii=False)
print('figuras ok; R peor', R['Rint_peor_tolerancia'], 'juego peor', R['juego_peor_tolerancia'])
