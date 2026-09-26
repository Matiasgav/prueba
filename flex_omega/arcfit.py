"""Cadena de arcos de curvatura constante (G1) ajustada a la elastica.
Extremos exactos (posicion y tangente) y largo total igual al del flex."""
import numpy as np
from scipy.optimize import minimize

def chain(p0, th0, kap, lens, npts=400):
    """Evalua la cadena: devuelve puntos muestreados por largo de arco."""
    s_all = []; P = []; p = np.array(p0, float); th = th0; s0 = 0
    for k, l in zip(kap, lens):
        ss = np.linspace(0, l, max(3, int(npts*l/np.sum(lens))))
        if abs(k) < 1e-9:
            xs = p[0] + ss*np.cos(th); ys = p[1] + ss*np.sin(th)
        else:
            xs = p[0] + (np.sin(th + k*ss) - np.sin(th))/k; ys = p[1] - (np.cos(th + k*ss) - np.cos(th))/k
        P.append(np.stack([xs, ys], 1)); s_all.append(s0 + ss)
        p = np.array([xs[-1], ys[-1]]); th += k*l; s0 += l
    return np.concatenate(s_all), np.concatenate(P), p, th

def endpoint(p0, th0, kap, lens):
    p = np.array(p0, float); th = th0
    for k, l in zip(kap, lens):
        if abs(k) < 1e-9: p = p + l*np.array([np.cos(th), np.sin(th)])
        else: p = p + np.array([np.sin(th + k*l) - np.sin(th), -(np.cos(th + k*l) - np.cos(th))])/k
        th += k*l
    return p, th

def fit(sx, sy, th0, th1, m, kmax=1.0, fixed0=()):
    """sx, sy: puntos de la elastica (tramo libre) equiespaciados en largo de arco."""
    ds = np.hypot(np.diff(sx), np.diff(sy)); s = np.concatenate([[0], np.cumsum(ds)]); Lf = s[-1]
    th = np.unwrap(np.arctan2(np.gradient(sy), np.gradient(sx)))
    # arranque: curvatura media por tramos iguales
    edges = np.linspace(0, Lf, m + 1); lens0 = np.diff(edges)
    k0 = np.array([(np.interp(edges[i+1], s, th) - np.interp(edges[i], s, th))/lens0[i] for i in range(m)])
    p0 = np.array([sx[0], sy[0]]); pe = np.array([sx[-1], sy[-1]])
    def unpack(v): return v[:m], v[m:]
    def obj(v):
        kap, lens = unpack(v)
        ss, P, _, _ = chain(p0, th0, kap, lens)
        xi = np.interp(ss, s, sx); yi = np.interp(ss, s, sy)
        return np.mean((P[:, 0]-xi)**2 + (P[:, 1]-yi)**2)
    cons = [{'type': 'eq', 'fun': lambda v: endpoint(p0, th0, *unpack(v))[0] - pe},
            {'type': 'eq', 'fun': lambda v: np.array([endpoint(p0, th0, *unpack(v))[1] - th1])},
            {'type': 'eq', 'fun': lambda v: np.array([np.sum(v[m:]) - Lf])}]
    bounds = [((0, 0) if i in fixed0 else (-kmax, kmax)) for i in range(m)] + [(0.3, None)]*m
    k0 = np.clip(k0, -kmax, kmax); k0[list(fixed0)] = 0
    r = minimize(obj, np.concatenate([k0, lens0]), constraints=cons, bounds=bounds, method='SLSQP',
                 options={'maxiter': 2000, 'ftol': 1e-12})
    kap, lens = unpack(r.x)
    ss, P, _, _ = chain(p0, th0, kap, lens, npts=2000)
    # desviacion maxima: distancia de cada punto de la elastica a la cadena
    Q = np.stack([sx, sy], 1)
    dev = max(np.min(np.hypot(*(P - q).T)) for q in Q[::5])
    return kap, lens, dev, r.success
