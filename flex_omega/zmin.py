"""Z minima de la S centrada segun el recto en los extremos y el radio exigido.
Criterio robusto: existe un largo L tal que L-0,25, L y L+0,25 cumplen R >= Rreq
con cuerpo del conector 6,3/6,65/7 y carrera 12 y 12,5 (ida y vuelta)."""
import numpy as np, sys
from multiprocessing import Pool
import s_lateral as S

def sweep(Z, L, a, travel, st, n=81):
    Ze, Le = Z - 2*st, L - 2*st
    s = np.linspace(0, 1, S.N); th = 0.3*np.sin(2*np.pi*s); Rmin = 99
    for d in np.r_[np.linspace(a, a - travel, n), np.linspace(a - travel, a, n)]:
        th, R, _, _ = S.solve(th, Le, Ze, d); Rmin = min(Rmin, R)
    return Rmin

def worst(args):
    Z, L, st = args
    return Z, L, st, min(sweep(Z, L, a, tr, st) for a in (5.65, 6.0, 6.35) for tr in (12.0, 12.5))

if __name__ == '__main__':
    st = float(sys.argv[1]); Zs = [float(v) for v in sys.argv[2].split(',')]
    jobs = [(Z, round(L, 3), st) for Z in Zs for L in np.arange(Z + 1.0, Z + 3.51, 0.125)]
    with Pool(4) as p: res = p.map(worst, jobs)
    for Z in Zs:
        r = sorted([(L, R) for ZZ, L, s_, R in res if ZZ == Z])
        print(f"recto {st} Z={Z}: " + " ".join(f"{L:.3f}:{R:.2f}" for L, R in r), flush=True)
