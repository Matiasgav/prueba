"""Elastica del flex, geometria v2 (mm).

- Flex de espesor TF=0.2. Se modela su linea media; radio interior = R_linea_media - TF/2.
- Mainboard a la izquierda de x=0; el flex sale por su cara inferior: cara inferior del flex en y=0.
  Primer tramo recto de S0=1 mm.
- Placa del conector vertical, alto 9.5 - R (R=3 -> de y=4 a y=10.5). El flex va por su cara derecha
  y sale por el borde inferior (y=YB=1+R) hacia abajo; ultimo tramo recto S1=1 mm por debajo de la placa.
- X = cara derecha del flex en la placa. Nominal X=W, retraido X=W-12.
- Obstaculos: piso y>=0, pared x>=0 (mainboard), y en cualquier estado la zona x >= X-TF-TB, y >= YB
  (placa + conector) esta prohibida. Nominal: nada por encima de 10.5.
"""
import numpy as np
from scipy.optimize import minimize

H, TRAVEL, RIN, S0, S1, TF, TB = 10.5, 12.0, 3.0, 1.0, 1.0, 0.2, 1.0
YB = 1 + RIN
N = 60
BETA = 12.0

def geom(th, h, p0):
    x = p0[0] + np.concatenate([[0], np.cumsum(h*np.cos(th))])
    y = p0[1] + np.concatenate([[0], np.cumsum(h*np.sin(th))])
    return x, y

def solve(th0, Lf, X, W):
    h = Lf/N; c = TF/2
    p0 = np.array([S0, c]); pe = np.array([X - c, YB - S1])
    xl = X - TF - TB - c  # borde izquierdo de la zona prohibida (linea media)
    a, b = 0.0, np.pi/2
    T = np.tril(np.ones((N, N)))
    def E(th):
        t = np.concatenate([[a], th, [b]]); d = np.diff(t); return (d@d)/h
    def dE(th):
        t = np.concatenate([[a], th, [b]]); d = np.diff(t); return 2*(d[:-1]-d[1:])/h
    def g(th):
        x, y = geom(th, h, p0); x, y = x[1:], y[1:]
        u, v = BETA*(xl - x), BETA*((YB - c) - y)
        m = np.maximum(u, v)
        obs = (m + np.log(np.exp(u-m)+np.exp(v-m)))/BETA - np.log(2)/BETA
        return np.concatenate([y - c, x - c, (W - c) - x, obs])
    def dg(th):
        x, y = geom(th, h, p0); x, y = x[1:], y[1:]
        u, v = BETA*(xl - x), BETA*((YB - c) - y)
        m = np.maximum(u, v); eu, ev = np.exp(u-m), np.exp(v-m); wu, wv = eu/(eu+ev), ev/(eu+ev)
        dx = T*(-h*np.sin(th)); dy = T*(h*np.cos(th))
        return np.vstack([dy, dx, -dx, -wu[:, None]*dx - wv[:, None]*dy])
    cons = [{'type': 'eq', 'fun': lambda th: np.array([p0[0]+h*np.cos(th).sum()-pe[0], p0[1]+h*np.sin(th).sum()-pe[1]]),
             'jac': lambda th: np.vstack([-h*np.sin(th), h*np.cos(th)])},
            {'type': 'ineq', 'fun': g, 'jac': dg}]
    r = minimize(E, th0, jac=dE, constraints=cons, method='SLSQP', options={'maxiter': 1000, 'ftol': 1e-10})
    return r.x, r

def analyze(th, Lf, X):
    h = Lf/N; c = TF/2
    t = np.concatenate([[0], th, [np.pi/2]])
    k = np.abs(np.diff(t))/h
    x, y = geom(th, h, (S0, c))
    xs = np.concatenate([[0], x, [X - c]]); ys = np.concatenate([[c], y, [YB]])
    return dict(Rin=1/k.max() - c, ytop=ys.max() + c, x=xs, y=ys, k=k)

def guess(Lf, X):
    s = np.linspace(0, 1, N)
    return np.pi/2*s + 2.2*np.sin(np.pi*s)

def sweep(W, L, steps=25):
    """Arranca en nominal (joroba suave), va a retraido (vuelta) y regresa (ida)."""
    Lf = L - S0 - S1
    s = np.linspace(0, 1, N)
    th = np.pi/2*s**3 + 1.4*np.sin(2*np.pi*s)*(1 - s)
    for A in (1.4, 1.0, 1.8, 0.6):
        th0 = np.pi/2*s**3 + A*np.sin(2*np.pi*s)*(1 - s)
        th, r = solve(th0, Lf, W, W)
        if r.success: break
    bw = []
    for X in np.linspace(W, W - TRAVEL, steps):
        th, r = solve(th, Lf, X, W); a = analyze(th, Lf, X); a.update(X=X, ok=r.success, th=th.copy()); bw.append(a)
    fw = []
    for X in np.linspace(W - TRAVEL, W, steps):
        th, r = solve(th, Lf, X, W); a = analyze(th, Lf, X); a.update(X=X, ok=r.success, th=th.copy()); fw.append(a)
    return fw, bw

def selfcross(a):
    """True si la linea media se cruza consigo misma (solucion no fisica)."""
    P = np.stack([a['x'], a['y']], 1); n = len(P) - 1
    for i in range(n):
        p, r = P[i], P[i+1] - P[i]
        for j in range(i + 2, n):
            q, t = P[j], P[j+1] - P[j]
            den = r[0]*t[1] - r[1]*t[0]
            if abs(den) < 1e-12: continue
            u = ((q - p)[0]*t[1] - (q - p)[1]*t[0]) / den; v = ((q - p)[0]*r[1] - (q - p)[1]*r[0]) / den
            if 0 < u < 1 and 0 < v < 1: return True
    return False

def evaluate(args):
    global YB
    W, L, Rb = args
    YB = 1 + Rb
    try: fw, bw = sweep(W, L)
    except Exception as e: return dict(W=W, L=L, err=str(e))
    return dict(W=W, L=L, Rb=Rb, Rin=min(a['Rin'] for a in fw+bw), Rfw=min(a['Rin'] for a in fw), Rbw=min(a['Rin'] for a in bw),
                ytop_nom=max(fw[-1]['ytop'], bw[0]['ytop']), selfx=any(selfcross(a) for a in fw+bw), ytop_ret=max(a['ytop'] for a in fw+bw), ok=all(a['ok'] for a in fw+bw))

if __name__ == '__main__':
    import sys, json
    from multiprocessing import Pool
    Ws = np.arange(float(sys.argv[1]), float(sys.argv[2]) + 1e-9, float(sys.argv[3]))
    Rbs = [float(v) for v in sys.argv[5].split(',')]
    jobs = [(W, L, Rb) for Rb in Rbs for W in Ws for L in np.arange(W + 9, W + 17.01, 0.5)]
    with Pool(4) as p: res = p.map(evaluate, jobs)
    json.dump(res, open(sys.argv[4], 'w'))
    for r in res:
        if 'err' in r: print('ERR', r); continue
        flag = '  <== OK' if r['Rin'] >= 3 and r['ytop_nom'] <= 10.5 + 1e-3 and r['ok'] and not r['selfx'] else ''
        print(f"Rb={r['Rb']} W={r['W']:.1f} L={r['L']:.1f} Rin={r['Rin']:.2f} (fw {r['Rfw']:.2f} bw {r['Rbw']:.2f}) ytop_nom={r['ytop_nom']:.2f} ytop_ret={r['ytop_ret']:.1f} ok={r['ok']}{flag}")
