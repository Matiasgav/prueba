"""Dimensionado de la S lateral (conector) con la pared lateral para la camara.

Vista de arriba. z: lateral; x: hacia el panel. Extremo fijo: canto de la seccion de camara (z = z0),
extremo movil: canto de la placa del conector (z = z0 + Z). Ambos salen en direccion +z con 1 mm recto.
Desplazamiento lateral del extremo movil respecto del fijo: a en nominal, a - 12 retraido.
a = (plano medio placa conector) - (plano medio seccion de camara) = -(b - 5.05 - 0.12 - 1.0) + 0.5 - 0.5
con b = cuerpo del conector detras del panel (6,3 a 7 mm) -> a entre -0.13 y -0.83.
Pared: la S no puede pasar de la cara delantera de la seccion de camara (+0,5 mm del plano medio).
"""
import numpy as np, sys
from multiprocessing import Pool
import s_lateral as S

STR = 1.0          # recto en cada extremo
import os
TRAVEL = float(os.environ.get('TRAVEL', 12.0))
WALL = 0.5

def a_of_b(b):
    # seccion de camara: plano medio en -(5.05 + 0.12 + 1.0 + 0.5) = -6.67 respecto del panel
    # placa del conector: cara delantera en -b, plano medio en -b - 0.5
    return (-b - 0.5) - (-6.67)

def sweep_R(Z, L, a, n=41):
    Ze, Le = Z - 2*STR, L - 2*STR
    s = np.linspace(0, 1, S.N); th = -0.3*np.sin(np.pi*s); Rs = []; xmin = 0; xmax = -9
    for d in np.r_[np.linspace(a, a - TRAVEL, n), np.linspace(a - TRAVEL, a, n)]:
        th, R, y0, y1 = S.solve(th, Le, Ze, d, wall=WALL)
        Rs.append(R); xmin = min(xmin, y0); xmax = max(xmax, y1)
    return min(Rs), xmin, xmax

def robust(args):
    Z, L = args
    out = [sweep_R(Z, L, a_of_b(b)) for b in (6.3, 6.65, 7.0)]
    return Z, L, min(o[0] for o in out), min(o[1] for o in out), max(o[2] for o in out)

if __name__ == '__main__':
    Zs = [float(v) for v in sys.argv[1].split(',')]
    lo, hi, st = (float(v) for v in os.environ.get('LRANGE', '2.0,7.0,0.5').split(','))
    jobs = [(Z, round(L, 2)) for Z in Zs for L in np.arange(Z + lo, Z + hi + 1e-9, st)]
    with Pool(4) as p:
        res = p.map(robust, jobs)
    for Z in Zs:
        r = [x for x in res if x[0] == Z]
        print(f"Z={Z}: " + "  ".join(f"L{L:.1f}:{R:.2f}" for _, L, R, _, _ in r))
