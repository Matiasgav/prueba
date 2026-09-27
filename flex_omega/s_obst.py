"""S lateral con la placa de la camara como obstaculo (layout del usuario, planta del 27/9).

Coordenadas relativas a la pestaña fija: z a lo largo de la S (0 = canto de la pestaña, Z = canto de la placa
del conector), y lateral hacia el panel (0 = linea del flex en la pestaña). Ambos extremos salen en +z con 1 mm recto.
Obstaculo: placa de camara, cara trasera en y = YO (hacia el panel todo ocupado) para z <= ZO. El flex (cara) debe
quedar CLEAR mm detras. En nominal el extremo movil esta en y = a (5 +/- 0,35), retraido en a - 12."""
import numpy as np
from scipy.optimize import minimize
N, c, STR = 60, 0.1, 1.0

def solve(th0, L, Z, d, yo, zo, mu=3e3):
    Le, Ze = L - 2*STR, Z - 2*STR; h = Le/N; zoe = zo - STR          # obstaculo en coordenadas del tramo elastico
    lam = np.zeros(2)
    def f(th):
        t = np.concatenate([[0.0], th, [0.0]]); dd = np.diff(t)
        v = dd@dd/h; g = 2*(dd[:-1]-dd[1:])/h
        cs, sn = np.cos(th), np.sin(th); z = np.cumsum(h*cs); y = np.cumsum(h*sn)
        r = np.array([z[-1] - Ze, y[-1] - d]); v += lam@r + mu/2*r@r
        gz = np.zeros(N); gy = np.zeros(N); gz[-1] += lam[0] + mu*r[0]; gy[-1] += lam[1] + mu*r[1]
        # obstaculo: penetracion = min(y - (yo - c), zoe - z)
        dy_, dz_ = y - (yo - c), zoe - z; pen = np.minimum(dy_, dz_); m = pen > 0
        v += mu*np.sum(pen[m]**2)
        uy = m & (dy_ <= dz_); uz = m & (dz_ < dy_)
        gy[uy] += 2*mu*pen[uy]; gz[uz] += -2*mu*pen[uz]
        Gz = np.cumsum(gz[::-1])[::-1]; Gy = np.cumsum(gy[::-1])[::-1]
        return v, g + Gz*(-h*sn) + Gy*(h*cs)
    th = th0
    for _ in range(12):
        th = minimize(f, th, jac=True, method='L-BFGS-B', options={'maxiter': 4000, 'gtol': 1e-10}).x
        z = np.sum(h*np.cos(th)); y = np.sum(h*np.sin(th)); r = np.array([z - Ze, y - d]); lam += mu*r
        if abs(r).max() < 1e-4: break
    t = np.concatenate([[0.0], th, [0.0]]); k = np.abs(np.diff(t))/h
    z = STR + np.concatenate([[0], np.cumsum(h*np.cos(th))]); y = np.concatenate([[0], np.cumsum(h*np.sin(th))])
    m = z <= zo
    gap = (yo - c) - y[m].max() if m.any() else 9
    return th, 1/k.max() - c, gap, z, y

def sweep(Z, L, a, yo, zo, travel=12.0, n=121, keep=False):
    s = np.linspace(0, 1, N); th = 0.3*np.sin(2*np.pi*s); Rmin = 99; gmin = 99; shapes = []
    for d in np.r_[np.linspace(a, a - travel, n), np.linspace(a - travel, a, n)]:
        th, R, gap, z, y = solve(th, L, Z, d, yo, zo); Rmin = min(Rmin, R); gmin = min(gmin, gap)
        if keep: shapes.append((d, z, y, R))
    return Rmin, gmin, shapes

def worst(args):
    Z, L, yo, zo = args
    r = [sweep(Z, L, a, yo, zo, tr)[:2] for a in (4.65, 5.0, 5.35) for tr in (12.0, 12.5)]
    return Z, L, yo, zo, min(x[0] for x in r), min(x[1] for x in r)
