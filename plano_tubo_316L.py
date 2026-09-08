# -*- coding: utf-8 -*-
"""
Plano de fabricacion (ISO, A3 apaisado):

    TUBO AISI 316L  Ø88.9 x 500  -  VENTANA 60 x 30 (R3) BISELADA A 30 deg

Salida: plano_tubo_316L_ventana_biselada.pdf
El canvas se escala a milimetros: todas las coordenadas del codigo son mm de hoja.

Reparto de la hoja (A3 420 x 297, recuadro ISO 5457):
    y 185..287 : vista principal 1:2   +   vista isometrica
    y  70..180 : DETALLE B 1:1 | CORTE A-A 1:2 | DETALLE C 5:1
    y  10..62  : notas   +   cajetin ISO 7200
"""

import math
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, black, white

# ----------------------------------------------------------------------------
# PIEZA
# ----------------------------------------------------------------------------
OD = 88.9
WT = 2.0
ID = OD - 2 * WT
LEN = 500.0
WIN_L = 60.0                               # dimension axial de la ventana (ext.)
WIN_C = 30.0                               # dimension circunferencial (ext.)
WIN_R = 3.0
BEV = 30.0                                 # bisel respecto de la normal
OFF = WT * math.tan(math.radians(BEV))     # 1.1547
ROOT_L = WIN_L - 2 * OFF
ROOT_C = WIN_C - 2 * OFF
ROOT_R = WIN_R - OFF

# ----------------------------------------------------------------------------
# HOJA
# ----------------------------------------------------------------------------
PAGE_W, PAGE_H = 420.0, 297.0
FX0, FY0, FX1, FY1 = 20.0, 10.0, 410.0, 287.0

W_FRAME = 0.7
W_THICK = 0.5
W_THIN = 0.25
W_HAIR = 0.18

D_HIDDEN = [2.0, 1.2]
D_CENTER = [8.0, 1.2, 1.2, 1.2]
D_PHANTOM = [8.0, 1.2, 1.2, 1.2, 1.2, 1.2]

GREY_L = Color(0.870, 0.882, 0.898)
GREY_M = Color(0.706, 0.725, 0.745)
GREY_D = Color(0.450, 0.470, 0.490)
GREY_XD = Color(0.235, 0.250, 0.270)

OUT = "plano_tubo_316L_ventana_biselada.pdf"
c = canvas.Canvas(OUT, pagesize=(PAGE_W * mm, PAGE_H * mm))
c.setTitle("PT-316L-VT-001 - Tubo AISI 316L 88.9x500 - Ventana 60x30 biselada")
c.setAuthor("Melanie Martinez")
c.scale(mm, mm)
c.setLineJoin(1)
c.setLineCap(1)

FONT = "Helvetica"
FONT_B = "Helvetica-Bold"
DIA = "Ø"


def fs(h):
    return h / 0.716


# ----------------------------------------------------------------------------
# PRIMITIVAS
# ----------------------------------------------------------------------------
def pen(w=W_THIN, dash=None, col=black):
    c.setLineWidth(w)
    c.setDash(dash if dash else [], 0)
    c.setStrokeColor(col)


def ln(x1, y1, x2, y2, w=W_THIN, dash=None, col=black):
    pen(w, dash, col)
    c.line(x1, y1, x2, y2)


def rect(x, y, w, h, lw=W_THIN, dash=None, fill=None, col=black):
    pen(lw, dash, col)
    if fill is not None:
        c.setFillColor(fill)
        c.rect(x, y, w, h, stroke=1, fill=1)
    else:
        c.rect(x, y, w, h, stroke=1, fill=0)


def circ(x, y, r, lw=W_THIN, dash=None, fill=None, col=black):
    pen(lw, dash, col)
    if fill is not None:
        c.setFillColor(fill)
        c.circle(x, y, r, stroke=1, fill=1)
    else:
        c.circle(x, y, r, stroke=1, fill=0)


def poly(pts, lw=W_THIN, dash=None, fill=None, close=True, col=black):
    pen(lw, dash, col)
    p = c.beginPath()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    if fill is not None:
        c.setFillColor(fill)
        c.drawPath(p, stroke=1, fill=1)
    else:
        c.drawPath(p, stroke=1, fill=0)


def arc(cx, cy, r, a0, a1, w=W_THIN, dash=None, col=black):
    pen(w, dash, col)
    p = c.beginPath()
    n = max(8, int(abs(a1 - a0) / 3) + 1)
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        p.moveTo(x, y) if i == 0 else p.lineTo(x, y)
    c.drawPath(p, stroke=1, fill=0)


def txt(x, y, s, h=2.5, anchor="l", font=FONT, rot=0, col=black):
    c.saveState()
    c.setFillColor(col)
    c.setFont(font, fs(h))
    c.translate(x, y)
    if rot:
        c.rotate(rot)
    if anchor == "c":
        c.drawCentredString(0, 0, s)
    elif anchor == "r":
        c.drawRightString(0, 0, s)
    else:
        c.drawString(0, 0, s)
    c.restoreState()


def tw(s, h=2.5, font=FONT):
    return c.stringWidth(s, font, fs(h))


def arrow(x, y, ux, uy, L=3.0, W=1.0):
    n = math.hypot(ux, uy)
    ux, uy = ux / n, uy / n
    px, py = -uy, ux
    c.setFillColor(black)
    p = c.beginPath()
    p.moveTo(x, y)
    p.lineTo(x - ux * L + px * W / 2, y - uy * L + py * W / 2)
    p.lineTo(x - ux * L - px * W / 2, y - uy * L - py * W / 2)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def hatch(path_pts, spacing=2.2, ang=45.0, w=W_HAIR):
    xs = [p[0] for p in path_pts]
    ys = [p[1] for p in path_pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    c.saveState()
    p = c.beginPath()
    p.moveTo(*path_pts[0])
    for q in path_pts[1:]:
        p.lineTo(*q)
    p.close()
    c.clipPath(p, stroke=0, fill=0)
    pen(w)
    a = math.radians(ang)
    dx, dy = math.cos(a), math.sin(a)
    diag = math.hypot(x1 - x0, y1 - y0) + 8
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    n = int(diag / spacing) + 3
    for i in range(-n, n + 1):
        ox, oy = cx - dy * i * spacing, cy + dx * i * spacing
        c.line(ox - dx * diag, oy - dy * diag, ox + dx * diag, oy + dy * diag)
    c.restoreState()


def rrect_pts(x, y, w, h, r, n=14):
    pts = []
    for cx, cy, a0, a1 in [(x + w - r, y + r, -90, 0), (x + w - r, y + h - r, 0, 90),
                           (x + r, y + h - r, 90, 180), (x + r, y + r, 180, 270)]:
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def wrap(text, width, h=2.2, font=FONT):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if c.stringWidth(t, font, fs(h)) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


# ----------------------------------------------------------------------------
# ACOTACION
# ----------------------------------------------------------------------------
AH, AW = 3.0, 1.0
TH = 2.5
GAP, OVR = 1.0, 1.8


def dim_h(x1, x2, y, label, from_y=None, th=TH, force_out=False, side="r", tail=7.0):
    if from_y is not None:
        s = 1 if y > from_y else -1
        for xx in (x1, x2):
            ln(xx, from_y + s * GAP, xx, y + s * OVR, W_THIN)
    small = abs(x2 - x1) < (tw(label, th) + 2 * AH + 2.0) or force_out
    ln(x1, y, x2, y, W_THIN)
    if not small:
        arrow(x1, y, -1, 0, AH, AW)
        arrow(x2, y, 1, 0, AH, AW)
        txt((x1 + x2) / 2, y + 1.1, label, th, "c")
    else:
        ln(x1 - tail, y, x1, y, W_THIN)
        ln(x2, y, x2 + tail, y, W_THIN)
        arrow(x1, y, 1, 0, AH, AW)
        arrow(x2, y, -1, 0, AH, AW)
        txt(x2 + 1.4, y + 1.1, label, th, "l") if side == "r" else \
            txt(x1 - 1.4, y + 1.1, label, th, "r")


def dim_v(y1, y2, x, label, from_x=None, th=TH, force_out=False, side="up", tail=7.0):
    if from_x is not None:
        s = 1 if x > from_x else -1
        for yy in (y1, y2):
            ln(from_x + s * GAP, yy, x + s * OVR, yy, W_THIN)
    small = abs(y2 - y1) < (tw(label, th) + 2 * AH + 2.0) or force_out
    ln(x, y1, x, y2, W_THIN)
    if not small:
        arrow(x, y1, 0, -1, AH, AW)
        arrow(x, y2, 0, 1, AH, AW)
        txt(x - 1.1, (y1 + y2) / 2, label, th, "c", rot=90)
    else:
        ln(x, y1 - tail, x, y1, W_THIN)
        ln(x, y2, x, y2 + tail, W_THIN)
        arrow(x, y1, 0, 1, AH, AW)
        arrow(x, y2, 0, -1, AH, AW)
        txt(x - 1.1, y2 + 1.4, label, th, "l", rot=90) if side == "up" else \
            txt(x - 1.1, y1 - 1.4, label, th, "r", rot=90)


def leader(x0, y0, x1, y1, x2, label, th=2.3, dot=False, arw=True, sub=None):
    ln(x0, y0, x1, y1, W_THIN)
    ln(x1, y1, x2, y1, W_THIN)
    if arw:
        arrow(x0, y0, x0 - x1, y0 - y1, AH, AW)
    if dot:
        c.setFillColor(black)
        c.circle(x0, y0, 0.5, stroke=0, fill=1)
    ax = "l" if x2 >= x1 else "r"
    ox = 1.0 if ax == "l" else -1.0
    txt(x2 + ox, y1 + 1.0, label, th, ax)
    if sub:
        txt(x2 + ox, y1 - 2.6, sub, th * 0.92, ax)


def dim_ang(cx, cy, r, a0, a1, label, th=2.4, off=2.2):
    arc(cx, cy, r, a0, a1, W_THIN)
    for a, s in ((a0, -1), (a1, 1)):
        ar = math.radians(a)
        arrow(cx + r * math.cos(ar), cy + r * math.sin(ar),
              -s * math.sin(ar), s * math.cos(ar), AH, AW)
    am = math.radians((a0 + a1) / 2)
    txt(cx + (r + off) * math.cos(am), cy + (r + off) * math.sin(am), label, th, "c")


def gdt_frame(x, y, cells, h=4.6, th=2.5):
    cx = x
    for cell in cells:
        if cell == "POS":
            w = h
            rect(cx, y, w, h, W_THIN)
            s = h * 0.82
            pen(W_THIN)
            c.circle(cx + w / 2, y + h / 2, s * 0.28, stroke=1, fill=0)
            c.line(cx + w / 2 - s * 0.46, y + h / 2, cx + w / 2 + s * 0.46, y + h / 2)
            c.line(cx + w / 2, y + h / 2 - s * 0.46, cx + w / 2, y + h / 2 + s * 0.46)
        else:
            w = tw(cell, th) + 2.8
            rect(cx, y, w, h, W_THIN)
            txt(cx + w / 2, y + h / 2 - th * 0.36, cell, th, "c")
        cx += w
    return cx - x


def datum(xa, ya, letter, dx, dy, lead=7.0, size=3.2):
    n = math.hypot(dx, dy)
    ux, uy = dx / n, dy / n
    px, py = -uy, ux
    poly([(xa, ya),
          (xa + ux * size * 0.9 + px * size * 0.45, ya + uy * size * 0.9 + py * size * 0.45),
          (xa + ux * size * 0.9 - px * size * 0.45, ya + uy * size * 0.9 - py * size * 0.45)],
         W_THIN, fill=black)
    ex, ey = xa + ux * lead, ya + uy * lead
    ln(xa + ux * size * 0.9, ya + uy * size * 0.9, ex, ey, W_THIN)
    bw, bh = 5.0, 4.8
    bx, by = ex - bw / 2 + ux * bw / 2, ey - bh / 2 + uy * bh / 2
    rect(bx, by, bw, bh, W_THIN, fill=white)
    txt(bx + bw / 2, by + 1.4, letter, 3.0, "c", FONT_B)


def surf_finish(x, y, value, h=5.0, rot=0):
    c.saveState()
    c.translate(x, y)
    if rot:
        c.rotate(rot)
    pen(W_THIN)
    c.line(0, 0, -h * 0.50, h * 0.87)
    c.line(0, 0, h * 0.60, h * 1.04)
    c.line(h * 0.60, h * 1.04, h * 1.90, h * 1.04)
    txt(h * 0.66, h * 1.22, value, 2.3, "l")
    c.restoreState()


def break_line(x, y0, y1, amp=1.1, n=6):
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append((x + (0 if i in (0, n) else (amp if i % 2 else -amp)),
                    y0 + (y1 - y0) * t))
    pen(W_THIN)
    p = c.beginPath()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    c.drawPath(p, stroke=1, fill=0)


def view_label(xc, y, name, scale):
    txt(xc, y, name, 3.5, "c", FONT_B)
    txt(xc, y - 4.2, scale, 2.5, "c")


# ============================================================================
# FORMATO ISO 5457
# ============================================================================
def sheet_frame():
    rect(FX0, FY0, FX1 - FX0, FY1 - FY0, W_FRAME)
    pen(W_FRAME)
    mx, my = (FX0 + FX1) / 2, (FY0 + FY1) / 2
    c.line(mx, FY1, mx, FY1 + 5)
    c.line(mx, FY0, mx, FY0 - 5)
    c.line(FX0, my, FX0 - 5, my)
    c.line(FX1, my, FX1 + 5, my)
    nx, ny = 8, 6
    dx, dy = (FX1 - FX0) / nx, (FY1 - FY0) / ny
    pen(W_HAIR)
    for i in range(1, nx):
        c.line(FX0 + i * dx, FY1, FX0 + i * dx, FY1 + 3.4)
        c.line(FX0 + i * dx, FY0, FX0 + i * dx, FY0 - 3.4)
    for i in range(1, ny):
        c.line(FX0, FY0 + i * dy, FX0 - 3.4, FY0 + i * dy)
        c.line(FX1, FY0 + i * dy, FX1 + 3.4, FY0 + i * dy)
    for i in range(nx):
        txt(FX0 + (i + .5) * dx, FY1 + 1.1, str(i + 1), 2.2, "c")
        txt(FX0 + (i + .5) * dx, FY0 - 2.9, str(i + 1), 2.2, "c")
    for i in range(ny):
        txt(FX0 - 2.0, FY0 + (i + .5) * dy - 0.9, "FEDCBA"[i], 2.2, "c")
        txt(FX1 + 2.0, FY0 + (i + .5) * dy - 0.9, "FEDCBA"[i], 2.2, "c")


# ============================================================================
# VISTA PRINCIPAL 1:2
# ============================================================================
FV_S = 0.5
FV_X = 34.0
FV_CY = 245.0


def fx(v):
    return FV_X + v * FV_S


def fy(v):
    return FV_CY + v * FV_S


def front_view():
    x0, x1 = fx(0), fx(LEN)
    yt, yb = fy(OD / 2), fy(-OD / 2)

    rect(x0, yb, x1 - x0, yt - yb, W_THICK)
    ln(x0, fy(ID / 2), x1, fy(ID / 2), W_THIN, D_HIDDEN)
    ln(x0, fy(-ID / 2), x1, fy(-ID / 2), W_THIN, D_HIDDEN)
    ln(x0 - 7, FV_CY, x1 + 7, FV_CY, W_THIN, D_CENTER)

    wx, ww, wh = fx((LEN - WIN_L) / 2), WIN_L * FV_S, WIN_C * FV_S
    poly(rrect_pts(wx, FV_CY - wh / 2, ww, wh, WIN_R * FV_S), W_THICK)
    poly(rrect_pts(fx((LEN - WIN_L) / 2 + OFF), FV_CY - ROOT_C * FV_S / 2,
                   ROOT_L * FV_S, ROOT_C * FV_S, ROOT_R * FV_S), W_THIN)
    xa = fx(LEN / 2)
    ln(xa, FV_CY - wh / 2 - 6, xa, FV_CY + wh / 2 + 6, W_THIN, D_CENTER)

    # plano de corte A-A
    for ye, s in ((yt + 2.0, 1), (yb - 2.0, -1)):
        ln(xa, ye, xa, ye + s * 6.0, W_THICK)
        ln(xa, ye + s * 6.0, xa + 7.0, ye + s * 6.0, W_THICK)
        arrow(xa, ye + s * 6.0, -1, 0, 3.4, 1.2)
        txt(xa + 8.0, ye + s * 6.0 - 1.4, "A", 4.0, "l", FONT_B)

    # circulo de detalle B
    dbr = 15.0
    circ(xa, FV_CY, dbr, W_THIN)
    a = math.radians(45)
    ln(xa + dbr * math.cos(a), FV_CY + dbr * math.sin(a), xa + 20, FV_CY + 17.0, W_THIN)
    ln(xa + 20, FV_CY + 17.0, xa + 28, FV_CY + 17.0, W_THIN)
    txt(xa + 29, FV_CY + 15.6, "B", 4.0, "l", FONT_B)

    dim_h(x0, xa, 214.0, "250", from_y=yb)
    dim_h(x0, x1, 205.0, "500", from_y=yb)
    datum(x0, FV_CY - 8.0, "B", -1, 0, lead=8.0)

    txt(FV_X, 195.0, "VISTA PRINCIPAL", 3.5, "l", FONT_B)
    txt(FV_X + 52.0, 195.0, "ESCALA 1:2", 2.5, "l")


# ============================================================================
# CORTE A-A 1:2
# ============================================================================
SA_CX, SA_CY, SA_S = 240.0, 130.0, 1.0


def section_aa():
    ro, ri = OD / 2 * SA_S, ID / 2 * SA_S
    ao = math.degrees((WIN_C / 2) / (OD / 2))
    ai = math.degrees((ROOT_C / 2) / (ID / 2))

    def P(r, a):
        return (SA_CX + r * math.cos(math.radians(a)),
                SA_CY + r * math.sin(math.radians(a)))

    pts, n = [], 220
    a0, a1 = 90 + ao, 450 - ao
    for i in range(n + 1):
        pts.append(P(ro, a0 + (a1 - a0) * i / n))
    b0, b1 = 450 - ai, 90 + ai
    for i in range(n + 1):
        pts.append(P(ri, b0 + (b1 - b0) * i / n))
    poly(pts, W_THICK, fill=white)
    hatch(pts, spacing=1.6, ang=45)
    poly(pts, W_THICK)

    ln(SA_CX - ro - 6, SA_CY, SA_CX + ro + 6, SA_CY, W_THIN, D_CENTER)
    ln(SA_CX, SA_CY - ro - 6, SA_CX, SA_CY + ro + 6, W_THIN, D_CENTER)

    # diametro exterior acotado sobre la propia seccion
    ad = -30.0
    p1, p2 = P(ro, 180 + ad), P(ro, ad)
    ln(p1[0], p1[1], p2[0], p2[1], W_THIN)
    arrow(p1[0], p1[1], p1[0] - p2[0], p1[1] - p2[1], AH, AW)
    arrow(p2[0], p2[1], p2[0] - p1[0], p2[1] - p1[1], AH, AW)
    lab = DIA + "88.9 ±0.9"
    ca, sa = math.cos(math.radians(ad)), math.sin(math.radians(ad))
    txt(SA_CX - sa * 1.4 - ca * tw(lab, TH) / 2,
        SA_CY + ca * 1.4 - sa * tw(lab, TH) / 2, lab, TH, "l", rot=ad)
    datum(p2[0], p2[1], "A", ca, sa, lead=10.0, size=2.8)

    # circulo de detalle C sobre el bisel
    dcx, dcy = P(ro, 90 - ao)
    dcx, dcy = dcx - 0.8, dcy - 1.5
    dcr = 11.0
    circ(dcx, dcy, dcr, W_THIN)
    a = math.radians(-18)
    ln(dcx + dcr * math.cos(a), dcy + dcr * math.sin(a), dcx + 18, dcy - 9.0, W_THIN)
    ln(dcx + 18, dcy - 9.0, dcx + 25, dcy - 9.0, W_THIN)
    txt(dcx + 26, dcy - 10.4, "C", 4.0, "l", FONT_B)

    view_label(SA_CX, 74.0, "CORTE A-A", "ESCALA 1:1")


# ============================================================================
# DETALLE B - VENTANA 2:1
# ============================================================================
DB_S = 2.0
DB_CX, DB_CY = 95.0, 130.0


def detail_b():
    W, H, R = WIN_L * DB_S, WIN_C * DB_S, WIN_R * DB_S
    x, y = DB_CX - W / 2, DB_CY - H / 2
    poly(rrect_pts(x, y, W, H, R, 20), W_THICK)
    poly(rrect_pts(x + OFF * DB_S, y + OFF * DB_S, ROOT_L * DB_S, ROOT_C * DB_S,
                   ROOT_R * DB_S, 20), W_THIN)
    ln(x - 8, DB_CY, x + W + 8, DB_CY, W_THIN, D_CENTER)
    ln(DB_CX, y - 8, DB_CX, y + H + 8, W_THIN, D_CENTER)

    dim_h(x, x + W, y - 11.0, "60", from_y=y)
    dim_v(y, y + H, x - 11.0, "30", from_x=x)
    leader(x + R * 0.29, y + H - R * 0.29, x - 4.0, y + H + 8.0, x + 2.0, "4x R3", 2.5)
    leader(x + W - OFF * DB_S - 0.8, y + H * 0.72, x + W + 6.0, y + H + 8.0,
           x + W + 11.0, "ARISTA DE RAÍZ", 2.4)

    gw = gdt_frame(DB_CX - 12.0, y - 21.5, ["POS", "0.5", "A", "B"])
    ln(DB_CX - 12.0 + gw / 2, y - 16.9, DB_CX - 12.0 + gw / 2, y - 11.0, W_THIN)

    view_label(DB_CX, 74.0, "DETALLE B", "ESCALA 2:1")


# ============================================================================
# DETALLE C - PREPARACION DE BISEL 5:1
# ============================================================================
DC_S = 5.0
DC_XR = 380.0        # arista de raiz sobre la cara interior
DC_YIN = 125.0


def detail_c():
    t = WT * DC_S
    off = OFF * DC_S
    yin, yout = DC_YIN, DC_YIN + t
    xl = DC_XR - 40.0

    mat = [(xl, yin), (DC_XR, yin), (DC_XR - off, yout), (xl, yout)]
    poly(mat, W_THICK, fill=white)
    hatch(mat, spacing=2.2, ang=45)
    poly(mat, W_THICK)
    break_line(xl, yin, yout, 1.1, 6)

    ln(xl - 10.0, yout, DC_XR - off, yout, W_HAIR, D_PHANTOM)
    ln(xl - 10.0, yin, DC_XR, yin, W_HAIR, D_PHANTOM)
    txt(xl - 11.0, yout - 0.9, "CARA EXT.", 2.3, "r")
    txt(xl - 11.0, yin - 0.9, "CARA INT.", 2.3, "r")

    # angulo del bisel respecto de la normal a la superficie
    ex, ey = DC_XR - off * 2.8, yin + t * 2.8
    ln(DC_XR - off, yout, ex, ey, W_HAIR, D_PHANTOM)
    ln(DC_XR, yin, DC_XR, yin + t * 3.1, W_HAIR, D_PHANTOM)
    dim_ang(DC_XR, yin, t * 2.0, math.degrees(math.atan2(ey - yin, ex - DC_XR)), 90.0,
            "30°±1°", 2.5, 3.2)

    dim_v(yin, yout, xl - 34.0, "2", from_x=xl - 10.0)
    leader(DC_XR, yin, DC_XR - 8.0, yin - 12.0, DC_XR - 13.0,
           "CARA DE RAÍZ 0", 2.4, dot=True, arw=False)
    surf_finish(DC_XR - off / 2 - 1.0, yin + t * 0.5, "Ra 3.2")

    view_label(DC_XR - 22.0, 74.0, "DETALLE C", "ESCALA 5:1")


# ============================================================================
# VISTA ISOMETRICA  (modelo 3D real: malla, caras ocultas y sombreado)
# ============================================================================
IS_BOX = (288.0, 184.0, 408.0, 285.0)

# base de camara isometrica: observador en la direccion (-1,-1,1)
CAM_R = (0.70710678, -0.70710678, 0.0)          # eje horizontal de pantalla
CAM_U = (0.40824829, 0.40824829, 0.81649658)    # eje vertical de pantalla
CAM_D = (-0.57735027, -0.57735027, 0.57735027)  # hacia el observador
LIGHT = (-0.4544, -0.5756, 0.6797)              # luz normalizada


def v_dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def v_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def v_cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def v_unit(a):
    n = math.sqrt(v_dot(a, a)) or 1.0
    return (a[0] / n, a[1] / n, a[2] / n)


def convex_hull(pts):
    pts = sorted(set(pts))

    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lo = []
    for q in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], q) <= 0:
            lo.pop()
        lo.append(q)
    up = []
    for q in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], q) <= 0:
            up.pop()
        up.append(q)
    return lo[:-1] + up[:-1]


def _half_len(s, a, b, r):
    """Semilongitud axial del contorno (rectangulo redondeado) a la altura s."""
    s = abs(s)
    if s >= b:
        return None
    if s <= b - r:
        return a
    return a - r + math.sqrt(max(0.0, r * r - (s - (b - r)) ** 2))


def _contour(rad, a, b, r, n=24):
    """Contorno de la ventana sobre el cilindro de radio rad, en 3D."""
    pts = []
    xc = LEN / 2
    for cx, cs, a0, a1 in [(xc + a - r, b - r, 0, 90), (xc - a + r, b - r, 90, 180),
                           (xc - a + r, -b + r, 180, 270), (xc + a - r, -b + r, 270, 360)]:
        for i in range(n + 1):
            ang = math.radians(a0 + (a1 - a0) * i / n)
            x = cx + r * math.cos(ang)
            sp = cs + r * math.sin(ang)
            th = math.radians(90) + sp / rad
            pts.append((x, rad * math.cos(th), rad * math.sin(th)))
    return pts


def iso_view():
    ro, ri = OD / 2, ID / 2
    aw, bw, rw = WIN_L / 2, WIN_C / 2, WIN_R
    ar, br, rr = ROOT_L / 2, ROOT_C / 2, ROOT_R

    def PR(p):
        return (v_dot(p, CAM_R), v_dot(p, CAM_U))

    def dep(p):
        return v_dot(p, CAM_D)

    # muestreo angular: fino en la zona de la ventana
    ths, ang = [], 0.0
    while ang < 360.0:
        ths.append(ang)
        ang += 1.5 if 55.0 <= ang <= 125.0 else 4.0
    ths.append(360.0)

    facets = []

    def add(pts3, n, base):
        i = 0.30 + 0.70 * max(0.0, v_dot(n, LIGHT))
        g = min(1.0, i) * base
        facets.append((sum(dep(q) for q in pts3) / len(pts3),
                       [PR(q) for q in pts3],
                       Color(g * 0.94, g * 0.96, g)))

    def cyl(rad, outward, base, hl):
        for i in range(len(ths) - 1):
            t0, t1 = math.radians(ths[i]), math.radians(ths[i + 1])
            tc = (t0 + t1) / 2.0
            nrm = (0.0, math.cos(tc), math.sin(tc))
            if not outward:
                nrm = (0.0, -nrm[1], -nrm[2])
            if v_dot(nrm, CAM_D) <= 0.0:
                continue
            h = hl(rad * (tc - math.pi / 2))
            segs = [(0.0, LEN)] if h is None else \
                [(0.0, LEN / 2 - h), (LEN / 2 + h, LEN)]
            c0, s0 = rad * math.cos(t0), rad * math.sin(t0)
            c1, s1 = rad * math.cos(t1), rad * math.sin(t1)
            for xa, xb in segs:
                if xb - xa < 1e-6:
                    continue
                k = max(1, int((xb - xa) / 22.0) + 1)
                for j in range(k):
                    u0 = xa + (xb - xa) * j / k
                    u1 = xa + (xb - xa) * (j + 1) / k
                    add([(u0, c0, s0), (u1, c0, s0), (u1, c1, s1), (u0, c1, s1)],
                        nrm, base)

    # superficie exterior y superficie del taladro
    cyl(ro, True, 0.92, lambda s: _half_len(s, aw, bw, rw))
    cyl(ri, False, 0.52, lambda s: _half_len(s, ar, br, rr))

    # coronas de los extremos
    for xe, nrm in ((0.0, (-1.0, 0.0, 0.0)), (LEN, (1.0, 0.0, 0.0))):
        if v_dot(nrm, CAM_D) <= 0.0:
            continue
        for i in range(len(ths) - 1):
            t0, t1 = math.radians(ths[i]), math.radians(ths[i + 1])
            add([(xe, ro * math.cos(t0), ro * math.sin(t0)),
                 (xe, ro * math.cos(t1), ro * math.sin(t1)),
                 (xe, ri * math.cos(t1), ri * math.sin(t1)),
                 (xe, ri * math.cos(t0), ri * math.sin(t0))], nrm, 0.80)

    # superficie del bisel (reglada entre el contorno exterior y el de raiz)
    co = _contour(ro, aw, bw, rw)
    ci = _contour(ri, ar, br, rr)
    wc = (LEN / 2, 0.0, ro)
    for i in range(len(co) - 1):
        quad = [co[i], co[i + 1], ci[i + 1], ci[i]]
        nrm = v_unit(v_cross(v_sub(quad[1], quad[0]), v_sub(quad[3], quad[0])))
        cen = tuple(sum(q[k] for q in quad) / 4.0 for k in range(3))
        if v_dot(nrm, v_sub(wc, cen)) < 0:
            nrm = (-nrm[0], -nrm[1], -nrm[2])
        if v_dot(nrm, CAM_D) <= 0.0:
            continue
        add(quad, nrm, 0.72)

    # ---- encuadre ----
    allp = [q for f in facets for q in f[1]]
    xs = [q[0] for q in allp]
    ys = [q[1] for q in allp]
    bx0, by0, bx1, by1 = IS_BOX
    sc = min((bx1 - bx0 - 4) / (max(xs) - min(xs)), (by1 - by0 - 12) / (max(ys) - min(ys)))
    ox = (bx0 + bx1) / 2 - (max(xs) + min(xs)) / 2 * sc
    oy = (by0 + by1) / 2 - (max(ys) + min(ys)) / 2 * sc + 3.0

    def M(q):
        return (ox + q[0] * sc, oy + q[1] * sc)

    # ---- pintado de atras hacia adelante ----
    facets.sort(key=lambda f: f[0])
    for _, pts2, col in facets:
        c.setFillColor(col)
        c.setStrokeColor(col)
        c.setLineWidth(0.12)
        c.setDash([], 0)
        pth = c.beginPath()
        q = M(pts2[0])
        pth.moveTo(*q)
        for w in pts2[1:]:
            pth.lineTo(*M(w))
        pth.close()
        c.drawPath(pth, stroke=1, fill=1)

    # ---- aristas ----
    sil = [M(PR((x, ro * math.cos(math.radians(t)), ro * math.sin(math.radians(t)))))
           for t in range(0, 360, 2) for x in (0.0, LEN)]
    poly(convex_hull([(round(q[0], 4), round(q[1], 4)) for q in sil]), W_THICK)
    for rad in (ro, ri):
        poly([M(PR((0.0, rad * math.cos(math.radians(t)),
                    rad * math.sin(math.radians(t))))) for t in range(0, 360, 2)], W_THICK)
    poly([M(PR(q)) for q in co], W_THICK)
    poly([M(PR(q)) for q in ci], W_THIN)

    view_label((bx0 + bx1) / 2, 187.0, "VISTA ISOMÉTRICA", "SIN ESCALA")


# ============================================================================
# NOTAS
# ============================================================================
NB = (20.0, 10.0, 185.0, 62.0)


def notes_block():
    x0, y0, x1, y1 = NB
    rect(x0, y0, x1 - x0, y1 - y0, W_THICK)
    ln(x0, y1 - 7.0, x1, y1 - 7.0, W_THICK)
    txt(x0 + 3.0, y1 - 5.0, "NOTAS", 3.2, "l", FONT_B)

    notes = [
        "Material: tubo sin costura ASTM A312 Gr. TP316L, Ø88.9 × 2 mm de pared "
        "(Sch. 5S). Certificado EN 10204 3.1.",
        "Tolerancias generales ISO 2768-mK. Cotas en mm.",
        "Bisel perimetral continuo según DETALLE C, pasante hasta la cara interior "
        "(cara de raíz 0), sin interrupción en los radios.",
        "Preparación para soldadura de penetración completa según ASME B31.3.",
        "Eliminar rebabas y escoria. Aristas vivas máx. 0.3 mm.",
        "Las cotas de la ventana se miden sobre el desarrollo de la superficie "
        "exterior.",
        "Decapado y pasivado de la zona afectada según ASTM A967. No emplear "
        "herramental de acero al carbono.",
    ]
    yy, hh, lh = y1 - 11.5, 2.4, 3.35
    for i, n in enumerate(notes, 1):
        first = True
        for line_ in wrap(n, (x1 - x0) - 14.0, hh):
            if first:
                txt(x0 + 3.0, yy, "%d." % i, hh, "l", FONT_B)
                first = False
            txt(x0 + 9.0, yy, line_, hh, "l")
            yy -= lh
        yy -= 0.6


# ============================================================================
# CAJETIN ISO 7200
# ============================================================================
TB = (230.0, 10.0, 410.0, 62.0)


def proj_symbol(cx, cy, s=1.0):
    h1, h2, L = 3.4 * s, 6.0 * s, 7.6 * s
    poly([(cx - L - 2.6, cy - h1 / 2), (cx - 2.6, cy - h2 / 2),
          (cx - 2.6, cy + h2 / 2), (cx - L - 2.6, cy + h1 / 2)], W_THIN)
    ln(cx - L - 4.2, cy, cx + 10.6, cy, W_HAIR, D_CENTER)
    circ(cx + 5.2, cy, h2 / 2, W_THIN)
    circ(cx + 5.2, cy, h1 / 2, W_THIN)


def title_block():
    x0, y0, x1, y1 = TB
    rect(x0, y0, x1 - x0, y1 - y0, W_THICK)

    yA = y1 - 16.0
    yB = y0 + 18.0
    ln(x0, yA, x1, yA, W_THICK)
    ln(x0, yB, x1, yB, W_THICK)

    # ---- banda superior: emisor y denominacion ----
    xc = x0 + 74.0
    ln(xc, yA, xc, y1, W_THIN)
    txt(x0 + 3.0, y1 - 6.0, "TALLER DE TUBERÍAS", 3.4, "l", FONT_B)
    txt(x0 + 3.0, y1 - 10.4, "Y RECIPIENTES A PRESIÓN", 2.5, "l")
    txt(x0 + 3.0, y1 - 14.2, "PLANTA PETROQUÍMICA — SECTOR 3", 2.0, "l")
    txt(xc + 3.0, y1 - 5.4, "TUBO AISI 316L  Ø88.9 × 500", 3.6, "l", FONT_B)
    txt(xc + 3.0, y1 - 10.0, "VENTANA 60 × 30 (R3) CON BISEL A 30°", 2.6, "l")
    txt(xc + 3.0, y1 - 14.0, "PUERTO DE INSTRUMENTACIÓN / INJERTO", 2.1, "l")

    # ---- banda media: firmas y datos del material ----
    xm = x0 + 92.0
    ln(xm, yB, xm, yA, W_THIN)
    rh = (yA - yB) / 3.0
    firmas = [("DIBUJÓ", "M. MARTINEZ", "08/09/2026"),
              ("REVISÓ", "J. A. FERRARI", "08/09/2026"),
              ("APROBÓ", "R. QUIROGA", "08/09/2026")]
    for i, (k, v, d) in enumerate(firmas):
        yy = yA - (i + 1) * rh
        if i:
            ln(x0, yy + rh, xm, yy + rh, W_HAIR)
        txt(x0 + 2.5, yy + rh * 0.34, k, 2.2, "l", FONT_B)
        txt(x0 + 18.0, yy + rh * 0.34, v, 2.5, "l")
        txt(xm - 2.5, yy + rh * 0.34, d, 2.2, "r")
    ln(x0 + 16.5, yB, x0 + 16.5, yA, W_HAIR)
    ln(xm - 20.0, yB, xm - 20.0, yA, W_HAIR)

    datos = [("MATERIAL", "ASTM A312 TP316L"),
             ("ACABADO", "Decapado y pasivado"),
             ("MASA", "2.15 kg")]
    for i, (k, v) in enumerate(datos):
        yy = yA - (i + 1) * rh
        if i:
            ln(xm, yy + rh, x1, yy + rh, W_HAIR)
        txt(xm + 2.5, yy + rh * 0.34, k, 2.2, "l", FONT_B)
        txt(xm + 24.0, yy + rh * 0.34, v, 2.4, "l")
    ln(xm + 22.0, yB, xm + 22.0, yA, W_HAIR)

    # ---- banda inferior ----
    xs = [x0, x0 + 32.0, x0 + 68.0, x0 + 88.0, x0 + 146.0, x0 + 162.0, x1]
    for xv in xs[1:-1]:
        ln(xv, y0, xv, yB, W_THIN)

    proj_symbol(xs[0] + 16.0, y0 + 11.4)
    txt(xs[0] + 16.0, y0 + 2.4, "PROYECCIÓN ISO-E", 2.0, "c")

    txt(xs[1] + 2.5, y0 + 13.0, "TOL. GENERALES", 2.0, "l", FONT_B)
    txt(xs[1] + 2.5, y0 + 8.0, "ISO 2768-mK", 2.8, "l")
    txt(xs[1] + 2.5, y0 + 3.4, "ISO 8015", 2.0, "l")

    txt(xs[2] + 2.5, y0 + 13.0, "ESCALA", 2.0, "l", FONT_B)
    txt(xs[2] + 2.5, y0 + 5.6, "1:2", 5.0, "l", FONT_B)

    txt(xs[3] + 2.5, y0 + 13.0, "Nº DE PLANO", 2.0, "l", FONT_B)
    txt(xs[3] + 2.5, y0 + 4.8, "PT-316L-VT-001", 4.6, "l", FONT_B)

    txt(xs[4] + 2.5, y0 + 13.0, "REV.", 2.0, "l", FONT_B)
    txt(xs[4] + 8.0, y0 + 5.2, "00", 5.0, "c", FONT_B)

    txt(xs[5] + 2.5, y0 + 13.0, "FORMATO", 2.0, "l", FONT_B)
    txt(xs[5] + 2.5, y0 + 8.2, "A3", 2.8, "l")
    txt(xs[5] + 2.5, y0 + 3.6, "HOJA 1 / 1", 2.2, "l")


# ============================================================================
sheet_frame()
front_view()
iso_view()
detail_b()
section_aa()
detail_c()
notes_block()
title_block()
c.showPage()
c.save()
print("OK ->", OUT)
