"""Configuración 'omega': soldadura abajo-izquierda con el cable hacia arriba,
salida arriba-izquierda hacia la izquierda (-x).
Uso: python3 omega_sweep.py xp yp [L0 L1 paso] [out.json]
Recorre L de L0 a L1 por continuación (retracción) y de vuelta (extracción).
"""
import sys, json, time
import numpy as np
import rod
from rod import Rod, r, YMAX

rod.EXIT = np.array([r, YMAX]); rod.EXIT_ANG = np.pi
xp, yp = float(sys.argv[1]), float(sys.argv[2])
L0, L1, st = (float(v) for v in sys.argv[3:6]) if len(sys.argv) > 5 else (30., 100., 2.5)
out = sys.argv[6] if len(sys.argv) > 6 else None
PHI = np.deg2rad(float(__import__("os").environ.get("PHI", "90")))
R = Rod((xp, yp), PHI)
TG = np.pi            # giro neto +90° (de arriba a izquierda)


def step(L, prev):
    if prev is not None:
        b = R.solve(L, prev['c'] * prev['L'] / L, TG, rounds=2)
        if b['ok']: return b
    best = None
    seeds = [np.full(R.K, (TG - R.phi) / L)]
    # semilla tipo lóbulo: giro a la derecha y luego vuelta grande a la izquierda
    s = np.linspace(0, 1, R.K)
    seeds.append(np.where(s < .15, -1 / 6, (TG - R.phi + (np.pi / 2)) / (0.85 * L)))
    for c0 in seeds:
        b = R.solve(L, c0, TG)
        if b['ok'] and (best is None or b['E'] < best['E']): best = b
    return best


def run(Ls):
    res, prev = [], None
    for L in Ls:
        b = step(L, prev)
        if b is not None: prev = b
        res.append(dict(L=float(L), ok=b is not None, Rmin=float(b['Rmin']) if b else None,
                        X=np.round(b['X'][::2], 2).tolist() if b else None))
    return res

t = time.time()
Ls = np.arange(L0, L1 + 1e-9, st)
ret = run(Ls); ext = run(Ls[::-1])
line = ' '.join(f"{a['L']:.0f}:{a['Rmin']:.1f}" if a['ok'] else f"{a['L']:.0f}:X" for a in ret)
line2 = ' '.join(f"{a['L']:.0f}:{a['Rmin']:.1f}" if a['ok'] else f"{a['L']:.0f}:X" for a in ext[::-1])
print(f"pad=({xp},{yp}) {time.time()-t:.0f}s\n  ret: {line}\n  ext: {line2}", flush=True)
if out:
    json.dump(dict(pose=dict(x=xp, y=yp, phi=float(np.degrees(PHI))), exit=dict(x=r, y=YMAX, ang=180),
                   retract=ret, extract=ext), open(out, 'w'))
