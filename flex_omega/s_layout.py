"""Modelo de la S en el layout del usuario (planta 27/9): conector a la izquierda, pestaña fija a la derecha.

Coordenadas de salida (vista de planta como en Solid Edge): z hacia la derecha, con z = 0 en el extremo izquierdo de la
placa del conector; x hacia el panel, con x = 0 en la linea del flex sobre la placa del conector (cara delantera).
Placa del conector z 0-16,5; S de z 16,5 a 32,0 (Z 15,5); pestaña z 32,0-46,0 con su linea de flex en x = -5,0.
Placa de la camara: cara trasera en x = -2,5, desde z = 22,0 hacia la derecha. Modulo de camara z 21,16-29,66."""
import json, numpy as np
from multiprocessing import Pool
from scipy.interpolate import CubicSpline
import s_obst as O, arcfit

Z, L, A, TRAVEL = 15.5, 19.0, 5.0, 12.0
YO, ZO = 2.2, 10.0                 # obstaculo en coords de la S (pestaña = origen): cara de la placa de camara - 0,3
ZC = 16.5                          # canto de la placa del conector
c = 0.1

def to_abs(zr, yr):
    """coords de la S (z desde la pestaña, y hacia el panel desde la linea de la pestaña) -> planta del usuario"""
    return ZC + Z - np.asarray(zr), np.asarray(yr) - A

def frames(n=61):
    """Arranca en nominal, va a retraido y vuelve (mismo camino que la verificacion robusta)."""
    out = {}
    s = np.linspace(0, 1, O.N); th = 0.3*np.sin(2*np.pi*s)
    th, *_ = O.solve(th, L, Z, A, YO, ZO)
    for name, ds in (('nom_a_ret', np.linspace(A, A - TRAVEL, n)), ('ret_a_nom', np.linspace(A - TRAVEL, A, n))):
        seq = []
        for d in ds:
            th, R, gap, z, y = O.solve(th, L, Z, d, YO, ZO)
            zz = np.concatenate([[0], z, [Z]]); yy = np.concatenate([[0], y, [d]])
            za, xa = to_abs(zz, yy)
            t = np.concatenate([[0.0], th, [0.0]]); k = np.abs(np.diff(t))/((L - 2)/O.N)
            seq.append(dict(ret=round(A - d, 3), z=np.round(za, 3).tolist(), x=np.round(xa, 3).tolist(),
                            k=np.round(k, 4).tolist(), R=round(R, 3), gap=round(gap + 0.3, 3)))
        out[name] = seq
    return out

def profile(fr):
    """Ajuste en coordenadas de la S (desde la pestaña, rumbo 0) y espejado a la planta del usuario."""
    za, xa = np.array(fr['z']), np.array(fr['x'])
    zr, yr = ZC + Z - za, xa + A                                  # vuelta a coords de la S
    zi, yi = zr[1:-1], yr[1:-1]
    s = np.concatenate([[0], np.cumsum(np.hypot(np.diff(zi), np.diff(yi)))])
    cands = []
    for npts in (600, 500, 700):
        ss = np.linspace(0, s[-1], npts); pz, py = CubicSpline(s, zi)(ss), CubicSpline(s, yi)(ss)
        for m in (3, 4, 5, 6):
            kap, lens, dev, ok = arcfit.fit(pz, py, 0.0, 0.0, m, kmax=1/2.6)
            if not ok: continue
            cands.append((dev, m, kap, lens, False))
            casi = tuple(i for i in range(m) if abs(kap[i]) < 1/25)
            if casi:
                k2, l2, d2, ok2 = arcfit.fit(pz, py, 0.0, 0.0, m, kmax=1/2.6, fixed0=casi, init=(kap, lens))
                if ok2: cands.append((d2, m, k2, l2, True))
    buenos = [x_ for x_ in cands if x_[0] < 0.06]
    dev, m, kap, lens, _ = min(buenos, key=lambda x_: (not x_[4], x_[1], x_[0])) if buenos else min(cands, key=lambda x_: x_[0])
    segs = [(0.0, 1.0)] + list(zip(kap, lens)) + [(0.0, 1.0)]
    merged = []
    for k, l in segs:
        k = 0.0 if abs(k) < 1/200 else k
        if k == 0 and merged and merged[-1][0] == 0: merged[-1] = (0.0, merged[-1][1] + l)
        else: merged.append((k, l))
    rows = []; p = np.array([0.0, 0.0]); th = 0.0
    for k, l in merged:
        if k == 0:
            q = p + l*np.array([np.cos(th), np.sin(th)])
            z0, x0 = to_abs(p[0], p[1]); z1, x1 = to_abs(q[0], q[1])
            rows.append(dict(tipo='Recta', z0=float(z0), x0=float(x0), z1=float(z1), x1=float(x1), largo=l, ang=180.0 - np.degrees(th)))
        else:
            nrm = np.array([-np.sin(th), np.cos(th)]); cen = p + nrm/k
            q = p + np.array([np.sin(th + k*l) - np.sin(th), -(np.cos(th + k*l) - np.cos(th))])/k
            z0, x0 = to_abs(p[0], p[1]); z1, x1 = to_abs(q[0], q[1]); cz, cx = to_abs(cen[0], cen[1])
            # el espejo en z invierte el sentido de giro
            rows.append(dict(tipo='Arco', z0=float(z0), x0=float(x0), z1=float(z1), x1=float(x1), cz=float(cz), cx=float(cx), R=1/abs(k),
                             Rint=1/abs(k) - c, sentido='horario' if k > 0 else 'antihorario', barrido=np.degrees(abs(k)*l), largo=l))
            th += k*l
        p = q
    return rows, dev

def rl_point(Lv):
    r = [O.sweep(Z, Lv, a, YO, ZO, tr, n=101)[:2] for a in (A - 0.35, A, A + 0.35) for tr in (12.0, 12.5)]
    return Lv, min(x[0] for x in r), min(x[1] for x in r) + 0.3

def dxf(rows, path):
    out = ['0', 'SECTION', '2', 'ENTITIES']
    def line(a, b, ly): out.extend(['0', 'LINE', '8', ly, '10', f'{a[0]:.4f}', '20', f'{a[1]:.4f}', '11', f'{b[0]:.4f}', '21', f'{b[1]:.4f}'])
    def arc(cz, cx, r, a0, a1, ly): out.extend(['0', 'ARC', '8', ly, '10', f'{cz:.4f}', '20', f'{cx:.4f}', '40', f'{r:.4f}', '50', f'{a0:.4f}', '51', f'{a1:.4f}'])
    # DXF con x hacia el panel positivo hacia abajo -> se exporta (z, -x) para que "arriba" sea hacia atras
    for off, ly in ((0, 'FLEX_LINEA_MEDIA'), (c, 'FLEX_CARA_A'), (-c, 'FLEX_CARA_B')):
        for r in rows:
            if r['tipo'] == 'Recta':
                th = np.radians(r['ang']); n = np.array([-np.sin(th), np.cos(th)])*off
                line((r['z0'] + n[0], -(r['x0'] + n[1])), (r['z1'] + n[0], -(r['x1'] + n[1])), ly)
            else:
                ccw = r['sentido'] == 'antihorario'; rad = r['R'] - off if ccw else r['R'] + off
                a0 = np.degrees(np.arctan2(-(r['x0'] - r['cx']), r['z0'] - r['cz'])); a1 = np.degrees(np.arctan2(-(r['x1'] - r['cx']), r['z1'] - r['cz']))
                arc(r['cz'], -r['cx'], rad, a1, a0, ly) if ccw else arc(r['cz'], -r['cx'], rad, a0, a1, ly)
    def rect(z0, z1, x0, x1, ly):
        for a, b in (((z0, -x0), (z1, -x0)), ((z1, -x0), (z1, -x1)), ((z1, -x1), (z0, -x1)), ((z0, -x1), (z0, -x0))): line(a, b, ly)
    rect(0, ZC, 0.1 - 1.0, 0.1, 'PLACA_CONECTOR_NOMINAL'); rect(0, ZC, 0.1 - 13.0, 0.1 - 12.0, 'PLACA_CONECTOR_RETRAIDA')
    rect(ZC + Z, ZC + Z + 14, -A + 0.1 - 1.0, -A + 0.1, 'PESTANA_FIJA')
    rect(22.0, 46.0, -2.5, -1.5, 'PLACA_CAMARA'); rect(21.16, 29.66, -0.38, 4.67, 'MODULO_CAMARA')
    out.extend(['0', 'ENDSEC', '0', 'EOF']); open(path, 'w').write('\n'.join(out) + '\n')

if __name__ == '__main__':
    fr = frames()
    nominal = fr['ret_a_nom'][-1]
    rows, dev = profile(nominal)
    dxf(rows, 'planos/S_conector_layout27_nominal.dxf')
    with Pool(4) as p:
        rl = p.map(rl_point, [round(v, 3) for v in np.arange(18.0, 20.01, 0.25)])
    data = dict(Z=Z, L=L, A=A, travel=TRAVEL, ZC=ZC, cam_pcb_x=-2.5, cam_pcb_z0=22.0, mod_z0=21.16, mod_z1=29.66,
                Rmin=round(min(f['R'] for s_ in fr.values() for f in s_), 3), gapmin=round(min(f['gap'] for s_ in fr.values() for f in s_), 3),
                seq=fr, perfil=rows, desvio=round(float(dev), 3), largo_perfil=round(sum(r['largo'] for r in rows), 3),
                rl=[dict(L=a, R=round(b, 3), gap=round(g, 3)) for a, b, g in rl])
    json.dump(data, open('s_layout.json', 'w'), separators=(',', ':'), default=float)
    print('Rmin', data['Rmin'], 'juego min', data['gapmin'], 'desvio', data['desvio'], 'largo', data['largo_perfil'])
    for r in rows: print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
    print([(d['L'], d['R'], d['gap']) for d in data['rl']])
