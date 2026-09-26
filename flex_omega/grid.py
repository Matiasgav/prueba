"""Barrido W x L: para cada combinacion simula ida (retraido->nominal) y vuelta."""
import numpy as np, json, sys
from multiprocessing import Pool
from elastica import *

def evaluate(args):
    W, L = args
    Lf = L - S0 - S1
    try:
        fw = sweep(W, L, steps=25)
        th = fw[-1]['th']; bw = []
        for X in np.linspace(W, W - TRAVEL, 25):
            th, r = solve(th, Lf, X, W); a = analyze(th, Lf, X); a['ok'] = r.success; bw.append(a)
    except Exception as e:
        return dict(W=W, L=L, err=str(e))
    allst = fw + bw
    nom = [fw[-1], bw[0]]
    return dict(W=W, L=L,
                Rmin=min(a['Rmin'] for a in allst),
                Rmin_fw=min(a['Rmin'] for a in fw), Rmin_bw=min(a['Rmin'] for a in bw),
                ymax_nom=max(a['ymax'] for a in nom), xmax=max(a['xmax'] for a in allst),
                xmin=min(a['xmin'] for a in allst), ok=all(a['ok'] for a in allst))

if __name__ == '__main__':
    Ws = np.arange(float(sys.argv[1]), float(sys.argv[2]) + 1e-9, float(sys.argv[3]))
    jobs = [(W, L) for W in Ws for L in np.arange(W + 10, W + 17.01, 0.5)]
    with Pool() as p:
        res = p.map(evaluate, jobs)
    json.dump(res, open(sys.argv[4], 'w'))
    for r in res:
        if 'err' in r: continue
        good = r['Rmin'] >= 3 and r['ymax_nom'] <= 10.51 and r['ok']
        if good: print(f"W={r['W']:.1f} L={r['L']:.1f} Rmin={r['Rmin']:.2f} (fw {r['Rmin_fw']:.2f} bw {r['Rmin_bw']:.2f}) ymax={r['ymax_nom']:.2f}")
