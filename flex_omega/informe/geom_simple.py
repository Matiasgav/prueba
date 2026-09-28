"""Geometria simplificada para dibujar la S en CAD: 1 recto + 3 arcos del mismo radio + rectas + 1 recto.
Mismo largo desarrollado (19,00), mismos extremos y tangentes que la forma simulada en nominal.
Coordenadas de la S: s desde la pestaña (z_rel), y lateral hacia el panel; extremos (0,0) y (15,5; 5) rumbo 0."""
import json, numpy as np
from scipy.optimize import least_squares
D = json.load(open('s_layout.json')); Z, L, A = D['Z'], D['L'], D['A']
fr = D['seq']['ret_a_nom'][-1]
zs = D['ZC'] + Z - np.array(fr['z']); ys = np.array(fr['x']) + A           # forma simulada en coords de la S

def chain(R, t1, t3, s1, s2, n=400):
    """recto 1 / arco hacia atras t1 / recto s1 / arco hacia el panel t1+t3 / recto s2 / arco t3 / recto 1"""
    segs = [(0, 1.0), (-1/R, R*t1), (0, s1), (1/R, R*(t1 + t3)), (0, s2), (-1/R, R*t3), (0, 1.0)]
    p = np.zeros(2); th = 0.0; pts = [p.copy()]
    for k, l in segs:
        m = max(2, int(n*l/L)); ss = np.linspace(0, l, m)[1:]
        for s_ in ss:
            if k == 0: q = p + s_*np.array([np.cos(th), np.sin(th)])
            else: q = p + np.array([np.sin(th + k*s_) - np.sin(th), -(np.cos(th + k*s_) - np.cos(th))])/k
            pts.append(q)
        p = pts[-1].copy(); th += k*l
    return np.array(pts), segs

def dev(P):
    Q = np.stack([zs, ys], 1); return np.array([np.min(np.hypot(*(P - q).T)) for q in Q[::2]])

def resid(v, R):
    t1, t3, s1, s2 = v
    P, segs = chain(R, t1, t3, s1, s2)
    return np.concatenate([[(P[-1, 0] - Z)*50, (P[-1, 1] - A)*50, (sum(l for _, l in segs) - L)*50], dev(P)*0.5])

best = None
for R in (3.0, 3.5, 4.0, 4.5):
    r = least_squares(resid, [0.5, 0.6, 2.5, 2.5], args=(R,), bounds=([0.05, 0.05, 0, 0], [2.5, 2.5, 15, 15]))
    P, segs = chain(R, *r.x); d = dev(P).max()
    err = (abs(P[-1, 0] - Z), abs(P[-1, 1] - A), abs(sum(l for _, l in segs) - L))
    print(f"R={R}: t1={np.degrees(r.x[0]):.2f} t3={np.degrees(r.x[1]):.2f} s1={r.x[2]:.3f} s2={r.x[3]:.3f} desvio max={d:.2f} err={max(err):.1e}")
    if max(err) < 1e-3 and (best is None or d < best[1]): best = (R, d, r.x)
R, d, (t1, t3, s1, s2) = best
# redondeo para dibujar: angulos a 0,5 grados; se recalculan las rectas para cerrar extremos y largo
t1r, = [np.radians(round(np.degrees(t1)*2)/2)]
def f2(v):
    t3_, s1_, s2_ = v; P, segs = chain(R, t1r, t3_, s1_, s2_)
    return [P[-1, 0] - Z, P[-1, 1] - A, sum(l for _, l in segs) - L]
r2 = least_squares(f2, [t3, s1, s2], xtol=1e-12, ftol=1e-12)
t3f, s1f, s2f = r2.x
P, segs = chain(R, t1r, t3f, s1f, s2f)
out = dict(R=R, Rint=R - 0.1, t1=float(np.degrees(t1r)), t2=float(np.degrees(t1r + t3f)), t3=float(np.degrees(t3f)),
           s1=float(s1f), s2=float(s2f), desvio=float(dev(P).max()), largo=float(sum(l for _, l in segs)),
           fin=[float(P[-1, 0]), float(P[-1, 1])], puntos=P.tolist())
json.dump(out, open('informe/geom_simple.json', 'w'))
print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in out.items() if k != 'puntos'})
