"""Simulacion del flex como elastica (varilla inextensible, ambos extremos empotrados).

Coordenadas en mm. Origen = inicio del tramo recto de 1 mm que sale de la mainboard.
- Extremo mainboard: sale horizontal (+x); los primeros S0 mm son rectos (zona de transicion rigido-flex).
- Extremo conector: entra vertical (+y) al borde de la placa del conector en (X, H);
  los ultimos S1 mm son rectos.
- Nominal: X = W. Retraido: X = W - TRAVEL.
Restricciones de contacto (paredes): y >= 0, 0 <= x <= W en todos los estados.
Chequeos: radio >= RMIN en todo el recorrido; en nominal y <= H.
"""
import numpy as np
from scipy.optimize import minimize

H, TRAVEL, RMIN, S0, S1 = 10.5, 12.0, 3.0, 1.0, 1.0
N = 60

def geom(th, h, p0):
    x = p0[0] + np.concatenate([[0], np.cumsum(h*np.cos(th))])
    y = p0[1] + np.concatenate([[0], np.cumsum(h*np.sin(th))])
    return x, y

def solve(th0, Lf, X, W, walls=True):
    h = Lf/N
    p0 = np.array([S0, 0.0]); pe = np.array([X, H - S1])
    a, b = 0.0, np.pi/2
    def E(th):
        t = np.concatenate([[a], th, [b]]); d = np.diff(t)
        return (d@d)/h
    def dE(th):
        t = np.concatenate([[a], th, [b]]); d = np.diff(t)
        return 2*(d[:-1]-d[1:])/h
    cons = [
        {'type': 'eq', 'fun': lambda th: np.array([p0[0]+h*np.cos(th).sum()-pe[0], p0[1]+h*np.sin(th).sum()-pe[1]]),
         'jac': lambda th: np.vstack([-h*np.sin(th), h*np.cos(th)])},
    ]
    if walls:
        T = np.tril(np.ones((N, N)))  # nodo k+1 depende de th[0..k]
        def g(th):
            x, y = geom(th, h, p0)
            return np.concatenate([y[1:], x[1:], W - x[1:]])
        def dg(th):
            return np.vstack([T*(h*np.cos(th)), T*(-h*np.sin(th)), T*(h*np.sin(th))])
        cons.append({'type': 'ineq', 'fun': g, 'jac': dg})
    r = minimize(E, th0, jac=dE, constraints=cons, method='SLSQP', options={'maxiter': 800, 'ftol': 1e-10})
    return r.x, r

def analyze(th, Lf, X):
    h = Lf/N
    t = np.concatenate([[0], th, [np.pi/2]])
    k = np.abs(np.diff(t))/h
    x, y = geom(th, h, (S0, 0))
    xs = np.concatenate([[0], x, [X]]); ys = np.concatenate([[0], y, [H]])
    return dict(Rmin=1/k.max(), ymax=ys.max(), ymin=ys.min(), xmin=xs.min(), xmax=xs.max(), x=xs, y=ys, k=k)

def sweep(W, L, steps=49, init=None):
    """Recorre de retraido (X=W-12) a nominal (X=W). Devuelve lista de estados."""
    Lf = L - S0 - S1
    s = np.linspace(0, 1, N)
    if init is None:
        # guess: bucle hacia arriba (omega) en posicion retraida
        Xr = W - TRAVEL
        th0 = np.pi/2 + 1.2*np.pi*np.sin(np.pi*s)*0.9 - np.pi/2*(1-s)
        th0 = np.pi/2*s + 2.2*np.sin(np.pi*s)
    else:
        th0 = init
    out = []
    Xs = np.linspace(W - TRAVEL, W, steps)
    th = th0
    for X in Xs:
        th, r = solve(th, Lf, X, W)
        a = analyze(th, Lf, X); a['X'] = X; a['ok'] = r.success; a['th'] = th.copy()
        out.append(a)
    return out

if __name__ == '__main__':
    import sys
    W, L = float(sys.argv[1]), float(sys.argv[2])
    for a in sweep(W, L)[::4]:
        print(f"X={a['X']:6.2f} Rmin={a['Rmin']:5.2f} ymax={a['ymax']:5.2f} x=[{a['xmin']:.2f},{a['xmax']:.2f}] ok={a['ok']}")
