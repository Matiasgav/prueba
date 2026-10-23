"""Planos del palpador con la PCB como carro: SVG a escala, con cotas.

Genera docs/palpador/plano_pcb.html (sección para insertar en la página):
vista isométrica, alzado con la carcasa y sus topes, planta, piezas (láminas,
tira de la punta y las dos PCB) y detalle de las uniones. La geometría sale de
cuna3d/palpador_pcb.py.
"""

from __future__ import annotations

import json
import math
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cuna3d.palpador_pcb import (ANG_NARIZ, ANG_RAMPA, BANDA_C1, B_LENG, B_PCB, B_TIRA, CARCASA, H_HOY, L_BRAZO,  # noqa: E402
                                 L_LENG, L_RAMPA, MU, NARIZ, PLANO, R_HOY, T, T_PCB, X_LENG, X_PUNTA, Y_CODO, Y_INF,
                                 Y_CHIP0, Y_PCB0, Y_PCB1, Y_SOLD, Y_SUP, Y_T, Z_TIRA, geometria)
from cuna3d.plano_tira import ESTILO as ESTILO_TIRA, caja, f, placa  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
X_HOY, X_FIN, XN, YN = geometria()
C = CARCASA
X_A = L_BRAZO                                   # cara interior de la PCB del carro
X_B = L_BRAZO + T_PCB                           # cara exterior
PISO0, PISO1, TECHO = C["y0"], C["y0"] + C["piso"], C["y_techo"]
CX0, CX1 = -T_PCB - 1.0, XN + 2.6
RAN_X0, RAN_X1 = X_PUNTA - T / 2 - 0.15, XN + 0.3
RAN_Z = B_LENG / 2 + C["juego_lateral"]
ZT = [(-Z_TIRA - B_TIRA, -Z_TIRA), (Z_TIRA, Z_TIRA + B_TIRA)]   # las dos tiras de cada nivel (z)
CHIP = (5.0, 5.0, 1.8)                           # y, z, x
Y_CHIP1 = Y_CHIP0 + CHIP[0]


def piezas():
    p = []
    p.append(caja(-T_PCB, 0, PISO1, TECHO, -B_PCB / 2, B_PCB / 2, "pcbf"))
    for y in (Y_SUP, Y_INF):
        for z0, z1 in ZT:
            p.append(placa((-T_PCB, y), (X_B, y), z0, z1, "chapa"))
    p.append(caja(X_A, X_B, Y_PCB0, Y_PCB1, -B_PCB / 2, B_PCB / 2, "pcb"))
    p.append(caja(X_B, X_B + CHIP[2], Y_CHIP0, Y_CHIP1, -CHIP[1] / 2, CHIP[1] / 2, "chip"))
    hc = B_LENG / 2
    p.append(placa((X_PUNTA, Y_PCB0 + Y_SOLD), (X_PUNTA, Y_CODO), -hc, hc, "leng"))
    p.append(placa((X_PUNTA, Y_CODO), (X_LENG, Y_T), -hc, hc, "leng"))
    p.append(placa((X_LENG, Y_T), (X_FIN, Y_T), -hc, hc, "leng"))
    p.append(placa((X_FIN, Y_T), (XN, YN), -hc, hc, "leng"))
    return p


S_ISO, OX_ISO, OY_ISO = 16.0, 470.0, 205.0


def iso(x, y, z):
    return OX_ISO + S_ISO * (x - z) * 0.866, OY_ISO - S_ISO * (y * 0.816 - (x + z) * 0.408)


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
            if sum(n[k] * (fc[k] - cen[k]) for k in range(3)) < 0:
                n = tuple(-c for c in n)
            if n[0] + n[1] + n[2] <= 1e-12:
                continue
            caras.append((sum(fc), cl, "xyz"[max(range(3), key=lambda k: abs(n[k]))], P))
    caras.sort(key=lambda r: r[0])
    out = []
    w = [iso(-4, 0, -6.5), iso(25, 0, -6.5), iso(25, 0, 6.5), iso(-4, 0, 6.5)]
    out.append('<polygon class="i-cuna" points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in w) + '"/>')
    for d, cl, k, q in caras:
        out.append(f'<polygon class="i-{cl} i-{k}" points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in (iso(*p) for p in q)) + '"/>')
    hx, hy = iso(X_HOY, 0.02, 0)
    out.append(f'<ellipse class="i-hoy" cx="{hx:.1f}" cy="{hy:.1f}" rx="{S_ISO*0.95:.1f}" ry="{S_ISO*0.5:.1f}"/>')
    xs, ys, zs = (CX0, CX1), (C["y0"], C["y1"]), (-5.0, 5.0)
    ar = [((a, b, zs[0]), (a, b, zs[1])) for a in xs for b in ys] + [((a, ys[0], c), (a, ys[1], c)) for a in xs for c in zs]
    ar += [((xs[0], b, c), (xs[1], b, c)) for b in ys for c in zs]
    for p, q in ar:
        (a1, b1), (a2, b2) = iso(*p), iso(*q)
        out.append(f'<line class="i-carcasa" x1="{a1:.1f}" y1="{b1:.1f}" x2="{a2:.1f}" y2="{b2:.1f}"/>')

    def rot(p, tx, ty, txt, cls="lbl"):
        a, b = iso(*p)
        return (f'<line class="guia" x1="{a:.1f}" y1="{b:.1f}" x2="{tx:.1f}" y2="{ty:.1f}"/>'
                f'<text class="{cls}" x="{tx + (4 if tx > a else -4):.1f}" y="{ty + 4:.1f}" text-anchor="{"start" if tx > a else "end"}">{txt}</text>')
    out += [rot((-T_PCB, 8.0, -1.5), 320, 40, "PCB fija (conector)"),
            rot((6, Y_SUP, 2.0), 320, 100, "2 láminas rectas arriba"),
            rot((6, Y_INF, -2.0), 320, 300, "2 láminas rectas abajo"),
            rot((-2, 0, 4), 320, 365, "cuña", "lbl-w"),
            rot((X_B, 7.5, -2.8), 880, 40, "PCB del carro (FR4 1,6)"),
            rot((X_B + CHIP[2], 6.5, 1.0), 880, 100, "ADXL1004 soldado (eje vertical)"),
            rot((XN - 0.2, YN, 0), 880, 270, "punta de chapa soldada: rampa · hoyuelo · nariz"),
            rot((CX1, C["y0"], -5.0), 880, 365, "carcasa (contorno)")]
    return "\n".join(out)


def svg_alzado():
    s, ox, oy = 26.0, 175.0, 320.0
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

    rect(-5.0, -1.4, CX1 + 2.3, 0, "cuna"); text(-4.7, -0.9, "cuña de G11", "lbl-w")
    pw = 1.0
    o.append(f'<path class="carcasa" d="M{X(CX0)} {Y(PISO0)} L{X(RAN_X0)} {Y(PISO0)} L{X(RAN_X0)} {Y(PISO1)} '
             f'L{X(CX0+pw)} {Y(PISO1)} L{X(CX0+pw)} {Y(TECHO)} L{X(CX1-pw)} {Y(TECHO)} L{X(CX1-pw)} {Y(PISO1)} '
             f'L{X(RAN_X1)} {Y(PISO1)} L{X(RAN_X1)} {Y(PISO0)} L{X(CX1)} {Y(PISO0)} L{X(CX1)} {Y(C["y1"])} '
             f'L{X(CX0)} {Y(C["y1"])} Z"/>')
    rect(-T_PCB, PISO1, 0, TECHO, "pcbf")
    o.append(f'<text class="ct-v" transform="translate({X(-T_PCB/2)+4:.1f},{Y(5.0):.1f}) rotate(-90)" text-anchor="middle">PCB fija</text>')
    rect(X_A, Y_PCB0, X_B, Y_PCB1, "pcb")
    rect(X_B, Y_CHIP0, X_B + CHIP[2], Y_CHIP1, "chip")
    xc = X_B + CHIP[2] / 2
    o.append(f'<path class="eje" d="M{X(xc)} {Y(Y_CHIP0+0.8)} L{X(xc)} {Y(Y_CHIP1-1.0)}" marker-end="url(#fl2)"/>')
    for y in (Y_SUP, Y_INF):
        o.append(f'<path class="chapa" d="M{X(-T_PCB)} {Y(y)} L{X(X_B)} {Y(y)}"/>')
        for x in (-T_PCB, X_A):
            rect(x, y - 0.17, x + T_PCB, y + 0.17, "sold")
    o.append(f'<path class="chapa-t" d="M{X(X_PUNTA)} {Y(Y_PCB0+Y_SOLD)} L{X(X_PUNTA)} {Y(Y_CODO)} L{X(X_LENG)} {Y(Y_T)} '
             f'L{X(X_FIN)} {Y(Y_T)} L{X(XN)} {Y(YN)}"/>')
    rect(X_B, Y_PCB0, X_B + 0.2, Y_PCB0 + Y_SOLD, "sold")
    a = math.sqrt(2 * R_HOY * H_HOY - H_HOY ** 2)
    o.append(f'<path class="hoy" d="M{X(X_HOY-a)} {Y(Y_T)} Q{X(X_HOY)} {Y(Y_T-2*H_HOY)} {X(X_HOY+a)} {Y(Y_T)}"/>')
    # rótulos
    text(1.0, Y_SUP - 0.55, "2 láminas 0,15 × 1,5", "lbl-a")
    text(1.0, Y_INF + 0.35, "2 láminas 0,15 × 1,5", "lbl-a")
    text(X_B + CHIP[2] + 0.35, Y_CHIP0 + 2.9, "ADXL1004", "lbl"); text(X_B + CHIP[2] + 0.35, Y_CHIP0 + 2.3, "eje sensible ↑", "ct")
    o.append(f'<text class="ct-v" transform="translate({X(X_A+T_PCB/2)+4:.1f},{Y(Y_PCB0+3.4):.1f}) rotate(-90)" text-anchor="middle">PCB carro</text>')
    text(X_B + 0.5, Y_PCB0 + 0.45, "punta soldada", "lbl-l")
    text(XN + 0.5, 0.35, "nariz 30°", "lbl-l")
    text(X_HOY + 0.35, -0.6, "hoyuelo R 2", "ct")
    text(X_PUNTA - 0.3, 0.4, "rampa 35°", "lbl-l", "end")
    # cotas
    cota_h(0, X_A, Y_SUP - 1.6, f(L_BRAZO, 0), dy=-0.55)
    cota_v(-3.6, Y_INF, Y_SUP, f(Y_SUP - Y_INF, 1), -1)
    cota_v(-3.6, 0, Y_INF, f(Y_INF, 1), -1)
    cota_v(CX1 + 1.2, 0, C["y0"], f(C["y0"], 1), 1)
    cota_v(CX1 + 1.2, C["y0"], C["y1"], f(C["y1"] - C["y0"], 1), 1)
    cota_v(X_A - 0.6, Y_PCB1, TECHO, f"tope de retracción {f(TECHO - Y_PCB1, 1)}", -1, "ct-r")
    cota_v(X_A - 0.6, PISO1, Y_PCB0, f"tope de caída {f(Y_PCB0 - PISO1, 1)}", -1, "ct-r")
    o.append(f'<path class="fuerza" d="M{X(X_HOY)} {Y(-1.3)} L{X(X_HOY)} {Y(-0.08)}" marker-end="url(#ff2)"/>')
    text(X_HOY + 0.3, -1.15, "F₀ 2 N", "lbl-v")
    return "\n".join(o)


def svg_planta():
    s, ox, oy = 24.0, 70.0, 130.0
    X = lambda x: ox + s * x
    Z = lambda z: oy + s * z
    o = []

    def rect(x0, z0, x1, z1, cl):
        o.append(f'<rect class="{cl}" x="{X(x0):.1f}" y="{Z(z0):.1f}" width="{s*(x1-x0):.1f}" height="{s*(z1-z0):.1f}"/>')

    def text(x, z, t, cl="ct", a="start"):
        o.append(f'<text class="{cl}" x="{X(x):.1f}" y="{Z(z):.1f}" text-anchor="{a}">{t}</text>')
    rect(RAN_X0, -RAN_Z, RAN_X1, RAN_Z, "ranura-pl")
    rect(-T_PCB, -B_PCB / 2, 0, B_PCB / 2, "pcbf-pl")
    for z0, z1 in ZT:
        rect(-T_PCB, z0, X_B, z1, "pl-chapa")
    rect(X_A, -B_PCB / 2, X_B, B_PCB / 2, "pcb-pl")
    rect(X_PUNTA - T / 2, -B_LENG / 2, XN, B_LENG / 2, "pl-leng")
    rect(X_B, -CHIP[1] / 2, X_B + CHIP[2], CHIP[1] / 2, "chip-pl")
    o.append(f'<circle class="hoy-pl" cx="{X(X_HOY):.1f}" cy="{Z(0):.1f}" r="{s*0.97:.1f}"/>')

    def cota_z(x, z0, z1, t):
        o.append(f'<line class="cota" x1="{X(x):.1f}" y1="{Z(z0):.1f}" x2="{X(x):.1f}" y2="{Z(z1):.1f}"/>')
        o.append(f'<text class="ct" x="{X(x)+5:.1f}" y="{(Z(z0)+Z(z1))/2+4:.1f}">{t}</text>')
    cota_z(7.0, ZT[1][0], ZT[1][1], f(B_TIRA, 1))
    cota_z(9.0, ZT[0][1], ZT[1][0], f(2 * Z_TIRA, 1))
    cota_z(RAN_X1 + 0.6, -RAN_Z, RAN_Z, f"ranura {f(2*RAN_Z, 1)}")
    text(-T_PCB, -3.8, "planta · las láminas de abajo, debajo de las de arriba · ranura del piso en rojo")
    text(X_B + 0.9, 3.95, "chip", "ct", "middle")
    return "\n".join(o)


def svg_piezas():
    """Piezas: lámina (×4), tira de la punta desplegada (a mayor escala) y las dos PCB de frente."""
    o = []

    def rect(x, y, w, h, cl):
        o.append(f'<rect class="{cl}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"/>')

    def text(x, y, t, cl="ct", a="start"):
        o.append(f'<text class="{cl}" x="{x:.1f}" y="{y:.1f}" text-anchor="{a}">{t}</text>')

    def cota(x0, x1, y, t):
        o.append(f'<line class="cota" x1="{x0:.1f}" y1="{y:.1f}" x2="{x1:.1f}" y2="{y:.1f}"/>')
        for x in (x0, x1):
            o.append(f'<line class="cota" x1="{x:.1f}" y1="{y-4:.1f}" x2="{x:.1f}" y2="{y+4:.1f}"/>')
        text((x0 + x1) / 2, y - 5, t, "ct", "middle")
    # lámina, escala 20 px/mm
    s, x0, y0 = 20.0, 20.0, 40.0
    Ll = L_BRAZO + 2 * T_PCB
    text(x0, y0 - 14, f"lámina × 4 · 17-7PH CH900 0,15 mm · Ni + Sn", "tb")
    rect(x0, y0, s * Ll, s * B_TIRA, "dev")
    for u in (T_PCB, T_PCB + L_BRAZO):
        o.append(f'<line class="pliegue" x1="{x0+s*u:.1f}" y1="{y0-5:.1f}" x2="{x0+s*u:.1f}" y2="{y0+s*B_TIRA+5:.1f}"/>')
    cota(x0, x0 + s * Ll, y0 + s * B_TIRA + 18, f(Ll, 1))
    text(x0, y0 + s * B_TIRA + 40, f"en rojo, las caras de las PCB: luz libre {f(L_BRAZO,0)}")
    text(x0 + s * Ll + 8, y0 + s * B_TIRA / 2 + 4, f"{f(B_TIRA,1)}")
    # tira de la punta desplegada, escala 40 px/mm
    s, x0, y0 = 40.0, 20.0, 150.0
    u = [0, Y_SOLD, Y_SOLD + (Y_PCB0 - Y_CODO)]
    u += [u[-1] + L_RAMPA, u[-1] + L_RAMPA + L_LENG]
    u_f = u[-1] + PLANO
    u_e = u_f + NARIZ
    text(x0, y0 - 14, "tira de la punta · mismo acero · hoyuelo acuñado R 2 · 3 pliegues: 55°, 35° y 30° (nariz)", "tb")
    b = s * B_LENG
    o.append(f'<path class="dev" d="M{x0} {y0} L{x0+s*u_f:.1f} {y0} A{b/2:.1f} {b/2:.1f} 0 0 1 {x0+s*u_f:.1f} {y0+b:.1f} L{x0} {y0+b:.1f} Z"/>')
    rect(x0 + s * u_f, y0 + 0.3 * s, s * (u_e - u_f) + b / 2, b - 0.6 * s, "dev")
    rect(x0, y0, s * Y_SOLD, b, "sold-pl")
    for uu in (u[2], u[3], u_f):
        o.append(f'<line class="pliegue" x1="{x0+s*uu:.1f}" y1="{y0-6:.1f}" x2="{x0+s*uu:.1f}" y2="{y0+b+6:.1f}"/>')
    o.append(f'<circle class="hoy-pl" cx="{x0+s*u[4]:.1f}" cy="{y0+b/2:.1f}" r="{s*0.97:.1f}"/>')
    nom = ["soldada", "vertical", "rampa", "lengüeta", "extremo"]
    puntos = u + [u_f]
    for k in range(5):
        cota(x0 + s * puntos[k], x0 + s * puntos[k + 1], y0 + b + 22 + (12 if k % 2 else 0), f(puntos[k + 1] - puntos[k], 2))
    text(x0 + s * u_e + b / 2 + 10, y0 + b / 2 + 4, f"ancho {f(B_LENG,1)}")
    # PCB de frente (z horizontal, y vertical), escala 22 px/mm
    s = 22.0

    def pcb(xp, yb, titulo, y_lo, y_hi, carro):
        Yy = lambda y: yb - s * (y - y_lo)
        text(xp, Yy(y_hi) - 10, titulo, "tb")
        rect(xp, Yy(y_hi), s * B_PCB, s * (y_hi - y_lo), "pcb-fr")
        for y in (Y_SUP, Y_INF):
            for z0, z1 in ZT:
                if carro:      # muesca abierta al borde
                    ya, yc = (y - 0.3, y_hi) if y > (y_lo + y_hi) / 2 else (y_lo, y + 0.3)
                else:
                    ya, yc = y - 0.3, y + 0.3
                rect(xp + s * (B_PCB / 2 + z0 - 0.05), Yy(yc), s * (z1 - z0 + 0.1), s * (yc - ya), "ranura-pcb")
        if carro:
            rect(xp + s * (B_PCB / 2 - CHIP[1] / 2), Yy(Y_CHIP1), s * CHIP[1], s * CHIP[0], "chip-fr")
            rect(xp + s * (B_PCB / 2 - B_LENG / 2), Yy(Y_PCB0 + Y_SOLD), s * B_LENG, s * Y_SOLD, "sold-pl")
            text(xp + s * B_PCB + 8, Yy(Y_SUP) + 4, "muescas metalizadas")
            text(xp + s * B_PCB + 8, Yy(Y_CHIP0 + 2.5) + 4, "ADXL1004")
            text(xp + s * B_PCB + 8, Yy(Y_PCB0 + 0.4) + 4, "pad de la punta")
        else:
            text(xp + s * B_PCB + 8, Yy(Y_SUP) + 4, "ranuras metalizadas")
            text(xp + s * B_PCB + 8, Yy(5.0) + 4, "conector")
    pcb(20.0, 505.0, "PCB del carro, cara exterior", Y_PCB0, Y_PCB1, True)
    pcb(360.0, 505.0, "PCB fija", PISO1, TECHO, False)
    return "\n".join(o)


ESTILO = ESTILO_TIRA + """
.i-pcb.i-x,.i-pcb.i-y,.i-pcb.i-z{fill:#2f7d4f}.i-pcbf.i-x,.i-pcbf.i-y,.i-pcbf.i-z{fill:#3c6e55}
.pcb{fill:#2f7d4f;stroke:#1d4d31}.pcbf{fill:#3c6e55;stroke:#1d4d31}
.pcb-pl{fill:#2f7d4f99;stroke:#1d4d31}.pcbf-pl{fill:#3c6e5599;stroke:#1d4d31}
.pcb-fr{fill:#2f7d4f33;stroke:#1d4d31;stroke-width:1.2}.chip-fr{fill:#232b33aa}
.ranura-pcb{fill:#c9a227;stroke:#8a6d12}.sold{fill:#c9a227}.sold-pl{fill:#c9a22799;stroke:#8a6d12}
.chapa-t{fill:none;stroke:var(--ok);stroke-width:3;stroke-linejoin:round}
.ct-v{font-size:10px;fill:#e8f2ea}
"""


def generar():
    res = json.loads((RAIZ / "results/cuna3d/palpador_pcb.json").read_text())
    st, rb = res["estatica"], res["robustez"]
    NOMR = {"coulomb": "real, μ {mu}", "libre": "sin rozamiento (cota)", "adherido": "trabada (cota)"}
    filas = ""
    for r in res["verificacion"]:
        d = sorted({x.split("·")[0] for x in r["despega"]})
        rz = NOMR[r["tg"]].format(mu=f(r["mu"], 2)) + (f', lengüeta {"+" if r["d_leng"] > 0 else "−"}{f(abs(r["d_leng"]), 2)} mm' if r["d_leng"] else "")
        filas += (f'<tr class="{"rec" if (r["tg"], r["F0"], r["mu"], r["d_leng"]) == ("coulomb", 2.0, MU[0], 0.0) else ""}"><td>{rz}</td><td class="n">{f(r["F0"],1)} N</td>'
                  f'<td>{"no" if not d else ", ".join(x.replace("_", " ") for x in d)}</td>'
                  f'<td>{"no" if not r["satura_en"] else ", ".join(x.replace("_", " ") for x in r["satura_en"])}</td>'
                  f'<td class="n">{f(r["Fc_min_sin_muy_floja"],2)} N</td>'
                  f'<td class="n">{" · ".join(f(g,2) for g in r["gaps_C1"])}</td><td class="n">{r["gap_C2_Hz"]:.0f} Hz</td></tr>')
    NOM = {"ajustada/moderada": "ajustada | moderada", "moderada/floja": "moderada | floja", "floja/muy_floja_juego": "floja | muy floja"}
    umb = "".join(f'<tr><td>{NOM[u["entre"]]}</td><td class="n">{f(u["umbral"],2)}</td><td class="n">± {f(u["hueco"]/2,2)}</td></tr>'
                  for u in res["umbrales_C1"])
    fp, fs_ = rb["F_horizontal_pandeo_N"], rb["F_horizontal_para_subir_N"]
    html = f"""<section id="pcb">
  <style>{ESTILO}</style>
  <div class="prose">
    <span class="eyebrow">11 · Variante con PCB: dos láminas rectas y el sensor soldado</span>
    <h2>La PCB es el carro; los resortes son láminas rectas</h2>
    <p>Es la misma mecánica que la sección 10 (dos brazos paralelos y una lengüeta corta como filtro), pero sin pliegues en los brazos. La "C" era la forma de sacar dos brazos paralelos de una sola chapa; con una PCB como carro, los brazos son láminas rectas.</p>
    <ul>
      <li><b>PCB del carro</b> (FR4 de 1,6 mm, vertical). El ADXL1004 va soldado en la cara exterior: su eje sensible está en el plano de la placa y queda vertical. No hace falta flex con refuerzo.</li>
      <li><b>Cuatro láminas rectas iguales</b> (17-7PH CH900 de 0,15 × {f(B_TIRA,1)} mm, niqueladas y estañadas), dos arriba y dos abajo, entre la PCB fija y la del carro. Son el paralelogramo (sin cabeceo: el carro gira {f(abs(st["giro_sensor_mrad"]),1)} mrad al precargar) y además los cuatro conductores: alimentación, masa, salida y sobrerrango. No hay cable que vaya al carro.</li>
      <li><b>Punta de chapa</b> del mismo acero, soldada en un pad de la cara exterior, debajo del chip: tramo vertical, rampa a 35°, lengüeta de {f(L_LENG,1)} mm con el hoyuelo, extremo redondeado y nariz. Es la única pieza con pliegues (tres).</li>
      <li><b>PCB fija</b>, atornillada a la carcasa, con el conector.</li>
    </ul>
    <p><b>Uniones.</b> Las láminas entran en muescas metalizadas abiertas al borde de la PCB del carro (así no queda un puente de FR4 finito) y en ranuras metalizadas de la PCB fija, soldadas y con epoxi. La soldadura sola, cargada todo el tiempo con el momento de la precarga, fluye y la precarga se pierde con los meses; el epoxi (o una prensa) toma la carga y la soldadura queda para la conexión eléctrica. Con cobre-berilio, que se suelda directo, no alcanza: la punta llega a la fluencia en el tope y los modos de la estructura bajan a 3,2 kHz.</p>
    <p><b>Robustez</b>, igual que en la sección 10. El techo es el tope de retracción ({f(rb["retraccion_mm"],1)} mm, la punta queda al ras del piso; tensión máxima {f(rb["sigma_tope_techo_MPa"],0)} MPa contra ~{f(rb["fluencia_MPa"],0)} MPa). El borde inferior de la PCB del carro apoya en el piso si no hay cuña (caída de {f(rb["caida_max_mm"],1)} mm como máximo). La ranura del piso es el tope lateral. Para subir un escalón hacen falta {f(fs_["rampa trasera 35°"],1)} N (rampa) o {f(fs_["nariz 30°"],1)} N (nariz); las láminas pandean, elásticamente, con {f(fp["empuje hacia atrás"],1)} N hacia atrás.</p>
  </div>
  <div class="fig plano" role="img" aria-label="Vista isométrica de la variante con PCB"><svg viewBox="0 0 1260 390">{svg_iso()}</svg></div>
  <div class="fig plano" role="img" aria-label="Alzado de la variante con PCB"><svg viewBox="0 0 900 370">
    <defs><marker id="fl2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10z" style="fill:#6aa8ef"/></marker>
    <marker id="ff2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10z" style="fill:var(--ok)"/></marker></defs>
    {svg_alzado()}</svg></div>
  <p class="note" style="font-size:.85rem;color:var(--ink-2)">Alzado en corte por el plano medio, estado cargado (F₀ = 2 N, piso a 1,0 mm de la cuña). En amarillo, las uniones soldadas. Topes en rojo. Medidas en mm.</p>
  <div class="fig plano" role="img" aria-label="Planta de la variante con PCB"><svg viewBox="0 0 640 230">{svg_planta()}</svg></div>
  <div class="fig plano" role="img" aria-label="Piezas de la variante con PCB"><svg viewBox="0 0 660 520">{svg_piezas()}</svg></div>
  <div class="prose"><h3>Números</h3></div>
  <div class="tbl"><table><tbody>
    <tr><td>Rigidez de precarga · flecha para 2 N</td><td class="n">{f(st["k_vertice_N_mm"],2)} N/mm · {f(st["flecha_vertice_mm"],2)} mm</td></tr>
    <tr><td>Precarga con ±0,3 mm de altura de la carcasa</td><td class="n">{" – ".join(f(x,2) for x in rb["F0_por_altura_N"])} N</td></tr>
    <tr><td>Tensión máxima: en precarga · en el tope · fluencia CH900</td><td class="n">{f(rb["sigma_precarga_MPa"],0)} · {f(rb["sigma_tope_techo_MPa"],0)} · ~{f(rb["fluencia_MPa"],0)} MPa</td></tr>
    <tr><td>Frecuencia del filtro · pico sin amortiguador</td><td class="n">{f(res["f0_Hz"],0)} Hz · {f(res["pico"],0)}</td></tr>
    <tr><td>Modos siguientes (fuera de la banda de C1)</td><td class="n">{" · ".join(f(x/1000,1) for x in res["modos_Hz"][1:6])} kHz</td></tr>
    <tr><td>Carro (ADXL1004 + PCB)</td><td class="n">{f(res["masa_carro_g"],3)} g</td></tr>
  </tbody></table></div>
  <div class="prose"><h3>Verificación contra la cuña 3D a 15 mm</h3>
    <p>Los 11 estados de la cuña, con energía del golpe ±10 % y rigidez de los flancos ±30 %, ζ 0,002, C1 en {f(BANDA_C1[0]/1000,0)}–{f(BANDA_C1[1]/1000,0)} kHz. Rozamiento real: Coulomb con μ 0,3 y 0,15.</p></div>
  <div class="tbl"><table><thead><tr><th>Rozamiento</th><th>F₀</th><th>¿Despega?</th><th>¿Satura?</th><th>F mín (resto)</th><th>Huecos de C1</th><th>Hueco de C2</th></tr></thead><tbody>{filas}</tbody></table></div>
  <div class="prose"><h3>Umbrales de C1 (F₀ 2 N, μ entre 0,15 y 0,3)</h3></div>
  <div class="tbl"><table><thead><tr><th>Entre</th><th>Umbral de C1</th><th>Margen</th></tr></thead><tbody>{umb}</tbody></table></div>
  <div class="prose"><h3>Fabricación y montaje</h3></div>
  <ol class="steps">
    <li>PCB del carro y PCB fija en el mismo panel (FR4 1,6 mm): muescas metalizadas al borde en la del carro, ranuras metalizadas en la fija, y el pad de la punta entre las dos muescas de abajo.</li>
    <li>Láminas y tira de la punta fotograbadas en 17-7PH condición C de 0,15 mm; hoyuelo acuñado y tres pliegues en la tira de la punta; envejecido CH900; niquelado y estañado.</li>
    <li>Soldar el ADXL1004 y los capacitores en la PCB del carro.</li>
    <li>En un útil que fija la distancia entre placas ({f(L_BRAZO,0)} mm de luz libre) y su paralelismo: colocar las cuatro láminas en las muescas y ranuras, soldar y poner epoxi. Soldar la punta en su pad, con epoxi.</li>
    <li>Atornillar la PCB fija a la carcasa (piso de 0,5 mm con la ranura de {f(2*RAN_Z,1)} mm; techo a {f(rb["retraccion_mm"],1)} mm de la PCB del carro).</li>
    <li>Ensayo de impacto del palpador montado: f₀ y ζ reales, para fijar los umbrales.</li>
  </ol>
</section>
"""
    (RAIZ / "docs/palpador/plano_pcb.html").write_text(html)
    return html


if __name__ == "__main__":
    generar()
    print("ok")
