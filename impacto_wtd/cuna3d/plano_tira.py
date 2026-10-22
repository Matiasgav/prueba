"""Planos del palpador de una tira (C plegada + lengüeta): SVG a escala, con cotas.

Genera docs/palpador/plano_tira.html (sección para insertar en la página):
vista isométrica, alzado, planta, desarrollo de la chapa y detalle del hoyuelo.
Toda la geometría sale de cuna3d/palpador_tira.py.
"""

from __future__ import annotations

import json
import math
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cuna3d.palpador_tira import (BANDA_C1, B_ALMA, B_CENTRO, B_LENG, B_SUP, B_TIRA, H_HOY, L_BRAZO,  # noqa: E402
                                  L_LENG, OREJA, R_HOY, RANURA, T, Y_INF, Y_SUP, Y_T)

RAIZ = pathlib.Path(__file__).resolve().parent.parent
L_PUNTA = 1.0          # lengüeta más allá del centro del hoyuelo
X_A = L_BRAZO          # plano del alma
CARCASA = dict(x0=-4.0, x1=20.0, y0=1.0, y1=10.0, z=5.0, pared=1.0)


def f(x, n=1):
    return f"{x:.{n}f}".replace(".", ",")


# ---------------------------------------------------------------------------
# Piezas como cajas 3D (x0, x1, y0, y1, z0, z1, clase)
# ---------------------------------------------------------------------------

def cajas():
    t = max(T, 0.15)
    c = []
    # orejas y brazos
    c.append((-OREJA, 0, Y_SUP - t / 2, Y_SUP + t / 2, -B_SUP / 2, B_SUP / 2, "chapa"))
    c.append((0, X_A, Y_SUP - t / 2, Y_SUP + t / 2, -B_SUP / 2, B_SUP / 2, "chapa"))
    for s in (-1, 1):
        z0, z1 = sorted((s * (B_ALMA / 2 - B_TIRA), s * B_ALMA / 2))
        c.append((0, X_A, Y_INF - t / 2, Y_INF + t / 2, z0, z1, "chapa"))
    c.append((-OREJA, 0, Y_INF - t / 2, Y_INF + t / 2, -B_ALMA / 2, B_ALMA / 2, "chapa"))
    # alma: parte ancha y centro que baja
    c.append((X_A - t / 2, X_A + t / 2, Y_INF, Y_SUP, -B_ALMA / 2, B_ALMA / 2, "chapa"))
    c.append((X_A - t / 2, X_A + t / 2, Y_T, Y_INF, -B_CENTRO / 2, B_CENTRO / 2, "chapa"))
    # lengüeta
    c.append((X_A, X_A + L_LENG + L_PUNTA, Y_T - t / 2, Y_T + t / 2, -B_LENG / 2, B_LENG / 2, "leng"))
    # extremo rígido del flex (refuerzo de FR4 + flex) y sensor, pegados por fuera del alma
    c.append((X_A + t / 2, X_A + t / 2 + 0.4, 1.4, 6.4, -3.0, 3.0, "fr4"))
    c.append((X_A + t / 2 + 0.4, X_A + t / 2 + 0.5, 1.4, 6.4, -3.0, 3.0, "flex"))
    c.append((X_A + t / 2 + 0.5, X_A + t / 2 + 2.3, 1.45, 6.35, -2.5, 2.5, "chip"))
    return c


# ---------------------------------------------------------------------------
# Vista isométrica (pintor: caras visibles +x, +y, +z, ordenadas por profundidad)
# ---------------------------------------------------------------------------

def iso(x, y, z, s=16.0, ox=442.0, oy=232.0):
    sx = (x - z) * 0.866
    sy = -(y * 0.816 - (x + z) * 0.408)
    return ox + s * sx, oy + s * sy


def svg_iso():
    caras = []
    for (x0, x1, y0, y1, z0, z1, cl) in cajas():
        quads = {
            "x": [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
            "y": [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
            "z": [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
        }
        for k, q in quads.items():
            d = sum(p[0] + p[1] + p[2] for p in q) / 4
            caras.append((d, cl, k, q))
    caras.sort(key=lambda r: r[0])
    out = []
    # cuña (fondo)
    w = [iso(-5, 0, -6.5), iso(20.5, 0, -6.5), iso(20.5, 0, 6.5), iso(-5, 0, 6.5)]
    out.append('<polygon class="i-cuna" points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in w) + '"/>')
    for d, cl, k, q in caras:
        pts = " ".join(f"{a:.1f},{b:.1f}" for a, b in (iso(*p) for p in q))
        out.append(f'<polygon class="i-{cl} i-{k}" points="{pts}"/>')
    # hoyuelo (elipse bajo la lengüeta, se ve por transparencia)
    xh = X_A + L_LENG
    hx, hy = iso(xh, 0.02, 0)
    out.append(f'<ellipse class="i-hoy" cx="{hx:.1f}" cy="{hy:.1f}" rx="{16*0.95:.1f}" ry="{16*0.5:.1f}"/>')
    # carcasa en alambre
    C = CARCASA
    xs, ys, zs = (C["x0"], C["x1"]), (C["y0"], C["y1"]), (-C["z"], C["z"])
    aristas = []
    for a in xs:
        for b in ys:
            aristas.append(((a, b, zs[0]), (a, b, zs[1])))
    for a in xs:
        for c in zs:
            aristas.append(((a, ys[0], c), (a, ys[1], c)))
    for b in ys:
        for c in zs:
            aristas.append(((xs[0], b, c), (xs[1], b, c)))
    for p, q in aristas:
        (a1, b1), (a2, b2) = iso(*p), iso(*q)
        out.append(f'<line class="i-carcasa" x1="{a1:.1f}" y1="{b1:.1f}" x2="{a2:.1f}" y2="{b2:.1f}"/>')
    # rótulos con guía
    def rot(p, tx, ty, txt, cls="lbl"):
        a, b = iso(*p)
        return (f'<line class="guia" x1="{a:.1f}" y1="{b:.1f}" x2="{tx:.1f}" y2="{ty:.1f}"/>'
                f'<text class="{cls}" x="{tx + (4 if tx > a else -4):.1f}" y="{ty + 4:.1f}" text-anchor="{"start" if tx > a else "end"}">{txt}</text>')
    out += [rot((-1.2, Y_SUP + 0.1, 0), 270, 70, "oreja superior (tornillo M1)"),
            rot((5, Y_SUP + 0.1, 0), 270, 130, "brazo superior · 3 mm"),
            rot((5, Y_INF, 2.3), 270, 330, "brazo inferior · 2 tiras de 1,5 mm"),
            rot((-3, 0, 4), 270, 395, "cuña", "lbl-w"),
            rot((X_A, 5.5, -2.8), 830, 40, "alma 6 mm"),
            rot((X_A + 2.3, 5.0, 1.0), 830, 120, "flex con ADXL1004, pegado al alma"),
            rot((X_A + L_LENG + 0.5, Y_T, 0), 830, 330, "lengüeta 2,4 mm con hoyuelo R 2"),
            rot((19.0, 1.0, -5.0), 830, 395, "carcasa 10 × 10 mm (contorno)")]
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Alzado (x-y) y planta (x-z)
# ---------------------------------------------------------------------------

def svg_alzado():
    s, ox, oy = 26.0, 190.0, 330.0
    X = lambda x: ox + s * x
    Y = lambda y: oy - s * y
    o = []
    def rect(x0, y0, x1, y1, cl):
        o.append(f'<rect class="{cl}" x="{X(min(x0,x1)):.1f}" y="{Y(max(y0,y1)):.1f}" width="{s*abs(x1-x0):.1f}" height="{s*abs(y1-y0):.1f}"/>')
    def line(x0, y0, x1, y1, cl):
        o.append(f'<line class="{cl}" x1="{X(x0):.1f}" y1="{Y(y0):.1f}" x2="{X(x1):.1f}" y2="{Y(y1):.1f}"/>')
    def text(x, y, t, cl="lbl", a="start"):
        o.append(f'<text class="{cl}" x="{X(x):.1f}" y="{Y(y):.1f}" text-anchor="{a}">{t}</text>')
    def cota_h(x0, x1, y, t, dy=0.35):
        line(x0, y, x1, y, "cota"); line(x0, y - 0.18, x0, y + 0.18, "cota"); line(x1, y - 0.18, x1, y + 0.18, "cota")
        text((x0 + x1) / 2, y + dy, t, "ct", "middle")
    def cota_v(x, y0, y1, t, lado=1):
        line(x, y0, x, y1, "cota"); line(x - 0.18, y0, x + 0.18, y0, "cota"); line(x - 0.18, y1, x + 0.18, y1, "cota")
        text(x + 0.3 * lado, (y0 + y1) / 2 - 0.1, t, "ct", "start" if lado > 0 else "end")
    C = CARCASA
    rect(-5.5, -1.8, 24.5, 0, "cuna"); text(-5.2, -1.15, "cuña de G11", "lbl-w")
    # carcasa (corte)
    o.append(f'<path class="carcasa" d="M{X(C["x0"])} {Y(C["y0"])} L{X(11.6)} {Y(C["y0"])} L{X(11.6)} {Y(C["y0"]+C["pared"])} '
             f'L{X(C["x0"]+C["pared"])} {Y(C["y0"]+C["pared"])} L{X(C["x0"]+C["pared"])} {Y(C["y1"]-C["pared"])} '
             f'L{X(C["x1"]-C["pared"])} {Y(C["y1"]-C["pared"])} L{X(C["x1"]-C["pared"])} {Y(C["y0"]+C["pared"])} '
             f'L{X(16.8)} {Y(C["y0"]+C["pared"])} L{X(16.8)} {Y(C["y0"])} L{X(C["x1"])} {Y(C["y0"])} L{X(C["x1"])} {Y(C["y1"])} '
             f'L{X(C["x0"])} {Y(C["y1"])} Z"/>')
    rect(-3.0, Y_INF - 0.6, -0.0, Y_INF - 0.08, "amarre"); rect(-3.0, Y_SUP + 0.08, 0.0, Y_SUP + 0.7, "amarre")
    rect(-3.0, Y_SUP - 0.7, 0.0, Y_SUP - 0.08, "amarre"); rect(-3.0, Y_INF + 0.08, 0.0, Y_INF + 0.7, "amarre")
    text(-1.5, Y_SUP + 1.1, "amarre", "ct", "middle")
    # chapa (línea media gruesa)
    o.append(f'<path class="chapa" d="M{X(-OREJA)} {Y(Y_SUP)} L{X(X_A-0.15)} {Y(Y_SUP)} Q{X(X_A)} {Y(Y_SUP)} {X(X_A)} {Y(Y_SUP-0.15)} '
             f'L{X(X_A)} {Y(Y_T+0.15)} Q{X(X_A)} {Y(Y_T)} {X(X_A+0.15)} {Y(Y_T)} L{X(X_A+L_LENG+L_PUNTA)} {Y(Y_T)}"/>')
    o.append(f'<path class="chapa2" d="M{X(-OREJA)} {Y(Y_INF)} L{X(X_A-0.15)} {Y(Y_INF)} Q{X(X_A)} {Y(Y_INF)} {X(X_A)} {Y(Y_INF+0.15)}"/>')
    # hoyuelo
    xh = X_A + L_LENG
    a = math.sqrt(2 * R_HOY * H_HOY - H_HOY ** 2)
    o.append(f'<path class="hoy" d="M{X(xh-a)} {Y(Y_T)} Q{X(xh)} {Y(Y_T-2*H_HOY)} {X(xh+a)} {Y(Y_T)}"/>')
    # extremo rígido del flex y sensor
    rect(X_A + 0.075, 1.4, X_A + 0.475, 6.4, "fr4"); rect(X_A + 0.475, 1.4, X_A + 0.575, 6.4, "flex")
    rect(X_A + 0.575, 1.45, X_A + 2.375, 6.35, "chip")
    o.append(f'<path class="eje" d="M{X(X_A+1.475)} {Y(2.3)} L{X(X_A+1.475)} {Y(5.5)}" marker-end="url(#fl)"/>')
    o.append(f'<path class="flexl" d="M{X(X_A+1.6)} {Y(6.4)} C{X(X_A+1.6)} {Y(8.4)} {X(8)} {Y(8.9)} {X(5)} {Y(8.55)} S{X(2)} {Y(8.8)} {X(1)} {Y(9.0)}"/>')
    # rótulos
    text(0.6, Y_SUP + 0.35, "brazo superior 0,15 × 3 × 13", "lbl-a", "start")
    text(0.3, Y_INF + 0.3, "brazo inferior 2 × (0,15 × 1,5 × 13)", "lbl-a", "start")
    text(X_A + 2.8, 4.0, "ADXL1004", "lbl"); text(X_A + 2.8, 3.4, "eje sensible ↑", "ct")
    text(X_A + 2.2, 7.5, "flex", "lbl-f", "start")
    text(X_A + L_LENG + 1.3, 0.3, "lengüeta 0,15 × 2,4", "lbl-l")
    text(X_A + L_LENG + 0.3, -0.6, "hoyuelo R 2 · h 0,25", "ct")
    # cotas
    cota_h(0, X_A, 7.6, f(L_BRAZO, 0))
    cota_h(X_A, X_A + L_LENG, -0.75, f(L_LENG, 1), dy=-0.55)
    cota_v(-4.6, Y_INF, Y_SUP, f(Y_SUP - Y_INF, 1), -1)
    cota_v(-4.6, 0, Y_INF, f(Y_INF, 1), -1)
    cota_v(23.3, 0, 1.0, "1,0", 1)
    cota_v(23.3, 1.0, 10.0, "9,0", 1)
    cota_v(X_A - 0.8, Y_T, Y_INF, f(Y_INF - Y_T, 2), -1)
    # precarga
    o.append(f'<path class="fuerza" d="M{X(xh)} {Y(-1.5)} L{X(xh)} {Y(-0.08)}" marker-end="url(#ff)"/>')
    text(xh + 0.3, -1.35, "F₀ 2 N", "lbl-v")
    return "\n".join(o)


def svg_planta():
    s, ox, oy = 26.0, 140.0, 140.0
    X = lambda x: ox + s * x
    Z = lambda z: oy + s * z
    o = []
    def rect(x0, z0, x1, z1, cl):
        o.append(f'<rect class="{cl}" x="{X(x0):.1f}" y="{Z(z0):.1f}" width="{s*(x1-x0):.1f}" height="{s*(z1-z0):.1f}"/>')
    def text(x, z, t, cl="lbl", a="start"):
        o.append(f'<text class="{cl}" x="{X(x):.1f}" y="{Z(z):.1f}" text-anchor="{a}">{t}</text>')
    # brazo inferior (debajo, punteado) y brazo superior
    for sg in (-1, 1):
        z0, z1 = sorted((sg * (B_ALMA / 2 - B_TIRA), sg * B_ALMA / 2))
        rect(0, z0, X_A, z1, "oculto")
    rect(-OREJA, -B_ALMA / 2, 0, B_ALMA / 2, "oculto")
    rect(-OREJA, -B_SUP / 2, X_A, B_SUP / 2, "pl-chapa")
    rect(X_A - 0.075, -B_ALMA / 2, X_A + 0.075, B_ALMA / 2, "pl-chapa")
    rect(X_A, -B_LENG / 2, X_A + L_LENG + L_PUNTA, B_LENG / 2, "pl-leng")
    rect(X_A + 0.575, -2.5, X_A + 2.375, 2.5, "chip-pl")
    text(X_A + 1.475, 3.75, "ADXL1004 (encima)", "ct", "middle")
    xh = X_A + L_LENG
    o.append(f'<circle class="hoy-pl" cx="{X(xh):.1f}" cy="{Z(0):.1f}" r="{s*0.97:.1f}"/>')
    for (x, z) in ((-1.25, 0),):
        o.append(f'<circle class="agujero" cx="{X(x):.1f}" cy="{Z(z):.1f}" r="{s*0.55:.1f}"/>')
    # cotas de anchos
    def cota_z(x, z0, z1, t):
        o.append(f'<line class="cota" x1="{X(x):.1f}" y1="{Z(z0):.1f}" x2="{X(x):.1f}" y2="{Z(z1):.1f}"/>')
        o.append(f'<text class="ct" x="{X(x)+5:.1f}" y="{(Z(z0)+Z(z1))/2+4:.1f}">{t}</text>')
    cota_z(6.5, -B_SUP / 2, B_SUP / 2, "3")
    cota_z(9.5, B_ALMA / 2 - B_TIRA, B_ALMA / 2, "1,5")
    cota_z(X_A + 3.6, -B_LENG / 2, B_LENG / 2, "2,4")
    cota_z(X_A - 1.3, -B_ALMA / 2, B_ALMA / 2, "6")
    text(-OREJA, -3.75, "planta · brazo inferior punteado (tiras laterales)", "ct")
    return "\n".join(o)


# ---------------------------------------------------------------------------
# Desarrollo de la chapa
# ---------------------------------------------------------------------------

def svg_desarrollo():
    s, ox, oy = 15.0, 30.0, 120.0
    U = lambda u: ox + s * u
    V = lambda v: oy + s * v
    # longitudes de línea media (se cotan así; el fotograbado aplica la compensación de pliegue)
    u0 = 0.0
    u1 = u0 + OREJA                 # fin oreja superior
    u2 = u1 + L_BRAZO               # pliegue 1 (brazo -> alma)
    u3 = u2 + (Y_SUP - Y_INF)       # pliegue 2 (alma -> tiras laterales, hacia atrás)
    u4 = u3 + (Y_INF - Y_T)         # pliegue 3 (centro -> lengüeta, hacia adelante)
    u5 = u4 + L_LENG + L_PUNTA      # fin de la lengüeta
    u6 = u3 + L_BRAZO               # fin de las tiras
    u7 = u6 + OREJA                 # fin oreja inferior
    o = []
    def poly(pts, cl):
        o.append(f'<polygon class="{cl}" points="' + " ".join(f"{U(a):.1f},{V(b):.1f}" for a, b in pts) + '"/>')
    hs, ha, ht, hc = B_SUP / 2, B_ALMA / 2, B_ALMA / 2 - B_TIRA, B_CENTRO / 2
    contorno = [(u0, -hs), (u2, -hs), (u2, -ha), (u7, -ha), (u7, ha), (u2, ha), (u2, hs), (u0, hs)]
    poly(contorno, "dev")
    # ventana entre tiras (menos la lengüeta)
    poly([(u3, -ht), (u5, -ht), (u5, -hc), (u3, -hc)], "hueco")
    poly([(u3, hc), (u5, hc), (u5, ht), (u3, ht)], "hueco")
    poly([(u5, -ht), (u6, -ht), (u6, ht), (u5, ht)], "hueco")
    # pliegues
    def pliegue(u, v0, v1, txt, ytxt):
        o.append(f'<line class="pliegue" x1="{U(u):.1f}" y1="{V(v0-0.3):.1f}" x2="{U(u):.1f}" y2="{V(v1+0.3):.1f}"/>')
        o.append(f'<text class="ct-r" x="{U(u):.1f}" y="{V(ytxt):.1f}" text-anchor="middle">{txt}</text>')
    pliegue(u2, -hs, hs, "", -ha - 0.9)
    o.append(f'<text class="ct-r" x="{U(u2 - 0.2):.1f}" y="{V(-hs - 0.6):.1f}" text-anchor="end">P1 · 90° abajo</text>')
    o.append(f'<line class="pliegue" x1="{U(u3):.1f}" y1="{V(-ha-0.2):.1f}" x2="{U(u3):.1f}" y2="{V(-ht+0.05):.1f}"/>')
    o.append(f'<line class="pliegue" x1="{U(u3):.1f}" y1="{V(ht-0.05):.1f}" x2="{U(u3):.1f}" y2="{V(ha+0.2):.1f}"/>')
    o.append(f'<text class="ct-r" x="{U(u3):.1f}" y="{V(ha+1.1):.1f}" text-anchor="middle">P2 · 90° (tiras, hacia atrás)</text>')
    o.append(f'<line class="pliegue" x1="{U(u4):.1f}" y1="{V(-hc-0.15):.1f}" x2="{U(u4):.1f}" y2="{V(hc+0.15):.1f}"/>')
    o.append(f'<text class="ct-r" x="{U(u4):.1f}" y="{V(-ha-0.7):.1f}" text-anchor="start">P3 · 90° (lengüeta, adelante)</text>')
    # agujeros y hoyuelo
    for (u, v) in ((u0 + OREJA / 2, 0), (u6 + OREJA / 2, 0)):
        o.append(f'<circle class="agujero" cx="{U(u):.1f}" cy="{V(v):.1f}" r="{s*0.55:.1f}"/>')
    o.append(f'<circle class="hoy-pl" cx="{U(u4 + L_LENG):.1f}" cy="{V(0):.1f}" r="{s*0.97:.1f}"/>')
    # rótulos de tramos
    def txt(u, v, t, cl="ct"):
        o.append(f'<text class="{cl}" x="{U(u):.1f}" y="{V(v):.1f}" text-anchor="middle">{t}</text>')
    txt((u1 + u2) / 2, 0.25, "brazo superior")
    txt((u2 + u3) / 2, 0.25, "alma")
    txt((u5 + u6) / 2 + 1.5, -ht - 0.55, "tira lateral")
    txt((u5 + u6) / 2 + 1.5, ht + 0.95, "tira lateral")
    o.append(f'<text class="ct-l" x="{U(u5 + 0.3):.1f}" y="{V(0.25):.1f}">← lengüeta</text>')
    # cotas
    def cota(ua, ub, v, t):
        o.append(f'<line class="cota" x1="{U(ua):.1f}" y1="{V(v):.1f}" x2="{U(ub):.1f}" y2="{V(v):.1f}"/>')
        for u in (ua, ub):
            o.append(f'<line class="cota" x1="{U(u):.1f}" y1="{V(v)-4:.1f}" x2="{U(u):.1f}" y2="{V(v)+4:.1f}"/>')
        o.append(f'<text class="ct" x="{(U(ua)+U(ub))/2:.1f}" y="{V(v)-4:.1f}" text-anchor="middle">{t}</text>')
    vb = ha + 2.4
    filas = {(u4, u4 + L_LENG): 1.3, (u3, u6): 2.6}
    for ua, ub in ((u0, u1), (u1, u2), (u2, u3), (u3, u4), (u4, u4 + L_LENG), (u3, u6), (u6, u7)):
        cota(ua, ub, vb + filas.get((ua, ub), 0.0), f(ub - ua, 2 if (ub - ua) % 1 else 0))
    cota(u0, u7, vb + 3.9, f"total {f(u7 - u0, 1)}")
    o.append(f'<text class="tb" x="{U(0):.1f}" y="{V(-ha-2.2):.1f}">Desarrollo · 17-7PH cond. C · 0,15 mm · fotograbado · cotas en la línea media</text>')
    return "\n".join(o), (u7 - u0)


def svg_detalle():
    s, ox, oy = 90.0, 165.0, 120.0
    X = lambda x: ox + s * x
    Y = lambda y: oy - s * y
    a = math.sqrt(2 * R_HOY * H_HOY - H_HOY ** 2)
    o = []
    o.append(f'<rect class="cuna" x="{X(-1.6):.1f}" y="{Y(0):.1f}" width="{s*3.8:.1f}" height="{s*0.35:.1f}"/>')
    # chapa con el hoyuelo (dos líneas: superior e inferior)
    yt, yb = Y_T + T / 2, Y_T - T / 2
    o.append(f'<path class="chapa-det" d="M{X(-1.5)} {Y(yb)} L{X(-a)} {Y(yb)} Q{X(0)} {Y(yb - 2*H_HOY + 0.0)} {X(a)} {Y(yb)} L{X(2.0)} {Y(yb)} '
             f'L{X(2.0)} {Y(yt)} L{X(a)} {Y(yt)} Q{X(0)} {Y(yt - 2*H_HOY)} {X(-a)} {Y(yt)} L{X(-1.5)} {Y(yt)} Z"/>')
    o.append(f'<line class="cota" x1="{X(-a):.1f}" y1="{Y(-0.25):.1f}" x2="{X(a):.1f}" y2="{Y(-0.25):.1f}"/>')
    o.append(f'<text class="ct" x="{X(0):.1f}" y="{Y(-0.25)+14:.1f}" text-anchor="middle">Ø {f(2*a,2)}</text>')
    o.append(f'<line class="cota" x1="{X(1.0):.1f}" y1="{Y(yb):.1f}" x2="{X(1.0):.1f}" y2="{Y(0):.1f}"/>')
    o.append(f'<text class="ct" x="{X(1.06):.1f}" y="{(Y(yb)+Y(0))/2+4:.1f}">h {f(H_HOY,2)}</text>')
    o.append(f'<text class="ct" x="{X(-1.5):.1f}" y="{Y(0.62):.1f}">esc. 10:1 · R {f(R_HOY,0)} mm acuñado · contacto puntual</text>')
    return "\n".join(o)


ESTILO = """
.plano svg text{font-family:var(--f-mono)}
.i-cuna{fill:var(--warnbg);stroke:var(--wedge);stroke-width:.8}
.i-chapa.i-y{fill:#9db8d6}.i-chapa.i-x{fill:#6f93bd}.i-chapa.i-z{fill:#4f76a3}
.i-leng.i-y{fill:#8fd0ad}.i-leng.i-x{fill:#5fb487}.i-leng.i-z{fill:#3f9468}
.i-fr4{fill:#7a9a4a}.i-flex{fill:#c98a1a}.i-chip{fill:#232b33}
.i-cu.i-x,.i-cu.i-y,.i-cu.i-z{fill:#c9824a}
.i-x,.i-y,.i-z{stroke:#1c2a38;stroke-width:.35}
.i-hoy{fill:none;stroke:var(--ok);stroke-width:1.2;stroke-dasharray:3 2}
.i-carcasa{stroke:var(--ink-2);stroke-width:.7;stroke-dasharray:5 4}
.guia{stroke:var(--ink-2);stroke-width:.7}
.lbl{font-size:12px;fill:var(--ink)}.lbl-w{font-size:12px;fill:var(--wedge)}.ct{font-size:11px;fill:var(--ink-2)}
.ct-r{font-size:10.5px;fill:var(--alarm)}.ct-l{font-size:11px;fill:var(--ok)}.tb{font-size:12px;fill:var(--ink)}
.lbl-a{font-size:12px;fill:var(--probe)}.lbl-l{font-size:12px;fill:var(--ok)}.lbl-cu{font-size:12px;fill:#b87333}
.lbl-f{font-size:11px;fill:#c98a1a}.lbl-v{font-size:12px;fill:var(--ok)}
.cuna{fill:var(--warnbg);stroke:var(--wedge);stroke-width:1}
.carcasa{fill:var(--paper);stroke:var(--ink-2);stroke-width:1.1}
.amarre{fill:var(--rule);stroke:var(--ink-2);stroke-width:.8}
.chapa{fill:none;stroke:var(--probe);stroke-width:3;stroke-linecap:round;stroke-linejoin:round}
.chapa2{fill:none;stroke:var(--probe);stroke-width:3;stroke-linecap:round;stroke-dasharray:9 3}
.hoy{fill:none;stroke:var(--ok);stroke-width:3}
.fr4{fill:#7a9a4a}.flex{fill:#c98a1a}.chip{fill:#232b33}.chip-pl{fill:#232b3326;stroke:#232b33;stroke-width:1.2;stroke-dasharray:5 3}
.cu{fill:#c9824a55;stroke:#b87333;stroke-width:1.2}.iman{fill:none;stroke:var(--ink-2);stroke-dasharray:4 3}
.flexl{fill:none;stroke:#c98a1a;stroke-width:2.4}.eje{stroke:#6aa8ef;stroke-width:2}
.cota{stroke:var(--ink-2);stroke-width:.8}.fuerza{stroke:var(--ok);stroke-width:2}
.oculto{fill:none;stroke:var(--probe);stroke-width:1;stroke-dasharray:4 3}
.pl-chapa{fill:#9db8d6aa;stroke:var(--probe);stroke-width:1.2}.pl-leng{fill:#8fd0adaa;stroke:var(--ok);stroke-width:1.2}
.hoy-pl{fill:none;stroke:var(--ok);stroke-width:1.2}.agujero{fill:var(--sheet);stroke:var(--ink-2)}
.dev{fill:var(--band);stroke:var(--probe);stroke-width:1.4}.hueco{fill:var(--sheet);stroke:var(--probe);stroke-width:1}
.pliegue{stroke:var(--alarm);stroke-width:1.1;stroke-dasharray:6 3}
.chapa-det{fill:#9db8d6;stroke:var(--probe);stroke-width:1.2}
"""


def generar():
    res = json.loads((RAIZ / "results/cuna3d/palpador_tira.json").read_text())
    dev, Ltot = svg_desarrollo()
    st = res["estatica"]
    ver = {(r["zeta"], r["F0"], r["tg"]): r for r in res["verificacion"]}
    filas = ""
    for z in (0.002, 0.005):
        for F0 in (1.6, 2.0, 2.4):
            for tg in ("libre", "adherido"):
                r = ver[(z, F0, tg)]
                d = sorted({x.split("·")[0] for x in r["despega"]})
                filas += (f'<tr class="{"rec" if (z, F0) == (0.002, 2.0) else ""}"><td class="n">{f(z,3)}</td><td class="n">{f(F0,1)} N</td><td>{tg}</td>'
                          f'<td>{"no" if not d else "sólo muy floja con juego"}</td><td class="n">{f(r["Fc_min_sin_muy_floja"],2)} N</td>'
                          f'<td class="n">{" · ".join(f(g,2) for g in r["gaps_C1"])}</td><td class="n">{r["gap_C2_Hz"]:.0f} Hz</td></tr>')
    NOM = {"ajustada/moderada": "ajustada | moderada", "moderada/floja": "moderada | floja", "floja/muy_floja_juego": "floja | muy floja"}
    umb = "".join(f'<tr><td>{NOM[u["entre"]]}</td><td class="n">{f(u["umbral"],2)}</td><td class="n">± {f(u["hueco"]/2,2)}</td></tr>'
                  for u in res["umbrales_C1"]["0.002_2.0"])
    html = f"""<section id="tira">
  <style>{ESTILO}</style>
  <div class="prose">
    <span class="eyebrow">10 · Diseño recomendado: una tira plegada</span>
    <h2>C plegada + lengüeta, en una sola pieza de chapa</h2>
    <p>Reemplaza al diseño de dos piezas de la sección 9: en el modelo de elementos finitos, con las láminas con su masa y sus modos propios, ese diseño saturaba el sensor y perdía la separación de C1. Esta tira separa los 5 niveles con o sin rozamiento en la punta y no satura.</p>
    <p><b>Piezas: dos, más dos tornillos.</b> La chapa (17-7PH de 0,15 mm, fotograbada y plegada tres veces) y el flex con el ADXL1004 soldado en su extremo rígido. No lleva amortiguador (ni aleta de cobre ni imanes) ni rigidizador aparte.</p>
    <ul>
      <li><b>Brazos.</b> El brazo superior (3 mm) y el inferior (dos tiras de 1,5 mm a los costados) forman un paralelogramo: el carro baja derecho (giro de 9 mrad) y la flecha de 1,5 mm da la precarga.</li>
      <li><b>Alma.</b> Por fuera va pegado el extremo rígido del flex con el ADXL1004, con el eje sensible vertical.</li>
      <li><b>Lengüeta.</b> El centro del alma baja 1,3 mm más y se pliega hacia adelante: es el filtro. El hoyuelo esférico acuñado en la punta es el contacto con la cuña.</li>
      <li><b>Sin amortiguador.</b> La resonancia del filtro (~{f(res["f0_Hz"],0)} Hz) queda con el amortiguamiento propio del acero (ζ ≈ 0,002). No hace falta domarla: C1 se mide en la banda {f(BANDA_C1[0]/1000,1)}–{f(BANDA_C1[1]/1000,0)} kHz, por encima de ella. El contacto no la amortigua (en el modelo suma ζ ≈ 0,00001: es 100 veces más rígido que la lengüeta y casi no se deforma), pero tampoco hace falta esperar a que se apague: el filtro de C1 la atenúa 45 dB y C2 mira 12–24 kHz.</li>
    </ul>
  </div>
  <div class="fig plano" role="img" aria-label="Vista isométrica del palpador de una tira"><svg viewBox="0 0 1140 430">{svg_iso()}</svg></div>
  <div class="fig plano" role="img" aria-label="Alzado acotado"><svg viewBox="0 0 900 420">
    <defs><marker id="fl" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10z" style="fill:#6aa8ef"/></marker>
    <marker id="ff" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10z" style="fill:var(--ok)"/></marker></defs>
    {svg_alzado()}</svg></div>
  <p class="note" style="font-size:.85rem;color:var(--ink-2)">Alzado en corte por el plano medio, estado cargado (punta apoyada con F₀ = 2 N). El brazo inferior va punteado: son dos tiras laterales, fuera del plano medio. Medidas en mm.</p>
  <div class="fig plano" role="img" aria-label="Planta"><svg viewBox="0 0 640 250">{svg_planta()}</svg></div>
  <div class="fig plano" role="img" aria-label="Desarrollo de la chapa"><svg viewBox="0 0 640 285">{dev}</svg></div>
  <div class="fig plano" role="img" aria-label="Detalle del hoyuelo" style="max-width:420px"><svg viewBox="0 0 420 190" style="min-width:0">{svg_detalle()}</svg></div>
  <div class="prose"><h3>Números</h3></div>
  <div class="tbl"><table><tbody>
    <tr><td>Desarrollo</td><td class="n">{f(Ltot,1)} × {f(B_ALMA,0)} mm, 0,15 mm de espesor</td></tr>
    <tr><td>Rigidez de precarga en la punta · flecha para 2 N</td><td class="n">{f(st["k_vertice_N_mm"],2)} N/mm · {f(st["flecha_vertice_mm"],2)} mm</td></tr>
    <tr><td>Precarga con ±0,3 mm de altura de la carcasa</td><td class="n">{f(2-0.3*st["k_vertice_N_mm"],2)} – 2,00 – {f(2+0.3*st["k_vertice_N_mm"],2)} N</td></tr>
    <tr><td>Tensión máxima (en el amarre del brazo superior) · fluencia CH900</td><td class="n">{f(st["sigma_max_MPa"],0)} · 1300 MPa</td></tr>
    <tr><td>Giro del sensor al precargar · deslizamiento del hoyuelo</td><td class="n">{f(abs(st["giro_sensor_mrad"]),1)} mrad · {f(st["desliz_vertice_mm"],2)} mm</td></tr>
    <tr><td>Frecuencia del filtro (punta apoyada) · pico sin amortiguador</td><td class="n">{f(res["f0_Hz"],0)} Hz · {f(res["pico"],0)}</td></tr>
    <tr><td>Modos siguientes</td><td class="n">{" · ".join(f(x/1000,1) for x in res["modos_Hz"][1:6])} kHz</td></tr>
    <tr><td>Carro (ADXL1004 + extremo rígido del flex)</td><td class="n">{f(res["masa_carro_g"],3)} g</td></tr>
  </tbody></table></div>
  <div class="prose"><h3>Verificación contra la cuña 3D a 15 mm</h3>
    <p>Son los 11 estados de la cuña, con energía del golpe ±10 % y rigidez de los flancos ±30 %. "Libre" es la punta que desliza; "adherido", la punta trabada por rozamiento. C1 se mide en {f(BANDA_C1[0]/1000,1)}–{f(BANDA_C1[1]/1000,0)} kHz. ζ 0,002 es el acero solo y ζ 0,005, por si el adhesivo y el flex suman algo. Los huecos de C1 son ajustada / moderada, moderada / floja y floja / muy floja; el de C2 es muy ajustada / ajustada. En "muy floja con juego" la cuña traquetea y la punta despega en algunos golpes: no cambia la clasificación (el hueco floja / muy floja sigue abierto).</p></div>
  <div class="tbl"><table><thead><tr><th>ζ</th><th>F₀</th><th>Punta</th><th>¿Despega?</th><th>F mín (resto)</th><th>Huecos de C1</th><th>Hueco de C2</th></tr></thead><tbody>{filas}</tbody></table></div>
  <div class="prose"><h3>Umbrales de C1 (ζ 0,002, F₀ 2 N, punta libre o trabada)</h3></div>
  <div class="tbl"><table><thead><tr><th>Entre</th><th>Umbral de C1</th><th>Margen</th></tr></thead><tbody>{umb}</tbody></table></div>
  <div class="prose"><h3>Fabricación</h3></div>
  <ol class="steps">
    <li>Fotograbado del desarrollo en 17-7PH condición C de 0,15 mm, con las ranuras de 0,3 mm alrededor de la lengüeta y la ventana entre las tiras.</li>
    <li>Acuñado del hoyuelo (punzón esférico de R 2 mm, 0,25 mm de alto) en la chapa plana.</li>
    <li>Plegado en un útil, en este orden: P3 (la lengüeta hacia adelante), P2 (las tiras hacia atrás) y P1 (el brazo superior). Radio interior ≥ 0,15 mm.</li>
    <li>Envejecido a CH900 (unos 480 °C, 1 h): sube la fluencia a unos 1300 MPa y fija la forma.</li>
    <li>Pegado del extremo rígido del flex, con el ADXL1004 ya soldado, en la cara exterior del alma (epoxi rígido, capa fina).</li>
    <li>Montaje: un tornillo M1 en cada oreja, sobre los amarres de la carcasa.</li>
    <li>Ensayo de impacto del palpador montado: f₀ y ζ reales, para fijar los umbrales.</li>
  </ol>
</section>
"""
    (RAIZ / "docs/palpador/plano_tira.html").write_text(html)
    return html


if __name__ == "__main__":
    generar()
    print("ok")
