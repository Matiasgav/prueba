"""Solver rapido generalizado (Lagrangiano aumentado + L-BFGS) con dos geometrias de placa de conector.

cfg['mode'] = 'colgada': placa de y=YB a 10.5, el flex sale por el borde INFERIOR hacia abajo (v2).
cfg['mode'] = 'piso'   : placa apoyada en el piso de y=0 a HB, el flex sale por el borde SUPERIOR hacia arriba.
En ambos el flex va por la cara derecha de la placa (conector tambien a la derecha).
Coordenadas: origen en el borde de la mainboard, cara inferior del flex en y=0. X = cara exterior del flex.
"""
import numpy as np
from scipy.optimize import minimize

N, TF, TB, S0, S1, H = 60, 0.2, 1.0, 1.0, 1.0, 10.5
c = TF/2

def ends(cfg, X):
    if cfg['mode'] == 'colgada':
        return np.array([X - c, cfg['YB'] - S1]), np.pi/2
    return np.array([X - c, cfg['HB'] + S1]), -np.pi/2

def obstacle(cfg, X):
    """Zona prohibida para la linea media: x > xl y (y > yo si colgada | y < yo si piso)."""
    xl = X - TF - TB - c
    if cfg['mode'] == 'piso_atras':  # flex por la cara trasera: la placa queda delante (x > X)
        return X - c - 1e-3, cfg['HB'] + c, -1
    if cfg['mode'] == 'colgada':
        return xl, cfg['YB'] - c, +1
    return xl, cfg['HB'] + c, -1

def solve(th0, cfg, L, X, W, mu=2e3, outer=10):
    Lf = L - S0 - S1; h = Lf/N
    p0 = np.array([S0, c]); pe, te = ends(cfg, X)
    xl, yo, sg = obstacle(cfg, X)
    lam = np.zeros(2)
    def f(th):
        t = np.concatenate([[0.0], th, [te]]); d = np.diff(t)
        val = (d@d)/h; grad = 2*(d[:-1]-d[1:])/h
        cs, sn = np.cos(th), np.sin(th)
        x = p0[0] + np.cumsum(h*cs); y = p0[1] + np.cumsum(h*sn)
        r = np.array([x[-1]-pe[0], y[-1]-pe[1]])
        val += lam@r + mu/2*(r@r)
        gx = np.zeros(N); gy = np.zeros(N)
        gx[-1] += lam[0] + mu*r[0]; gy[-1] += lam[1] + mu*r[1]
        for v, gv, s in ((c - y, gy, -1), (c - x, gx, -1), (x - (W - c), gx, 1)):
            p = np.maximum(v, 0); val += mu*(p@p); gv += s*2*mu*p
        dx_, dy_ = x - xl, sg*(y - yo)
        pen = np.minimum(dx_, dy_); m = pen > 0
        val += mu*np.sum(pen[m]**2)
        ux = m & (dx_ <= dy_); uy = m & (dy_ < dx_)
        gx[ux] += 2*mu*pen[ux]; gy[uy] += 2*mu*sg*pen[uy]
        Gx = np.cumsum(gx[::-1])[::-1]; Gy = np.cumsum(gy[::-1])[::-1]
        return val, grad + Gx*(-h*sn) + Gy*(h*cs)
    th = th0.copy()
    for _ in range(outer):
        th = minimize(f, th, jac=True, method='L-BFGS-B', options={'maxiter': 3000, 'gtol': 1e-9}).x
        x = p0[0] + np.sum(h*np.cos(th)); y = p0[1] + np.sum(h*np.sin(th))
        r = np.array([x-pe[0], y-pe[1]]); lam += mu*r
        if np.abs(r).max() < 1e-3: break
    return th, np.abs(r).max() < 2e-3 and violation(th, cfg, L, X, W) < 0.02

def shape(th, cfg, L, X):
    Lf = L - S0 - S1; h = Lf/N; pe, te = ends(cfg, X)
    t = np.concatenate([[0.0], th, [te]]); k = np.abs(np.diff(t))/h
    x = S0 + np.concatenate([[0], np.cumsum(h*np.cos(th))]); y = c + np.concatenate([[0], np.cumsum(h*np.sin(th))])
    endy = cfg['YB'] if cfg['mode'] == 'colgada' else cfg['HB']
    xs = np.concatenate([[0], x, [X - c]]); ys = np.concatenate([[c], y, [endy]])
    return dict(X=X, x=xs, y=ys, k=k, Rin=1/k.max() - c, ytop=ys.max() + c)

def violation(th, cfg, L, X, W):
    a = shape(th, cfg, L, X); x, y = a['x'][1:-1], a['y'][1:-1]
    xl, yo, sg = obstacle(cfg, X)
    return max(0, (c-y).max(), (c-x).max(), (x-(W-c)).max(), np.minimum(x-xl, sg*(y-yo)).max())

def guesses(cfg):
    s = np.linspace(0, 1, N)
    if cfg['mode'] == 'colgada':
        return [np.pi/2*s**3 + A*np.sin(2*np.pi*s)*(1-s) for A in (1.4, 1.0, 1.8, 0.6, 2.2)]
    # arco: sube y baja sobre la placa
    return [np.pi/2*np.sin(np.pi*s)*A - np.pi/2*s**2 for A in (1.2, 1.0, 1.5, 0.8, 1.8)]

def sweep(cfg, W, L, steps=25, travel=12.0):
    th = None
    for g in guesses(cfg):
        t, ok = solve(g, cfg, L, W, W)
        if ok: th = t; break
    if th is None: return None, None
    bw, fw = [], []
    for X in np.linspace(W, W - travel, steps):
        th, ok = solve(th, cfg, L, X, W); a = shape(th, cfg, L, X); a.update(ok=ok, th=th.copy()); bw.append(a)
    for X in np.linspace(W - travel, W, steps):
        th, ok = solve(th, cfg, L, X, W); a = shape(th, cfg, L, X); a.update(ok=ok, th=th.copy()); fw.append(a)
    return fw, bw

def selfcross(a):
    P = np.stack([a['x'], a['y']], 1); n = len(P) - 1
    for i in range(n):
        p, r = P[i], P[i+1] - P[i]
        for j in range(i + 2, n):
            q, t = P[j], P[j+1] - P[j]; den = r[0]*t[1] - r[1]*t[0]
            if abs(den) < 1e-12: continue
            u = ((q-p)[0]*t[1] - (q-p)[1]*t[0])/den; v = ((q-p)[0]*r[1] - (q-p)[1]*r[0])/den
            if 0 < u < 1 and 0 < v < 1: return True
    return False

def score(args):
    cfg, W, L, travel = args
    fw, bw = sweep(cfg, W, L, steps=13, travel=travel)
    if fw is None: return -1.0
    st = fw + bw
    if not all(a['ok'] for a in st) or max(fw[-1]['ytop'], bw[0]['ytop']) > H + 1e-3: return -1.0
    if any(selfcross(a) for a in (fw[0], fw[6], bw[6], fw[-1])): return -1.0
    return min(a['Rin'] for a in st)

def best_L(pool, cfg, W, travel=12.0):
    Ls = np.arange(W + 4, W + 18.01, 1.0)
    s = pool.map(score, [(cfg, W, L, travel) for L in Ls]); i = int(np.argmax(s))
    Lr = [Ls[i] - .5, Ls[i] + .5]; s2 = pool.map(score, [(cfg, W, L, travel) for L in Lr])
    return max(list(zip(s, Ls)) + list(zip(s2, Lr)))

def wmin(pool, cfg, rmin=3.0, travel=12.0, lo=10.0, hi=36.0, tol=0.25):
    R, L = best_L(pool, cfg, hi, travel); best = (hi, L, R)
    if R < rmin: return None, (hi, L, R)
    while hi - lo > tol:
        mid = (lo + hi)/2; R, L = best_L(pool, cfg, mid, travel)
        if R >= rmin: hi = mid; best = (mid, L, R)
        else: lo = mid
    return best, None
