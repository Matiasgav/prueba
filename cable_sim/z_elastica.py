"""Elástica del cable plegado en Z (dos pisos), en proyección frontal.

Mismo modelo que el lazo simple, con:
  - giro neto de 540° (tres lazos: derecha, izquierda, derecha),
  - contacto contra sí mismo SOLO entre puntos del mismo piso; el tramo del
    lazo izquierdo (cambio de piso) no choca con nada salvo las paredes.
Aproximación: el lazo izquierdo es en realidad inclinado en profundidad
(algo más largo y abierto que su proyección), así que su radio real es
algo mayor que el que da esta proyección.
Uso: python3 z_elastica.py out.json
"""
import sys, json, time
import numpy as np
import rod
from rod import Rod, r, YMAX, XMIN, XMAX
import dibujo_z as dz

rod.EXIT = np.array([r, YMAX]); rod.EXIT_ANG = np.pi
TG = 3 * np.pi
VENT = 14.0      # media ventana (mm) del cambio de piso alrededor del lazo izquierdo


def make_rod(K=44):
    R = Rod((XMIN, r), 0.0, K=K, M=4)
    R.s_mid = None

    def pairmask(si, sj, L):
        mid = R.s_mid if R.s_mid is not None else L / 2
        li = np.where(si < mid - VENT, 0, np.where(si > mid + VENT, 1, -1))
        lj = np.where(sj < mid - VENT, 0, np.where(sj > mid + VENT, 1, -1))
        return (li == lj) & (li >= 0)
    R.pairmask = pairmask
    return R


def seed_from_path(R, e):
    """Curvatura inicial a partir de la forma cinemática."""
    t = dz.XR - e / 4
    A, B = dz.path(t, dz.XL, t)
    P = np.vstack([A, B[1:], rod.EXIT[None]])
    seg = np.diff(P, axis=0); ls = np.linalg.norm(seg, axis=1); m = ls > 1e-6
    seg, ls = seg[m], ls[m]
    s = np.r_[0, np.cumsum(ls)]; L = s[-1]
    th = np.unwrap(np.arctan2(seg[:, 1], seg[:, 0]))
    th = th - th[0]
    sm = 0.5 * (s[1:] + s[:-1])
    knots = np.linspace(0, L, R.K)
    thk = np.interp(knots, sm, th)
    kap = np.gradient(thk, knots)
    kap = np.convolve(kap, np.ones(3) / 3, mode='same')
    # mitad del recorrido en arco = lazo izquierdo
    R.s_mid = float(np.interp(np.pi * 1.5, th, sm))
    return kap, L


def main(out):
    R = make_rod()
    res = []
    t0 = time.time()
    prev = None
    for e in np.arange(0, 120.1, 2.0):
        c0, Lk = seed_from_path(R, e)
        L = Lk if prev is None else prev["L"] - 2.0
        cands = [c0 * Lk / L]
        if prev is not None: cands.insert(0, prev['c'] * prev['L'] / L)
        best = None
        for c in cands:
            b = R.solve(L, c, TG, rounds=3)
            if b['ok'] and (best is None or b['E'] < best['E']): best = b
        if best is None:
            print(f"e={e:4.0f} L={L:6.1f}  sin solución", flush=True)
            res.append(dict(e=float(e), L=float(L), ok=False)); continue
        prev = best
        th = best['th']; s = R.t * L
        R.s_mid = float(np.interp(1.5 * np.pi, th - th[0], s))
        # radio por piso
        kap = np.abs(best['kap'])
        mid = R.s_mid
        zona = lambda a, b_: 1 / kap[(s >= a) & (s <= b_)].max()
        RA, R2, RB = zona(0, mid - VENT), zona(mid - VENT, mid + VENT), zona(mid + VENT, L)
        X = best['X']
        tips = (X[s < mid - VENT, 0].max(), X[(s > mid - VENT) & (s < mid + VENT), 0].min(), X[s > mid + VENT, 0].max())
        print(f"e={e:4.0f} L={L:6.1f}  R lazo1/izq/lazo3 = {RA:4.1f} / {R2:4.1f} / {RB:4.1f}   "
              f"puntas x = {tips[0]:4.1f} {tips[1]:4.1f} {tips[2]:4.1f}   ({time.time()-t0:.0f}s)", flush=True)
        res.append(dict(e=float(e), L=float(L), ok=True, R=[RA, R2, RB], tips=list(map(float, tips)),
                        mid=mid, X=np.round(X[::2], 2).tolist(), s=np.round(s[::2], 2).tolist()))
    json.dump(res, open(out, 'w'))

if __name__ == "__main__":
    main(sys.argv[1])
