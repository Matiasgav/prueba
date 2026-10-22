"""Planos del palpador de una tira, versión robusta: SVG a escala, con cotas.

Genera docs/palpador/plano_tira.html (sección para insertar en la página):
vista isométrica, alzado con la carcasa y sus topes, planta, desarrollo de la
chapa y detalle de la punta. Toda la geometría sale de cuna3d/palpador_tira.py.
"""

from __future__ import annotations

import json
import math
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cuna3d.palpador_tira import (ANG_NARIZ, ANG_RAMPA, BANDA_C1, B_ALMA, B_CENTRO, B_SUP, B_TIRA,  # noqa: E402
                                  CARCASA, CHIP, H_HOY, L_BRAZO, L_LENG, L_RAMPA, MU, NARIZ, OREJA, PCB, PLANO,
                                  R_HOY, RANURA, T, X_HOY, X_LENG, X_NARIZ, Y_CODO, Y_INF, Y_PCB, Y_SUP, Y_T)

RAIZ = pathlib.Path(__file__).resolve().parent.parent
X_A = L_BRAZO          # plano del alma
XN = X_NARIZ + NARIZ * math.cos(math.radians(ANG_NARIZ))     # fin de la nariz
YN = Y_T + NARIZ * math.sin(math.radians(ANG_NARIZ))
C = CARCASA
CX0, CX1 = -OREJA - 2.0, XN + 2.6                             # carcasa: paredes trasera y delantera (exterior)
PISO0, PISO1 = C["y0"], C["y0"] + C["piso"]                   # piso: caras inferior y superior
TECHO = C["y_techo"]                                          # cara interior del techo
J = C["juego_lateral"]
RAN_X0, RAN_X1 = X_A - T / 2 - 0.15, XN + 0.3                 # ranura del piso (x): el borde trasero es tope
RAN_Z = B_CENTRO / 2 + J                                      # ranura del piso (z, mitad)
X_PCB = X_A + T / 2                                           # cara exterior del alma


def f(x, n=1):
    return f"{x:.{n}f}".replace(".", ",")


# ---------------------------------------------------------------------------
# Piezas como prismas: placa a lo largo de un segmento (x, y) con espesor, o caja
# ---------------------------------------------------------------------------

def placa(p0, p1, z0, z1, cl, t=T):
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = -(y1 - y0) / L * t / 2, (x1 - x0) / L * t / 2
    a, b = (x0 - nx, y0 - ny), (x1 - nx, y1 - ny)
    c, d = (x1 + nx, y1 + ny), (x0 + nx, y0 + ny)
    return ([(*a, z0), (*b, z0), (*c, z0), (*d, z0), (*a, z1), (*b, z1), (*c, z1), (*d, z1)], cl)


def caja(x0, x1, y0, y1, z0, z1, cl):
    return placa((x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2), z0, z1, cl, t=y1 - y0)


def piezas():
    p = []
    p.append(placa((-OREJA, Y_SUP), (X_A, Y_SUP), -B_SUP / 2, B_SUP / 2, "chapa"))
    for s in (-1, 1):
        z0, z1 = sorted((s * (B_ALMA / 2 - B_TIRA), s * B_ALMA / 2))
        p.append(placa((0, Y_INF), (X_A, Y_INF), z0, z1, "chapa"))
    p.append(placa((-OREJA, Y_INF), (0, Y_INF), -B_ALMA / 2, B_ALMA / 2, "chapa"))
    p.append(placa((X_A, Y_SUP), (X_A, Y_INF), -B_ALMA / 2, B_ALMA / 2, "chapa"))
    hc = B_CENTRO / 2
    p.append(placa((X_A, Y_INF), (X_A, Y_CODO), -hc, hc, "leng"))
    p.append(placa((X_A, Y_CODO), (X_LENG, Y_T), -hc, hc, "leng"))
    p.append(placa((X_LENG, Y_T), (X_NARIZ, Y_T), -hc, hc, "leng"))
    p.append(placa((X_NARIZ, Y_T), (XN, YN), -hc, hc, "leng"))
    # extremo rígido del flex (refuerzo de FR4 + flex) y sensor, pegados por fuera del alma
    y0, y1 = Y_PCB, Y_PCB + PCB[0]
    p.append(caja(X_PCB, X_PCB + PCB[2], y0, y1, -PCB[1] / 2, PCB[1] / 2, "fr4"))
    p.append(caja(X_PCB + PCB[2], X_PCB + PCB[2] + 0.1, y0, y1, -PCB[1] / 2, PCB[1] / 2, "flex"))
    p.append(caja(X_PCB + PCB[2] + 0.1, X_PCB + PCB[2] + 0.1 + CHIP, y0 + 0.05, y1 - 0.05, -2.5, 2.5, "chip"))
    return p


# ---------------------------------------------------------------------------
# Vista isométrica (pintor con caras visibles hacia la cámara en +x +y +z)
# ---------------------------------------------------------------------------

S_ISO, OX_ISO, OY_ISO = 15.0, 455.0, 215.0


def iso(x, y, z):
    sx = (x - z) * 0.866
    sy = -(y * 0.816 - (x + z) * 0.408)
    return OX_ISO + S_ISO * sx, OY_ISO + S_ISO * sy


def svg_iso():
    caras = []
    idx = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    for V, cl in piezas():
        cen = [sum(v[k] for v in V) / 8 for k in range(3)]
        for q in idx:
            P = [V[i] for i in q]
            u = [P[1][k] - P[0][k] for k in range(3)]
            w = [P[3][k] - P[0][k] for k in range(3)]
            n = (u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0])
            fc = [sum(p[k] for p in P) / 4 for k in range(3)]
            if sum(n[k] * (fc[k] - cen[k]) for k in range(3)) < 0:   # normal hacia adentro: invertir
                n = tuple(-c for c in n)
            if n[0] + n[1] + n[2] <= 1e-12:
                continue
            m = max(range(3), key=lambda k: abs(n[k]))
            caras.append((sum(fc), cl, "xyz"[m], P))
    caras.sort(key=lambda r: r[0])
    out = []
    w = [iso(-5, 0, -6.5), iso(26, 0, -6.5), iso(26, 0, 6.5), iso(-5, 0, 6.5)]
    out.append('<polygon class="i-cuna" points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in w) + '"/>')
    for d, cl, k, q in caras:
        pts = " ".join(f"{a:.1f},{b:.1f}" for a, b in (iso(*p) for p in q))
        out.append(f'<polygon class="i-{cl} i-{k}" points="{pts}"/>')
    hx, hy = iso(X_HOY, 0.02, 0)
    out.append(f'<ellipse class="i-hoy" cx="{hx:.1f}" cy="{hy:.1f}" rx="{S_ISO*0.95:.1f}" ry="{S_ISO*0.5:.1f}"/>')
    # carcasa en alambre y ranura del piso
    xs, ys, zs = (CX0, CX1), (C["y0"], C["y1"]), (-5.0, 5.0)
    aristas = [((a, b, zs[0]), (a, b, zs[1])) for a in xs for b in ys]
    aristas += [((a, ys[0], c), (a, ys[1], c)) for a in xs for c in zs]
    aristas += [((xs[0], b, c), (xs[1], b, c)) for b in ys for c in zs]
    for p, q in aristas:
        (a1, b1), (a2, b2) = iso(*p), iso(*q)
        out.append(f'<line class="i-carcasa" x1="{a1:.1f}" y1="{b1:.1f}" x2="{a2:.1f}" y2="{b2:.1f}"/>')
    r = [iso(RAN_X0, PISO0, -RAN_Z), iso(RAN_X1, PISO0, -RAN_Z), iso(RAN_X1, PISO0, RAN_Z), iso(RAN_X0, PISO0, RAN_Z)]
    out.append('<polygon class="i-ranura" points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in r) + '"/>')

    def rot(p, tx, ty, txt, cls="lbl"):
        a, b = iso(*p)
        return (f'<line class="guia" x1="{a:.1f}" y1="{b:.1f}" x2="{tx:.1f}" y2="{ty:.1f}"/>'
                f'<text class="{cls}" x="{tx + (4 if tx > a else -4):.1f}" y="{ty + 4:.1f}" text-anchor="{"start" if tx > a else "end"}">{txt}</text>')
    out += [rot((-1.2, Y_SUP + 0.1, 0), 275, 40, "oreja superior (tornillo M1)"),
            rot((7, Y_SUP + 0.1, 0), 275, 95, "brazo superior · 3 × 13 mm"),
            rot((7, Y_INF, 2.3), 275, 300, "brazo inferior · 2 tiras de 1,5 mm"),
            rot((-3, 0, 4), 275, 370, "cuña", "lbl-w"),
            rot((X_A, Y_SUP - 1, -2.8), 875, 40, "alma 6 mm"),
            rot((X_PCB + 2.3, 6.5, 1.0), 875, 100, "flex con ADXL1004, pegado al alma"),
            rot((XN - 0.2, YN, 0), 875, 270, "punta: rampa 35° · hoyuelo R 2 · nariz 30°"),
            rot((RAN_X1, PISO0, RAN_Z), 875, 320, "ranura del piso (tope lateral)"),
            rot((CX1, C["y0"], -5.0), 875, 370, "carcasa 10 × 10 mm (contorno)")]
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Alzado (x-y) con la carcasa y los topes
# ---------------------------------------------------------------------------

def svg_alzado():
    s, ox, oy = 24.0, 170.0, 300.0
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

    def cota_v(x, y0, y1, t, lado=1, cl="ct"):
        line(x, y0, x, y1, "cota"); line(x - 0.18, y0, x + 0.18, y0, "cota"); line(x - 0.18, y1, x + 0.18, y1, "cota")
        text(x + 0.3 * lado, (y0 + y1) / 2 - 0.12, t, cl, "start" if lado > 0 else "end")

    rect(-6.5, -1.6, CX1 + 2.5, 0, "cuna"); text(-6.2, -1.05, "cuña de G11", "lbl-w")
    # carcasa en corte: paredes, techo y piso de 0,5 con la ranura
    pw = 1.0
    o.append(f'<path class="carcasa" d="M{X(CX0)} {Y(PISO0)} L{X(RAN_X0)} {Y(PISO0)} L{X(RAN_X0)} {Y(PISO1)} '
             f'L{X(CX0+pw)} {Y(PISO1)} L{X(CX0+pw)} {Y(TECHO)} L{X(CX1-pw)} {Y(TECHO)} L{X(CX1-pw)} {Y(PISO1)} '
             f'L{X(RAN_X1)} {Y(PISO1)} L{X(RAN_X1)} {Y(PISO0)} L{X(CX1)} {Y(PISO0)} L{X(CX1)} {Y(C["y1"])} '
             f'L{X(CX0)} {Y(C["y1"])} Z"/>')
    # amarres (orejas apretadas entre bloque y tapa)
    rect(-OREJA - 0.3, Y_SUP + T / 2, 0, TECHO, "amarre"); rect(-OREJA - 0.3, Y_SUP - 0.7, 0, Y_SUP - T / 2, "amarre")
    rect(-OREJA - 0.3, PISO1, 0, Y_INF - T / 2, "amarre"); rect(-OREJA - 0.3, Y_INF + T / 2, 0, Y_INF + 0.7, "amarre")
    text(-OREJA / 2, Y_INF + 1.15, "amarres", "ct", "middle")
    # chapa (línea media gruesa)
    o.append(f'<path class="chapa" d="M{X(-OREJA)} {Y(Y_SUP)} L{X(X_A-0.2)} {Y(Y_SUP)} Q{X(X_A)} {Y(Y_SUP)} {X(X_A)} {Y(Y_SUP-0.2)} '
             f'L{X(X_A)} {Y(Y_CODO)} L{X(X_LENG)} {Y(Y_T)} L{X(X_NARIZ)} {Y(Y_T)} L{X(XN)} {Y(YN)}"/>')
    o.append(f'<path class="chapa2" d="M{X(-OREJA)} {Y(Y_INF)} L{X(X_A-0.2)} {Y(Y_INF)} Q{X(X_A)} {Y(Y_INF)} {X(X_A)} {Y(Y_INF+0.2)}"/>')
    a = math.sqrt(2 * R_HOY * H_HOY - H_HOY ** 2)
    o.append(f'<path class="hoy" d="M{X(X_HOY-a)} {Y(Y_T)} Q{X(X_HOY)} {Y(Y_T-2*H_HOY)} {X(X_HOY+a)} {Y(Y_T)}"/>')
    # sensor
    y0, y1 = Y_PCB, Y_PCB + PCB[0]
    rect(X_PCB, y0, X_PCB + PCB[2], y1, "fr4"); rect(X_PCB + PCB[2], y0, X_PCB + PCB[2] + 0.1, y1, "flex")
    xc0 = X_PCB + PCB[2] + 0.1
    rect(xc0, y0 + 0.05, xc0 + CHIP, y1 - 0.05, "chip")
    o.append(f'<path class="eje" d="M{X(xc0+CHIP/2)} {Y(y0+0.8)} L{X(xc0+CHIP/2)} {Y(y1-1.2)}" marker-end="url(#fl)"/>')
    o.append(f'<path class="flexl" d="M{X(X_PCB+1.2)} {Y(y1)} C{X(X_PCB+1.2)} {Y(y1+1.4)} {X(CX1-2.5)} {Y(y1+0.6)} {X(CX1-pw)} {Y(y1+1.2)}"/>')
    # rótulos
    text(1.0, Y_SUP - 0.45, "brazo superior 0,15 × 3 × 13", "lbl-a")
    text(1.0, Y_INF + 0.35, "brazo inferior 2 × (0,15 × 1,5 × 13)", "lbl-a")
    text(xc0 + CHIP + 0.35, y0 + 2.9, "ADXL1004", "lbl"); text(xc0 + CHIP + 0.35, y0 + 2.3, "eje sensible ↑", "ct")
    text(CX1 - 2.4, y1 + 1.6, "flex", "lbl-f", "end")
    text(XN + 0.5, 0.35, "nariz 30°", "lbl-l")
    text(X_HOY + 0.35, -0.6, "hoyuelo R 2 · h 0,25", "ct")
    text(X_A - 0.35, 0.4, "rampa 35°", "lbl-l", "end")
    # cotas
    cota_h(0, X_A, Y_SUP - 1.3, f(L_BRAZO, 0), dy=-0.55)
    cota_v(-5.6, Y_INF, Y_SUP, f(Y_SUP - Y_INF, 1), -1)
    cota_v(-5.6, 0, Y_INF, f(Y_INF, 1), -1)
    cota_v(CX1 + 1.3, 0, C["y0"], f(C["y0"], 1), 1)
    cota_v(CX1 + 1.3, C["y0"], C["y1"], f(C["y1"] - C["y0"], 0), 1)
    # topes
    cota_v(X_A - 4.0, Y_SUP + T / 2, TECHO, f"tope de retracción {f(TECHO - Y_SUP - T/2, 1)}", -1, "ct-r")
    cota_v(X_A - 1.0, PISO1, Y_INF - T / 2, f"tope de caída {f(Y_INF - T/2 - PISO1, 1)}", -1, "ct-r")
    o.append(f'<path class="fuerza" d="M{X(X_HOY)} {Y(-1.45)} L{X(X_HOY)} {Y(-0.08)}" marker-end="url(#ff)"/>')
    text(X_HOY + 0.3, -1.3, "F₀ 2 N", "lbl-v")
    return "\n".join(o)


def svg_planta():
    s, ox, oy = 22.0, 85.0, 135.0
    X = lambda x: ox + s * x
    Z = lambda z: oy + s * z
    o = []

    def rect(x0, z0, x1, z1, cl):
        o.append(f'<rect class="{cl}" x="{X(x0):.1f}" y="{Z(z0):.1f}" width="{s*(x1-x0):.1f}" height="{s*(z1-z0):.1f}"/>')

    def text(x, z, t, cl="lbl", a="start"):
        o.append(f'<text class="{cl}" x="{X(x):.1f}" y="{Z(z):.1f}" text-anchor="{a}">{t}</text>')
    rect(RAN_X0, -RAN_Z, RAN_X1, RAN_Z, "ranura-pl")
    for sg in (-1, 1):
        z0, z1 = sorted((sg * (B_ALMA / 2 - B_TIRA), sg * B_ALMA / 2))
        rect(0, z0, X_A, z1, "oculto")
    rect(-OREJA, -B_ALMA / 2, 0, B_ALMA / 2, "oculto")
    rect(-OREJA, -B_SUP / 2, X_A, B_SUP / 2, "pl-chapa")
    rect(X_A - T / 2, -B_ALMA / 2, X_A + T / 2, B_ALMA / 2, "pl-chapa")
    rect(X_A, -B_CENTRO / 2, XN, B_CENTRO / 2, "pl-leng")
    xc0 = X_PCB + PCB[2] + 0.1
    rect(X_PCB, -PCB[1] / 2, xc0 + CHIP, PCB[1] / 2, "chip-pl")
    o.append(f'<circle class="hoy-pl" cx="{X(X_HOY):.1f}" cy="{Z(0):.1f}" r="{s*0.97:.1f}"/>')
    for x in (-OREJA / 2,):
        o.append(f'<circle class="agujero" cx="{X(x):.1f}" cy="{Z(0):.1f}" r="{s*0.55:.1f}"/>')

    def cota_z(x, z0, z1, t):
        o.append(f'<line class="cota" x1="{X(x):.1f}" y1="{Z(z0):.1f}" x2="{X(x):.1f}" y2="{Z(z1):.1f}"/>')
        o.append(f'<text class="ct" x="{X(x)+5:.1f}" y="{(Z(z0)+Z(z1))/2+4:.1f}">{t}</text>')
    cota_z(7.5, -B_SUP / 2, B_SUP / 2, "3")
    cota_z(12.5, B_ALMA / 2 - B_TIRA, B_ALMA / 2, "1,5")
    cota_z(RAN_X1 + 0.8, -RAN_Z, RAN_Z, f"ranura {f(2*RAN_Z, 1)}")
    cota_z(X_A - 1.3, -B_ALMA / 2, B_ALMA / 2, "6")
    text(-OREJA, -3.9, "planta · brazo inferior punteado (tiras laterales) · ranura del piso en rojo", "ct")
    text(X_PCB + 1.2, 3.85, "sensor (encima)", "ct", "middle")
    return "\n".join(o)


# ---------------------------------------------------------------------------
# Desarrollo de la chapa
# ---------------------------------------------------------------------------

def svg_desarrollo():
    s, ox, oy = 12.5, 22.0, 120.0
    U = lambda u: ox + s * u
    V = lambda v: oy + s * v
    u0 = 0.0
    u1 = u0 + OREJA                 # fin oreja superior
    u2 = u1 + L_BRAZO               # P1 (brazo -> alma)
    u3 = u2 + (Y_SUP - Y_INF)       # P2 (tiras, atrás)
    uc = u3 + (Y_INF - Y_CODO)      # P3 (comienzo de la rampa)
    u4 = uc + L_RAMPA               # P4 (rampa -> lengüeta)
    uh = u4 + L_LENG                # hoyuelo
    u5 = uh + PLANO                 # P5 (nariz)
    u6 = u5 + NARIZ                 # fin de la nariz
    u7 = u3 + L_BRAZO               # fin de las tiras
    u8 = u7 + OREJA                 # fin oreja inferior
    o = []

    def poly(pts, cl):
        o.append(f'<polygon class="{cl}" points="' + " ".join(f"{U(a):.1f},{V(b):.1f}" for a, b in pts) + '"/>')
    hs, ha, ht, hc = B_SUP / 2, B_ALMA / 2, B_ALMA / 2 - B_TIRA, B_CENTRO / 2
    poly([(u0, -hs), (u2, -hs), (u2, -ha), (u8, -ha), (u8, ha), (u2, ha), (u2, hs), (u0, hs)], "dev")
    poly([(u3, -ht), (u6, -ht), (u6, -hc), (u3, -hc)], "hueco")
    poly([(u3, hc), (u6, hc), (u6, ht), (u3, ht)], "hueco")
    poly([(u6, -ht), (u7, -ht), (u7, ht), (u6, ht)], "hueco")

    def pl(u, v0, v1):
        o.append(f'<line class="pliegue" x1="{U(u):.1f}" y1="{V(v0):.1f}" x2="{U(u):.1f}" y2="{V(v1):.1f}"/>')

    def rot(u, v, t, a="middle"):
        o.append(f'<text class="ct-r" x="{U(u):.1f}" y="{V(v):.1f}" text-anchor="{a}">{t}</text>')
    pl(u2, -hs - 0.3, hs + 0.3); rot(u2 - 0.2, -hs - 0.6, "P1 · 90°", "end")
    pl(u3, -ha - 0.2, -ht); pl(u3, ht, ha + 0.2); rot(u3, ha + 1.1, "P2 · 90° (tiras, atrás)")
    pl(uc, -hc - 0.15, hc + 0.15); pl(u4, -hc - 0.15, hc + 0.15); pl(u5, -hc - 0.15, hc + 0.15)
    rot(u3 - 0.3, -ha - 0.7, f"P3 · {90-ANG_RAMPA:.0f}° · P4 · {ANG_RAMPA:.0f}° · P5 · {ANG_NARIZ:.0f}° (punta)", "start")
    for u in (u0 + OREJA / 2, u7 + OREJA / 2):
        o.append(f'<circle class="agujero" cx="{U(u):.1f}" cy="{V(0):.1f}" r="{s*0.55:.1f}"/>')
    o.append(f'<circle class="hoy-pl" cx="{U(uh):.1f}" cy="{V(0):.1f}" r="{s*0.97:.1f}"/>')

    def txt(u, v, t, cl="ct"):
        o.append(f'<text class="{cl}" x="{U(u):.1f}" y="{V(v):.1f}" text-anchor="middle">{t}</text>')
    txt((u1 + u2) / 2, 0.25, "brazo superior")
    txt((u2 + u3) / 2, 0.25, "alma")
    txt((u6 + u7) / 2 + 1.5, -ht - 0.55, "tira lateral")
    txt((u6 + u7) / 2 + 1.5, ht + 0.95, "tira lateral")
    o.append(f'<text class="ct-l" x="{U(u6 + 0.3):.1f}" y="{V(0.25):.1f}">← punta</text>')

    def cota(ua, ub, v, t):
        o.append(f'<line class="cota" x1="{U(ua):.1f}" y1="{V(v):.1f}" x2="{U(ub):.1f}" y2="{V(v):.1f}"/>')
        for u in (ua, ub):
            o.append(f'<line class="cota" x1="{U(u):.1f}" y1="{V(v)-4:.1f}" x2="{U(u):.1f}" y2="{V(v)+4:.1f}"/>')
        o.append(f'<text class="ct" x="{(U(ua)+U(ub))/2:.1f}" y="{V(v)-4:.1f}" text-anchor="middle">{t}</text>')
    vb = ha + 2.4
    filas = {(uc, u4): 1.3, (u4, uh): 2.6, (uh, u6): 1.3, (u3, u7): 3.9}
    for ua, ub in ((u0, u1), (u1, u2), (u2, u3), (u3, uc), (uc, u4), (u4, uh), (uh, u6), (u3, u7), (u7, u8)):
        cota(ua, ub, vb + filas.get((ua, ub), 0.0), f(ub - ua, 2 if abs((ub - ua) - round(ub - ua)) > 1e-6 else 0))
    cota(u0, u8, vb + 5.2, f"total {f(u8 - u0, 1)}")
    o.append(f'<text class="tb" x="{U(0):.1f}" y="{V(-ha-2.2):.1f}">Desarrollo · 17-7PH cond. C · 0,15 mm · fotograbado · cotas en la línea media</text>')
    return "\n".join(o), (u8 - u0)


def svg_detalle():
    """Punta a 8:1: pierna, plano con el hoyuelo y nariz, sobre la cuña y dentro de la ranura del piso."""
    s, ox, oy = 52.0, 30.0, 172.0
    X = lambda x: ox + s * (x - (X_A - 1.6))
    Y = lambda y: oy - s * y
    o = []
    o.append(f'<rect class="cuna" x="{X(X_A-1.6):.1f}" y="{Y(0):.1f}" width="{s*(XN-X_A+2.4):.1f}" height="{s*0.4:.1f}"/>')
    # piso de la carcasa con la ranura
    o.append(f'<rect class="carcasa" x="{X(X_A-1.6):.1f}" y="{Y(PISO1):.1f}" width="{s*(RAN_X0-X_A+1.6):.1f}" height="{s*C["piso"]:.1f}"/>')
    o.append(f'<rect class="carcasa" x="{X(RAN_X1):.1f}" y="{Y(PISO1):.1f}" width="{s*0.5:.1f}" height="{s*C["piso"]:.1f}"/>')
    o.append(f'<path class="chapa-l" d="M{X(X_A)} {Y(Y_INF+0.4)} L{X(X_A)} {Y(Y_CODO)} L{X(X_LENG)} {Y(Y_T)} L{X(X_NARIZ)} {Y(Y_T)} L{X(XN)} {Y(YN)}"/>')
    a = math.sqrt(2 * R_HOY * H_HOY - H_HOY ** 2)
    o.append(f'<path class="hoy" d="M{X(X_HOY-a)} {Y(Y_T)} Q{X(X_HOY)} {Y(Y_T-2*H_HOY)} {X(X_HOY+a)} {Y(Y_T)}"/>')
    o.append(f'<text class="ct" x="{X(X_A-1.5):.1f}" y="{Y(2.75):.1f}">esc. 8:1 · las rampas suben la punta ante un escalón en los dos sentidos</text>')
    o.append(f'<text class="ct-l" x="{X(X_A-0.1):.1f}" y="{Y(0.55):.1f}" text-anchor="end">rampa 35°</text>')
    o.append(f'<text class="ct-l" x="{X(X_NARIZ-0.1):.1f}" y="{Y(YN+0.45):.1f}" text-anchor="end">nariz 30°</text>')
    o.append(f'<text class="ct" x="{X(X_HOY):.1f}" y="{Y(-0.3):.1f}" text-anchor="middle">hoyuelo R 2 · h 0,25</text>')
    o.append(f'<text class="ct" x="{X(X_A-1.5):.1f}" y="{Y(PISO1)-5:.1f}">piso 0,5</text>')
    return "\n".join(o)


ESTILO = """
.plano svg text{font-family:var(--f-mono)}
.i-cuna{fill:var(--warnbg);stroke:var(--wedge);stroke-width:.8}
.i-chapa.i-y{fill:#9db8d6}.i-chapa.i-x{fill:#6f93bd}.i-chapa.i-z{fill:#4f76a3}
.i-leng.i-y{fill:#8fd0ad}.i-leng.i-x{fill:#5fb487}.i-leng.i-z{fill:#3f9468}
.i-fr4{fill:#7a9a4a}.i-flex{fill:#c98a1a}.i-chip{fill:#232b33}
.i-x,.i-y,.i-z{stroke:#1c2a38;stroke-width:.35}
.i-hoy{fill:none;stroke:var(--ok);stroke-width:1.2;stroke-dasharray:3 2}
.i-carcasa{stroke:var(--ink-2);stroke-width:.7;stroke-dasharray:5 4}
.i-ranura{fill:none;stroke:var(--alarm);stroke-width:1}
.guia{stroke:var(--ink-2);stroke-width:.7}
.lbl{font-size:12px;fill:var(--ink)}.lbl-w{font-size:12px;fill:var(--wedge)}.ct{font-size:11px;fill:var(--ink-2)}
.ct-r{font-size:10.5px;fill:var(--alarm)}.ct-l{font-size:11px;fill:var(--ok)}.tb{font-size:12px;fill:var(--ink)}
.lbl-a{font-size:12px;fill:var(--probe)}.lbl-l{font-size:12px;fill:var(--ok)}
.lbl-f{font-size:11px;fill:#c98a1a}.lbl-v{font-size:12px;fill:var(--ok)}
.cuna{fill:var(--warnbg);stroke:var(--wedge);stroke-width:1}
.carcasa{fill:var(--rule);stroke:var(--ink-2);stroke-width:1.1}
.amarre{fill:var(--paper);stroke:var(--ink-2);stroke-width:.8}
.chapa{fill:none;stroke:var(--probe);stroke-width:3;stroke-linecap:round;stroke-linejoin:round}
.chapa2{fill:none;stroke:var(--probe);stroke-width:3;stroke-linecap:round;stroke-dasharray:9 3}
.chapa-l{fill:none;stroke:var(--ok);stroke-width:7.8;stroke-linejoin:round;stroke-opacity:.7}
.hoy{fill:none;stroke:var(--ok);stroke-width:3}
.fr4{fill:#7a9a4a}.flex{fill:#c98a1a}.chip{fill:#232b33}.chip-pl{fill:#232b3326;stroke:#232b33;stroke-width:1.2;stroke-dasharray:5 3}
.flexl{fill:none;stroke:#c98a1a;stroke-width:2.4}.eje{stroke:#6aa8ef;stroke-width:2}
.cota{stroke:var(--ink-2);stroke-width:.8}.fuerza{stroke:var(--ok);stroke-width:2}
.oculto{fill:none;stroke:var(--probe);stroke-width:1;stroke-dasharray:4 3}
.ranura-pl{fill:none;stroke:var(--alarm);stroke-width:1.2;stroke-dasharray:6 3}
.pl-chapa{fill:#9db8d6aa;stroke:var(--probe);stroke-width:1.2}.pl-leng{fill:#8fd0adaa;stroke:var(--ok);stroke-width:1.2}
.hoy-pl{fill:none;stroke:var(--ok);stroke-width:1.2}.agujero{fill:var(--sheet);stroke:var(--ink-2)}
.dev{fill:var(--band);stroke:var(--probe);stroke-width:1.4}.hueco{fill:var(--sheet);stroke:var(--probe);stroke-width:1}
.pliegue{stroke:var(--alarm);stroke-width:1.1;stroke-dasharray:6 3}
"""


def generar():
    res = json.loads((RAIZ / "results/cuna3d/palpador_tira.json").read_text())
    dev, Ltot = svg_desarrollo()
    st, rb = res["estatica"], res["robustez"]
    NOMR = {"coulomb": "real, μ {mu}", "libre": "sin rozamiento (cota)", "adherido": "trabada (cota)"}
    filas = ""
    for r in res["verificacion"]:
        d = sorted({x.split("·")[0] for x in r["despega"]})
        rz = NOMR[r["tg"]].format(mu=f(r["mu"], 2))
        filas += (f'<tr class="{"rec" if (r["tg"], r["F0"], r["mu"]) == ("coulomb", 2.0, MU[0]) else ""}"><td>{rz}</td><td class="n">{f(r["F0"],1)} N</td>'
                  f'<td>{"no" if not d else ", ".join(x.replace("_", " ") for x in d)}</td>'
                  f'<td>{"no" if not r["satura_en"] else ", ".join(x.replace("_", " ") for x in r["satura_en"])}</td>'
                  f'<td class="n">{f(r["Fc_min_sin_muy_floja"],2)} N</td>'
                  f'<td class="n">{" · ".join(f(g,2) for g in r["gaps_C1"])}</td><td class="n">{r["gap_C2_Hz"]:.0f} Hz</td></tr>')
    NOM = {"ajustada/moderada": "ajustada | moderada", "moderada/floja": "moderada | floja", "floja/muy_floja_juego": "floja | muy floja"}
    umb = "".join(f'<tr><td>{NOM[u["entre"]]}</td><td class="n">{f(u["umbral"],2)}</td><td class="n">± {f(u["hueco"]/2,2)}</td></tr>'
                  for u in res["umbrales_C1"])
    fp, fs_ = rb["F_horizontal_pandeo_N"], rb["F_horizontal_para_subir_N"]
    html = f"""<section id="tira">
  <style>{ESTILO}</style>
  <div class="prose">
    <span class="eyebrow">10 · Diseño recomendado: una tira plegada, protegida por la carcasa</span>
    <h2>C plegada con punta liviana y rampas</h2>
    <p><b>Piezas: dos, más dos tornillos.</b> La chapa (17-7PH de 0,15 mm, fotograbada, con el hoyuelo acuñado, cinco pliegues en un útil y envejecida) y el flex con el ADXL1004 soldado en su extremo rígido. Sin amortiguador ni rigidizador. La carcasa, que ya existe, protege la chapa con topes: no se agregan piezas.</p>
    <p><b>Corrección.</b> La versión anterior de esta sección modelaba la lengüeta terminando justo en el centro del hoyuelo. La chapa real tiene que seguir ~1 mm para que entre la base del hoyuelo, y con esa masa en la punta se perdía la separación entre ajustada y moderada. Además, el modelo ahora tiene rozamiento de Coulomb en la punta (traba hasta μ·F y desliza), que es el caso real. Con μ 0,15–0,3 la punta prácticamente no desliza.</p>
    <p><b>Por qué no se puede simplificar más.</b></p>
    <ul>
      <li><b>Con un solo brazo</b>, el carro gira 330 mrad al precargar y aparece un modo de cabeceo a 1,5 kHz, dentro de la banda de C1.</li>
      <li><b>Sin punta separada</b> (sensor rígido contra la cuña), todo lo que se mueve con la punta tendría que pesar menos de 25 mg para no despegar. El ADXL1004 solo ya pesa hasta 200 mg.</li>
      <li><b>Sostener el carro con espuma</b> lo deja inclinarse ~0,6 rad con el rozamiento de la punta mientras el robot avanza.</li>
      <li><b>Chapa más gruesa con brazos más largos</b> (0,20 × 18 mm): el primer modo de los brazos baja a 2,8 kHz, dentro de la banda, y la clasificación pasa a depender de ±0,1 mm de lengüeta.</li>
      <li><b>Lengüeta inclinada</b> como rampa: con la punta trabada se estira a lo largo en vez de flexionar, el filtro deja de filtrar y el sensor satura.</li>
    </ul>
    <p><b>Robustez: la carcasa limita todo y la punta tiene rampas.</b></p>
    <ul>
      <li><b>Rampas.</b> Atrás, una rampa a 35° (sólo el tramo que asoma bajo el piso; la lengüeta, que es el filtro, sigue horizontal); adelante, la nariz a 30°. Ante un escalón la punta sube: hacen falta {f(fs_["rampa trasera 35°"],1)} N y {f(fs_["nariz 30°"],1)} N de fuerza horizontal con la punta retraída al tope, y los brazos recién pandean (elásticamente) con {f(fp["empuje hacia atrás"],1)} N hacia atrás y {f(fp["empuje hacia adelante"],0)} N hacia adelante.</li>
      <li><b>Tope de retracción (techo).</b> La punta sobresale {f(rb["asoma_mm"],1)} mm y puede subir {f(rb["retraccion_mm"],1)} mm, hasta quedar al ras del piso. En el tope: brazos a {f(rb["sigma_tope_techo_MPa"],0)} MPa y lengüeta a {f(rb["sigma_lengueta_tope_MPa"],0)} MPa. Por eso el envejecido CH900 es obligatorio: fluencia típica ~{f(rb["fluencia_CH900_MPa"],0)} MPa, contra ~{f(rb["fluencia_C_MPa"],0)} MPa sin tratar (confirmar con el certificado del material).</li>
      <li><b>Tope de caída (piso).</b> Sin cuña debajo, el brazo inferior y el sensor se apoyan en el piso: la punta baja como mucho {f(rb["caida_max_mm"],1)} mm.</li>
      <li><b>Tope lateral y trasero (ranura del piso).</b> El tramo vertical y la punta pasan por una ranura con {f(C["juego_lateral"],1)} mm de juego por lado. Un tirón de costado lo toma la carcasa (la punta recién fluye con ~{f(rb["F_lateral_fluencia_N"],0)} N), y un empujón hacia atrás apoya el tramo vertical en el borde de la ranura.</li>
      <li><b>Lo que no cubre.</b> Un escalón más alto que la nariz (~0,5 mm) y más bajo que el piso (1 mm) que venga de frente pega en el canto de la nariz. Ahí la fuerza pasa a la ranura, pero un enganche muy fuerte puede doblar la punta. La chapa es barata y se cambia con dos tornillos.</li>
    </ul>
    <p><b>Sin amortiguador.</b> La resonancia del filtro (~{f(res["f0_Hz"],0)} Hz) queda sin amortiguar y no hace falta: C1 se mide en {f(BANDA_C1[0]/1000,1)}–{f(BANDA_C1[1]/1000,0)} kHz, por encima de ella, y C2 mira 12–24 kHz.</p>
  </div>
  <div class="fig plano" role="img" aria-label="Vista isométrica del palpador"><svg viewBox="0 0 1240 400">{svg_iso()}</svg></div>
  <div class="fig plano" role="img" aria-label="Alzado acotado con la carcasa y los topes"><svg viewBox="0 0 960 360">
    <defs><marker id="fl" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10z" style="fill:#6aa8ef"/></marker>
    <marker id="ff" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10z" style="fill:var(--ok)"/></marker></defs>
    {svg_alzado()}</svg></div>
  <p class="note" style="font-size:.85rem;color:var(--ink-2)">Alzado en corte por el plano medio, estado cargado (punta apoyada con F₀ = 2 N, piso a 1,0 mm de la cuña). El brazo inferior va punteado: son dos tiras laterales, fuera del plano medio. Topes en rojo. Medidas en mm.</p>
  <div class="fig plano" role="img" aria-label="Planta"><svg viewBox="0 0 720 240">{svg_planta()}</svg></div>
  <div class="fig plano" role="img" aria-label="Desarrollo de la chapa"><svg viewBox="0 0 660 300">{dev}</svg></div>
  <div class="fig plano" role="img" aria-label="Detalle de la punta" style="max-width:560px"><svg viewBox="0 0 560 215" style="min-width:0">{svg_detalle()}</svg></div>
  <div class="prose"><h3>Números</h3></div>
  <div class="tbl"><table><tbody>
    <tr><td>Desarrollo</td><td class="n">{f(Ltot,1)} × {f(B_ALMA,0)} mm, 0,15 mm de espesor</td></tr>
    <tr><td>Rigidez de precarga en la punta · flecha para 2 N</td><td class="n">{f(st["k_vertice_N_mm"],2)} N/mm · {f(st["flecha_vertice_mm"],2)} mm</td></tr>
    <tr><td>Precarga con ±0,3 mm de altura de la carcasa</td><td class="n">{" – ".join(f(x,2) for x in rb["F0_por_altura_N"])} N</td></tr>
    <tr><td>Tensión máxima: en precarga · en el tope de retracción · fluencia CH900</td><td class="n">{f(rb["sigma_precarga_MPa"],0)} · {f(rb["sigma_tope_techo_MPa"],0)} · ~{f(rb["fluencia_CH900_MPa"],0)} MPa</td></tr>
    <tr><td>Giro del sensor al precargar · deslizamiento del hoyuelo</td><td class="n">{f(abs(st["giro_sensor_mrad"]),1)} mrad · {f(st["desliz_vertice_mm"],2)} mm</td></tr>
    <tr><td>Frecuencia del filtro (punta apoyada) · pico sin amortiguador</td><td class="n">{f(res["f0_Hz"],0)} Hz · {f(res["pico"],0)}</td></tr>
    <tr><td>Modos siguientes</td><td class="n">{" · ".join(f(x/1000,1) for x in res["modos_Hz"][1:6])} kHz</td></tr>
    <tr><td>Carro (ADXL1004 + extremo rígido del flex)</td><td class="n">{f(res["masa_carro_g"],3)} g</td></tr>
  </tbody></table></div>
  <div class="prose"><h3>Verificación contra la cuña 3D a 15 mm</h3>
    <p>Son los 11 estados de la cuña, con energía del golpe ±10 % y rigidez de los flancos ±30 %, ζ 0,002 (acero solo). El rozamiento real es Coulomb con μ 0,3 (nominal) y 0,15 (superficie lubricada o barnizada); "sin rozamiento" y "trabada" son las dos cotas extremas. C1 se mide en {f(BANDA_C1[0]/1000,1)}–{f(BANDA_C1[1]/1000,0)} kHz. Los huecos de C1 son ajustada / moderada, moderada / floja y floja / muy floja; el de C2 es muy ajustada / ajustada (C2 necesita la calibración por generador).</p></div>
  <div class="tbl"><table><thead><tr><th>Rozamiento</th><th>F₀</th><th>¿Despega?</th><th>¿Satura?</th><th>F mín (resto)</th><th>Huecos de C1</th><th>Hueco de C2</th></tr></thead><tbody>{filas}</tbody></table></div>
  <div class="prose"><h3>Umbrales de C1 (F₀ 2 N, μ entre 0,15 y 0,3)</h3></div>
  <div class="tbl"><table><thead><tr><th>Entre</th><th>Umbral de C1</th><th>Margen</th></tr></thead><tbody>{umb}</tbody></table></div>
  <div class="prose"><h3>Fabricación</h3></div>
  <ol class="steps">
    <li>Fotograbado del desarrollo en 17-7PH condición C de 0,15 mm, con las ranuras de {f(RANURA,1)} mm alrededor de la punta, la ventana entre las tiras y las esquinas del extremo de la punta redondeadas siguiendo el hoyuelo.</li>
    <li>Acuñado del hoyuelo (punzón esférico de R 2 mm, 0,25 mm de alto) en la chapa plana.</li>
    <li>Plegado en un útil, en este orden: P5 (nariz), P4 y P3 (rampa), P2 (las tiras hacia atrás) y P1 (el brazo superior). Radio interior ≥ 0,15 mm.</li>
    <li>Envejecido a CH900 (unos 480 °C, 1 h), obligatorio: la tensión en el tope de retracción lo necesita.</li>
    <li>Pegado del extremo rígido del flex, con el ADXL1004 ya soldado, en la cara exterior del alma (epoxi rígido, capa fina).</li>
    <li>Montaje: un tornillo M1 en cada oreja, sobre los amarres de la carcasa. La carcasa lleva el piso de 0,5 mm con la ranura de {f(2*RAN_Z,1)} mm y el techo a {f(rb["retraccion_mm"],1)} mm del brazo superior.</li>
    <li>Ensayo de impacto del palpador montado: f₀ y ζ reales, para fijar los umbrales.</li>
  </ol>
</section>
"""
    (RAIZ / "docs/palpador/plano_tira.html").write_text(html)
    return html


if __name__ == "__main__":
    generar()
    print("ok")
