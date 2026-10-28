"""Figura 2: nudo ocho reconstruido paso a paso, renderizado en 3D.

Recorrido (como en las guías de nudos): el firme entra arriba, rodea el lóbulo superior, baja en diagonal
por la cintura, rodea el lóbulo inferior, sube cruzando la cintura y el chicote baja por el centro. La línea
media es una curva suave: el recorrido se cierra por fuera y se reemplaza por su serie de Fourier truncada.
La altura z en los cruces es una suma de gaussianas (sube el tramo de arriba, baja el de abajo); los cruces
alternan como en la referencia. El repaso del chicote es la misma curva desplazada en paralelo.

Verificación por teoría de nudos sobre la cuerda 3D dibujada: 4 cruces, determinante 5 y polinomio de
Alexander t² − 3t + 1, que identifican al nudo ocho (4_1). Además se controla que los tramos no se
interpenetren. Salida: img/nudo_ocho_3d.svg (build.js la convierte a PNG).
Uso: python3 nudo_ocho_3d.py
"""
import base64
import io
import math
from pathlib import Path

import numpy as np
from PIL import Image

AQUI = Path(__file__).parent
CONTROL = [(0, -265), (0, -225), (10, -188), (50, -160), (74, -114), (56, -64), (-22, -22), (-58, 18), (-74, 70),
           (-50, 124), (0, 142), (52, 124), (74, 70), (52, 22), (-22, -22), (-58, -62), (-64, -106), (-42, -146),
           (-8, -128), (28, -100), (32, -60), (32, 40), (32, 160), (32, 235)]
RADIO = 7.6            # radio de la cuerda en el dibujo
SEP = 8.5             # media separación entre los dos ramales del nudo doble
DZ = 22              # altura de cada ramal sobre / bajo el plano en un cruce
AZUL = (0.16, 0.36, 0.78)
NAR = (0.91, 0.45, 0.10)
METAL = (0.62, 0.65, 0.68)
GIRO_Y, GIRO_X = math.radians(16), math.radians(-14)   # punto de vista algo lateral y desde arriba
SS = 2                 # sobremuestreo para suavizar bordes


# ---------------------------------------------------------------- geometría
def catmull(P, n=24):
    P = [P[0]] + list(P) + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = (np.array(P[k], float) for k in (i - 1, i, i + 1, i + 2))
        for k in range(n):
            t = k / n
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(np.array(P[-2], float))
    return np.array(out)


def _corte(a, b, c, d):
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = a, b, c, d
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-9:
        return False
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den
    return 0 <= t <= 1 and 0 <= u <= 1


# Curva suave: el recorrido se cierra por fuera (sin agregar cruces), se muestrea a paso constante y se
# reemplaza por su serie de Fourier truncada (C∞, sin quiebres). Se conserva el tramo del nudo.
CIERRE = [(20, 330), (140, 380), (250, 250), (250, -260), (130, -380), (0, -340)]
MUESTRAS, ARMONICOS = 2400, 20


def _remuestrear(P, n, cerrada=False):
    Q = np.vstack([P, P[:1]]) if cerrada else P
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Q, axis=0), axis=1))]
    s = np.linspace(0, d[-1], n, endpoint=not cerrada)
    return np.c_[[np.interp(s, d, Q[:, k]) for k in range(Q.shape[1])]].T, d


def _suave():
    abierta = catmull(CONTROL)
    cerrada = np.vstack([abierta, catmull([CONTROL[-1]] + CIERRE + [CONTROL[0]])[1:-1]])
    P, d = _remuestrear(cerrada, MUESTRAS, cerrada=True)
    F = np.fft.rfft(P, axis=0)
    F[ARMONICOS + 1:] = 0
    S = np.fft.irfft(F, n=MUESTRAS, axis=0)
    largo_nudo = np.sum(np.linalg.norm(np.diff(abierta, axis=0), axis=1))
    return S[: int(MUESTRAS * largo_nudo / d[-1])]


def cruces_2d(L):
    """Pares (i, j) de tramos que se cortan en la proyección (cada cruce una sola vez)."""
    out = []
    for i in range(len(L) - 1):
        a, b = L[i], L[i + 1]
        for j in range(i + 3, len(L) - 1):
            if _corte(a, b, L[j], L[j + 1]) and all(abs(i - p) > 6 or abs(j - q) > 6 for p, q in out):
                out.append((i, j))
    return out


LINEA = _suave()
NL = len(LINEA)
CRUCES = cruces_2d(LINEA)
assert len(CRUCES) == 4, "el ocho debe tener 4 cruces"
_ev = sorted([(i, k) for k, (i, _) in enumerate(CRUCES)] + [(j, k) for k, (_, j) in enumerate(CRUCES)])
# Cruces alternados, como la referencia: en la cintura pasa por encima la diagonal que baja de arriba a la
# derecha hacia abajo a la izquierda.
ENCIMA = {idx for n, (idx, _) in enumerate(_ev) if n % 2 == 1}

# altura z: función suave (suma de gaussianas sobre el largo de la cuerda) que sube en el tramo de arriba de
# cada cruce y baja en el de abajo
_s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(LINEA, axis=0), axis=1))]
Z = np.zeros(NL)
for i, j in CRUCES:
    for idx in (i, j):
        Z += (DZ if idx in ENCIMA else -DZ) * np.exp(-((_s - _s[idx]) / 30.0) ** 2)
MEDIA = np.c_[LINEA, Z]


# ---------------------------------------------------------------- verificación por teoría de nudos
def alexander(P, t):
    """Determinante de un menor de la matriz de Alexander del nudo que forma la cuerda P (3D), evaluado en t.

    Los cruces se buscan en la proyección de la cuerda y en cada uno pasa por encima el tramo de mayor z;
    el diagrama se cierra uniendo los extremos por fuera (sin agregar cruces). Los arcos son los tramos
    entre dos pasos por debajo; cada cruce aporta la fila (1 − t)·arco_encima + t·arco_entrante − arco_saliente
    (cruce positivo) o (1 − t)·arco_encima − arco_entrante + t·arco_saliente (cruce negativo).
    """
    L = P[:, :2]
    cr = cruces_2d(L)
    debajo = sorted((i, j) if P[i, 2] < P[j, 2] else (j, i) for i, j in cr)          # (abajo, encima)
    pos = [u for u, _ in debajo]
    arco = lambda k: (np.searchsorted(pos, k, side="right") - 1) % len(pos)
    tg = lambda k: (L[min(k + 1, len(L) - 1)] - L[max(k - 1, 0)]) * [1, -1]             # y hacia arriba
    M = np.zeros((len(pos), len(pos)))
    for f, (u, o) in enumerate(debajo):
        (ox_, oy_), (ux_, uy_) = tg(o), tg(u)
        positivo = ox_ * uy_ - oy_ * ux_ > 0
        M[f, arco(o)] += 1 - t
        M[f, (f - 1) % len(pos)] += t if positivo else -1
        M[f, f] += -1 if positivo else t
    return np.linalg.det(M[1:, 1:]), len(cr)


def verificar_nudo(P=None):
    """Comprueba sobre la cuerda 3D que forma el nudo ocho (4_1): 4 cruces, determinante 5 y
    polinomio de Alexander t² − 3t + 1 (salvo ± t^k)."""
    P = MEDIA if P is None else P
    d, n = alexander(P, -1.0)
    assert n == 4 and round(abs(d)) == 5, f"{n} cruces, determinante {abs(d):.0f}: no es un nudo ocho"
    for t in (2.0, 3.0, 5.0):
        r = alexander(P, t)[0] / (t * t - 3 * t + 1)
        k = math.log(abs(r), t)
        assert abs(k - round(k)) < 1e-6, "el polinomio de Alexander no es el del nudo ocho"
    return round(abs(d))


def verificar_cuerda(*ramales):
    """Distancia mínima entre tramos no contiguos de la cuerda, en diámetros (≥ 1: no se interpenetra)."""
    P = np.vstack([densificar(np.asarray(r, float), RADIO / 2)[0] for r in ramales])
    D = np.linalg.norm(P[:, None] - P[None], axis=2)
    k = np.arange(len(P))
    D[np.abs(k[:, None] - k[None]) < int(2.5 * 2 * RADIO / (RADIO / 2))] = 1e9
    return D.min() / (2 * RADIO)


def desplazar(P, d):
    """Desplaza la línea en el plano del dibujo (normal en xy), conservando z."""
    t = np.gradient(P[:, :2], axis=0)
    n = np.c_[-t[:, 1], t[:, 0]] / np.linalg.norm(t, axis=1, keepdims=True)
    return np.c_[P[:, :2] + d * n, P[:, 2]]


def densificar(P, paso):
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    s = np.arange(0, d[-1] + 1e-9, paso)
    return np.c_[[np.interp(s, d, P[:, k]) for k in range(3)]].T, s


def curva(puntos, n=16):
    return np.array([np.r_[p, 0] if len(p) == 2 else p for p in catmull([tuple(q) for q in puntos], n)])


# ---------------------------------------------------------------- render
class Escena:
    def __init__(self, ancho, alto, escala, cx, cy):
        self.w, self.h, self.e, self.cx, self.cy = ancho * SS, alto * SS, escala * SS, cx * SS, cy * SS
        self.z = np.full((self.h, self.w), -1e9)
        self.n = np.zeros((self.h, self.w, 3))
        self.col = np.zeros((self.h, self.w, 3))
        self.tex = np.ones((self.h, self.w))
        rot_y = np.array([[math.cos(GIRO_Y), 0, math.sin(GIRO_Y)], [0, 1, 0], [-math.sin(GIRO_Y), 0, math.cos(GIRO_Y)]])
        rot_x = np.array([[1, 0, 0], [0, math.cos(GIRO_X), -math.sin(GIRO_X)], [0, math.sin(GIRO_X), math.cos(GIRO_X)]])
        self.rot = rot_x @ rot_y

    def tubo(self, P, color, radio=RADIO, trenzado=True):
        """Cuerda: esferas densas a lo largo de P (x, y hacia abajo, z hacia el observador)."""
        P, s = densificar(np.asarray(P, float), radio / 4)
        Q = P @ self.rot.T
        T = np.gradient(Q, axis=0)
        T /= np.linalg.norm(T, axis=1, keepdims=True)
        ref = np.cross(T, [0, 0, 1.0])
        ref /= np.maximum(np.linalg.norm(ref, axis=1, keepdims=True), 1e-9)
        r = radio * self.e
        R = int(math.ceil(r)) + 1
        yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
        for k in range(len(Q)):
            px, py = self.cx + Q[k, 0] * self.e, self.cy + Q[k, 1] * self.e
            x0, y0 = int(round(px)), int(round(py))
            dx, dy = xx + x0 - px, yy + y0 - py
            d2 = dx * dx + dy * dy
            m = d2 < r * r
            dz = np.sqrt(np.maximum(r * r - d2, 0))
            zz = Q[k, 2] * self.e + dz
            ys, xs = yy[m] + y0, xx[m] + x0
            ok = (ys >= 0) & (ys < self.h) & (xs >= 0) & (xs < self.w)
            ys, xs, zv = ys[ok], xs[ok], zz[m][ok]
            nv = np.c_[dx[m][ok], dy[m][ok], dz[m][ok]] / r
            mejor = zv > self.z[ys, xs]
            ys, xs, zv, nv = ys[mejor], xs[mejor], zv[mejor], nv[mejor]
            self.z[ys, xs] = zv
            self.n[ys, xs] = nv
            self.col[ys, xs] = color
            if trenzado:                                 # dos hélices cruzadas: aspecto de cuerda trenzada
                u = nv - (nv @ T[k])[:, None] * T[k]
                fi = np.arctan2(u @ np.cross(T[k], ref[k]), u @ ref[k])
                a = s[k] / radio * 2.2
                self.tex[ys, xs] = 0.86 + 0.14 * np.maximum(np.sin(a * 3 + 3 * fi), np.sin(a * 3 - 3 * fi))
            else:
                self.tex[ys, xs] = 1.0

    def anillo(self, centro, radio, grosor, eje):
        """Ojal metálico: toro de radio `radio` alrededor del eje dado (en coordenadas del dibujo)."""
        eje = np.asarray(eje, float) / np.linalg.norm(eje)
        a = np.cross(eje, [0, 0, 1.0]) if abs(eje[2]) < 0.9 else np.cross(eje, [1.0, 0, 0])
        a /= np.linalg.norm(a)
        b = np.cross(eje, a)
        t = np.linspace(0, 2 * math.pi, 200)
        P = np.asarray(centro, float) + radio * (np.outer(np.cos(t), a) + np.outer(np.sin(t), b))
        self.tubo(P, METAL, grosor, trenzado=False)

    def imagen(self):
        hay = self.z > -1e8
        luz = np.array([-0.45, -0.6, 0.66])
        luz /= np.linalg.norm(luz)
        n = self.n
        dif = np.clip(n @ luz, 0, 1)
        refl = 2 * (n @ luz)[..., None] * n - luz
        esp = np.clip(refl[..., 2], 0, 1) ** 24
        c = self.col * (0.38 + 0.62 * dif)[..., None] * self.tex[..., None] + 0.28 * esp[..., None]
        # contorno: salto de profundidad entre píxeles vecinos (separa la cuerda de arriba de la de abajo)
        z = np.where(hay, self.z, -1e4)
        salto = np.zeros_like(hay)
        lim = RADIO * self.e * 0.35
        for sy, sx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            zv = np.roll(np.roll(z, sy, 0), sx, 1)
            salto |= (zv - z) > lim
        # sombra que proyecta la cuerda de arriba sobre la de abajo (luz desde arriba a la izquierda)
        desp = int(RADIO * self.e * 0.7)
        zl = np.roll(np.roll(z, desp, 0), desp, 1)
        sombra = hay & ((zl - z) > RADIO * self.e * 0.8)
        c = np.where(sombra[..., None], c * 0.5, c)
        # contorno algo más grueso en los saltos de profundidad
        borde = salto | np.roll(salto, 1, 0) | np.roll(salto, 1, 1)
        c = np.where(borde[..., None], c * 0.2, c)
        c = np.where((n[..., 2] < 0.22)[..., None], c * 0.55, c)
        rgba = np.dstack([np.clip(c, 0, 1) * 255, hay * 255]).astype(np.uint8)
        im = Image.fromarray(rgba, "RGBA")
        return im.resize((self.w // SS, self.h // SS), Image.LANCZOS)


# ---------------------------------------------------------------- recorridos de cada paso
def firme_y_chicote():
    """Paso 1: ocho simple."""
    return MEDIA


def lazo_y_ojal(base, sep):
    """Lazo que pasa por el ojal: une el ramal de ida (−sep) con el de vuelta (+sep) bajo el nudo."""
    ida, vuelta = desplazar(base, -sep), desplazar(base, sep)
    yb = base[-1, 1] + 40
    u = curva([ida[-1], (ida[-1][0], yb, 0), (base[-1][0], yb + sep, 0), (vuelta[-1][0], yb, 0), vuelta[-1]], 10)
    ojal = (base[-1][0], yb + sep, 0)
    return ida, vuelta, u, ojal


SEPARACION = []


def figura():
    paneles = []
    # 1. ocho simple
    e1 = Escena(560, 640, 1.0, 280, 300)
    e1.tubo(MEDIA, AZUL)
    paneles.append(e1.imagen())
    # 2. pasar el chicote por el ojal y volver
    e2 = Escena(560, 640, 1.0, 280, 268)
    xa, ya = MEDIA[-1, 0], MEDIA[-1, 1] + 48
    vuelta = curva([MEDIA[-1], (xa, ya, 0), (xa + 26, ya + 34, 0), (xa + 56, ya, 0), (xa + 62, ya - 70, 0), (xa + 46, ya - 140, 0)])
    e2.anillo((xa + 4, ya + 26, 0), 30, 5, (1, 0, 0.7))
    e2.tubo(np.r_[MEDIA, vuelta[1:]], AZUL)
    paneles.append((e2.imagen(), (xa + 46, ya - 140), ya + 26 + 32))
    # 3. repasar (mitad del recorrido) y 4. completo, peinado y apretado
    for hasta, chicote in ((9 * 24, 0), (36, 52)):
        e = Escena(560, 640, 1.0, 280, 285)
        ida, vuelta, u, ojal = lazo_y_ojal(MEDIA, SEP)
        rep = vuelta[hasta:][::-1]
        if chicote:
            t = rep[-1] - rep[-4]
            rep = np.r_[rep, [rep[-1] + chicote * t / np.linalg.norm(t)]]
        e.anillo(ojal, 30, 5, (1, 0, 0.7))
        cuerda = densificar(np.r_[ida, u[1:], rep[1:]], RADIO / 2)[0]   # ida, lazo y repaso: una sola cuerda
        n_az = len(densificar(np.r_[ida, u[1:]], RADIO / 2)[0])
        e.tubo(cuerda[:n_az + 1], AZUL)
        e.tubo(cuerda[n_az:], NAR)
        SEPARACION.append(verificar_cuerda(cuerda))
        paneles.append((e.imagen(), rep[-1], ojal[1] + 32))
    return paneles


def png_b64(im):
    b = io.BytesIO()
    im.save(b, "PNG")
    return base64.b64encode(b.getvalue()).decode()


# ---------------------------------------------------------------- composición (SVG → PNG con Chromium en build.js)
T = 34
W, H = 1600, 1700


def main():
    det = verificar_nudo()
    p1, (p2, fin2, rb2), (p3, fin3, rb3), (p4, fin4, rb4) = figura()
    capas = []

    def texto(x, y, t, tam=T, ancla="start", peso="normal", color="#1A1A1A"):
        for i, r in enumerate(t.split("\n")):
            capas.append(f'<text x="{x:.1f}" y="{y + i * (tam + 8):.1f}" font-size="{tam}" text-anchor="{ancla}" font-weight="{peso}" fill="{color}">{r}</text>')

    def flecha(x1, y1, x2, y2, col="#1A1A1A"):
        a = math.atan2(y2 - y1, x2 - x1)
        capas.append(f'<path d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}" stroke="{col}" stroke-width="4" fill="none"/>')
        capas.append(f'<path d="M{x2:.1f},{y2:.1f} L{x2 - 22 * math.cos(a - 0.42):.1f},{y2 - 22 * math.sin(a - 0.42):.1f} '
                     f'L{x2 - 22 * math.cos(a + 0.42):.1f},{y2 - 22 * math.sin(a + 0.42):.1f} Z" fill="{col}"/>')

    def panel(n, x0, y0, titulo, nota, im, robot=None, cy=285):
        capas.append(f'<rect x="{x0}" y="{y0}" width="770" height="830" fill="none" stroke="#B0B6BA" stroke-width="1.5" rx="8"/>')
        capas.append(f'<circle cx="{x0 + 46}" cy="{y0 + 46}" r="24" fill="#E8731A"/>')
        texto(x0 + 46, y0 + 57, str(n), 32, "middle", "bold", "#FFFFFF")
        texto(x0 + 84, y0 + 58, titulo, T, peso="bold")
        texto(x0 + 30, y0 + 745, nota, T, color="#222")
        ix, iy = x0 + 105, y0 + 75
        if robot is not None:
            _, yr = a_panel(ix, iy, (20, robot, 0), cy)
            capas.append(f'<rect x="{ix + 180}" y="{yr - 6:.1f}" width="220" height="52" rx="6" fill="#B7BCC1" stroke="#5F6368" stroke-width="2"/>')
            texto(ix + 290, yr + 32, "Robot", 30, "middle", color="#2B2F33")
        capas.append(f'<image x="{ix}" y="{iy}" width="560" height="640" href="data:image/png;base64,{png_b64(im)}"/>')
        return ix, iy

    def a_panel(ix, iy, p, cy):
        """Proyección de un punto del modelo al panel (misma rotación que el render)."""
        q = np.r_[p[:2], p[2] if len(p) > 2 else 0]
        e = Escena(1, 1, 1, 0, 0)
        r = e.rot @ q
        return ix + 280 + r[0], iy + cy + r[1]

    ix, iy = panel(1, 20, 20, "Hacer un ocho simple", "A unos 30 cm del extremo,\ncon el chicote hacia el robot.", p1, cy=300)
    texto(ix + 305, iy + 70, "Firme", T)
    texto(ix + 280, iy + 600, "Chicote", T, "end")
    ix, iy = panel(2, 810, 20, "Pasar por el ojal", "Pasar el chicote por el ojal\nde amarre del robot.", p2, rb2, cy=268)
    x, y = a_panel(ix, iy, fin2, 268)
    flecha(x + 40, y + 60, x + 40, y - 30, "#E8731A")
    ix, iy = panel(3, 20, 870, "Repasar el ocho", "Seguir el recorrido del ocho\nal revés, paralelo a la cuerda.", p3, rb3)
    x, y = a_panel(ix, iy, fin3, 285)
    flecha(x - 10, y + 10, x - 70, y - 55, "#E8731A")
    ix, iy = panel(4, 810, 870, "Peinar y apretar", "Pares paralelos, sin cruces.\nChicote de 3 a 5 cm.", p4, rb4)
    x, y = a_panel(ix, iy, fin4, 285)
    capas.append(f'<path d="M{x - 26},{y} L{x - 26},{y + 52} M{x - 34},{y} L{x - 18},{y} M{x - 34},{y + 52} L{x - 18},{y + 52}" stroke="#1A1A1A" stroke-width="2.5"/>')
    texto(x - 40, y + 20, "Chicote", 30, "end")
    texto(x - 40, y + 54, "3 a 5 cm", 30, "end", "bold")

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
           f'font-family="Arial, Liberation Sans, Helvetica, sans-serif"><rect width="{W}" height="{H}" fill="#FFFFFF"/>'
           + "".join(capas) + "</svg>")
    (AQUI / "img" / "nudo_ocho_3d.svg").write_text(svg, encoding="utf8")
    print(f"img/nudo_ocho_3d.svg — nudo ocho verificado (determinante {det}, Alexander t² − 3t + 1); "
          f"separación mínima entre tramos: {min(SEPARACION):.2f} diámetros")


if __name__ == "__main__":
    main()
