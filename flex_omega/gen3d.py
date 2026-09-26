"""Genera la geometria 3D animada de las opciones (mm). Ejes: x = carrera (hacia el panel), y = altura, z = lateral.
Cada frame: cintas (linea media, vector de ancho, ancho, radio interior por punto) y cajas (placas, conector)."""
import json, numpy as np
import s_lateral

c = 0.1; STEPS = 41

def box(x0, x1, y0, y1, z0, z1, kind):
    return dict(min=[x0, y0, z0], max=[x1, y1, z1], kind=kind)

def radius(P):
    """Radio interior por punto a partir de la curvatura discreta de la poligonal."""
    P = np.asarray(P, float); R = np.full(len(P), 99.0)
    for i in range(1, len(P) - 1):
        a, b, d = P[i-1], P[i], P[i+1]
        u, v = b - a, d - b
        ang = np.arccos(np.clip(u @ v / (np.linalg.norm(u)*np.linalg.norm(v) + 1e-12), -1, 1))
        ds = 0.5*(np.linalg.norm(u) + np.linalg.norm(v))
        if ang > 1e-6: R[i] = ds/ang - c
    R[0], R[-1] = R[1], R[-2]
    return np.minimum(R, 99)

def ribbon(P, b, w):
    P = np.asarray(P, float)
    keep = np.r_[True, np.linalg.norm(np.diff(P, axis=0), axis=1) > 1e-6]; P = P[keep]
    return dict(p=np.round(P, 3).tolist(), b=list(b), w=w, R=np.round(radius(P), 2).tolist())

def arc(cx, cy, r, a0, a1, n=16):
    t = np.linspace(a0, a1, n); return np.stack([cx + r*np.cos(t), cy + r*np.sin(t)], 1)

# ---------- Opcion 1: placa del conector en el piso (elastica 2D extruida) ----------
def opcion_piso():
    d = [x for x in json.load(open('planos/planos.json')) if x['id'] == 'A_piso'][0]
    W = d['W']; frames = []
    seq = d['fw']  # retraido -> nominal
    idx = np.linspace(0, len(seq) - 1, STEPS).round().astype(int)
    for i in idx:
        f = seq[i]; X = f['X']
        P = np.stack([f['x'], f['y'], np.zeros(len(f['x']))], 1)
        P = np.vstack([P, [[X - c, 0.3, 0]]])  # tramo pegado a la cara de la placa
        frames.append(dict(ret=round(W - X, 3), ribbons=[ribbon(P, (0, 0, 1), 10)], boxes=[
            box(-10, 0, 0.2, 1.2, -14, 14, 'mainboard'),
            box(X - 1.2, X - 0.2, 0, 5, -8, 8, 'placa'),
            box(X, X + 5, 0.6, 4.4, -6, 6, 'conector')]))
    return dict(id='piso', nombre='Placa en el piso', W=W, Rmin=d['Rmin_recorrido'], frames=frames)

# ---------- Opcion 2: S lateral con el flex de canto ----------
def opcion_s(W=13.0, Z=14.0, L=15.7):
    xs = W - 0.5 - 6  # x de la linea media en la pestaña (el extremo movil queda a +-6)
    z0 = 4.0          # canto de la pestaña por donde sale la tira
    # flex plano desde la mainboard hasta la pestaña: recta, curva R3,1 hacia arriba, vertical hasta y=4,3
    a = arc(xs - 3.1, 3.2, 3.1, -np.pi/2, 0)
    flat = np.vstack([[0, c], [xs - 3.1, c], a[1:], [xs, 4.3]])
    frames = []; s = np.linspace(0, 1, s_lateral.N); th = 0.3*np.sin(2*np.pi*s)
    for ret in np.linspace(12, 0, STEPS):
        X = W - ret; dlat = (X - 0.5) - xs
        th, R, _, _ = s_lateral.solve(th, L, Z, dlat)
        h = L/s_lateral.N
        zz = np.concatenate([[0], np.cumsum(h*np.cos(th))]); xx = np.concatenate([[0], np.cumsum(h*np.sin(th))])
        S = np.stack([xs + xx, np.full(len(xx), 5.3), z0 + zz], 1)
        inc = np.stack([flat[:, 0], flat[:, 1], np.full(len(flat), -5.0)], 1)
        frames.append(dict(ret=round(ret, 3), ribbons=[ribbon(inc, (0, 0, 1), 10), ribbon(S, (0, 1, 0), 10)], boxes=[
            box(-10, 0, 0.2, 1.2, -14, 8, 'mainboard'),
            box(xs - 0.5, xs + 0.5, 4.3, 10.4, -10, z0, 'pestana'),
            box(xs - 0.5, xs + 0.5, 0.3, 10.4, 0.2, z0, 'pestana'),
            box(X - 1.0, X, 0.3, 10.4, z0 + Z, z0 + Z + 18, 'placa'),
            box(X, X + 5, 2.0, 8.5, z0 + Z + 3, z0 + Z + 15, 'conector')]))
    return dict(id='s', nombre='S lateral de canto', W=W, Rmin=3.73, frames=frames)

# ---------- Opcion 3: U rodante de canto (en canal) ----------
def opcion_u(W=13.0, G=7.6):
    Rc = (G - 2*c)/2 - 0.0  # radio de la linea media en la punta (aprox. circular para el dibujo)
    xf = W - 6.5            # pestaña fija
    frames = []
    a_in = arc(xf - 3.1, 3.2, 3.1, -np.pi/2, 0)
    for ret in np.linspace(12, 0, STEPS):
        X = W - ret; xm = X - 0.5
        xL = (W + 2.6) - ret/2    # la U avanza la mitad de la carrera
        zm = -3.1; zf = zm - 2*Rc
        pts = [[xm, 0.0]]
        pts += arc(xm + 3.1, 0.0, 3.1, np.pi, 1.5*np.pi)[1:].tolist()           # sale del canto -z de la placa y gira a +x
        pts += [[xL, zm]]
        pts += arc(xL, zm - Rc, Rc, np.pi/2, -np.pi/2)[1:].tolist()              # U
        pts += [[xf + 3.1, zf]]
        pts += arc(xf + 3.1, zf - 3.1, 3.1, np.pi/2, np.pi)[1:].tolist()         # gira hacia -z, entra a la pestaña
        pts += [[xf, zf - 3.1 - 1.0]]
        pts = [p for i, p in enumerate(pts) if i == 0 or np.hypot(p[0]-pts[i-1][0], p[1]-pts[i-1][1]) > 1e-6]
        P = np.array([[p[0], 5.3, p[1]] for p in pts])
        zt = zf - 4.1
        inc = np.stack([np.r_[0, xf - 3.1, a_in[1:, 0], xf], np.r_[c, c, a_in[1:, 1], 4.3], np.full(len(a_in) + 2, zt - 6)], 1)
        frames.append(dict(ret=round(ret, 3), ribbons=[ribbon(inc, (0, 0, 1), 10), ribbon(P, (0, 1, 0), 10)], boxes=[
            box(-10, 0, 0.2, 1.2, zt - 14, 8, 'mainboard'),
            box(xf - 0.5, xf + 0.5, 4.3, 10.4, zt - 11, zt - 1, 'pestana'),
            box(xf - 0.5, xf + 0.5, 0.3, 10.4, zt - 1, zt, 'pestana'),
            box(X - 1.0, X, 0.3, 10.4, 0, 18, 'placa'),
            box(X, X + 5, 2.0, 8.5, 3, 15, 'conector'),
            box(xf + 3.5, W + 12, 0.3, 10.4, zm + c + 0.0, zm + c + 0.3, 'guia'),
            box(xf + 3.5, W + 12, 0.3, 10.4, zf - c - 0.3, zf - c, 'guia')]))
    return dict(id='u', nombre='U rodante de canto', W=W, Rmin=3.0, frames=frames)

if __name__ == '__main__':
    out = [opcion_piso(), opcion_s(), opcion_u()]
    for o in out:
        print(o['id'], len(o['frames']), 'Rmin dibujo', min(min(r['R']) for f in o['frames'] for r in f['ribbons']))
    json.dump(out, open('opciones3d.json', 'w'), separators=(',', ':'))
