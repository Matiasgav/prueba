"""Flex de canto (ancho vertical) que absorbe la carrera con una S lateral, en el plano horizontal.
Extremos empotrados paralelos (ambos en direccion +z); desplazamiento lateral d en x.
Pre-offset: nominal d=+6, retraido d=-6 (la S trabaja la mitad para cada lado).
Busca el largo en z minimo para que el radio interior sea >= 3 en todo el recorrido."""
import numpy as np
from scipy.optimize import minimize
N = 60; c = 0.1

def solve(th0, L, Z, d, mu=2e3):
    h = L/N; lam = np.zeros(2)
    def f(th):
        t = np.concatenate([[0.0], th, [0.0]]); dd = np.diff(t)
        v = dd@dd/h; g = 2*(dd[:-1]-dd[1:])/h
        cs, sn = np.cos(th), np.sin(th)
        r = np.array([h*cs.sum() - Z, h*sn.sum() - d])
        v += lam@r + mu/2*r@r
        g += (lam[0] + mu*r[0])*(-h*sn) + (lam[1] + mu*r[1])*(h*cs)
        return v, g
    th = th0
    for _ in range(10):
        th = minimize(f, th, jac=True, method='L-BFGS-B', options={'maxiter': 3000, 'gtol': 1e-10}).x
        r = np.array([h*np.cos(th).sum() - Z, h*np.sin(th).sum() - d]); lam += mu*r
        if abs(r).max() < 1e-4: break
    t = np.concatenate([[0.0], th, [0.0]]); k = np.abs(np.diff(t))/h
    y = np.cumsum(h*np.sin(th))
    return th, 1/k.max() - c, y.min(), y.max()

def worst(L, Z, travel=12.0):
    s = np.linspace(0, 1, N); th = 0.3*np.sin(2*np.pi*s)
    Rs = []; ext = [0, 0]
    for d in np.linspace(travel/2, -travel/2, 25):
        th, R, ymn, ymx = solve(th, L, Z, d); Rs.append(R); ext = [min(ext[0], ymn), max(ext[1], ymx)]
    return min(Rs), ext

import sys
for Z in [float(v) for v in sys.argv[1].split(",")]:
    best = max(((worst(Z*f, Z), Z*f) for f in (1.02, 1.05, 1.08, 1.12, 1.16, 1.2, 1.25)), key=lambda t: t[0][0])
    (R, ext), L = best
    print(f"largo en z={Z}  mejor L={L:.1f}  R int min={R:.2f}  barrido lateral x=[{ext[0]:.1f},{ext[1]:.1f}]")
