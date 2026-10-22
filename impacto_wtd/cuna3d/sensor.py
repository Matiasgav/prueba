"""El palpador con acelerómetro MEMS, excitado por el movimiento 3D de la cuña.

QUÉ RESUELVE

El palpador apoya sobre la cara superior de la cuña, a 10 mm del golpe, con
1 N de precarga. El modelo 3D (cuna3d/estudio.py) da el desplazamiento de la
cuña en ese punto, w(t), para cada estado de ajuste. Acá ese w(t) mueve la
base de una cadena de masas y resortes que es el palpador, y la salida es lo
que entrega el acelerómetro después de su propia respuesta, su ruido y su
rango.

Acople en un solo sentido: el palpador empuja la cuña con ~1 N, contra los
~300 N del golpe y una cuña de 114 g; no cambia el movimiento de la cuña.

CADENA (y positivo hacia el robot, x medido desde el equilibrio estático)

    cuña w(t) ──Hertz── m_1 ──k_1,c_1── m_2 ── ... ── m_n ── F0 (precarga constante)
                punta                                    acelerómetro en m_n

    delta = delta_0 + w - x_1                  interpenetración punta-cuña
    F_c   = K_c <delta>^(3/2) (1 + chi d(delta)/dt)_+          (Hertz unilateral)
    F_i   = k_i (s_i0 + x_i - x_{i+1}) + c_i (v_i - v_{i+1})   (resorte i, compresión)
    m_1 a_1 = F_c - F_1
    m_i a_i = F_{i-1} - F_i
    m_n a_n = F_{n-1} - F0

Despegue: F_c = 0.  Se integra con RK4 a paso fijo chico frente al modo de
contacto de la punta.

ACELERÓMETRO: ADXL1004 (Analog Devices): ±500 g, 24 kHz a -3 dB, resonancia
45 kHz, 125 µg/√Hz, < 0,2 g. Se modela su resonancia como un segundo orden
poco amortiguado (Q = 30 [E]: el 3 dB a 24 kHz sale de la resonancia, no de
un polo), su ruido blanco, su saturación y un muestreo de 100 kHz.
ADXL1005: ±100 g, 23 kHz, resonancia 42 kHz, 75 µg/√Hz.
"""

from __future__ import annotations

import json
import math
import os
import pathlib
import sys
from dataclasses import dataclass, field

import numpy as np
from scipy.signal import bilinear, butter, lfilter, sosfiltfilt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

G = 9.81
RAIZ = pathlib.Path(__file__).resolve().parent.parent
PALP = RAIZ / "results" / "cuna3d" / "palpador"
OUT = RAIZ / "results" / "cuna3d"


# ---------------------------------------------------------------------------
# Acelerómetros
# ---------------------------------------------------------------------------

@dataclass
class Acelerometro:
    nombre: str
    rango_g: float
    f_res: float
    Q: float
    ruido_ug_rtHz: float
    bw_3dB: float
    masa_g: float = 0.2

    def leer(self, t: np.ndarray, a: np.ndarray, fs: float = 100e3, rng=None) -> tuple[np.ndarray, np.ndarray, bool]:
        """Aceleración real [m/s^2] -> lectura muestreada [g]."""
        dt = t[1] - t[0]
        w0 = 2 * math.pi * self.f_res
        b, aa = bilinear([w0 ** 2], [1, w0 / self.Q, w0 ** 2], fs=1 / dt)
        y = lfilter(b, aa, a / G)
        # antialias analógico (1 polo a 30 kHz) y muestreo
        b1, a1 = butter(1, 30e3, fs=1 / dt)
        y = lfilter(b1, a1, y)
        paso = max(1, int(round(1 / (fs * dt))))
        ts, ys = t[::paso], y[::paso]
        if rng is not None:
            sigma = self.ruido_ug_rtHz * 1e-6 * math.sqrt(fs / 2)
            ys = ys + rng.normal(0, sigma, ys.size)
        sat = bool(np.any(np.abs(ys) >= self.rango_g))
        return ts, np.clip(ys, -self.rango_g, self.rango_g), sat


ADXL1004 = Acelerometro("ADXL1004", 500.0, 45e3, 30.0, 125.0, 24e3)
ADXL1005 = Acelerometro("ADXL1005", 100.0, 42e3, 30.0, 75.0, 23e3)


# ---------------------------------------------------------------------------
# Palpadores
# ---------------------------------------------------------------------------

@dataclass
class Palpador:
    """Cadena punta -> resortes -> masa del acelerómetro. masas[0] es la punta."""
    nombre: str
    masas: list            # [kg], la primera es la punta (del lado de la cuña)
    k: list                # [N/m] entre masas consecutivas (len = n-1)
    zeta: list             # amortiguamiento de cada resorte, referido a la masa aguas abajo
    F0: float = 1.0
    R_punta: float = 1e-3
    chi: float = 0.236     # pérdida local en el G11, la calibrada con Leeb [s/m]
    nota: str = ""

    def Kc(self) -> float:
        Est = 1 / ((1 - 0.29 ** 2) / 210e9 + (1 - 0.2 ** 2) / 20e9)
        return 4 / 3 * Est * math.sqrt(self.R_punta)

    def c(self) -> list:
        return [2 * z * math.sqrt(k * m) for k, z, m in zip(self.k, self.zeta, self.masas[1:])]

    def k_contacto(self) -> float:
        return 1.5 * self.Kc() ** (2 / 3) * self.F0 ** (1 / 3)

    def modos(self) -> np.ndarray:
        """Frecuencias propias con la punta apoyada (contacto linealizado)."""
        n = len(self.masas)
        K = np.zeros((n, n))
        K[0, 0] += self.k_contacto()
        for i, k in enumerate(self.k):
            K[i, i] += k
            K[i + 1, i + 1] += k
            K[i, i + 1] -= k
            K[i + 1, i] -= k
        M = np.diag(self.masas)
        w2 = np.linalg.eigvals(np.linalg.solve(M, K)).real
        return np.sort(np.sqrt(np.maximum(w2, 0))) / (2 * math.pi)

    def a_despegue_g(self) -> float:
        """Invariante: el contacto se pierde cuando la cadena acelera F0 / m_total."""
        return self.F0 / sum(self.masas) / G

    def frf(self, f: np.ndarray) -> np.ndarray:
        """Transmisibilidad lineal exacta a_carro / a_cuña (contacto linealizado en F0).

        Linealizando alrededor de la precarga: rigidez de contacto k_c,
        amortiguamiento de contacto c_c = chi * F0 (Hunt-Crossley), y la
        cadena de resortes. Se resuelve (K + i w C - w^2 M) X = F(w) W.
        """
        n = len(self.masas)
        kc, cc = self.k_contacto(), self.chi * self.F0
        K = np.zeros((n, n)); C = np.zeros((n, n))
        K[0, 0] += kc; C[0, 0] += cc
        for i, (k, c) in enumerate(zip(self.k, self.c())):
            for (a, b, sg) in ((i, i, 1), (i + 1, i + 1, 1), (i, i + 1, -1), (i + 1, i, -1)):
                K[a, b] += sg * k
                C[a, b] += sg * c
        M = np.diag(self.masas)
        out = []
        for fi in np.atleast_1d(f):
            w = 2 * math.pi * fi
            F = np.zeros(n, complex); F[0] = kc + 1j * w * cc
            X = np.linalg.solve(K + 1j * w * C - w * w * M, F)
            out.append(abs(X[-1]))
        return np.array(out)

    def simular(self, t_w: np.ndarray, w: np.ndarray, vw: np.ndarray, t_fin: float | None = None,
                dt: float | None = None):
        """Integra la cadena excitada por w(t). Devuelve t, a_acel (m/s^2), F_c."""
        n = len(self.masas)
        m = self.masas
        k = self.k
        c = self.c()
        Kc, chi, F0 = self.Kc(), self.chi, self.F0
        d0 = (F0 / Kc) ** (2 / 3)
        s0 = [F0 / ki for ki in k]
        f_max = max(self.modos().max(), 1.0)
        dt = min(0.04 / f_max, 0.1e-6) if dt is None else dt
        t_fin = t_w[-1] if t_fin is None else t_fin
        N = int(t_fin / dt)
        tt = np.arange(N) * dt
        W = np.interp(tt, t_w, w)
        VW = np.interp(tt, t_w, vw)
        x = [0.0] * n
        v = [0.0] * n
        a_out = np.empty(N)
        Fc_out = np.empty(N)

        def deriv(x, v, wi, vwi):
            dl = d0 + wi - x[0]
            if dl > 0:
                Fc = Kc * dl ** 1.5 * (1 + chi * (vwi - v[0]))
                Fc = Fc if Fc > 0 else 0.0
            else:
                Fc = 0.0
            F = [k[i] * (s0[i] + x[i] - x[i + 1]) + c[i] * (v[i] - v[i + 1]) for i in range(n - 1)]
            a = [0.0] * n
            if n == 1:
                a[0] = (Fc - F0) / m[0]
            else:
                a[0] = (Fc - F[0]) / m[0]
                for i in range(1, n - 1):
                    a[i] = (F[i - 1] - F[i]) / m[i]
                a[n - 1] = (F[n - 2] - F0) / m[n - 1]
            return a, Fc

        for j in range(N):
            wi, vwi = W[j], VW[j]
            w2 = W[j + 1] if j + 1 < N else wi
            v2 = VW[j + 1] if j + 1 < N else vwi
            wm, vm = 0.5 * (wi + w2), 0.5 * (vwi + v2)
            a1, Fc = deriv(x, v, wi, vwi)
            x2 = [x[i] + 0.5 * dt * v[i] for i in range(n)]
            v2_ = [v[i] + 0.5 * dt * a1[i] for i in range(n)]
            a2, _ = deriv(x2, v2_, wm, vm)
            x3 = [x[i] + 0.5 * dt * v2_[i] for i in range(n)]
            v3 = [v[i] + 0.5 * dt * a2[i] for i in range(n)]
            a3, _ = deriv(x3, v3, wm, vm)
            x4 = [x[i] + dt * v3[i] for i in range(n)]
            v4 = [v[i] + dt * a3[i] for i in range(n)]
            a4, _ = deriv(x4, v4, w2, v2)
            a_out[j] = a1[n - 1]
            Fc_out[j] = Fc
            x = [x[i] + dt / 6 * (v[i] + 2 * v2_[i] + 2 * v3[i] + v4[i]) for i in range(n)]
            v = [v[i] + dt / 6 * (a1[i] + 2 * a2[i] + 2 * a3[i] + a4[i]) for i in range(n)]
        return tt, a_out, Fc_out


def _flexura(f0: float, m: float, m_t: float, F0: float = 1.0, R: float = 1e-3) -> float:
    """Rigidez de flexura que, en serie con el contacto, da f0 con la masa m."""
    p = Palpador("tmp", [m_t, m], [1.0], [0.0], F0, R)
    k_tot = m * (2 * math.pi * f0) ** 2
    return 1 / (1 / k_tot - 1 / p.k_contacto())


M_ACEL = 0.68e-3          # carro + acelerómetro + placa (lastrado si hace falta)
M_PUNTA = 10e-6           # bolita de acero de 1,3 mm + pegamento

DISEÑOS = [
    Palpador("rigido", [0.5e-3], [], [], nota="punta, placa y acelerómetro como una sola masa de 0,5 g; sólo el resorte de precarga"),
    Palpador("flexura", [M_PUNTA, M_ACEL], [_flexura(1250, M_ACEL, M_PUNTA)], [0.02],
             nota="flexura metálica entre la punta y el carro, f0 = 1,25 kHz, zeta = 0,02"),
    Palpador("elastomero", [M_PUNTA, M_ACEL], [_flexura(1250, M_ACEL, M_PUNTA)], [0.15],
             nota="la misma rigidez con un elastómero, zeta = 0,15"),
    Palpador("flexura_3k", [M_PUNTA, M_ACEL], [_flexura(3000, M_ACEL, M_PUNTA)], [0.02],
             nota="flexura más rígida, f0 = 3 kHz: más señal, menos margen"),
    Palpador("doble_etapa", [M_PUNTA, 0.15e-3, 0.55e-3], [6.0e4, 9.0e4], [0.03, 0.03],
             nota="dos flexuras en serie con una masa intermedia de 0,15 g: filtro de 4.º orden"),
    Palpador("flexura_600", [M_PUNTA, M_ACEL], [_flexura(600, M_ACEL, M_PUNTA)], [0.02],
             nota="flexura más blanda, f0 = 600 Hz: sigue menos el movimiento lento de la cuña libre"),
    Palpador("flexura_liviana", [M_PUNTA, 0.40e-3], [_flexura(1250, 0.40e-3, M_PUNTA)], [0.02],
             nota="f0 = 1,25 kHz con el carro en 0,40 g (ADXL1004 de 0,2 g sobre una placa mínima): despega a 255 g"),
]

# sensibilidad a la precarga del diseño de referencia
PRECARGAS = [Palpador(f"flexura_F{F0:.1f}", [M_PUNTA, M_ACEL], [_flexura(1250, M_ACEL, M_PUNTA, F0)], [0.02], F0=F0,
                      nota=f"flexura de 1,25 kHz con {F0:.1f} N de precarga") for F0 in (0.7, 1.3)]
DISEÑOS += PRECARGAS


# ---------------------------------------------------------------------------
# Rasgos de la señal
# ---------------------------------------------------------------------------

def rasgos(ts: np.ndarray, a_g: np.ndarray) -> dict:
    fs = 1 / (ts[1] - ts[0])
    win = ts <= 3e-3
    a = a_g[win]
    sos = butter(4, [150, 5000], btype="band", fs=fs, output="sos")
    ab = sosfiltfilt(sos, a)
    E = float(np.sum(a ** 2) / fs * 1e3)                    # [g^2 ms]
    Eb = float(np.sum(ab ** 2) / fs * 1e3)
    # fracción de energía por encima de 5 kHz
    A = np.abs(np.fft.rfft(a)) ** 2
    f = np.fft.rfftfreq(a.size, 1 / fs)
    alta = float(A[f > 5e3].sum() / max(A.sum(), 1e-30))
    return {"E_g2ms": E, "E_banda_g2ms": Eb, "pico_g": float(np.abs(a).max()),
            "rms_banda_g": float(np.sqrt(np.mean(ab ** 2))), "frac_alta": alta}


# ---------------------------------------------------------------------------
# Estudio
# ---------------------------------------------------------------------------

def cargar_cuna():
    from cuna3d.estudio import ESTADOS
    out = {}
    for est, _, _ in ESTADOS:
        f = PALP / f"{est.nombre}.npz"
        if f.exists():
            d = np.load(f)
            out[est.nombre] = {"t": d["t"], "w": d["uy"], "vw": d["vy"], "aw": d["ay"]}
    return out


def _uno(arg):
    pal_i, nombre, datos = arg
    pal = DISEÑOS[pal_i]
    tt, a, Fc = pal.simular(datos["t"], datos["w"], datos["vw"])
    res = {"despega": bool(np.any(Fc <= 0)), "frac_despegado": float(np.mean(Fc <= 0)),
           "Fc_min_N": float(Fc.min()), "Fc_max_N": float(Fc.max()),
           "a_real_pico_g": float(np.abs(a).max() / G)}
    for ac in (ADXL1004, ADXL1005):
        ts, y, sat = ac.leer(tt, a)
        r = rasgos(ts, y)
        # ruido: Monte Carlo sobre el rasgo de energía
        rng = np.random.default_rng(1)
        En = [rasgos(*ac.leer(tt, a, rng=rng)[:2])["E_banda_g2ms"] for _ in range(20)]
        res[ac.nombre] = {**r, "satura": sat, "E_banda_sigma": float(np.std(En)),
                          "senal_ms": np.round(y[::4][:300], 4).tolist()}
    # señal para graficar (cada 10 µs) y fuerza de contacto
    paso = max(1, int(round(10e-6 / (tt[1] - tt[0]))))
    res["t_ms"] = np.round(tt[::paso] * 1e3, 4).tolist()
    res["a_g"] = np.round(a[::paso] / G, 3).tolist()
    res["Fc_N"] = np.round(Fc[::paso], 4).tolist()
    return pal.nombre, nombre, res


def main():
    from multiprocessing import Pool
    cuna = cargar_cuna()
    tareas = [(i, n, d) for i in range(len(DISEÑOS)) for n, d in cuna.items()]
    with Pool(4) as pool:
        out = pool.map(_uno, tareas)
    res = {p.nombre: {"nota": p.nota, "masas_g": [m * 1e3 for m in p.masas], "k_N_mm": [k / 1e3 for k in p.k],
                      "zeta": p.zeta, "modos_Hz": p.modos().round(1).tolist(), "a_despegue_g": p.a_despegue_g(),
                      "k_contacto_N_um": p.k_contacto() / 1e6, "estados": {}} for p in DISEÑOS}
    for pal, est, r in out:
        res[pal]["estados"][est] = r
    for p in DISEÑOS:
        print(f"\n== {p.nombre}: modos {p.modos().round(0)} Hz, a_despegue {p.a_despegue_g():.0f} g")
        for est, r in res[p.nombre]["estados"].items():
            a4 = r["ADXL1004"]
            print(f"  {est:24s} despega={str(r['despega']):5s} ({r['frac_despegado']*100:5.2f} %)  Fc_min={r['Fc_min_N']:6.3f} N  "
                  f"pico={a4['pico_g']:7.1f} g  E_banda={a4['E_banda_g2ms']:9.3f} ± {a4['E_banda_sigma']:.4f}  "
                  f"sat1004={a4['satura']} sat1005={r['ADXL1005']['satura']}", flush=True)
    with open(OUT / "sensor.json", "w") as fh:
        json.dump({"acelerometros": {a.nombre: a.__dict__ for a in (ADXL1004, ADXL1005)}, "palpadores": res}, fh)


if __name__ == "__main__":
    main()
