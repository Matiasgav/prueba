"""Verificación estructural del eslabón regulable v5 (7075-T651 + pernos templados).

Caso de carga: fuerza F entre los ejes de acople, en la dirección del ancho (X).
  tracción  (F > 0): los ejes se separan.
  compresión (F < 0): los ejes se acercan.
  La carga entra repartida en partes iguales por los dos agujeros de cada barra (y = 5 y y = 185).

Con el carro trabado el mecanismo es isostático: la estática da todas las fuerzas internas.
La traba todavía no está definida: se supone una traba ideal en el medio del carro (entre P1 y P2),
contra la cara de la columna, y se informa la fuerza que tiene que aguantar (traba_por_N).
Para cada pieza se calcula la tensión por newton de carga y la capacidad es
  F_admisible = tensión admisible / tensión por newton
en cada modo de falla. Se informa el mínimo y qué lo gobierna.

Las secciones de las barras y del carro se miden sobre los sólidos del CAD (secciones.py).

Uso:
  python analisis.py           tabla de capacidades y rigidez, guarda salida/capacidad.json
"""

import json
import math
import os

import cadquery as cq
import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

import eslabon as E
import secciones as S

# ---------------------------------------------------------------- materiales
AL = dict(nombre="7075-T651", Sy=503.0, Su=572.0, E=71700.0)
AL["tau_y"] = 0.577 * AL["Sy"]
_CORTE_ISO8734 = {4.0: 19.7e3, 5.0: 30.8e3, 6.0: 44.2e3}   # corte doble mínimo de rotura, ISO 8734
PERNO = dict(nombre=f"pasador templado Ø{E.D_PERNO:g}", d=E.D_PERNO,
             corte_doble_rotura=_CORTE_ISO8734[E.D_PERNO],
             sigma_flexion=1500.0)           # admisible a flexión (acero templado 550-650 HV)
PERNO["corte_doble_fluencia"] = 0.75 * PERNO["corte_doble_rotura"]
F_BRY_MAX = 1.5                               # aplastamiento admisible máximo = 1,5 Sy (e/D >= 1,5)


def f_bry(e_sobre_d):
    return AL["Sy"] * min(F_BRY_MAX, max(e_sobre_d, 0.5))


# espesores de capa
T_MED = E.Z_MED[1] - E.Z_MED[0]                          # eslabones largos
T_CORTO = E.Z_CORTO[1] - E.Z_CORTO[0]               # eslabón corto (una pieza)
T_MEJ = E.Z_MED_CORTE[0]                                 # mejillas de A
T_MEJ_K = E.Z_MED_CORTE[0] - E.Z_CARRO[0]                 # mejillas del carro (bajo las alas de B)
_Z_HUECO = min(E.Z_EMBOC[0], E.Z_CABLE - E.CORTE_CABLE[-1][1])  # piso del hueco central (corto o cable)
T_ALA_C = _Z_HUECO - E.Z_MED[0]                      # alas del eslabón 1 a cada lado de la embocadura
T_MEJ_O = _Z_HUECO                                       # B a cada lado del corto en O


# ---------------------------------------------------------------- estática
def estatica(w, F=1.0):
    k = E.cinematica(w)
    u = np.array([k["s"], k["p"]]) / E.L2
    v = (k["C"] - k["O"]) / np.linalg.norm(k["C"] - k["O"])
    cr = lambda a, b: a[0] * b[1] - a[1] * b[0]
    acA = [(np.array([E.X_ACOPLE, y]), np.array([-F / 2, 0.0])) for y in (5.0, 185.0)]
    acB = [(np.array([k["xb"] + E.BWB - E.X_ACOPLE, y]), np.array([F / 2, 0.0])) for y in (5.0, 185.0)]
    Q1, Q2, P1, P2, C, O = (k[n] for n in ("Q1", "Q2", "P1", "P2", "C", "O"))
    # barra A: FQ1 (2 incógnitas) + f2*u en Q2
    Ft = sum(f for _, f in acA)
    Mt = sum(cr(r - Q1, f) for r, f in acA)
    M = np.array([[1, 0, u[0]], [0, 1, u[1]], [0, 0, cr(Q2 - Q1, u)]])
    fq1x, fq1y, f2 = np.linalg.solve(M, -np.array([Ft[0], Ft[1], Mt]))
    FQ1 = np.array([fq1x, fq1y])
    # eslabón 1: -FQ1 en Q1, -fs*v en C, FP1 en P1
    M = np.array([[-v[0], 1, 0], [-v[1], 0, 1], [cr(C - P1, -v), 0, 0]])
    fs, px, py = np.linalg.solve(M, -np.array([-FQ1[0], -FQ1[1], cr(Q1 - P1, -FQ1)]))
    FP1 = np.array([px, py])
    # carro: recibe -FP1 y -f2*u; B lo sostiene con los ganchos (X repartida) y la traba (Y)
    G1, G2 = -FP1, -f2 * u
    y_c0, y_c1 = Y_CARRO_GLOBAL(k)
    y_tr = E.Y0 + k["p"] + E.DP / 2      # traba supuesta en el medio del carro, entre P1 y P2
    x_tr = k["xb"] + E.C_CARRO
    Fp = -(G1[1] + G2[1])
    # reparto lineal q(y) = a + b (y - ym) sobre [y_c0, y_c1]; equilibrio en X y de momentos
    L = y_c1 - y_c0
    ym = (y_c0 + y_c1) / 2
    xg = k["xb"] + E.C_CARRO
    a = -(G1[0] + G2[0]) / L
    m_rest = cr(P1 - np.array([xg, ym]), G1) + cr(P2 - np.array([xg, ym]), G2) + cr(np.array([x_tr, y_tr]) - np.array([xg, ym]), np.array([0, Fp]))
    # momento de q respecto de (xg, ym): sum -(y-ym)*q dy  = -b L^3/12
    b = m_rest / (L ** 3 / 12)
    return dict(k=k, u=u, v=v, FQ1=FQ1, f2=f2, fs=fs, FP1=FP1, G1=G1, G2=G2, Fp=Fp,
                q=(a, b, y_c0, y_c1, ym, xg), tr=(x_tr, y_tr), acA=acA, acB=acB)


def Y_CARRO_GLOBAL(k):
    return E.Y0 + k["p"] + E.CARRO_Y[0], E.Y0 + k["p"] + E.CARRO_Y[1]


def cargas_ganchos(est, n=60):
    """Reacción repartida de B sobre el carro, discretizada."""
    a, b, y0, y1, ym, xg = est["q"]
    ys = np.linspace(y0, y1, n + 1)
    yc = (ys[:-1] + ys[1:]) / 2
    dy = ys[1] - ys[0]
    return [(np.array([xg, y]), np.array([(a + b * (y - ym)) * dy, 0.0])) for y in yc]


# ---------------------------------------------------------------- utilidades geométricas
def distancia_borde(poly, centro, direccion, r_agujero):
    """Distancia desde el centro del agujero hasta el borde exterior en una dirección."""
    d = np.asarray(direccion, float)
    if np.linalg.norm(d) < 1e-12:
        return 1e9
    d = d / np.linalg.norm(d)
    rayo = LineString([centro, (centro[0] + d[0] * 200, centro[1] + d[1] * 200)])
    inter = rayo.intersection(poly.boundary)
    pts = [p for p in getattr(inter, "geoms", [inter]) if not p.is_empty]
    dist = [Point(centro).distance(p) for p in pts]
    dist = [x for x in dist if x > r_agujero + 1e-3]
    return min(dist) if dist else 1e9


def contorno_capa(pieza, z):
    """Contorno 2D (shapely) de una pieza del CAD cortada a la altura z."""
    sol = pieza.val() if hasattr(pieza, "val") else pieza
    bb = sol.BoundingBox()
    plano = cq.Solid.makeBox(bb.xlen + 4, bb.ylen + 4, 0.02, cq.Vector(bb.xmin - 2, bb.ymin - 2, z - 0.01))
    cara = sol.intersect(plano)
    polys = []
    for f in cara.Faces():
        if abs(f.normalAt().z) < 0.99:
            continue
        def pts(wire):
            # recorrido ordenado del contorno (los tramos sueltos pueden venir invertidos)
            n = max(200, int(wire.Length() / 0.1))
            return [(p.x, p.y) for p in (wire.positionAt(t) for t in np.linspace(0, 1, n, endpoint=False))]
        ext = Polygon(pts(f.outerWire())).buffer(0)
        hol = [Polygon(pts(wi)).buffer(0) for wi in f.innerWires()]
        polys.append(ext.difference(unary_union(hol)) if hol else ext)
    return unary_union(polys)


# ---------------------------------------------------------------- comprobaciones locales
def orejeta(F_parte, poly, centro, t, d, nombre):
    """Agujero de perno cargado: aplastamiento, desgarro y tracción neta (por N de carga)."""
    Fm = np.linalg.norm(F_parte)
    if Fm < 1e-12:
        return {}
    e = distancia_borde(poly, centro, F_parte, d / 2)
    perp = np.array([-F_parte[1], F_parte[0]])
    e1 = distancia_borde(poly, centro, perp, d / 2)
    e2 = distancia_borde(poly, centro, -perp, d / 2)
    out = {}
    out[f"{nombre}: aplastamiento"] = f_bry(e / d) / (Fm / (d * t))
    a_desg = 2 * t * max(e - d / 2 * math.cos(math.radians(40)), 0.05)
    out[f"{nombre}: desgarro"] = AL["tau_y"] / (Fm / a_desg)
    a_neta = t * (min(e1, 30) - d / 2 + min(e2, 30) - d / 2)
    out[f"{nombre}: tracción neta"] = AL["Sy"] / (Fm / a_neta)
    return out


def perno(Fm, t_medio, t_ext, juego, nombre):
    out = {}
    out[f"perno {nombre}: corte doble"] = PERNO["corte_doble_fluencia"] / Fm
    m = Fm / 2 * (t_ext / 2 + juego + t_medio / 4)
    sigma = 32 * m / (math.pi * PERNO["d"] ** 3)
    out[f"perno {nombre}: flexión"] = PERNO["sigma_flexion"] / sigma
    return out


def pandeo(N_comp, L, I, A, nombre, K=1.0):
    if N_comp <= 1e-12:
        return {}
    r = math.sqrt(I / A)
    esb = K * L / r
    esb_c = math.sqrt(2 * math.pi ** 2 * AL["E"] / AL["Sy"])
    if esb >= esb_c:
        scr = math.pi ** 2 * AL["E"] / esb ** 2
    else:
        scr = AL["Sy"] - (AL["Sy"] * esb / (2 * math.pi)) ** 2 / AL["E"]
    return {f"{nombre}: pandeo": scr * A / N_comp}


# ---------------------------------------------------------------- eslabón 1 como viga
def secciones_eslabon1():
    """Secciones medidas sobre el sólido real (vientre engrosado y embocadura del corto).
    Se gira el eslabón 90° para cortarlo con planos y = cte: la y local queda como -x."""
    sol = E.eslabon1().val().rotate((0, 0, 0), (0, 0, 1), 90)
    out = []
    for xi in np.arange(E.R_OJO, E.L2 - E.R_OJO + 1e-9, 0.25):
        sc = S.seccion(sol, xi)
        if sc["A"] <= 0:
            continue
        ec = -sc["xc"]
        out.append((xi, sc["A"], ec, sc["I"], -sc["xmax"], -sc["xmin"]))
    return out


SEC_E1 = None


def esfuerzos_eslabon1(est):
    """N, M y tensión máxima a lo largo del eslabón 1 (por N de carga)."""
    global SEC_E1
    if SEC_E1 is None:
        SEC_E1 = secciones_eslabon1()
    u = est["u"]
    e2 = np.array([-u[1], u[0]])
    k = est["k"]
    fuerzas = [(0.0, -est["FQ1"]), (E.L1, -est["fs"] * est["v"]), (E.L2, est["FP1"])]
    peor = (0, None)
    integ = 0.0
    nmax_comp = 0.0
    for xi, A, ec, I, lo, hi in SEC_E1:
        izq = [(x, f) for x, f in fuerzas if x < xi]
        Fsum = sum((f for _, f in izq), np.zeros(2))
        N = -Fsum @ u
        # momento interno respecto del baricentro de la sección (coordenadas locales)
        M = -sum((x - xi) * (f @ e2) - (0 - ec) * (f @ u) for x, f in izq)
        s1 = N / A - M * (hi - ec) / I
        s2 = N / A - M * (lo - ec) / I
        s = max(abs(s1), abs(s2))
        if s > peor[0]:
            peor = (s, xi)
        integ += (N ** 2 / (AL["E"] * A) + M ** 2 / (AL["E"] * I)) * 0.25
        nmax_comp = max(nmax_comp, -N)
    return peor, integ, nmax_comp


# ---------------------------------------------------------------- barras y carro
TABLAS = {}


def tabla_secciones(nombre, pieza, y0, y1, paso=0.5):
    if nombre not in TABLAS:
        ys = np.arange(y0, y1 + 1e-9, paso)
        TABLAS[nombre] = (ys, [S.seccion(pieza, y) for y in ys])
    return TABLAS[nombre]


def flexion_barra(fuerzas, tabla, dx=0.0, dy=0.0):
    """Tensión máxima e integral de energía a lo largo de una pieza; fuerzas en coordenadas globales."""
    ys, secs = tabla
    peor = (0.0, None)
    integ = 0.0
    paso = ys[1] - ys[0]
    for y, sc in zip(ys, secs):
        if sc["A"] <= 1e-6:
            continue
        yg = y + dy
        xc = sc["xc"] + dx
        abajo = [(r, f) for r, f in fuerzas if r[1] < yg]
        N = -sum(f[1] for _, f in abajo)
        M = sum((r[0] - xc) * f[1] - (r[1] - yg) * f[0] for r, f in abajo)
        s = abs(N) / sc["A"] + abs(M) * sc["c"] / sc["I"]
        if s > peor[0]:
            peor = (s, y)
        integ += (N ** 2 / (AL["E"] * sc["A"]) + M ** 2 / (AL["E"] * sc["I"])) * paso
    return peor, integ


# ---------------------------------------------------------------- verificación completa
class Modelo:
    def __init__(self):
        self.A = E.barra_a()
        self.B = E.barra_b()
        self.K = E.carro()
        self.tA = tabla_secciones("A", self.A, 0.25, E.LARGO - 0.25)
        self.tB = tabla_secciones("B", self.B, 0.25, E.LARGO - 0.25)
        self.tK = tabla_secciones("carro", self.K, E.CARRO_Y[0] + 0.25, E.CARRO_Y[1] - 0.25)
        zm = sum(E.Z_MED) / 2
        zi = T_MEJ / 2
        self.cA = contorno_capa(self.A, zi)
        self.cK = contorno_capa(self.K, (E.Z_CARRO[0] + E.Z_MED_CORTE[0]) / 2)
        self.cB_O = contorno_capa(self.B, _Z_HUECO - 0.4)
        self.e1 = E.perfil_eslabon1()
        self.e2 = E.perfil_eslabon2()
        self.ec = E.perfil_corto()

    def verificar(self, w, signo=1):
        est = estatica(w, F=signo * 1.0)
        k, u, v = est["k"], est["u"], est["v"]
        caps = {}
        rig = 0.0
        d = E.D_PERNO
        R = lambda vec, ang: np.array([vec[0] * math.cos(-ang) - vec[1] * math.sin(-ang),
                                       vec[0] * math.sin(-ang) + vec[1] * math.cos(-ang)])
        al, ac = k["ang_largo"], k["ang_corto"]

        # eslabón 1: viga + ojos
        (smax, xi), integ, ncomp = esfuerzos_eslabon1(est)
        caps["eslabón 1: flexión + axial"] = AL["Sy"] / smax
        rig += integ
        caps.update(orejeta(R(-est["FQ1"], al), self.e1, (0, 0), T_MED, d, "eslabón 1 ojo Q1"))
        caps.update(orejeta(R(est["FP1"], al), self.e1, (E.L2, 0), T_MED, d, "eslabón 1 ojo P1"))
        caps.update(orejeta(R(-est["fs"] * v, al), self.e1, (E.L1, 0), 2 * T_ALA_C, d, "eslabón 1 alas en C"))
        caps.update(pandeo(ncomp, E.L1, 2 * E.R_OJO * T_MED ** 3 / 12, 2 * E.R_OJO * T_MED, "eslabón 1 fuera del plano"))

        # eslabón 2: biela
        f2 = est["f2"]
        a2 = 2 * E.R_OJO * T_MED
        rig += f2 ** 2 * E.L2 / (AL["E"] * a2)
        caps.update(orejeta(R(-f2 * u, al), self.e2, (0, 0), T_MED, d, "eslabón 2 ojo Q2"))
        caps.update(orejeta(R(f2 * u, al), self.e2, (E.L2, 0), T_MED, d, "eslabón 2 ojo P2"))
        if f2 < 0:
            caps.update(pandeo(-f2, E.L2, T_MED * (2 * E.R_OJO) ** 3 / 12, a2, "eslabón 2 en el plano"))
            caps.update(pandeo(-f2, E.L2, 2 * E.R_OJO * T_MED ** 3 / 12, a2, "eslabón 2 fuera del plano"))

        # eslabón corto: una pieza de T_CORTO
        fs = est["fs"]
        ap = 2 * E.R_CORTO * T_CORTO
        rig += fs ** 2 * E.L1 / (AL["E"] * ap)
        caps.update(orejeta(R(-fs * v, ac), self.ec, (0, 0), T_CORTO, d, "eslabón corto ojo O"))
        caps.update(orejeta(R(fs * v, ac), self.ec, (E.L1, 0), T_CORTO, d, "eslabón corto ojo C"))
        if fs < 0:
            caps.update(pandeo(-fs, E.L1, 2 * E.R_CORTO * T_CORTO ** 3 / 12, ap, "eslabón corto fuera del plano"))

        # pernos (todos en doble corte)
        pins = {"Q1": est["FQ1"], "Q2": f2 * u, "P1": est["FP1"], "P2": f2 * u, "C": fs * v, "O": fs * v}
        for n, Fv in pins.items():
            Fm = np.linalg.norm(Fv)
            if n == "C":
                caps.update(perno(Fm, T_CORTO, T_ALA_C, 0.1, n))
            elif n == "O":
                caps.update(perno(Fm, T_CORTO, T_MEJ_O, 0.1, n))
            elif n in ("P1", "P2"):
                caps.update(perno(Fm, T_MED, T_MEJ_K, 0.1, n))
            else:
                caps.update(perno(Fm, T_MED, T_MEJ, 0.1, n))

        # agujeros en mejillas de A y del carro, y en la lengüeta de B
        caps.update(orejeta(est["FQ1"] * 0.5, self.cA, (E.D_A, E.Y0), T_MEJ, d, "barra A mejilla Q1"))
        caps.update(orejeta(f2 * u * 0.5, self.cA, (E.D_A, E.Y0 + E.DP), T_MEJ, d, "barra A mejilla Q2"))
        caps.update(orejeta(est["G1"] * 0.5, self.cK, (E.E_B, 0), T_MEJ_K, d, "carro mejilla P1"))
        caps.update(orejeta(est["G2"] * 0.5, self.cK, (E.E_B, E.DP), T_MEJ_K, d, "carro mejilla P2"))
        caps.update(orejeta(fs * v * 0.5, self.cB_O, (E.E_B, E.Y0), T_MEJ_O, d, "barra B horquilla O"))

        # barra A
        fA = est["acA"] + [(k["Q1"], est["FQ1"]), (k["Q2"], f2 * u)]
        (s, y), integ = flexion_barra(fA, self.tA)
        caps["barra A: flexión + axial"] = AL["Sy"] / s
        rig += integ
        # barra B (columna) con las reacciones del carro
        ganchos = cargas_ganchos(est)
        fB = est["acB"] + [(k["O"], fs * v), (np.array(est["tr"]), np.array([0, -est["Fp"]]))]
        fB += [(r, -f) for r, f in ganchos]
        (s, y), integ = flexion_barra(fB, self.tB, dx=k["xb"])
        caps["barra B: flexión + axial"] = AL["Sy"] / s
        rig += integ
        # carro
        fK = [(k["P1"], est["G1"]), (k["P2"], est["G2"]), (np.array(est["tr"]), np.array([0, est["Fp"]]))] + ganchos
        (s, y), integ = flexion_barra(fK, self.tK, dx=k["xb"], dy=E.Y0 + k["p"])
        caps["carro: flexión + axial"] = AL["Sy"] / s
        rig += integ

        # labios de las alas (arriba y abajo) cuando los eslabones tiran del carro hacia A, carga q [N/mm]:
        #   cada labio es un voladizo de LABIO_Z que cuelga del ala, ancho LABIO_X, cargado a media altura
        a, b, y0, y1, ym, xg = est["q"]
        qmax = max(abs(a + b * (y0 - ym)), abs(a + b * (y1 - ym)))
        if qmax > 1e-12:
            q_flex = AL["Sy"] * E.LABIO_X ** 2 / 6 / (E.LABIO_Z / 2)
            q_corte = AL["tau_y"] * E.LABIO_X
            caps["labios de las alas"] = 2 * min(q_flex, q_corte) / qmax
        # agujeros de acople D5 x 10
        caps["acople: aplastamiento"] = f_bry(1.5) / (0.5 / (E.D_ACOPLE * E.P_ACOPLE))
        return caps, rig, est


def resumen_caps(caps):
    k = min(caps, key=caps.get)
    return caps[k], k


def correr(anchos=None, verbose=True):
    if anchos is None:
        anchos = [E.W_MIN + 2.5 * i for i in range(int((E.W_MAX - E.W_MIN) / 2.5) + 1)]
    m = Modelo()
    filas = []
    for w in anchos:
        ct, rig, est = m.verificar(w, +1)
        cc, _, _ = m.verificar(w, -1)
        ft, mt = resumen_caps(ct)
        fc, mc = resumen_caps(cc)
        k = est["k"]
        filas.append(dict(W=w, p=k["p"], s=k["s"], traccion=ft, modo_traccion=mt, compresion=fc, modo_compresion=mc,
                          rigidez_mm_por_kN=rig * 1000, fuerzas=dict(
                              eslabon1_Q1=float(np.linalg.norm(est["FQ1"])), eslabon2=float(est["f2"]),
                              corto=float(est["fs"]), traba=float(est["Fp"])),
                          traba_por_N=abs(float(est["Fp"])),
                          caps_traccion=ct, caps_compresion=cc))
        if verbose:
            print(f"W={w:6.1f}  tracción {ft:7.0f} N ({mt})   compresión {fc:7.0f} N ({mc})   "
                  f"rigidez {rig * 1000:.3f} mm/kN")
    return filas


if __name__ == "__main__":
    filas = correr()
    aqui = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(aqui, "salida"), exist_ok=True)
    with open(os.path.join(aqui, "salida", "capacidad.json"), "w") as fh:
        json.dump([{k: v for k, v in f.items()} for f in filas], fh, indent=1, ensure_ascii=False)
