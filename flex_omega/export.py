"""Genera frames (ida y vuelta) para el diagrama animado."""
import numpy as np, json
from multiprocessing import Pool
from elastica import *

def run(W, L, steps=41):
    Lf = L - S0 - S1
    fw = sweep(W, L, steps=steps)
    th = fw[-1]['th']; bw = []
    for X in np.linspace(W, W - TRAVEL, steps):
        th, r = solve(th, Lf, X, W); a = analyze(th, Lf, X); a['X'] = X; bw.append(a)
    # nodo a nodo: radio local (promedio de los dos segmentos) para colorear
    def fr(a):
        k = a['k']  # N+1 valores en nodos internos (incluye clamps)
        return dict(X=round(a['X'], 3), x=[round(v, 3) for v in a['x']], y=[round(v, 3) for v in a['y']],
                    k=[round(v, 4) for v in k], Rmin=round(a['Rmin'], 3), ymax=round(a['ymax'], 3))
    return dict(W=W, L=L, fw=[fr(a) for a in fw], bw=[fr(a) for a in bw],
                Rmin=round(min(a['Rmin'] for a in fw + bw), 3))

def best_L(W):
    best = None
    for L in np.arange(W + 6, W + 17.01, 0.5):
        try: d = run(W, L, steps=25)
        except Exception: continue
        if best is None or d['Rmin'] > best[1]: best = (L, d['Rmin'])
    return best

if __name__ == '__main__':
    bl = best_L(26.4); print('W=26.4 mejor L', bl)
    with Pool(3) as p:
        res = p.starmap(run, [(31.0, 45.0), (30.0, 44.5), (26.4, float(bl[0]))])
    for r in res: print(r['W'], r['L'], r['Rmin'])
    json.dump(res, open('frames.json', 'w'), separators=(',', ':'))
