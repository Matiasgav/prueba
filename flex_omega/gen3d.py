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

def ribbon(P, b, w, rreq=3.0):
    P = np.asarray(P, float)
    keep = np.r_[True, np.linalg.norm(np.diff(P, axis=0), axis=1) > 1e-6]; P = P[keep]
    return dict(p=np.round(P, 3).tolist(), b=list(b), w=w, R=np.round(radius(P), 2).tolist(), rreq=rreq)

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


# ---------- Opcion 5: camara centrada (geometria real del STEP), S por detras, LED con guia de luz ----------
def opcion_camara_centrada(Xn=13.0, b=6.5, Z=17.0, L=22.0, H=11.9, cinta=0.25):
    y0 = cinta; xp = Xn + b; xcam = xp - 5.05          # modulo de 5,05 mm de profundidad (STEP)
    ylens = y0 + 4.25
    xs0 = xcam - 0.12 - 1.0                             # cara delantera de la interfaz: flex 0,12 + conector apareado ~1,0
    xi = xs0 - 0.5                                      # plano medio de la interfaz = extremo fijo de la S
    zc = 26.0 - 11.8                                    # centro del conector de la camara (11,8 mm de la lente)
    zs0 = 16.0; zs1 = zs0 + Z                           # S despues del conector de la camara
    wall_face = xs0                                     # la S no pasa de la cara delantera de la interfaz
    ys0, ys1 = y0 + 0.35, y0 + 0.35 + 11.0              # tira de la S de 11 mm (48 V en 1 oz + Gigabit)
    # flex de la mainboard: entra por la muesca inferior de la interfaz (z 0,5 a 11,9)
    ai = arc(xi - 3.1, y0 + 0.1 + 3.1, 3.1, -np.pi/2, 0)
    inc = np.stack([np.r_[0, xi - 3.1, ai[1:, 0], xi], np.r_[y0 + 0.1, y0 + 0.1, ai[1:, 1], y0 + 4.45], np.full(len(ai) + 2, 6.2)], 1)
    cam_fpc = np.array([[xcam - 0.06, ylens, 30.25], [xcam - 0.06, ylens, 11.25]])
    frames = []; s = np.linspace(0, 1, s_lateral.N); th = -0.3*np.sin(np.pi*s); Rall = []
    for ret in np.linspace(12, 0, STEPS):
        X = Xn - ret; dlat = (X - 0.5) - xi
        th, Rr, _, _ = s_lateral.solve(th, L, Z, dlat, wall=wall_face - xi); Rall.append(Rr)
        h = L/s_lateral.N
        zz = np.concatenate([[0], np.cumsum(h*np.cos(th))]); xx = np.concatenate([[0], np.cumsum(h*np.sin(th))])
        S = np.stack([xi + xx, np.full(len(xx), (ys0 + ys1)/2), zs0 + zz], 1)
        frames.append(dict(ret=round(ret, 3), ribbons=[
            ribbon(inc, (0, 0, 1), 11.4), ribbon(S, (0, 1, 0), 11.0),
            dict(p=cam_fpc.tolist(), b=[0, 1, 0], w=8.5, R=[99, 99], rreq=1.44)], boxes=[
            box(-10, 0, y0 + 0.2, y0 + 1.2, -2, 54, 'mainboard'),
            box(xi - 0.5, xi + 0.5, y0 + 4.45, H, 0, 12.4, 'placa'),               # interfaz: muesca para el flex de entrada
            box(xi - 0.5, xi + 0.5, y0, H, 12.4, zs0, 'placa'),                    # interfaz: zona completa (conector camara + salida S)
            box(xs0, xcam - 0.12, ylens + 0.55 - 3.0, ylens + 0.55 + 3.0, zc - 1.0, zc + 1.0, 'conector'),
            box(xcam, xcam + 0.35, y0, y0 + 9.6, 11.25, 17.25, 'rigidizador'),      # FR4 de la cola de la camara
            box(xcam, xp, y0, y0 + 8.5, 21.75, 30.25, 'camara'),
            dict(cyl=True, x0=xp - 0.6, len=0.6, y=ylens, z=26.0, r=2.2, kind='rosca'),
            box(wall_face + 0.05, wall_face + 0.55, y0, y0 + 11.4, zs0 + 0.5, zs1 - 0.5, 'guia'),
            box(xs0, xs0 + 3.0, y0 + 7.0, y0 + 10.0, 7.0, 10.0, 'led'),               # LED en la seccion de camara, antes de la cola
            box(xs0 + 3.0, xs0 + 4.9, y0 + 7.6, y0 + 9.4, 7.6, 9.4, 'guia_luz'),     # guia de luz: sale hacia adelante
            box(xs0 + 3.1, xs0 + 4.9, y0 + 7.6, y0 + 9.4, 9.4, 13.0, 'guia_luz'),    # corre en z por delante de la cola
            box(xs0 + 3.1, xs0 + 4.9, y0 + 3.4, y0 + 9.4, 13.0, 14.8, 'guia_luz'),   # baja a la altura de la lente
            box(xs0 + 3.1, xs0 + 4.9, y0 + 3.4, y0 + 5.2, 14.8, 20.0, 'guia_luz'),
            box(xs0 + 4.9, xp, y0 + 3.4, y0 + 5.2, 18.2, 20.0, 'guia_luz'),                # sale al panel a ~7 mm de la lente
            box(X - 1.0, X, y0, H, zs1, 52.0, 'placa'),
            box(X, X + b, y0, H, 38.0, 50.0, 'conector'),
            dict(cyl=True, x0=X + b, len=12, y=(y0 + H)/2, z=44.0, r=6, kind='rosca'),
            box(xp, xp + 1.5, -1, 13.5, -2, 54, 'panel')]))
    return dict(id='camc', nombre='Cámara centrada, S por detrás', W=Xn, Rmin=round(min(Rall), 2), env=[0, 52], H=H, frames=frames)

# ---------- Opcion 6: camara horizontal invertida + conector con M12 acodado en placa horizontal ----------
def opcion_horizontal(Xn=28.0, L=38.0, b=6.5, H=11.9, cinta=0.25):
    import fast3
    y0 = cinta; xp = Xn + b; xcam = xp - 5.05
    cfg = dict(mode='horizontal', H=H - cinta)
    fw, bw = fast3.sweep(cfg, Xn, L, steps=STEPS)
    # cola de la camara: sube 1,05 (zona con rigidizador SUS), curva R1,2 hacia atras, 1,47 recto y rigidizador de 6 mm
    Rt = 1.5 + 0.06; ytail = y0 + 8.5 + 1.05
    tail = [[xcam - 0.06, y0 + 8.5], [xcam - 0.06, ytail]]
    tail += (arc(xcam - 0.06 - Rt, ytail, Rt, 0, np.pi/2)[1:]).tolist()
    tail += [[xcam - 0.06 - Rt - 1.47 - 6.0, ytail + Rt]]
    tail3 = np.array([[p[0], p[1], 26.0] for p in tail])
    ycb1 = ytail + Rt - 0.06 - 1.0; ycb0 = ycb1 - 1.0       # placa de camara bajo el conector (1 mm apareado)
    xcb0, xcb1 = xcam - 10.0, xcam - 2.5
    # flex de la mainboard a la placa de camara: sube con dos curvas R3,1
    ym = (ycb0 + ycb1)/2; xa = xcb0 - 7.2
    riser = [[0, y0 + 0.1], [xa, y0 + 0.1]]
    riser += arc(xa, y0 + 0.1 + 3.1, 3.1, -np.pi/2, 0)[1:].tolist()
    riser += [[xa + 3.1, ym - 3.1]]
    riser += arc(xa + 6.2, ym - 3.1, 3.1, np.pi, np.pi/2)[1:].tolist()
    riser += [[xcb0, ym]]
    riser3 = np.array([[p[0], p[1], 26.5] for p in riser])
    # isla del LED: lengueta de la placa de camara + bisagra flex que baja 90 grados
    xt = xp - 8.5
    hinge = [[xt, ym]] + arc(xt, ym - 2.6, 2.6, np.pi/2, 0)[1:].tolist() + [[xt + 2.6, ym - 3.2]]
    hinge3 = np.array([[p[0], p[1], 17.5] for p in hinge]); xi = xt + 2.6
    frames = []
    for f in fw:
        X = f['X']
        arcP = np.stack([f['x'], np.array(f['y']) + y0, np.full(len(f['x']), 44.0)], 1)
        frames.append(dict(ret=round(Xn - X, 3), ribbons=[ribbon(arcP, (0, 0, 1), 11), ribbon(tail3, (0, 0, 1), 8.5, rreq=1.44),
                                                          ribbon(riser3, (0, 0, 1), 9), ribbon(hinge3, (0, 0, 1), 4, rreq=2.4)], boxes=[
            box(-10, 0, y0 + 0.2, y0 + 1.2, -2, 54, 'mainboard'),
            box(X, X + 6.0, y0 + 0.2, y0 + 1.2, 36.0, 52.0, 'placa'),
            box(X + 0.5, X + b, y0 + 1.2, H, 38.0, 50.0, 'conector'),
            dict(cyl=True, x0=X + b, len=12, y=(y0 + H)/2, z=44.0, r=6, kind='rosca'),
            box(xcam, xp, y0, y0 + 8.5, 21.75, 30.25, 'camara'),
            dict(cyl=True, x0=xp - 0.6, len=0.6, y=y0 + 4.25, z=26.0, r=2.2, kind='rosca'),
            box(xcam - 0.06 - Rt - 1.47 - 6.0, xcam - 0.06 - Rt - 1.47, ytail + Rt + 0.06, ytail + Rt + 0.41, 21.2, 30.8, 'rigidizador'),
            box(xcam - Rt - 1.47 - 4.3, xcam - Rt - 1.47 - 2.3, ycb1, ycb1 + 1.0, 23.0, 29.0, 'conector'),
            box(xcb0, xcb1, ycb0, ycb1, 21.0, 32.0, 'placa'),
            box(xcam - 6.0, xt, ycb0, ycb1, 14.0, 21.0, 'placa'),
            box(xi - 0.5, xi + 0.5, y0 + 2.0, ym - 3.2, 15.0, 20.0, 'placa'),
            box(xi + 0.5, xi + 3.5, y0 + 2.5, y0 + 5.5, 16.0, 19.0, 'led'),
            box(xp, xp + 1.5, -1, 13.5, -2, 54, 'panel')]))
    return dict(id='horiz', nombre='Cámara horizontal + M12 acodado', W=Xn, Rmin=round(min(a['Rin'] for a in fw + bw), 2),
                env=[0, 52], H=H, frames=frames)

# ---------- Opcion 7: pared de flex desde el canto lateral de la mainboard (propuesta del usuario) ----------
def opcion_pared(Xn=13.0, b=6.5, Z=17.0, L=22.0, H=11.9, cinta=0.25):
    """Igual que la 5 en la zona de camara, S y conector, pero la alimentacion llega por una pared:
    el flex sale del canto izquierdo de la mainboard, sube 90 grados (R 3,1), gira 90 grados en la esquina
    (eje vertical, R 3,1) y sigue como pared paralela al panel hasta la seccion rigida de la camara.
    Por la esquina solo entran ~7 mm de alto: MIPI, LED y alimentacion de la camara. 48 V y Gigabit suben
    por un segundo tramo desde el canto delantero de la mainboard hasta la base de la seccion de camara."""
    y0 = cinta; xp = Xn + b; xcam = xp - 5.05; ylens = y0 + 4.25
    xs0 = xcam - 0.12 - 1.0; xw = xs0 - 0.5          # plano medio de la pared / seccion de camara
    zc = 26.0 - 11.8; zs0 = 16.0; zs1 = zs0 + Z
    zml = 3.6                                         # canto izquierdo de la mainboard
    zcs0 = zml                                        # la seccion de camara empieza donde termina la esquina
    xmf = xw - 3.1 - 1.3                              # canto delantero de la mainboard frente a la seccion de camara
    yw0, yw1 = y0 + 4.35, y0 + 11.35                  # pared por la esquina: 7 mm de alto
    # tramo 1: dobla hacia arriba en el canto izquierdo (perfil en z-y, ancho en x)
    a1 = arc(zml, y0 + 0.1 + 3.1, 3.1, -np.pi/2, -np.pi)[1:]
    p1 = np.vstack([[[zml, y0 + 0.1]], a1, [[zml - 3.1, yw0]]])
    xa, xb = 0.5, xw - 3.1
    wall1 = np.stack([np.full(len(p1), (xa + xb)/2), p1[:, 1], p1[:, 0]], 1)
    # tramo 2: pared de canto, recta en x, esquina R 3,1 y recta en z hasta la seccion de camara
    zw = zml - 3.1
    cor = arc(xb, zw + 3.1, 3.1, -np.pi/2, 0)
    p2 = np.vstack([[[xa, zw]], cor, [[xw, zcs0]]])
    wall2 = np.stack([p2[:, 0], np.full(len(p2), (yw0 + yw1)/2), p2[:, 1]], 1)
    # tramo 3: 48 V + Gigabit desde el canto delantero de la mainboard a la base de la seccion de camara
    a3 = arc(xw - 3.1, y0 + 0.1 + 3.1, 3.1, -np.pi/2, 0)
    p3 = np.vstack([[[xmf, y0 + 0.1]], a3, [[xw, y0 + 4.45]]])
    up = np.stack([p3[:, 0], p3[:, 1], np.full(len(p3), (zcs0 + 0.2 + 12.2)/2)], 1)
    cam_fpc = np.array([[xcam - 0.06, ylens, 30.25], [xcam - 0.06, ylens, 11.25]])
    frames = []; s = np.linspace(0, 1, s_lateral.N); th = -0.3*np.sin(np.pi*s); Rall = []
    for ret in np.linspace(12, 0, STEPS):
        X = Xn - ret; dlat = (X - 0.5) - xw
        th, Rr, _, _ = s_lateral.solve(th, L, Z, dlat, wall=xs0 - xw); Rall.append(Rr)
        h = L/s_lateral.N
        zz = np.concatenate([[0], np.cumsum(h*np.cos(th))]); xx = np.concatenate([[0], np.cumsum(h*np.sin(th))])
        S = np.stack([xw + xx, np.full(len(xx), y0 + 0.35 + 5.5), zs0 + zz], 1)
        frames.append(dict(ret=round(ret, 3), ribbons=[
            ribbon(wall1, (1, 0, 0), xb - xa), ribbon(wall2, (0, 1, 0), yw1 - yw0), ribbon(up, (0, 0, 1), 12.0 - zcs0),
            ribbon(S, (0, 1, 0), 11.0),
            dict(p=cam_fpc.tolist(), b=[0, 1, 0], w=8.5, R=[99, 99], rreq=1.44)], boxes=[
            box(-10, xmf, y0 + 0.2, y0 + 1.2, zml, zs0, 'mainboard'),              # mainboard hasta cerca de la pared
            box(-10, -0.5, y0 + 0.2, y0 + 1.2, zs0, 54, 'mainboard'),              # recortada donde barre la S y el conector
            box(xw - 0.5, xw + 0.5, y0 + 4.45, H, zcs0, 12.4, 'placa'),            # seccion rigida de camara (muesca abajo)
            box(xw - 0.5, xw + 0.5, y0, H, 12.4, zs0, 'placa'),
            box(xs0, xcam - 0.12, ylens + 0.55 - 3.0, ylens + 0.55 + 3.0, zc - 1.0, zc + 1.0, 'conector'),
            box(xcam, xcam + 0.35, y0, y0 + 9.6, 11.25, 17.25, 'rigidizador'),
            box(xcam, xp, y0, y0 + 8.5, 21.75, 30.25, 'camara'),
            dict(cyl=True, x0=xp - 0.6, len=0.6, y=ylens, z=26.0, r=2.2, kind='rosca'),
            box(xs0 + 0.05, xs0 + 0.55, y0, y0 + 11.4, zs0 + 0.5, zs1 - 0.5, 'guia'),
            box(xs0, xs0 + 3.0, y0 + 7.0, y0 + 10.0, 7.0, 10.0, 'led'),               # LED en la seccion de camara, antes de la cola
            box(xs0 + 3.0, xs0 + 4.9, y0 + 7.6, y0 + 9.4, 7.6, 9.4, 'guia_luz'),     # guia de luz: sale hacia adelante
            box(xs0 + 3.1, xs0 + 4.9, y0 + 7.6, y0 + 9.4, 9.4, 13.0, 'guia_luz'),    # corre en z por delante de la cola
            box(xs0 + 3.1, xs0 + 4.9, y0 + 3.4, y0 + 9.4, 13.0, 14.8, 'guia_luz'),   # baja a la altura de la lente
            box(xs0 + 3.1, xs0 + 4.9, y0 + 3.4, y0 + 5.2, 14.8, 20.0, 'guia_luz'),
            box(xs0 + 4.9, xp, y0 + 3.4, y0 + 5.2, 18.2, 20.0, 'guia_luz'),                # sale al panel a ~7 mm de la lente
            box(X - 1.0, X, y0, H, zs1, 52.0, 'placa'),
            box(X, X + b, y0, H, 38.0, 50.0, 'conector'),
            dict(cyl=True, x0=X + b, len=12, y=(y0 + H)/2, z=44.0, r=6, kind='rosca'),
            box(xp, xp + 1.5, -1, 13.5, -2, 54, 'panel')]))
    return dict(id='pared', nombre='Pared de flex desde el canto lateral', W=Xn, Rmin=round(min(Rall), 2), env=[0, 52], H=H, frames=frames)

# ---------- Opciones LED A/B/C sobre el diseño final (S centrada Z 14 + pared lateral para la camara) ----------
def opcion_led(var):
    """var: 'A' placa del LED con conector board-to-board, 'B' isla del mismo rigid-flex, 'C' placa en el panel + FFC.
    Coordenadas: x = XP + x_rel (x_rel desde la cara interior del panel), y sobre la cinta de 0,25, z en los 52 mm."""
    d2 = json.load(open('s2d.json'))
    y0, H = 0.25, 11.9; XP = 13.0 + 6.65
    X = lambda xr: XP + xr
    frames = []
    # camara (STEP): modulo, lente, cola, rigidizador FR4 y conector AXT
    cam = [box(X(-5.05), X(0), y0, y0 + 8.5, 21.75, 30.25, 'camara'),
           dict(cyl=True, x0=X(-0.6), len=0.6, y=y0 + 4.25, z=26.0, r=2.2, kind='rosca'),
           box(X(-5.05), X(-4.7), y0, y0 + 9.6, 11.25, 17.25, 'rigidizador'),
           box(X(-6.17), X(-5.17), y0 + 1.8, y0 + 7.8, 13.2, 15.2, 'conector')]
    cam_fpc = dict(p=[[X(-5.11), y0 + 4.25, 30.25], [X(-5.11), y0 + 4.25, 11.25]], b=[0, 1, 0], w=8.5, R=[99, 99], rreq=1.44)
    # seccion de camara alimentada por la pared lateral (esquina)
    xwf = X(-6.27); zml = 3.6; zw = zml - 3.1; xa = X(-24.0); xb = xwf - 3.1
    a1 = arc(zml, y0 + 0.1 + 3.1, 3.1, -np.pi/2, -np.pi)[1:]
    p1 = np.vstack([[[zml, y0 + 0.1]], a1, [[zw, y0 + 4.35]]])
    wall1 = np.stack([np.full(len(p1), xa + 3.0), p1[:, 1], p1[:, 0]], 1)
    cor = arc(xb, zw + 3.1, 3.1, -np.pi/2, 0)
    p2 = np.vstack([[[xa, zw]], cor, [[xwf, zml]]])
    wall2 = np.stack([p2[:, 0], np.full(len(p2), y0 + 7.85), p2[:, 1]], 1)
    # pestaña fija de la S y su alimentacion desde la mainboard (48 V + Gigabit)
    xtf = X(-12.75)
    at = arc(xtf - 3.1, y0 + 0.1 + 3.1, 3.1, -np.pi/2, 0)
    pt = np.vstack([[[X(-17.5), y0 + 0.1]], at, [[xtf, y0 + 4.45]]])
    feed = np.stack([pt[:, 0], pt[:, 1], np.full(len(pt), 9.5)], 1)
    fixed = [box(-10, X(-17.5), y0 + 0.2, y0 + 1.2, zml, 16.0, 'mainboard'),
             box(-10, X(-20.5), y0 + 0.2, y0 + 1.2, 16.0, 54.0, 'mainboard'),
             box(X(-7.17), X(-6.17), y0, H, zml, 16.0, 'placa'),                          # seccion de camara
             box(X(-13.65), X(-12.65), y0 + 4.45, H, 4.0, 15.0, 'placa'),                # pestaña fija
             box(X(-13.65), X(-12.65), y0, H, 15.0, 16.0, 'placa'),
             box(XP, XP + 1.5, -1, 13.5, -2, 54, 'panel')]
    led = []; extra_rib = []
    if var == 'A':
        led = [box(X(-4.17), X(-3.57), y0 + 0.6, y0 + 8.0, 6.0, 21.5, 'placa'),          # placa del LED 0,6 mm
               box(X(-6.17), X(-4.17), y0 + 2.0, y0 + 6.5, 6.5, 9.5, 'conector'),        # B2B apareado 2,0 mm
               box(X(-3.57), X(-1.07), y0 + 3.0, y0 + 6.0, 17.8, 20.8, 'led')]
    elif var == 'B':
        xi = X(-4.2); R = 2.6; jog = xi - xwf; ph = np.arccos(1 - jog/(2*R))
        t1 = np.linspace(np.pi, np.pi - ph, 12); q1 = np.stack([xwf + R + R*np.cos(t1), 16.0 + R*np.sin(t1)], 1)
        c2 = q1[-1] + R*np.array([-np.cos(ph), np.sin(ph)])
        t2 = np.linspace(-ph, 0, 12); q2 = np.stack([c2[0] + R*np.cos(t2), c2[1] + R*np.sin(t2)], 1)
        arm = np.vstack([q1, q2[1:], [[xi, 21.6]]])
        extra_rib = [ribbon(np.stack([arm[:, 0], np.full(len(arm), y0 + 10.8), arm[:, 1]], 1), (0, 1, 0), 1.7, rreq=2.5)]
        led = [box(xi - 0.4, xi + 0.4, y0 + 2.4, y0 + 9.7, 17.4, 21.6, 'placa'),          # isla rigida
               box(xi - 0.4, xi + 0.4, y0 + 9.7, y0 + 11.6, 20.2, 21.6, 'placa'),
               box(xi + 0.4, xi + 2.9, y0 + 3.0, y0 + 6.0, 17.9, 20.9, 'led')]
    else:
        xf = X(-4.35)
        ffc = [[X(-5.17), 8.0], [xf - 0.6, 8.0]] + arc(xf - 0.6, 8.6, 0.6, -np.pi/2, 0)[1:].tolist() + \
              [[xf, 17.2]] + arc(xf + 0.6, 17.2, 0.6, np.pi, np.pi/2)[1:].tolist()
        ffc3 = np.array([[p[0], y0 + 10.75, p[1]] for p in ffc])
        extra_rib = [dict(ribbon(ffc3, (0, 1, 0), 1.7, rreq=0.5), col='#d9d4c7')]
        led = [box(X(-6.17), X(-5.17), y0 + 9.6, y0 + 11.6, 6.5, 9.5, 'conector'),       # ZIF en la seccion de camara
               box(X(-3.4), X(-2.6), y0 + 1.0, y0 + 11.6, 16.5, 21.5, 'placa'),          # placa del LED pegada al panel
               box(X(-4.1), X(-3.4), y0 + 9.9, y0 + 11.6, 17.3, 20.5, 'conector'),       # ZIF en la placa del LED
               box(X(-2.6), X(-0.1), y0 + 3.0, y0 + 6.0, 17.8, 20.8, 'led')]
    for f in d2['seq']['ret_a_nom'][::2] + [d2['seq']['ret_a_nom'][-1]]:
        ret = f['ret']; Xf = X(-6.65) - ret
        Sp = np.stack([np.array(f['x']) + XP, np.full(len(f['x']), y0 + 0.35 + 5.5), np.array(f['z'])], 1)
        frames.append(dict(ret=round(ret, 3), ribbons=[ribbon(wall1, (1, 0, 0), 6.0), ribbon(wall2, (0, 1, 0), 7.0),
                                                        ribbon(feed, (0, 0, 1), 10.0), ribbon(Sp, (0, 1, 0), 11.0, rreq=2.5),
                                                        cam_fpc] + extra_rib,
                           boxes=fixed + cam + led + [box(Xf - 1.0, Xf, y0, H, 30.0, 52.0, 'placa'),
                                                      box(Xf, Xf + 6.65, y0, H, 38.0, 50.0, 'conector'),
                                                      dict(cyl=True, x0=Xf + 6.65, len=12, y=(y0 + H)/2, z=44.0, r=6, kind='rosca')]))
    frames = frames[::-1]   # de retraido a nominal
    frames = sorted(frames, key=lambda f: -f['ret'])
    names = {'A': 'LED A · placa + B2B', 'B': 'LED B · isla rigid-flex', 'C': 'LED C · placa en panel + FFC'}
    return dict(id='led' + var, nombre=names[var], W=X(-6.65), Rmin=round(d2['Rmin'], 2), env=[0, 52], H=H, frames=frames,
                focus=dict(target=[X(-4.5), 5.5, 16.5], pos=[X(-4.5) + 16, 22, 16.5 - 20]))

# ---------- Sujecion del conjunto (sobre LED A) ----------
def opcion_sujecion():
    o = opcion_led('A'); XP = 13.0 + 6.65; X = lambda xr: XP + xr; y0 = 0.25
    extra = [
        # tornillo del apilado: atraviesa la seccion de camara, el separador de 2,0 y la placa del LED y rosca en un buje del panel
        dict(cyl=True, x0=X(-7.97), len=0.8, y=y0 + 7.6, z=10.3, r=1.5, kind='tornillo'),          # cabeza M1.6
        dict(cyl=True, x0=X(-7.17), len=5.7, y=y0 + 7.6, z=10.3, r=0.8, kind='tornillo'),          # cuerpo M1.6 x 6
        dict(cyl=True, x0=X(-6.17), len=2.0, y=y0 + 7.6, z=10.3, r=1.3, kind='separador'),         # separador 2,0 = altura del B2B
        dict(cyl=True, x0=X(-3.57), len=3.57, y=y0 + 7.6, z=10.3, r=1.7, kind='chasis'),           # buje del panel
        # espuma que aprieta la cola de la camara contra su conector y apoya la placa del LED
        box(X(-4.7), X(-4.17), y0 + 1.5, y0 + 8.5, 11.5, 17.0, 'espuma'),
        # nervio del panel: apoya la punta de la placa del LED y separa la luz del LED de la camara
        box(X(-3.57), X(0), y0 + 0.6, y0 + 8.0, 20.9, 21.5, 'chasis'),
        # guias de la pestaña fija (ranura vertical en dos postes del chasis)
        box(X(-16.0), X(-13.7), 0, 11.9, 14.6, 16.0, 'chasis'),
        box(X(-16.0), X(-13.7), 0, 11.9, 2.9, 4.3, 'chasis'),
        # tuerca del M12 del lado de afuera del panel
        dict(cyl=True, x0=XP + 1.5, len=2.0, y=(y0 + 11.9)/2, z=44.0, r=8.0, kind='tuerca'),
    ]
    for f in o['frames']:
        f['boxes'] = f['boxes'] + extra
    o.update(id='sujecion', nombre='Sujeción del conjunto',
             focus=dict(target=[X(-6.0), 5.5, 12.0], pos=[X(-6.0) - 14, 24, 12.0 - 22]))
    return o

def _main():
    out = [opcion_piso(), opcion_s(), opcion_u(), opcion_camara(), opcion_camara_centrada(), opcion_horizontal(), opcion_pared(), opcion_led('A'), opcion_led('B'), opcion_led('C'), opcion_sujecion()]
    for o in out:
        print(o['id'], len(o['frames']), 'R/Rreq min', round(min(min(r['R'])/r.get('rreq', 3.0) for f in o['frames'] for r in f['ribbons']), 3))
    json.dump(out, open('opciones3d.json', 'w'), separators=(',', ':'))

# ---------- Opcion 4: placa de interfaz fija + camara MIPI + S doble de canto ----------
def opcion_camara(Xn=13.0, b=4.0, Z=16.0, L=19.2, gap=1.0):
    """Xn: cara de la placa del conector en nominal. b: cuerpo del conector detras del panel.
    La camara (8,5 x 8,5 x 5,5) queda fija contra el panel y su flex se enchufa en la placa de interfaz,
    que es la pestaña fija ampliada. Dos tiras en S (flex de dos capas independientes) llevan 48 V y Gigabit."""
    xp = Xn + b                     # cara interior del panel
    xi1 = xp - 5.5 - 0.2 - 1.5      # cara delantera de la placa de interfaz (modulo + flex camara + conector)
    xi = xi1 - 0.5                  # plano medio de la placa de interfaz
    zi0, zi1 = 0.0, 21.0            # placa de interfaz en z
    z0 = zi1; zc0 = z0 + Z          # S y placa del conector
    a = (Xn - 0.5) - xi             # desplazamiento de la S en nominal
    ai = arc(xi - 3.1, 3.2, 3.1, -np.pi/2, 0)
    inc = np.stack([np.r_[0, xi - 3.1, ai[1:, 0], xi], np.r_[c, c, ai[1:, 1], 4.3], np.full(len(ai) + 2, 8.5)], 1)
    frames = []; s = np.linspace(0, 1, s_lateral.N); th = 0.3*np.sin(2*np.pi*s); Rall = []
    for ret in np.linspace(12, 0, STEPS):
        X = Xn - ret; dlat = (X - 0.5) - xi
        th, R, _, _ = s_lateral.solve(th, L, Z, dlat); Rall.append(R)
        h = L/s_lateral.N
        zz = np.concatenate([[0], np.cumsum(h*np.cos(th))]); xx = np.concatenate([[0], np.cumsum(h*np.sin(th))])
        rib = [ribbon(inc, (0, 0, 1), 15)]
        for off in (-gap/2, gap/2):
            rib.append(ribbon(np.stack([xi + off + xx, np.full(len(xx), 5.3), z0 + zz], 1), (0, 1, 0), 10))
        cam_flex = np.array([[xp - 5.6, 5.25, 5.25], [xp - 5.6, 5.25, 20.5]])
        rib.append(dict(p=cam_flex.tolist(), b=[0, 1, 0], w=6, R=[99, 99]))
        frames.append(dict(ret=round(ret, 3), ribbons=rib, boxes=[
            box(-10, 0, 0.2, 1.2, -4, 56, 'mainboard'),
            box(xi - 0.5, xi + 0.5, 4.3, 10.4, zi0, zi1 - 4, 'pestana'),
            box(xi - 0.5, xi + 0.5, 0.3, 10.4, zi1 - 4, zi1, 'pestana'),
            box(xi1, xi1 + 1.5, 3.0, 7.5, 15.5, 20.0, 'conector'),              # conector de la camara
            box(xp - 5.5, xp, 1.0, 9.5, 1.0, 9.5, 'camara'),                     # modulo MIPI
            box(X - 1.0, X, 0.3, 10.4, zc0, zc0 + 14, 'placa'),
            box(X, X + b, 0.3, 10.4, zc0 + 1, zc0 + 13, 'conector'),              # cuerpo del conector
            dict(cyl=True, x0=X + b, len=12, y=5.25, z=zc0 + 7, r=6, kind='rosca'),
            box(xp, xp + 1.5, -1, 13, -2, 54, 'panel')]))
    return dict(id='cam', nombre='Interfaz fija + cámara + S doble', W=Xn, Rmin=round(min(Rall), 2), a=round(a, 2), env=[0, 52], frames=frames)

if __name__ == '__main__':
    _main()
