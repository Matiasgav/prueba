"""Frames para la pagina (geometria v2, solver rapido)."""
import json, numpy as np
from multiprocessing import Pool
import fast

def fr(a):
    return dict(X=round(a['X'], 3), x=[round(v, 3) for v in a['x']], y=[round(v, 3) for v in a['y']],
                k=[round(v, 4) for v in a['k']], Rmin=round(a['Rin'], 3), ymax=round(a['ytop'], 3))

def run(W, L, Rb, label):
    fw, bw = fast.sweep(W, L, Rb, steps=49)
    st = fw + bw
    return dict(label=label, W=W, L=L, Rb=Rb, YB=1 + Rb, fw=[fr(a) for a in fw], bw=[fr(a) for a in bw],
                Rmin=round(min(a['Rin'] for a in st), 3), ytop=round(max(a['ytop'] for a in st), 2),
                ynom=round(max(fw[-1]['ytop'], bw[0]['ytop']), 2))

def bestL(W, Rb):
    with Pool(4) as p:
        r = p.starmap(run, [(W, L, Rb, '') for L in np.arange(W + 6, W + 16.01, 0.5)])
    r = [d for d in r if d['ynom'] <= 10.5]
    return max(r, key=lambda d: d['Rmin'])

if __name__ == '__main__':
    u = bestL(26.4, 3.0); print('tu dibujo', u['L'], u['Rmin'])
    with Pool(3) as p:
        res = p.starmap(run, [(32.0, 43.5, 4.0, 'propuesta'), (30.5, 42.0, 4.0, 'mínimo'), (26.4, u['L'], 3.0, 'tu dibujo')])
    for d in res: print(d['label'], d['W'], d['L'], d['Rb'], d['Rmin'], d['ynom'], d['ytop'])
    json.dump(res, open('frames_v2.json', 'w'), separators=(',', ':'))
