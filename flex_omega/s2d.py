"""Paquete 2D de la S del conector (opcion 2 centrada): animacion, curva R vs L, perfil para Solid Edge y DXF.

Vista de arriba, cotas en mm desde la cara interior del panel (x = 0, x negativo hacia atras) y desde el borde
lateral izquierdo de los 52 mm (z = 0). El flex va de canto: 11 mm de alto (y 0,6 a 11,6 sobre la cinta).
"""
import json, numpy as np
from multiprocessing import Pool
import s_lateral as S, arcfit, s_centrada as C

Z, L, TRAVEL = 14.0, 16.6, 12.0
RREQ = 2.5                      # radio interior minimo exigido
B = 6.65                        # cuerpo del conector detras del panel (nominal de 6,3-7)
XB = -B - 0.1                   # linea media del flex (cara delantera de la placa del conector) en nominal
A = 6.0                         # la pestaña queda 6 mm detras
XT = XB - A                     # linea media del flex en la pestaña fija (cara delantera)
Z0 = 16.0                       # canto de la pestaña por donde sale el flex
STR, c = 1.0, 0.1

def frames_for(a, n=61):
    Ze, Le = Z - 2*STR, L - 2*STR; h = Le/S.N
    s = np.linspace(0, 1, S.N); th = 0.3*np.sin(2*np.pi*s)
    seq = {}
    for name, ds in (('nom_a_ret', np.linspace(a, a - TRAVEL, n)), ('ret_a_nom', np.linspace(a - TRAVEL, a, n))):
        out = []
        for d in ds:
            th, R, _, _ = S.solve(th, Le, Ze, d)
            t = np.concatenate([[0], th, [0]]); k = np.abs(np.diff(t))/h
            zz = np.concatenate([[0], np.cumsum(h*np.cos(th))]); xx = np.concatenate([[0], np.cumsum(h*np.sin(th))])
            # agrega los rectos de 1 mm
            z = np.concatenate([[Z0], Z0 + STR + zz, [Z0 + Z]]); x = np.concatenate([[XT], XT + xx, [XT + d]])
            out.append(dict(ret=round(a - d, 3), z=np.round(z, 3).tolist(), x=np.round(x, 3).tolist(),
                            k=np.round(k, 4).tolist(), R=round(R, 3), th=th.copy()))
        seq[name] = out
    return seq

def rl_point(Lv):
    res = [C.sweep(Z, Lv, a, tr, n=121)[0] for a in (5.65, 6.0, 6.35) for tr in (12.0, 12.5)]
    return Lv, min(res)

def fit_profile(fr):
    """Perfil nominal como cadena de rectas y arcos tangentes (para la brida de contorno)."""
    z, x = np.array(fr['z']), np.array(fr['x'])
    zi, xi = z[1:-1], x[1:-1]                        # tramo libre entre los rectos
    from scipy.interpolate import CubicSpline
    s = np.concatenate([[0], np.cumsum(np.hypot(np.diff(zi), np.diff(xi)))])
    cands = []
    for npts in (600, 500, 700):                                   # varios muestreos: SLSQP a veces no converge
        ss = np.linspace(0, s[-1], npts); pz, px = CubicSpline(s, zi)(ss), CubicSpline(s, xi)(ss)
        for m in (3, 4, 5, 6):
            kap, lens, dev, ok = arcfit.fit(pz, px, 0.0, 0.0, m, kmax=1/(RREQ + c))
            if not ok: continue
            cands.append((dev, m, kap, lens, False))
            casi = tuple(i for i in range(m) if abs(kap[i]) < 1/25)   # arcos de R > 25 -> rectas
            if casi:
                k2, l2, d2, ok2 = arcfit.fit(pz, px, 0.0, 0.0, m, kmax=1/(RREQ + c), fixed0=casi, init=(kap, lens))
                if ok2: cands.append((d2, m, k2, l2, True))
    # preferimos el perfil con rectas y pocos elementos que quede dentro de 0,05 mm
    buenos = [x for x in cands if x[0] < 0.06]
    dev, m, kap, lens, _ = min(buenos, key=lambda x: (not x[4], x[1], x[0])) if buenos else min(cands, key=lambda x: x[0])
    segs = [('L', 0.0, STR)] + [('L' if abs(k) < 1/200 else 'A', k, l) for k, l in zip(kap, lens)] + [('L', 0.0, STR)]
    merged = []
    for sg in segs:
        if sg[0] == 'L' and merged and merged[-1][0] == 'L': merged[-1] = ('L', 0.0, merged[-1][2] + sg[2])
        else: merged.append(sg)
    rows = []; p = np.array([Z0, XT]); th = 0.0
    for t, k, l in merged:
        if t == 'L' or abs(k) < 1/200:
            q = p + l*np.array([np.cos(th), np.sin(th)])
            rows.append(dict(tipo='Recta', z0=p[0], x0=p[1], z1=q[0], x1=q[1], largo=l, ang=np.degrees(th)))
        else:
            nrm = np.array([-np.sin(th), np.cos(th)]); cen = p + nrm/k
            q = p + np.array([np.sin(th + k*l) - np.sin(th), -(np.cos(th + k*l) - np.cos(th))])/k
            rows.append(dict(tipo='Arco', z0=p[0], x0=p[1], z1=q[0], x1=q[1], cz=cen[0], cx=cen[1], R=1/abs(k),
                             Rint=1/abs(k) - c, sentido='antihorario' if k > 0 else 'horario', barrido=np.degrees(abs(k)*l), largo=l))
            th += k*l
        p = q
    return rows, dev

def dxf(rows, path):
    out = ['0', 'SECTION', '2', 'ENTITIES']
    def line(a, b, ly): out.extend(['0', 'LINE', '8', ly, '10', f'{a[0]:.4f}', '20', f'{a[1]:.4f}', '11', f'{b[0]:.4f}', '21', f'{b[1]:.4f}'])
    def arc(cz, cx, r, a0, a1, ly): out.extend(['0', 'ARC', '8', ly, '10', f'{cz:.4f}', '20', f'{cx:.4f}', '40', f'{r:.4f}', '50', f'{a0:.4f}', '51', f'{a1:.4f}'])
    for off, ly in ((0, 'FLEX_LINEA_MEDIA'), (c, 'FLEX_CARA_A'), (-c, 'FLEX_CARA_B')):
        for r in rows:
            if r['tipo'] == 'Recta':
                th = np.radians(r['ang']); n = np.array([-np.sin(th), np.cos(th)])*off
                line((r['z0'] + n[0], r['x0'] + n[1]), (r['z1'] + n[0], r['x1'] + n[1]), ly)
            else:
                a0 = np.degrees(np.arctan2(r['x0'] - r['cx'], r['z0'] - r['cz'])); a1 = np.degrees(np.arctan2(r['x1'] - r['cx'], r['z1'] - r['cz']))
                ccw = r['sentido'] == 'antihorario'; rad = r['R'] - off if ccw else r['R'] + off
                arc(r['cz'], r['cx'], rad, a0, a1, ly) if ccw else arc(r['cz'], r['cx'], rad, a1, a0, ly)
    # placas de referencia (plano medio +-0,5) y panel
    def rect(z0, z1, x0, x1, ly):
        for a, b in (((z0, x0), (z1, x0)), ((z1, x0), (z1, x1)), ((z1, x1), (z0, x1)), ((z0, x1), (z0, x0))): line(a, b, ly)
    rect(Z0 - 12, Z0, XT - 0.9, XT + 0.1, 'PESTANA_FIJA')
    rect(Z0 + Z, 52, XB - 0.9, XB + 0.1, 'PLACA_CONECTOR_NOMINAL')
    rect(Z0 + Z, 52, XB - 12.9, XB - 11.9, 'PLACA_CONECTOR_RETRAIDA')
    line((0, 0), (52, 0), 'PANEL'); line((0, -30), (0, 2), 'LIMITE_52'); line((52, -30), (52, 2), 'LIMITE_52')
    out.extend(['0', 'ENDSEC', '0', 'EOF'])
    open(path, 'w').write('\n'.join(out) + '\n')

if __name__ == '__main__':
    seq = frames_for(A)
    nominal = seq['ret_a_nom'][-1]
    rows, dev = fit_profile(nominal)
    dxf(rows, 'planos/S_conector_nominal.dxf')
    tol = {}
    with Pool(4) as p:
        rl = p.map(rl_point, [round(v, 3) for v in np.arange(15.75, 17.51, 0.125)])
        tolres = p.starmap(C.sweep, [(Z, L, a, tr, 121) for a in (5.65, 6.0, 6.35) for tr in (12.0, 12.5)])
    tol = [dict(a=a, tr=tr, R=round(r[0], 2), xmin=round(r[1], 2), xmax=round(r[2], 2)) for (a, tr), r in zip([(a, tr) for a in (5.65, 6.0, 6.35) for tr in (12.0, 12.5)], tolres)]
    for s_ in seq.values():
        for f in s_: f.pop('th')
    data = dict(Z=Z, L=L, travel=TRAVEL, RREQ=RREQ, B=B, XB=XB, XT=XT, Z0=Z0, A=A,
                Rmin=round(min(f['R'] for s_ in seq.values() for f in s_), 3),
                seq=seq, perfil=rows, desvio=round(float(dev), 3), largo_perfil=round(sum(r['largo'] for r in rows), 3),
                rl=[dict(L=Lv, R=round(R, 3)) for Lv, R in rl], tol=tol)
    json.dump(data, open('s2d.json', 'w'), separators=(',', ':'), default=float)
    print('Rmin animacion', data['Rmin'], 'desvio ajuste', data['desvio'], 'largo perfil', data['largo_perfil'])
    for r in rows: print(r)
    print(tol)
    print([(d['L'], d['R']) for d in data['rl']])
