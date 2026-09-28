"""S con desplazamiento nominal distinto de 6 (pestaña A mm detras de la placa del conector).
Robusto: cuerpo del conector 6,3-7 (A +/- 0,35), carrera 12 y 12,5, ida y vuelta, 1 mm recto."""
import numpy as np, sys, os
from multiprocessing import Pool
import s_lateral as S
STR = 1.0

def sweep(Z, L, a, travel, n=121):
    Ze, Le = Z - 2*STR, L - 2*STR
    s = np.linspace(0, 1, S.N); th = 0.3*np.sin(2*np.pi*s); Rmin = 99; x0 = 0; x1 = 0
    for d in np.r_[np.linspace(a, a - travel, n), np.linspace(a - travel, a, n)]:
        th, R, y0, y1 = S.solve(th, Le, Ze, d); Rmin = min(Rmin, R); x0 = min(x0, y0); x1 = max(x1, y1)
    return Rmin, x0, x1

def worst(args):
    Z, L, A = args
    r = [sweep(Z, L, a, tr) for a in (A - 0.35, A, A + 0.35) for tr in (12.0, 12.5)]
    return Z, L, A, min(x[0] for x in r), min(x[1] for x in r), max(x[2] for x in r)

if __name__ == '__main__':
    A = float(sys.argv[1]); Zs = [float(v) for v in sys.argv[2].split(',')]
    lo, hi, st = (float(v) for v in os.environ.get('LRANGE', '1.5,3.5,0.125').split(','))
    jobs = [(Z, round(L, 3), A) for Z in Zs for L in np.arange(Z + lo, Z + hi + 1e-9, st)]
    with Pool(4) as p: res = p.map(worst, jobs)
    for Z in Zs:
        print(f"A={A} Z={Z}: " + " ".join(f"{L:.3f}:{R:.2f}" for ZZ, L, AA, R, _, _ in res if ZZ == Z), flush=True)
