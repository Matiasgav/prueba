"""Solver rapido de la elastica: Lagrangiano aumentado + L-BFGS con gradiente analitico.
Misma geometria y restricciones que elastica2.py (v2)."""
import numpy as np
from scipy.optimize import minimize
import elastica2 as E

XEXTRA = 0.0
# guias de radio (discos que el flex no puede penetrar): 'mb' fija en la salida de la mainboard,
# 'cn' solidaria a la placa del conector (se mueve con ella). Radio = radio interior de la guia.
GUIDES = set()
# el bucle puede pasar sobre la mainboard (x<0) si y > HL (altura libre sobre sus componentes)
LEFT, HL = 0.0, 3.0
RG = 3.0  # espacio permitido mas alla de la linea nominal (bajo el conector)

N = E.N

def solve(th0, Lf, X, W, YB, mu=2e3, outer=8):
    h = Lf/N; c = E.TF/2
    p0 = np.array([E.S0, c]); pe = np.array([X - c, YB - E.S1])
    xl = X - E.TF - E.TB - c; yo = YB - c
    lam = np.zeros(2)
    def f(th):
        t = np.concatenate([[0.0], th, [np.pi/2]]); d = np.diff(t)
        en = (d@d)/h; gen = 2*(d[:-1]-d[1:])/h
        cs, sn = np.cos(th), np.sin(th)
        x = p0[0] + np.cumsum(h*cs); y = p0[1] + np.cumsum(h*sn)
        # extremo (igualdad)
        r = np.array([x[-1]-pe[0], y[-1]-pe[1]])
        val = en + lam@r + mu/2*(r@r)
        gx = np.zeros(N); gy = np.zeros(N)  # dval/dx_k, dval/dy_k por nodo
        gx[-1] += lam[0] + mu*r[0]; gy[-1] += lam[1] + mu*r[1]
        # paredes: y>=c, x>=c, x<=W-c
        xw = np.where(y > HL, -LEFT, 0.0) + c
        for v, gv, sgn in ((c - y, gy, -1), (xw - x, gx, -1), (x - (W + XEXTRA - c), gx, 1)):
            p = np.maximum(v, 0); val += mu*(p@p); gv += sgn*2*mu*p
        # obstaculo placa+conector: prohibido x>xl y y>yo -> penetracion = min(x-xl, y-yo)
        dx_, dy_ = x - xl, y - yo
        pen = np.minimum(dx_, dy_); m = pen > 0
        val += mu*np.sum(pen[m]**2)
        usex = m & (dx_ <= dy_); usey = m & (dy_ < dx_)
        gx[usex] += 2*mu*pen[usex]; gy[usey] += 2*mu*pen[usey]
        # guias de radio
        for cx, cy in discs(X, YB):
            ddx, ddy = x - cx, y - cy; dist = np.sqrt(ddx**2 + ddy**2) + 1e-12
            p = np.maximum(RG + c - dist, 0); val += mu*(p@p)
            gx += -2*mu*p*ddx/dist; gy += -2*mu*p*ddy/dist
        # dx_k/dth_j = -h sin th_j (j<=k)  -> suma acumulada inversa
        Gx = np.cumsum(gx[::-1])[::-1]; Gy = np.cumsum(gy[::-1])[::-1]
        grad = gen + Gx*(-h*sn) + Gy*(h*cs)
        return val, grad
    th = th0.copy()
    for _ in range(outer):
        res = minimize(f, th, jac=True, method='L-BFGS-B', options={'maxiter': 3000, 'gtol': 1e-9})
        th = res.x
        x = p0[0] + np.sum(h*np.cos(th)); y = p0[1] + np.sum(h*np.sin(th))
        r = np.array([x-pe[0], y-pe[1]])
        lam += mu*r
        if np.abs(r).max() < 1e-3: break
    viol = violation(th, Lf, X, W, YB)
    return th, (np.abs(r).max() < 2e-3 and viol < 0.02)

def discs(X, YB):
    c = E.TF/2; out = []
    if 'mb' in GUIDES: out.append((E.S0, 2*c + RG))
    if 'cn' in GUIDES: out.append((X - 2*c - RG, YB - E.S1))
    return out

def violation(th, Lf, X, W, YB):
    h = Lf/N; c = E.TF/2
    x = E.S0 + np.cumsum(h*np.cos(th)); y = c + np.cumsum(h*np.sin(th))
    xl = X - E.TF - E.TB - c; yo = YB - c
    dv = [ (RG + c - np.hypot(x-cx, y-cy)).max() for cx, cy in discs(X, YB)]
    return max([0] + dv + [(c-y).max(), (np.where(y > HL, -LEFT, 0.0) + c - x).max(), (x-(W+XEXTRA-c)).max(), np.minimum(x-xl, y-yo).max()])

def sweep(W, L, Rb, steps=25):
    YB = 1 + Rb; E.YB = YB
    Lf = L - E.S0 - E.S1; s = np.linspace(0, 1, N)
    best = None
    for A in (1.4, 1.0, 1.8, 0.6, 2.2):
        th, ok = solve(np.pi/2*s**3 + A*np.sin(2*np.pi*s)*(1-s), Lf, W, W, YB)
        if ok: best = th; break
    if best is None: return None, None
    th = best; bw = []; fw = []
    for X in np.linspace(W, W - E.TRAVEL, steps):
        th, ok = solve(th, Lf, X, W, YB); a = E.analyze(th, Lf, X); a.update(X=X, ok=ok, th=th.copy()); bw.append(a)
    for X in np.linspace(W - E.TRAVEL, W, steps):
        th, ok = solve(th, Lf, X, W, YB); a = E.analyze(th, Lf, X); a.update(X=X, ok=ok, th=th.copy()); fw.append(a)
    return fw, bw
