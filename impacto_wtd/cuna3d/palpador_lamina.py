"""Palpador de una sola tira plegada (boceto del usuario, oct 2026).

    empotramiento ──── brazo horizontal (precarga) ────┐
                                                        │ tramo vertical: flex + ADXL1004
                                         cola ╲      ╱  ┘
                                               ╲  ╱  pata de la V (filtro)
                                    ───────────  V  ───────── cuña
                                              vértice (con un hoyuelo esférico acuñado)

Es la misma cadena que el diseño de láminas paralelas (precarga -> carro con el
sensor -> resorte del filtro -> punta), pero todo en flexión y sin guía: el
carro gira además de trasladarse y las patas trabajan como voladizos. Por eso
se modela como pórtico plano de vigas de Euler-Bernoulli (u, v, theta por
nodo) con masa consistente, el acelerómetro como masa excéntrica rígidamente
unida al tramo vertical, y el contacto en el vértice:

  * normal: Hertz esfera-plano (hoyuelo de radio R acuñado en el vértice),
    unilateral, con la pérdida local calibrada con Leeb;
  * tangencial: libre (el vértice desliza) o adherido, como dos casos límite.

La dinámica se integra en coordenadas modales del sistema con el contacto
linealizado en la precarga, más la corrección no lineal del contacto
(F_c(delta) - k_c delta) aplicada en el vértice. Así el despegue sale solo.

Uso:  python -m cuna3d.palpador_lamina
"""

from __future__ import annotations

import json
import math
import os
import sys
import zlib
from dataclasses import asdict, dataclass, field
from multiprocessing import Pool

import numpy as np
import scipy.linalg as sla

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cuna3d.clasificacion import caracteristicas  # noqa: E402
from cuna3d.distancia import D_MM, DIST, NIVELES, VARIANTES  # noqa: E402
from cuna3d.resonancia import PARCIALES  # noqa: E402
from cuna3d.sensor import ADXL1004, G, OUT  # noqa: E402

E_AC, RHO_AC, SY_AC = 197e9, 7800.0, 1300e6
E_EST = 1 / ((1 - 0.29 ** 2) / 210e9 + (1 - 0.2 ** 2) / 20e9)


@dataclass
class Lamina:
    t: float = 0.15e-3
    # puntos [m] y tramos (i, j, ancho). Por defecto, el boceto del usuario:
    # empotramiento, codo, pie del tramo vertical, vértice, fin de la cola
    P: list = field(default_factory=lambda: [(0.0, 7.5e-3), (14e-3, 7.5e-3), (14e-3, 2.0e-3),
                                             (12.5e-3, 0.0), (11.7e-3, 0.6e-3)])
    S: list = field(default_factory=lambda: [(0, 1, 6e-3), (1, 2, 6e-3), (2, 3, 2e-3), (3, 4, 2e-3)])
    fijos: list = field(default_factory=lambda: [0])     # puntos empotrados
    i_apex: int = 3                                     # punto de contacto con la cuña
    seg_sensor: int = 1                                 # tramo donde va pegado el sensor
    nombre: str = "boceto"
    masas_puntuales: list = field(default_factory=list)   # (punto, masa [kg])
    h_elem: float = 0.25e-3
    # acelerómetro + rigidizador + flex: masa excéntrica pegada al tramo vertical
    m_sensor: float = 0.237e-3
    e_sensor: float = -1.3e-3      # centro de masa respecto de la línea media del tramo vertical (x)
    J_sensor: float = 0.237e-3 * (5e-3 ** 2 + 1.8e-3 ** 2) / 12
    y_sensor: float = 4.75e-3      # altura del sensor sobre la cuña
    R_hoyuelo: float = 2e-3
    zeta: float = 0.002            # acero sin amortiguador agregado
    chi: float = 0.236
    tangencial: str = "libre"      # "libre", "adherido" o "coulomb" (traba hasta mu·Fc y desliza)
    mu: float = 0.3                # rozamiento punta-cuña para "coulomb"
    delta_precarga: float = None   # se calcula para F0

    # ------------------------------------------------------------------
    def malla(self):
        """Nodos (fusionados por coordenada), elementos y nodo de cada punto."""
        X, key = [], {}

        def nodo(p):
            k = (round(p[0] * 1e7), round(p[1] * 1e7))
            if k not in key:
                key[k] = len(X)
                X.append(np.array(p, float))
            return key[k]

        conn, bseg, segs_nodos = [], [], []
        for seg in self.S:
            a, c, b = seg[:3]
            tt_ = seg[3] if len(seg) > 3 and seg[3] else self.t
            mat = (seg[4], seg[5]) if len(seg) > 5 else (E_AC, RHO_AC)   # (E, densidad): acero por defecto
            pa, pc = np.array(self.P[a]), np.array(self.P[c])
            n = max(2, int(math.ceil(np.linalg.norm(pc - pa) / self.h_elem)))
            ids = [nodo(pa + (pc - pa) * k / n) for k in range(n + 1)]
            segs_nodos.append(ids)
            for k in range(n):
                conn.append((ids[k], ids[k + 1]))
                bseg.append((b, tt_) + mat)
        idx_P = [nodo(p) for p in self.P]
        self._segs = segs_nodos
        return np.array(X), conn, bseg, idx_P

    def matrices(self):
        X, conn, bseg, idx_P = self.malla()
        nn = len(X)
        K = np.zeros((3 * nn, 3 * nn))
        M = np.zeros((3 * nn, 3 * nn))
        for (i, j), (b, tk, Em, rho) in zip(conn, bseg):
            d = X[j] - X[i]
            L = np.linalg.norm(d)
            c, s = d / L
            A, I = b * tk, b * tk ** 3 / 12
            EA, EI = Em * A, Em * I
            kl = np.zeros((6, 6))
            kl[[0, 3], [0, 3]] = EA / L
            kl[0, 3] = kl[3, 0] = -EA / L
            kb = EI / L ** 3 * np.array([[12, 6 * L, -12, 6 * L], [6 * L, 4 * L * L, -6 * L, 2 * L * L],
                                         [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L * L, -6 * L, 4 * L * L]])
            ib = [1, 2, 4, 5]
            for a_, p in enumerate(ib):
                for b_, q in enumerate(ib):
                    kl[p, q] += kb[a_, b_]
            m = rho * A * L
            ml = np.zeros((6, 6))
            ml[[0, 3], [0, 3]] = m / 3
            ml[0, 3] = ml[3, 0] = m / 6
            mb = m / 420 * np.array([[156, 22 * L, 54, -13 * L], [22 * L, 4 * L * L, 13 * L, -3 * L * L],
                                     [54, 13 * L, 156, -22 * L], [-13 * L, -3 * L * L, -22 * L, 4 * L * L]])
            for a_, p in enumerate(ib):
                for b_, q in enumerate(ib):
                    ml[p, q] += mb[a_, b_]
            T = np.zeros((6, 6))
            R = np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])
            T[:3, :3] = R
            T[3:, 3:] = R
            dofs = [3 * i, 3 * i + 1, 3 * i + 2, 3 * j, 3 * j + 1, 3 * j + 2]
            K[np.ix_(dofs, dofs)] += T.T @ kl @ T
            M[np.ix_(dofs, dofs)] += T.T @ ml @ T
        # sensor: masa excéntrica en el nodo del tramo vertical más cercano a y_sensor
        vert = self._segs[self.seg_sensor]
        ns = vert[int(np.argmin(np.abs(X[vert, 1] - self.y_sensor)))]
        e = self.e_sensor
        # punto material en (x_n + e, y_n): u_p = u - theta*0, v_p = v + theta*e  (rotación chica)
        Tm = np.array([[1, 0, 0], [0, 1, e], [0, 0, 1]])
        Ms = np.diag([self.m_sensor, self.m_sensor, self.J_sensor])
        d = [3 * ns, 3 * ns + 1, 3 * ns + 2]
        M[np.ix_(d, d)] += Tm.T @ Ms @ Tm
        for ip, mp in self.masas_puntuales:
            k = idx_P[ip]
            M[3 * k, 3 * k] += mp
            M[3 * k + 1, 3 * k + 1] += mp
        self._X, self._idx_P, self._ns = X, idx_P, ns
        return K, M

    def libres(self, K):
        n = K.shape[0]
        fijos = {3 * self._idx_P[i] + d for i in self.fijos for d in range(3)}
        return np.array([k for k in range(n) if k not in fijos])

    def k_contacto(self, F0):
        Kc = 4 / 3 * E_EST * math.sqrt(self.R_hoyuelo)
        return 1.5 * Kc ** (2 / 3) * F0 ** (1 / 3), Kc

    def apex(self):
        return self._idx_P[self.i_apex]

    # ------------------------------------------------------------------
    def estatica(self, F0: float):
        """Precarga: fuerza F0 hacia arriba en el vértice. Devuelve flecha y tensiones."""
        K, M = self.matrices()
        fr = self.libres(K)
        f = np.zeros(K.shape[0])
        ia = self.apex()
        f[3 * ia + 1] = F0
        if self.tangencial == "adherido":
            # el vértice no desliza durante el apriete: restricción en x
            fr = fr[fr != 3 * ia]
        u = np.zeros(K.shape[0])
        u[fr] = np.linalg.solve(K[np.ix_(fr, fr)], f[fr])
        # tensión de flexión máxima por elemento (momento en los extremos, local)
        X, conn, bseg, _ = self.malla()
        smax, donde = 0.0, None
        for (i, j), (b, tk, Em, rho) in zip(conn, bseg):
            if Em != E_AC:             # la tensión que interesa es la del acero
                continue
            d = X[j] - X[i]
            L = np.linalg.norm(d)
            c, s = d / L
            # desplazamientos transversales locales
            v1 = -s * u[3 * i] + c * u[3 * i + 1]
            v2 = -s * u[3 * j] + c * u[3 * j + 1]
            t1, t2 = u[3 * i + 2], u[3 * j + 2]
            I = b * tk ** 3 / 12
            M1 = E_AC * I / L ** 2 * (6 * v1 + 4 * L * t1 - 6 * v2 + 2 * L * t2)
            sig = abs(M1) * (tk / 2) / I
            if sig > smax:
                smax, donde = sig, X[i]
        return {"flecha_vertice_mm": u[3 * ia + 1] * 1e3, "k_vertice_N_mm": F0 / u[3 * ia + 1] / 1e3,
                "desliz_vertice_mm": u[3 * ia] * 1e3, "giro_sensor_mrad": u[3 * self._ns + 2] * 1e3,
                "sigma_max_MPa": smax / 1e6, "donde_mm": (donde * 1e3).round(2).tolist()}

    def sistema(self, F0: float):
        """K, M reducidas (libres) con el contacto linealizado, y vectores de salida."""
        K, M = self.matrices()
        fr = self.libres(K)
        ia = self.apex()
        kc, Kc = self.k_contacto(F0)
        Kt = K.copy()
        Kt[3 * ia + 1, 3 * ia + 1] += kc
        if self.tangencial == "adherido":
            Kt[3 * ia, 3 * ia] += 0.8 * kc
        Kr, Mr = Kt[np.ix_(fr, fr)], M[np.ix_(fr, fr)]
        pos = {g: k for k, g in enumerate(fr)}
        self._ix = pos[3 * ia]         # dirección tangencial del vértice (para "coulomb")
        self._kt = 0.8 * kc
        ns = self._ns
        # salida: aceleración vertical en el punto del sensor = v + theta * e
        out = np.zeros(len(fr))
        out[pos[3 * ns + 1]] = 1.0
        out[pos[3 * ns + 2]] = self.e_sensor
        return Kr, Mr, pos[3 * ia + 1], out, kc, Kc

    def modos(self, F0: float, n: int = 12):
        Kr, Mr, iv, out, kc, _ = self.sistema(F0)
        w2, phi = sla.eigh(Kr, Mr)
        f = np.sqrt(np.maximum(w2[:n], 0)) / (2 * math.pi)
        # participación de cada modo en la lectura del sensor ante movimiento del vértice
        part = np.abs((phi[:, :n].T @ out) * (phi[iv, :n] * kc))
        return f, phi[:, :n], part / max(part.max(), 1e-30)

    def frf(self, F0: float, f: np.ndarray):
        """|a_sensor / a_cuña| para movimiento vertical de la cuña en el vértice (contacto lineal)."""
        Kr, Mr, iv, out, kc, _ = self.sistema(F0)
        w2, phi = sla.eigh(Kr, Mr)
        wn = np.sqrt(np.maximum(w2, 0))
        cc = self.chi * F0
        res = []
        for fi in np.atleast_1d(f):
            w = 2 * math.pi * fi
            # fuerza en el vértice por unidad de desplazamiento de la cuña: (kc + i w cc)
            Fq = phi[iv, :] * (kc + 1j * w * cc)
            q = Fq / (wn ** 2 - w ** 2 + 2j * self.zeta * wn * w)
            res.append(abs(out @ (phi @ q)))
        return np.array(res)

    def a_despegue_g(self, F0):
        """Masa efectiva vista desde el vértice en el modo del filtro -> F0/m (orientativo)."""
        f, phi, part = self.modos(F0, 3)
        return None

    # ------------------------------------------------------------------
    def simular(self, t_w, w, vw, F0: float, f_max_modo: float = 2e6, dt: float = 0.05e-6):
        # el corte de modos tiene que incluir el modo de la punta sobre el contacto (~100-400 kHz):
        # con 200 kHz quedaba afuera, la punta resultaba rígida contra la cuña y despegaba siempre
        Kr, Mr, iv, out, kc, Kc = self.sistema(F0)
        w2, phi = sla.eigh(Kr, Mr)
        keep = np.sqrt(np.maximum(w2, 0)) / (2 * math.pi) < f_max_modo
        phi, w2 = phi[:, keep], w2[keep]
        wn = np.sqrt(np.maximum(w2, 0))
        pa = phi[iv, :]                # forma modal en el vértice (vertical)
        po = out @ phi                 # salida del sensor en coordenadas modales
        d0 = (F0 / Kc) ** (2 / 3)
        N = int(t_w[-1] / dt)
        tt = np.arange(N) * dt
        W = np.interp(tt, t_w, w)
        VW = np.interp(tt, t_w, vw)
        q = np.zeros(phi.shape[1])
        v = np.zeros_like(q)
        a_out = np.empty(N)
        Fc_out = np.empty(N)
        two_z_w = 2 * self.zeta * wn
        coulomb = self.tangencial == "coulomb"
        px = phi[self._ix, :]
        kt, s_t = self._kt, 0.0        # resorte tangencial del contacto y punto de anclaje (se corre al deslizar)
        for j in range(N):
            x_ap = pa @ q
            v_ap = pa @ v
            dl = d0 + W[j] - x_ap
            if dl > 0:
                Fc = Kc * dl ** 1.5 * (1 + self.chi * (VW[j] - v_ap))
                Fc = Fc if Fc > 0 else 0.0
            else:
                Fc = 0.0
            # el contacto linealizado ya está en K: fuerza = (Fc - F0) + kc * (x_ap) ... respecto del equilibrio
            f_ap = (Fc - F0) + kc * x_ap
            a = -w2 * q - two_z_w * v + pa * f_ap
            if coulomb:
                x_t = px @ q
                Ft = -kt * (x_t - s_t)
                lim = self.mu * Fc
                if abs(Ft) > lim:
                    Ft = math.copysign(lim, Ft)
                    s_t = x_t + Ft / kt
                a += px * Ft
            v += dt * a if j else 0.5 * dt * a
            q += dt * v
            a_out[j] = po @ a
            Fc_out[j] = Fc
        return tt, a_out, Fc_out


# ---------------------------------------------------------------------------

def evaluar(lam: Lamina, F0: float, banda=(150, 5000)):
    i_d = int(np.argmin(np.abs(D_MM - 15.0)))
    casos = [(n, v) for n in NIVELES for v in VARIANTES] + [(n, "base") for n in PARCIALES]
    filas = []
    for n, v in casos:
        d = np.load(DIST / f"{n}__{v}.npz")
        tt, a, Fc = lam.simular(d["t"], d["uy"][:, i_d], d["vy"][:, i_d], F0)
        rng = np.random.default_rng(zlib.crc32(f"{n}{v}{F0}{lam.tangencial}".encode()))
        ts, y, sat = ADXL1004.leer(tt, a, rng=rng)
        c = caracteristicas(ts, y, float(d["E"]) * 1e3, banda)
        filas.append({"estado": n, "var": v, "despega": bool(np.any(Fc <= 0)), "Fc_min": float(Fc.min()),
                      "satura": sat, "a_pico_g": float(np.abs(a).max() / G), "C1": c["C1"], "C2": c["C2"]})
    iv = {n: [r["C1"] for r in filas if r["estado"] == n] for n in NIVELES}
    gaps = [min(iv[b]) - max(iv[a]) for a, b in zip(NIVELES[1:], NIVELES[2:])]
    ma = [r["C2"] for r in filas if r["estado"] == "muy_ajustada" and r["var"] in ("base", "E-10", "E+10")]
    aj = [r["C2"] for r in filas if r["estado"] == "ajustada" and r["var"] in ("base", "E-10", "E+10")]
    return {"despega": [f"{r['estado']}·{r['var']}" for r in filas if r["despega"]],
            "Fc_min": min(r["Fc_min"] for r in filas), "satura": any(r["satura"] for r in filas),
            "gaps_C1": gaps, "gap_C2_Hz": min(ma) - max(aj), "filas": filas}


def _eval(arg):
    lam, F0 = arg
    return evaluar(lam, F0)


def informe(lam: Lamina, F0: float):
    st = lam.estatica(F0)
    f, phi, part = lam.modos(F0)
    H = lam.frf(F0, np.array([200, 600, 1000, 1250, 1500, 3000, 18000, 30000, 43000]))
    fs = np.linspace(300, 4000, 3701)
    Hs = lam.frf(F0, fs)
    print(f"[{lam.tangencial}] F0={F0} N  estática: {st}")
    print("  modos [Hz] y participación en la lectura:", [(round(x), round(p, 3)) for x, p in zip(f, part)])
    print(f"  pico del filtro {Hs.max():.1f} a {fs[np.argmax(Hs)]:.0f} Hz ; T(200)={H[0]:.3f} T(18k)={H[6]:.2e} T(30k)={H[7]:.2e} T(43k)={H[8]:.2e}")
    return st, f, part, fs[np.argmax(Hs)], Hs.max(), H


def variantes(Lt2=2.4e-3, Lt3=2.4e-3):
    """Tres versiones de 'una tira plegada', con 0,15 mm de 17-7PH."""
    mm = 1e-3
    v1 = Lamina(nombre="boceto (V)", P=[(0, 6.5 * mm), (8.2 * mm, 6.5 * mm), (8.2 * mm, 2.0 * mm), (6.7 * mm, 0), (5.9 * mm, 0.6 * mm)],
                S=[(0, 1, 6 * mm), (1, 2, 6 * mm), (2, 3, 2 * mm), (3, 4, 2 * mm)], fijos=[0], i_apex=3, seg_sensor=1,
                y_sensor=4.25 * mm)
    v2 = Lamina(nombre="brazo + lengüeta", P=[(0, 6.0 * mm), (8.2 * mm, 6.0 * mm), (8.2 * mm, 0.5 * mm), (8.2 * mm + Lt2, 0.5 * mm)],
                S=[(0, 1, 6 * mm), (1, 2, 6 * mm), (2, 3, 2 * mm)], fijos=[0], i_apex=3, seg_sensor=1, y_sensor=3.25 * mm)
    v3 = Lamina(nombre="C plegada + lengüeta", P=[(0, 6.5 * mm), (13 * mm, 6.5 * mm), (13 * mm, 1.0 * mm), (0, 1.0 * mm), (13 * mm + Lt3, 1.0 * mm)],
                S=[(0, 1, 3 * mm), (1, 2, 6 * mm), (2, 3, 3 * mm), (2, 4, 2 * mm)], fijos=[0, 3], i_apex=4, seg_sensor=1,
                y_sensor=3.75 * mm)
    # tubo inox Ø0,6/0,4 como rectángulo equivalente (misma A e I)
    I_t = math.pi / 64 * ((0.6 * mm) ** 4 - (0.4 * mm) ** 4)
    A_t = math.pi / 4 * ((0.6 * mm) ** 2 - (0.4 * mm) ** 2)
    t_eq = math.sqrt(12 * I_t / A_t)
    b_eq = A_t / t_eq
    Lm = 3.19 * mm
    v4 = Lamina(nombre="piezas A+B (tubo)", t=0.10 * mm,
                P=[(0, 6.5 * mm), (12 * mm, 6.5 * mm), (12 * mm, 1.5 * mm), (0, 1.5 * mm),
                   (12 * mm, 3.7 * mm), (12 * mm + Lm, 3.7 * mm), (12 * mm, 2.2 * mm), (12 * mm + Lm, 2.2 * mm),
                   (12 * mm + Lm, -0.7 * mm)],
                S=[(0, 1, 8 * mm), (1, 4, 8 * mm), (4, 6, 8 * mm), (6, 2, 8 * mm), (2, 3, 8 * mm),
                   (4, 5, 2 * mm), (6, 7, 2 * mm), (5, 7, b_eq, t_eq), (7, 8, b_eq, t_eq)],
                fijos=[0, 3], i_apex=8, seg_sensor=1, y_sensor=4.5 * mm,
                m_sensor=0.269e-3, J_sensor=0.269e-3 * (5e-3 ** 2 + 1.8e-3 ** 2) / 12,
                masas_puntuales=[(8, 4.8e-6)])
    return [v1, v2, v3, v4]


def main():
    from dataclasses import replace
    F0 = 2.0
    tareas = []
    for lam in variantes():
        for tg in ("libre", "adherido"):
            l2 = replace(lam, tangencial=tg)
            print(f"\n=== {l2.nombre}")
            informe(l2, F0)
            tareas.append((l2, F0))
    with Pool(4) as pool:
        ev = pool.map(_eval, tareas)
    out = {}
    for (lam, _), e in zip(tareas, ev):
        print(f"{lam.nombre:22s} [{lam.tangencial:8s}] despega={len(e['despega']):2d}  Fc_min={e['Fc_min']:.2f} N  "
              f"satura={e['satura']}  gaps C1={np.round(e['gaps_C1'], 2)}  gap C2={e['gap_C2_Hz']:.0f} Hz")
        out[f"{lam.nombre}|{lam.tangencial}"] = {k: v for k, v in e.items() if k != "filas"}
    with open(OUT / "palpador_lamina.json", "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
