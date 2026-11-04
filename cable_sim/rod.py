"""Elástica plana, versión reducida (rápida).

La curvatura del eje se representa como lineal a tramos en K nodos
equiespaciados de la longitud interna L:  kappa(s) = sum c_j * hat_j(s).
theta(s) = phi + ∫kappa ;  r(s) = P + ∫(cos theta, sin theta).
Energía de flexión U = 1/2 ∫ kappa² ds (EI = 1) -> la forma de equilibrio
es la que minimiza U con las restricciones (SLSQP):
  igualdad : theta(L) = 90° (+2πm, sentido de giro) y r(L) = salida E
  desigual.: eje a >= r de las paredes, tramos no vecinos a >= 2r
Como kappa es lineal a tramos, |kappa|max = max|c_j|  ->  Rmin = 1/max|c_j|.
"""
import numpy as np
from scipy.optimize import minimize

W, H = 42.62, 24.57
D = 3.5; r = D / 2
XMIN, XMAX, YMIN, YMAX = r, W - r, r, H - r
EXIT = np.array([r, YMAX])          # entra al canal de 3.5 mm entre pared y placa
EXIT_ANG = np.pi / 2
K = 16      # nodos de curvatura
M = 4       # sub-muestras por tramo


class Rod:
    def __init__(self, P, phi, K=K, M=M):
        self.P = np.asarray(P, float); self.phi = float(phi); self.K = K; self.M = M
        self.t = np.linspace(0, 1, (K - 1) * M + 1)          # parámetro de muestreo
        knots = np.linspace(0, 1, K)
        self.B = np.maximum(0, 1 - np.abs(self.t[:, None] - knots[None, :]) * (K - 1))

    def curve(self, c, L):
        kap = self.B @ c
        dt = L * np.diff(self.t)
        th = self.phi + np.r_[0, np.cumsum(0.5 * (kap[1:] + kap[:-1]) * dt)]
        thm = 0.5 * (th[1:] + th[:-1])
        X = self.P + np.vstack([[0, 0], np.cumsum(np.c_[np.cos(thm), np.sin(thm)] * dt[:, None], 0)])
        return kap, th, X

    def energy(self, c, L):
        kap = self.B @ c; dt = L * np.diff(self.t)
        return 0.5 * np.sum(0.5 * (kap[1:] ** 2 + kap[:-1] ** 2) * dt)

    def jac(self, c, L):
        """Derivadas analíticas de theta y X respecto de c."""
        kap, th, X = self.curve(c, L)
        dt = L * np.diff(self.t)
        A = np.vstack([np.zeros(self.K), np.cumsum(0.5 * (self.B[1:] + self.B[:-1]) * dt[:, None], 0)])
        Am = 0.5 * (A[1:] + A[:-1])
        thm = 0.5 * (th[1:] + th[:-1])
        jx = np.vstack([np.zeros(self.K), np.cumsum((-np.sin(thm) * dt)[:, None] * Am, 0)])
        jy = np.vstack([np.zeros(self.K), np.cumsum((np.cos(thm) * dt)[:, None] * Am, 0)])
        return kap, th, X, A, jx, jy

    def solve(self, L, c0, turn_target, rounds=3):
        dt = L * np.diff(self.t)
        Q = 0.5 * (self.B[1:] ** 2 + self.B[:-1] ** 2) * dt[:, None]   # para gradiente aprox.
        Bm = self.B
        w8 = np.r_[dt / 2, 0] + np.r_[0, dt / 2]                         # pesos trapecio
        H_ = (Bm * w8[:, None]).T @ Bm                                   # U = 1/2 c'Hc

        ds = dt[0]
        gap = int(np.ceil(1.6 * D / ds)) + 1
        n = len(self.t)
        I0, J0 = np.triu_indices(n, k=gap)
        c = np.asarray(c0, float).copy()

        def eq(c):
            kap, th, X = self.curve(c, L)
            return np.r_[th[-1] - turn_target, X[-1] - EXIT]

        def eq_j(c):
            kap, th, X, A, jx, jy = self.jac(c, L)
            return np.vstack([A[-1], jx[-1], jy[-1]])

        for _ in range(rounds):
            kap, th, X = self.curve(c, L)
            if len(I0):
                d = np.linalg.norm(X[I0] - X[J0], axis=1)
                sel = d < 3 * D
                I, J = I0[sel], J0[sel]
            else:
                I = J = np.array([], int)

            def ineq(c, I=I, J=J):
                kap, th, X = self.curve(c, L)
                x, y = X[1:, 0], X[1:, 1]
                w = np.r_[x - XMIN, XMAX - x, y - YMIN, YMAX - y]
                if len(I):
                    dd = X[I] - X[J]
                    w = np.r_[w, (np.einsum('ij,ij->i', dd, dd) - D * D) / D]
                return w

            def ineq_j(c, I=I, J=J):
                kap, th, X, A, jx, jy = self.jac(c, L)
                rows = [jx[1:], -jx[1:], jy[1:], -jy[1:]]
                if len(I):
                    dd = X[I] - X[J]
                    rows.append(2 * (dd[:, :1] * (jx[I] - jx[J]) + dd[:, 1:] * (jy[I] - jy[J])) / D)
                return np.vstack(rows)

            res = minimize(lambda c: 0.5 * c @ H_ @ c, c, jac=lambda c: H_ @ c, method='SLSQP',
                           constraints=[dict(type='eq', fun=eq, jac=eq_j),
                                        dict(type='ineq', fun=ineq, jac=ineq_j)],
                           options=dict(maxiter=300, ftol=1e-12))
            c = res.x
        kap, th, X = self.curve(c, L)
        e = eq(c)
        x, y = X[1:, 0], X[1:, 1]
        wmin = min((x - XMIN).min(), (XMAX - x).min(), (y - YMIN).min(), (YMAX - y).min())
        scmin = (np.linalg.norm(X[I0] - X[J0], axis=1).min() - D) if len(I0) else 9.0
        ok = bool(np.abs(e).max() < 1e-3 and wmin > -1e-3 and scmin > -0.05)
        return dict(c=c, X=X, th=th, kap=kap, L=L, E=0.5 * c @ H_ @ c, ok=ok,
                    Rmin=1 / max(np.abs(c).max(), 1e-9), target=turn_target)


def targets(phi):
    d = (EXIT_ANG - phi + np.pi) % (2 * np.pi) - np.pi     # giro neto más corto
    return [phi + d, phi + d + 2 * np.pi, phi + d - 2 * np.pi]


def straight_guess(rod, L, target):
    return np.full(rod.K, (target - rod.phi) / L)


def best_state(rod, L, prev=None, light=False):
    best = None
    tries = []
    if prev is not None: tries.append((prev['c'] * prev['L'] / L, prev['target']))
    for tg in targets(rod.phi)[:2]:
        tries.append((straight_guess(rod, L, tg), tg))
        # arco + contra-arco (S) como semilla alternativa
        if light: continue
        s = np.sin(np.linspace(0, 2 * np.pi, rod.K)) * 0.06
        tries.append((straight_guess(rod, L, tg) + s, tg))
        tries.append((straight_guess(rod, L, tg) - s, tg))
    for c0, tg in tries:
        r_ = rod.solve(L, c0, tg)
        if r_['ok'] and (best is None or r_['E'] < best['E'] - 1e-9):
            best = r_
    return best
