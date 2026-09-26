"""Busqueda dirigida del ancho minimo W (bisección) con el mejor largo L para cada W.

Para cada W: se evalua un abanico de L en paralelo (13 posiciones de carrera, ida y vuelta)
y se refina alrededor del mejor. Criterio: R interior >= 3 en todo el recorrido,
nada por encima de 10,5 en nominal, solver convergido y sin autointersecciones.
"""
import sys, time
import numpy as np
from multiprocessing import Pool
import elastica2 as E
import fast

STEPS = 13
RMIN = 3.0
import os
RMIN = float(os.environ.get('RMIN', 3.0)); E.TRAVEL = float(os.environ.get('TRAVEL', 12)); fast.XEXTRA = float(os.environ.get('XEXTRA', 0)); fast.LEFT = float(os.environ.get('LEFT', 0)); fast.GUIDES = set(filter(None, os.environ.get('GUIDES', '').split(',')))

def score(args):
    W, L, Rb = args
    fw, bw = fast.sweep(W, L, Rb, steps=STEPS)
    if fw is None:
        return -1.0
    st = fw + bw
    if not all(a['ok'] for a in st) or max(fw[-1]['ytop'], bw[0]['ytop']) > 10.501:
        return -1.0
    if any(E.selfcross(a) for a in (fw[0], fw[len(fw)//2], bw[len(bw)//2], fw[-1])):
        return -1.0
    return min(a['Rin'] for a in st)

def best_L(pool, W, Rb):
    Ls = np.arange(W + 4, W + 16.01, 1.0)
    s = pool.map(score, [(W, L, Rb) for L in Ls])
    i = int(np.argmax(s)); L0 = Ls[i]
    Lr = [L0 - .5, L0 + .5]
    s2 = pool.map(score, [(W, L, Rb) for L in Lr])
    cand = list(zip(s, Ls)) + list(zip(s2, Lr))
    return max(cand)

if __name__ == '__main__':
    Rb = float(sys.argv[1]); lo, hi = 12.0, 36.0
    t0 = time.time()
    with Pool(4) as pool:
        Rhi, Lhi = best_L(pool, hi, Rb)
        print(f"Rb={Rb} W={hi} -> R={Rhi:.2f} L={Lhi}", flush=True)
        while hi - lo > 0.25:
            mid = (lo + hi) / 2
            R, L = best_L(pool, mid, Rb)
            print(f"Rb={Rb} W={mid} -> R={R:.2f} L={L}  ({time.time()-t0:.0f}s)", flush=True)
            if R >= RMIN: hi, Lhi, Rhi = mid, L, R
            else: lo = mid
    print(f"RESULT Rb={Rb} Wmin={hi} L={Lhi} R={Rhi:.2f}")
