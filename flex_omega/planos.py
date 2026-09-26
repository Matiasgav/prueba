"""Planos en posicion nominal para el boceto de chapa (Solid Edge).

La linea media simulada se ajusta con una cadena de rectas y arcos tangentes (G1), con extremos exactos,
el mismo largo desarrollado que el flex y radio interior >= el minimo de cada alternativa.
Salida: planos/<id>_nominal.dxf (capas FLEX_LINEA_MEDIA, FLEX_CARA_A, FLEX_CARA_B, MAINBOARD,
PLACA_CONECTOR, REFERENCIA) y planos/planos.json con la tabla de segmentos y los frames de la animacion.
"""
import json, numpy as np
from scipy.interpolate import CubicSpline
import fast3, arcfit

c = fast3.c
DESIGNS = [
    dict(id='A_piso', nombre='Placa en el piso', cfg=dict(mode='piso', HB=5.0), W=24.0, L=30.0, Rreq=3.0),
    dict(id='B_colgada_R4', nombre='Placa colgada (9,5 − 4)', cfg=dict(mode='colgada', YB=5.0), W=32.0, L=43.5, Rreq=3.0),
    dict(id='C_tu_dibujo', nombre='Tu dibujo (9,5 − 3)', cfg=dict(mode='colgada', YB=4.0), W=26.4, L=38.4, Rreq=2.5),
]

def frames(seq):
    return [dict(X=round(f['X'], 3), x=[round(v, 3) for v in f['x']], y=[round(v, 3) for v in f['y']],
                 k=[round(v, 4) for v in f['k']], Rmin=round(f['Rin'], 3), ymax=round(f['ytop'], 3)) for f in seq]

def build(d):
    fw, bw = fast3.sweep(d['cfg'], d['W'], d['L'], steps=49)
    st = fw + bw; a = fw[-1]
    x, y = a['x'][1:-1], a['y'][1:-1]
    s = np.concatenate([[0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
    ss = np.linspace(0, s[-1], 800); sx, sy = CubicSpline(s, x)(ss), CubicSpline(s, y)(ss)
    th1 = np.pi/2 if d['cfg']['mode'] == 'colgada' else -np.pi/2
    kmax = 1/(d['Rreq'] + c)
    for m in (5, 6, 7, 8, 9):
        kap, lens, dev, ok = arcfit.fit(sx, sy, 0.0, th1, m, kmax=kmax)
        if ok and dev < 0.1: break
    fixed = tuple(i for i in range(m) if abs(kap[i]) < 1/80)
    if fixed:
        kap, lens, dev, ok = arcfit.fit(sx, sy, 0.0, th1, m, kmax=kmax, fixed0=fixed)
    # segmentos: recta inicial 1 mm, cadena, recta final 1 mm
    segs = [('L', 0.0, fast3.S0)] + [('L' if abs(k) < 1e-9 else 'A', k, l) for k, l in zip(kap, lens)] + [('L', 0.0, fast3.S1)]
    merged = []
    for sgm in segs:
        if sgm[0] == 'L' and merged and merged[-1][0] == 'L': merged[-1] = ('L', 0.0, merged[-1][2] + sgm[2])
        else: merged.append(sgm)
    rows = []; p = np.array([0.0, c]); th = 0.0
    for t, k, l in merged:
        if t == 'L':
            q = p + l*np.array([np.cos(th), np.sin(th)])
            rows.append(dict(tipo='Recta', x0=p[0], y0=p[1], x1=q[0], y1=q[1], largo=l, dir=np.degrees(th)))
        else:
            nrm = np.array([-np.sin(th), np.cos(th)]); cen = p + nrm/k
            q = p + np.array([np.sin(th + k*l) - np.sin(th), -(np.cos(th + k*l) - np.cos(th))])/k
            rows.append(dict(tipo='Arco', x0=p[0], y0=p[1], x1=q[0], y1=q[1], cx=cen[0], cy=cen[1], R=1/abs(k),
                             Rint=1/abs(k) - c, Rext=1/abs(k) + c, sentido='antihorario' if k > 0 else 'horario',
                             barrido=np.degrees(abs(k)*l), largo=l))
            th += k*l
        p = q
    d.update(Rmin_recorrido=round(min(f['Rin'] for f in st), 2), ytop_retraido=round(max(f['ytop'] for f in st), 1),
             ytop_nominal=round(a['ytop'], 2), desvio_ajuste=round(float(dev), 3), segmentos=rows,
             Rint_min_plano=round(min(r['Rint'] for r in rows if r['tipo'] == 'Arco'), 2),
             largo_plano=round(sum(r['largo'] for r in rows), 3), fin=[round(p[0], 4), round(p[1], 4)],
             fw=frames(fw), bw=frames(bw), YB=d['cfg'].get('YB'), HB=d['cfg'].get('HB'), mode=d['cfg']['mode'],
             Rmin=round(min(f['Rin'] for f in st), 3), ytop=round(max(f['ytop'] for f in st), 2))
    return d

def dxf(d):
    out = ['0', 'SECTION', '2', 'ENTITIES']
    def line(p, q, layer):
        out.extend(['0', 'LINE', '8', layer, '10', f'{p[0]:.4f}', '20', f'{p[1]:.4f}', '11', f'{q[0]:.4f}', '21', f'{q[1]:.4f}'])
    def arc(cx, cy, r, a0, a1, layer):
        out.extend(['0', 'ARC', '8', layer, '10', f'{cx:.4f}', '20', f'{cy:.4f}', '40', f'{r:.4f}', '50', f'{a0:.4f}', '51', f'{a1:.4f}'])
    for off, layer in ((0, 'FLEX_LINEA_MEDIA'), (+c, 'FLEX_CARA_A'), (-c, 'FLEX_CARA_B')):
        for r in d['segmentos']:
            if r['tipo'] == 'Recta':
                th = np.radians(r['dir']); n = np.array([-np.sin(th), np.cos(th)])*off
                line((r['x0'] + n[0], r['y0'] + n[1]), (r['x1'] + n[0], r['y1'] + n[1]), layer)
            else:
                a0 = np.degrees(np.arctan2(r['y0'] - r['cy'], r['x0'] - r['cx'])); a1 = np.degrees(np.arctan2(r['y1'] - r['cy'], r['x1'] - r['cx']))
                ccw = r['sentido'] == 'antihorario'
                rad = r['R'] - off if ccw else r['R'] + off  # cara A = lado izquierdo del recorrido
                if ccw: arc(r['cx'], r['cy'], rad, a0, a1, layer)
                else: arc(r['cx'], r['cy'], rad, a1, a0, layer)
    W = d['W']
    boxes = [((-6, 0.2, 0, 1.2), 'MAINBOARD')]
    if d['mode'] == 'colgada': boxes.append(((W - 1.2, d['YB'], W - 0.2, 10.5), 'PLACA_CONECTOR'))
    else: boxes.append(((W - 1.2, 0, W - 0.2, d['HB']), 'PLACA_CONECTOR'))
    for (x0, y0, x1, y1), layer in boxes:
        for p, q in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))): line(p, q, layer)
    line((-6, 10.5), (W + 3, 10.5), 'REFERENCIA'); line((-6, 0), (W + 3, 0), 'REFERENCIA'); line((W, 0), (W, 10.5), 'REFERENCIA')
    out.extend(['0', 'ENDSEC', '0', 'EOF'])
    open(f"planos/{d['id']}_nominal.dxf", 'w').write('\n'.join(out) + '\n')

if __name__ == '__main__':
    from multiprocessing import Pool
    with Pool(3) as p: res = p.map(build, DESIGNS)
    for d in res:
        dxf(d)
        print(f"{d['id']}: W={d['W']} L={d['L']} largo plano={d['largo_plano']} fin={d['fin']} desvio={d['desvio_ajuste']} "
              f"Rint plano min={d['Rint_min_plano']} Rin recorrido={d['Rmin_recorrido']} ytop nom={d['ytop_nominal']} ret={d['ytop_retraido']}")
        for r in d['segmentos']:
            print('   ', r['tipo'], f"({r['x0']:.3f},{r['y0']:.3f})->({r['x1']:.3f},{r['y1']:.3f})",
                  f"R={r['R']:.3f} c=({r['cx']:.3f},{r['cy']:.3f}) {r['sentido']} {r['barrido']:.2f}°" if r['tipo'] == 'Arco' else f"dir={r['dir']:.1f}°", f"L={r['largo']:.3f}")
    json.dump(res, open('planos/planos.json', 'w'), separators=(',', ':'), default=float)
