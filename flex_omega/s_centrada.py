"""S lateral centrada (opcion 2) para el conector: la pestaña fija esta 6 mm detras de la posicion nominal
de la placa del conector, asi la S trabaja +6 / -6 mm. 1 mm recto en cada extremo. Sin pared.
Tolerancia: cuerpo del conector 6,3-7 mm -> desplazamiento nominal 6 +/- 0,35."""
import numpy as np, sys, os
from multiprocessing import Pool
import s_lateral as S
STR = 1.0

def sweep(Z, L, a, travel, n=161, wall=None):
    Ze, Le = Z - 2*STR, L - 2*STR
    s = np.linspace(0, 1, S.N); th = 0.3*np.sin(2*np.pi*s); Rs = []; x0 = 0; x1 = 0; shapes = []
    for d in np.r_[np.linspace(a, a - travel, n), np.linspace(a - travel, a, n)]:
        th, R, y0, y1 = S.solve(th, Le, Ze, d, wall=wall)
        Rs.append(R); x0 = min(x0, y0); x1 = max(x1, y1); shapes.append(th.copy())
    return min(Rs), x0, x1, Rs, shapes

def robust(args):
    Z, L = args
    res = [sweep(Z, L, a, tr)[:3] for a in (5.65, 6.0, 6.35) for tr in (12.0, 12.5)]
    return Z, L, min(r[0] for r in res), min(r[1] for r in res), max(r[2] for r in res)

if __name__ == '__main__':
    Zs = [float(v) for v in sys.argv[1].split(',')]
    lo, hi, st = (float(v) for v in os.environ.get('LRANGE', '0.5,4.0,0.25').split(','))
    jobs = [(Z, round(L, 2)) for Z in Zs for L in np.arange(Z + lo, Z + hi + 1e-9, st)]
    with Pool(4) as p: res = p.map(robust, jobs)
    for Z in Zs:
        print(f"Z={Z}: " + "  ".join(f"L{L}:{R:.2f}[{x0:+.1f},{x1:+.1f}]" for ZZ, L, R, x0, x1 in res if ZZ == Z))
