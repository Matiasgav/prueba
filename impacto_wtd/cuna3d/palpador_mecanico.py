"""Diseño mecánico del palpador: geometría, masas, rigideces, modos y verificación.

Módulo de 10 x 10 mm de sección (radial x circunferencial), hermano del
módulo de impacto, con el eje del palpador a 15 mm del golpe a lo largo de
la ranura. Ejes del módulo:  x axial (a lo largo de la ranura),
y radial (positivo alejándose de la cuña), z circunferencial.

    carcasa (Al 7075) ──láminas de precarga── carro (alma de chapa + flex con ADXL1004 + aleta de Cu)
                                               │
                                     láminas de medición
                                               │
                                  vástago (tubo de Ti) + casquete esférico R 2 mm ── cuña

  * Una sola pieza de chapa de 17-7PH de 0,10 mm, fotograbada y plegada, hace
    las láminas de precarga, el alma del carro y las láminas de medición. El
    alma queda vertical: ahí se pega el flex del ADXL1004, cuyo eje sensible
    está en el plano del encapsulado.
  * Precarga: dos láminas paralelas (empotrada-guiada) que también guían el
    carro. La carcasa queda a una altura fija respecto del bore (el robot
    rueda sobre los dientes), y la flecha de las láminas da la precarga:
    F0 = k_p * delta_p. Con 10 mm de alto no entra un resorte blando de 8 mm
    de carrera, así que la precarga es un resorte real (k_p ~ 1,4 N/mm),
    no una fuerza constante.
  * Filtro: dos láminas paralelas cortas entre el carro y el vástago,
    con f0 = 1,25 kHz con la masa real del carro.
  * Amortiguamiento: aleta de cobre en el carro que se mueve dentro del
    entrehierro de dos imanes fijos a la carcasa (corrientes de Foucault).
    Amortigua el carro contra la carcasa: baja el pico de resonancia sin
    abrir un camino para la alta frecuencia, que es lo que haría un
    amortiguador en paralelo con la flexura. El acero de las láminas solo
    tiene zeta ~ 0,002.

Todo valor marcado [E] es estimado.

Uso:  python -m cuna3d.palpador_mecanico
"""

from __future__ import annotations

import json
import math
import os
import sys
import zlib
from dataclasses import asdict, dataclass
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cuna3d.clasificacion import caracteristicas  # noqa: E402
from cuna3d.distancia import D_MM, DIST, NIVELES, VARIANTES  # noqa: E402
from cuna3d.resonancia import PARCIALES  # noqa: E402
from cuna3d.sensor import ADXL1004, G, OUT, Palpador  # noqa: E402

E_AC, RHO_AC = 197e9, 7800.0          # 17-7PH CH900 (láminas)
SY_AC = 1300e6                        # fluencia 17-7PH CH900 [V, tabla de proveedor]
E_TI, RHO_TI = 114e9, 4430.0
RHO_AL, RHO_CU, RHO_FR4 = 2810.0, 8960.0, 1850.0
SIGMA_CU = 5.8e7
E_EST = 1 / ((1 - 0.29 ** 2) / 210e9 + (1 - 0.2 ** 2) / 20e9)


@dataclass
class Diseno:
    # láminas de precarga (empotrada-guiada, 2 en paralelo)
    Lp: float = 12e-3
    bp: float = 8e-3               # ancho: sube el modo lateral del carro por encima de la banda de C2
    tp: float = 0.10e-3            # chapa única de 0,10 mm para toda la pieza plegada
    sep_p: float = 5e-3            # separación radial entre las dos láminas
    delta_p: float = 1.26e-3       # flecha nominal = carrera de precarga (F0 ~ 2,3 N)
    tol_altura: float = 0.30e-3    # tolerancia de altura de la carcasa sobre la cuña [E]
    # láminas de medición
    Lm: float = 5.0e-3             # se recalcula para dar f0
    bm: float = 2.0e-3
    tm: float = 0.10e-3            # misma chapa; corta: modo propio lejos de la resonancia del ADXL1004
    sep_m: float = 1.5e-3
    f0: float = 1250.0
    # punta
    R_punta: float = 2e-3
    h_casquete: float = 0.30e-3
    rho_casquete: float = 6050.0   # circonia Y-TZP: liviana, dura, E ~ 210 GPa como el acero
    d_ext_tubo: float = 0.6e-3
    d_int_tubo: float = 0.4e-3
    L_tubo: float = 4.4e-3          # de la lámina superior de medición (y = 3,7) a la base del casquete (y = -0,7)
    rho_tubo: float = 7900.0       # inoxidable 304: se suelda con láser a las láminas de 17-7PH (acero-Ti no)
    m_collar: float = 1.5e-6       # láminas soldadas con láser al tubo: sólo el cordón y un anillo mínimo
    # carro
    m_adxl: float = 0.20e-3        # < 0,2 g según la hoja de datos: se toma el máximo
    pcb: tuple = (5e-3, 6e-3, 0.4e-3)
    m_flex: float = 10e-6          # tramo del cable plano que se mueve con el carro [E]
    m_componentes: float = 5e-6    # capacitores 0402 + adhesivo
    alma: tuple = (5e-3, 8e-3)     # alma vertical del carro (parte de la chapa plegada), alto x ancho
    rigidizador: tuple = (5e-3, 7e-3, 0.5e-3)   # respaldo de FR4 pegado al alma, debajo del flex
    aleta: tuple = (4e-3, 4e-3, 0.4e-3)   # aleta de cobre del amortiguador
    # amortiguador de Foucault
    B_entrehierro: float = 0.8     # [T] dos N52 de 4 x 4 x 2 mm sobre yugo, entrehierro 1 mm [E]
    k_geom: float = 0.40           # factor de borde de la aleta (corrientes que cierran) [E]
    zeta_lamina: float = 0.002     # amortiguamiento propio del acero [E]

    # ---- derivados -------------------------------------------------------
    def k_p(self):
        return 2 * E_AC * self.bp * self.tp ** 3 / self.Lp ** 3

    def F0(self, dz=0.0):
        return self.k_p() * (self.delta_p + dz)

    def masa_lamina_p(self):
        return RHO_AC * self.Lp * self.bp * self.tp

    def masa_lamina_m(self):
        return RHO_AC * self.Lm * self.bm * self.tm

    def masas_punta(self):
        h, R = self.h_casquete, self.R_punta
        cas = self.rho_casquete * math.pi * h * h * (3 * R - h) / 3
        tubo = self.rho_tubo * math.pi / 4 * (self.d_ext_tubo ** 2 - self.d_int_tubo ** 2) * self.L_tubo
        lam = 0.37 * 2 * self.masa_lamina_m()
        return {"casquete": cas, "tubo": tubo, "collar": self.m_collar, "láminas de medición (37 %)": lam}

    def masas_carro(self):
        a, b, c = self.pcb
        x, y, z = self.aleta
        return {"ADXL1004": self.m_adxl, "placa FR4": RHO_FR4 * a * b * c, "cable plano": self.m_flex,
                "componentes y adhesivo": self.m_componentes,
                "alma de chapa": RHO_AC * self.alma[0] * self.alma[1] * self.tp,
                "rigidizador FR4": RHO_FR4 * self.rigidizador[0] * self.rigidizador[1] * self.rigidizador[2],
                "aleta de Cu": RHO_CU * x * y * z,
                "láminas de precarga (37 %)": 0.37 * 2 * self.masa_lamina_p(),
                "láminas de medición (63 %)": 0.63 * 2 * self.masa_lamina_m()}

    def m_t(self):
        return sum(self.masas_punta().values())

    def m_c(self):
        return sum(self.masas_carro().values())

    def k_contacto(self, F0):
        Kc = 4 / 3 * E_EST * math.sqrt(self.R_punta)
        return 1.5 * Kc ** (2 / 3) * F0 ** (1 / 3)

    def ajustar_Lm(self):
        """Largo de las láminas de medición que da f0 con la masa real del carro (punta apoyada)."""
        for _ in range(20):                         # la masa del carro depende un poco de Lm
            k_tot = (self.m_c()) * (2 * math.pi * self.f0) ** 2 - self.k_p()
            k_m = 1 / (1 / k_tot - 1 / self.k_contacto(self.F0()))
            self.Lm = (2 * E_AC * self.bm * self.tm ** 3 / k_m) ** (1 / 3)
        return self.Lm

    def k_m(self):
        return 2 * E_AC * self.bm * self.tm ** 3 / self.Lm ** 3

    def c_foucault(self):
        x, y, z = self.aleta
        return self.k_geom * SIGMA_CU * self.B_entrehierro ** 2 * x * y * z

    def zeta_efectivo(self):
        k = 1 / (1 / self.k_m() + 1 / self.k_contacto(self.F0())) + self.k_p()
        return (self.c_foucault() + 2 * self.zeta_lamina * math.sqrt(self.k_m() * self.m_c())) / (2 * math.sqrt(k * self.m_c()))

    def tensiones(self):
        """Tensión de flexión máxima en las láminas (empotrada-guiada: 3 E t delta / L^2)."""
        dp = self.delta_p + self.tol_altura
        dm = self.F0(self.tol_altura) / self.k_m()
        return {"precarga_MPa": 3 * E_AC * self.tp * dp / self.Lp ** 2 / 1e6,
                "medicion_MPa": 3 * E_AC * self.tm * dm / self.Lm ** 2 / 1e6,
                "fluencia_MPa": SY_AC / 1e6}

    def modos_parasitos(self):
        """Estimaciones analíticas de los modos que no son el del filtro."""
        def lamina_ff(L, t):                       # 1.er modo propio de una lámina empotrada-empotrada
            return 22.37 / (2 * math.pi * L ** 2) * math.sqrt(E_AC * t ** 2 / (12 * RHO_AC))
        kz_m = self.k_m() * (self.bm / self.tm) ** 2
        kz_p = self.k_p() * (self.bp / self.tp) ** 2
        return {
            "punta lateral sobre láminas de medición (sin rozamiento en el contacto)": math.sqrt(kz_m / self.m_t()) / (2 * math.pi),
            "carro lateral sobre láminas de precarga": math.sqrt(kz_p / self.m_c()) / (2 * math.pi),
            "lámina de precarga, modo propio": lamina_ff(self.Lp, self.tp),
            "lámina de medición, modo propio": lamina_ff(self.Lm, self.tm),
            "punta axial sobre el contacto de Hertz": math.sqrt((self.k_contacto(self.F0()) + self.k_m()) / self.m_t()) / (2 * math.pi),
        }

    def presion_hertz(self, F):
        a = (3 * F * self.R_punta / (4 * E_EST)) ** (1 / 3)
        return 3 * F / (2 * math.pi * a * a)

    def palpador(self, dz=0.0, f_c=1.0, f_k=1.0):
        """Modelo dinámico. dz: error de altura; f_c, f_k: tolerancias de Foucault y de las láminas."""
        km = self.k_m() * f_k
        zl = self.zeta_lamina
        return Palpador("mecanico", [self.m_t(), self.m_c()], [km], [zl], F0=self.F0(dz), R_punta=self.R_punta,
                        k_suelo=self.k_p(), c_suelo=self.c_foucault() * f_c)


# ---------------------------------------------------------------------------
# Verificación dinámica contra la cuña 3D, con tolerancias de fabricación
# ---------------------------------------------------------------------------

TOLERANCIAS = {                       # (dz, f_c, f_k)
    "nominal": (0.0, 1.0, 1.0),
    "baja": (-0.30e-3, 1.0, 1.0),     # carcasa 0,3 mm más alta: menos precarga (1,9 N)
    "alta": (+0.30e-3, 1.0, 1.0),
    "Foucault -40 %": (0.0, 0.6, 1.0),
    "Foucault +40 %": (0.0, 1.4, 1.0),
    "láminas +16 %": (0.0, 1.0, 1.16),   # espesor +5 % -> k x 1,16 -> f0 +8 %
    "láminas -14 %": (0.0, 1.0, 0.86),
    "peor caso": (-0.30e-3, 0.6, 1.16),
}


def _caso(arg):
    estado, var, tol, dis = arg
    i_d = int(np.argmin(np.abs(D_MM - 15.0)))
    d = np.load(DIST / f"{estado}__{var}.npz")
    p = dis.palpador(*TOLERANCIAS[tol])
    tt, a, Fc = p.simular(d["t"], d["uy"][:, i_d], d["vy"][:, i_d])
    rng = np.random.default_rng(zlib.crc32(f"{estado}{var}{tol}".encode()))
    ts, y, sat = ADXL1004.leer(tt, a, rng=rng)
    c = caracteristicas(ts, y, float(d["E"]) * 1e3)
    return {"estado": estado, "var": var, "tol": tol, "despega": bool(np.any(Fc <= 0)),
            "Fc_min": float(Fc.min()), "Fc_max": float(Fc.max()), "satura": sat,
            "a_pico_g": float(np.abs(a).max() / G), "C1": c["C1"], "C2": c["C2"]}


def main():
    dis = Diseno()
    dis.ajustar_Lm()
    p = dis.palpador()
    print(f"Lm = {dis.Lm*1e3:.2f} mm   k_m = {dis.k_m()/1e3:.1f} N/mm   k_p = {dis.k_p()/1e3:.2f} N/mm")
    print(f"F0 = {dis.F0():.2f} N (tolerancia de altura: {dis.F0(-dis.tol_altura):.2f} a {dis.F0(dis.tol_altura):.2f} N)")
    print(f"m_punta = {dis.m_t()*1e6:.1f} mg  {[(k, round(v*1e6, 1)) for k, v in dis.masas_punta().items()]}")
    print(f"m_carro = {dis.m_c()*1e3:.3f} g  {[(k, round(v*1e6, 1)) for k, v in dis.masas_carro().items()]}")
    print(f"modos con la punta apoyada: {p.modos().round(0)} Hz ; c_Foucault = {dis.c_foucault():.3f} N s/m ; zeta = {dis.zeta_efectivo():.3f}")
    print(f"tensiones: {dis.tensiones()}")
    print(f"modos parásitos: { {k: round(v) for k, v in dis.modos_parasitos().items()} }")
    print(f"presión de Hertz: {dis.presion_hertz(dis.F0(dis.tol_altura))/1e6:.0f} MPa estática máx")
    H = p.frf(np.linspace(900, 1700, 801))
    print(f"pico del filtro: {H.max():.1f} ; a_despegue = {p.a_despegue_g():.0f} g")
    casos = [(n, v) for n in NIVELES for v in VARIANTES] + [(n, "base") for n in PARCIALES]
    tareas = [(n, v, t, dis) for n, v in casos for t in TOLERANCIAS]
    with Pool(4) as pool:
        filas = pool.map(_caso, tareas, chunksize=8)
    resumen = {}
    for t in TOLERANCIAS:
        fs = [r for r in filas if r["tol"] == t]
        iv = {n: [r["C1"] for r in fs if r["estado"] == n] for n in NIVELES}
        gaps = [min(iv[b]) - max(iv[a]) for a, b in zip(NIVELES[1:], NIVELES[2:])]
        ma = [r["C2"] for r in fs if r["estado"] == "muy_ajustada" and r["var"] in ("base", "E-10", "E+10")]
        aj = [r["C2"] for r in fs if r["estado"] == "ajustada" and r["var"] in ("base", "E-10", "E+10")]
        resumen[t] = {"despega": [f"{r['estado']}·{r['var']}" for r in fs if r["despega"]],
                      "Fc_min": min(r["Fc_min"] for r in fs), "Fc_max": max(r["Fc_max"] for r in fs),
                      "satura": any(r["satura"] for r in fs), "gaps_C1": gaps, "gap_C2_Hz": min(ma) - max(aj),
                      "C1": {n: [min(v), max(v)] for n, v in iv.items()},
                      "parciales_C1": {r["estado"]: r["C1"] for r in fs if r["estado"] in PARCIALES}}
        print(f"{t:16s} despega={len(resumen[t]['despega'])}  Fc_min={resumen[t]['Fc_min']:.2f} N  Fc_max={resumen[t]['Fc_max']:.2f} N  "
              f"satura={resumen[t]['satura']}  gaps C1={np.round(gaps, 2)}  gap C2={resumen[t]['gap_C2_Hz']:.0f} Hz", flush=True)
    out = {"diseno": {k: (list(v) if isinstance(v, tuple) else v) for k, v in asdict(dis).items()},
           "derivados": {"k_p_N_mm": dis.k_p() / 1e3, "k_m_N_mm": dis.k_m() / 1e3, "Lm_mm": dis.Lm * 1e3,
                         "F0_N": [dis.F0(-dis.tol_altura), dis.F0(), dis.F0(dis.tol_altura)],
                         "m_punta_mg": dis.m_t() * 1e6, "m_carro_g": dis.m_c() * 1e3,
                         "masas_punta_mg": {k: v * 1e6 for k, v in dis.masas_punta().items()},
                         "masas_carro_mg": {k: v * 1e6 for k, v in dis.masas_carro().items()},
                         "modos_Hz": p.modos().tolist(), "c_foucault": dis.c_foucault(), "zeta": dis.zeta_efectivo(),
                         "pico_filtro": float(H.max()), "a_despegue_g": p.a_despegue_g(),
                         "tensiones": dis.tensiones(), "parasitos_Hz": dis.modos_parasitos(),
                         "p_hertz_MPa": dis.presion_hertz(dis.F0(dis.tol_altura)) / 1e6},
           "verificacion": resumen}
    with open(OUT / "palpador_mecanico.json", "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
