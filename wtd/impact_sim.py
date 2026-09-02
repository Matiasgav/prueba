"""Simulación no lineal del impacto martillo <-> cuña.

Integra en el tiempo, sin ninguna de las hipótesis del modelo cerrado de
acoplamiento modal (§4.6 del brief):

  * contacto de Hertz real entre el martillo y la cuña (F = k d^1.5),
  * apoyo bilineal de la cuña (hombro unilateral + ripple precargado),
  * N modos de flexión de la cuña, incluidos los de cuerpo rígido cuando la
    cuña está suelta,
  * amortiguamiento modal del material y fricción distribuida del asiento,
  * rebote, separación y RE-IMPACTOS (el "rattle" de la cuña floja).

Sirve para dos cosas:
  1. Verificar de forma independiente la fórmula cerrada eta = eta_0 S^2.
  2. Generar las firmas temporales y espectrales de cada estado de ajuste,
     que es lo que hay que discriminar.

Integrador: velocity-Verlet con predictor de velocidad para las fuerzas
disipativas. Explícito, energía bien conservada en el tramo libre, y estable
con dt muy por debajo del período del contacto más rígido.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .hertz import contact_stiffness, hertz_impact
from .materials import G11_HERTZ, STEEL, Material
from .wedge import SupportSpec, WedgeModel, WedgeSpec


@dataclass
class HammerSpec:
    mass: float = 8.0e-3        # [kg]
    R_tip: float = 6.0e-3       # radio de la punta [m]
    tip_material: Material = STEEL
    e_local: float = 1.0        # restitución local del contacto (1 = elástico)


@dataclass
class SimConfig:
    dt: float = 5e-8
    t_end: float = 4.0e-3
    decimate: int = 20          # guardar 1 de cada N pasos
    x_strike: float | None = None   # posición del golpe (None = centro)
    x_palpator: float | None = None  # posición del acelerómetro
    n_modes: int = 20


def _hunt_crossley_alpha(e_local: float, v_i: float) -> float:
    """Coeficiente de Hunt-Crossley para una restitución local dada."""
    if e_local >= 1.0 or v_i <= 0.0:
        return 0.0
    return 3.0 * (1.0 - e_local) / (2.0 * e_local * v_i)


def simulate(wedge: WedgeSpec, support: SupportSpec, hammer: HammerSpec,
             v_impact: float, cfg: SimConfig | None = None) -> dict:
    cfg = cfg or SimConfig()
    model = WedgeModel(wedge, support, n_modes=cfg.n_modes)

    x_s = cfg.x_strike if cfg.x_strike is not None else wedge.span / 2.0
    x_p = cfg.x_palpator if cfg.x_palpator is not None else wedge.span * 0.25
    i_s = int(np.argmin(np.abs(model.x_nodes - x_s)))
    i_p = int(np.argmin(np.abs(model.x_nodes - x_p)))

    phi_s = model.Phi[i_s, :].copy()
    phi_p = model.Phi[i_p, :].copy()

    k_h = contact_stiffness(hammer.R_tip, hammer.tip_material, G11_HERTZ)
    alpha_hc = _hunt_crossley_alpha(hammer.e_local, v_impact)

    n = model.n_modes
    # Se arranca del EQUILIBRIO ESTÁTICO bajo la precarga: la cuña ajustada
    # está flectada por el ripple contra los hombros, y esa flecha inicial no
    # es cero. Ignorarla metería un transitorio espurio del tamaño del
    # impacto.
    q = model.static_equilibrium()
    q0 = q.copy()
    qd = np.zeros(n)
    w_eq = model.Phi @ q
    x_h = float(w_eq[i_s])
    v_h = v_impact
    two_zeta_w = 2.0 * support.zeta * model.omega
    w2 = model.omega ** 2

    def accel(q, qd, x_h, v_h):
        w = model.Phi @ q
        wd = model.Phi @ qd
        f_nodal = model.support_force(w, wd)
        pen = x_h - w[i_s]
        vel = v_h - wd[i_s]
        if pen > 0.0:
            Fc = k_h * pen ** 1.5
            if alpha_hc > 0.0:
                Fc *= max(0.0, 1.0 + alpha_hc * vel)
        else:
            Fc = 0.0
        f_nodal[i_s] += Fc
        a_q = model.Phi.T @ f_nodal - two_zeta_w * qd - w2 * q
        a_h = -Fc / hammer.mass
        return a_q, a_h, Fc, w, wd

    n_steps = int(cfg.t_end / cfg.dt)
    nrec = n_steps // cfg.decimate + 1
    rec_t = np.empty(nrec)
    rec_xh = np.empty(nrec)
    rec_vh = np.empty(nrec)
    rec_F = np.empty(nrec)
    rec_wp = np.empty(nrec)
    rec_ap = np.empty(nrec)
    rec_ws = np.empty(nrec)
    rec_seat = np.empty(nrec)

    a_q, a_h, Fc, w, wd = accel(q, qd, x_h, v_h)
    j = 0
    contacts = 0
    in_contact = False
    t_first_sep = None
    t_last_sep = None
    v_first_sep = None
    F_peak = 0.0
    t_contact_total = 0.0
    dt = cfg.dt

    for step in range(n_steps):
        t = step * dt
        if step % cfg.decimate == 0 and j < nrec:
            a_p = float(phi_p @ a_q)
            rec_t[j] = t
            rec_xh[j] = x_h - w_eq[i_s]
            rec_vh[j] = v_h
            rec_F[j] = Fc
            rec_wp[j] = float(phi_p @ (q - q0))
            rec_ap[j] = a_p
            rec_ws[j] = float(phi_s @ (q - q0))
            rec_seat[j] = model.contact_state(w)["frac_seated"]
            j += 1

        if Fc > 0.0:
            t_contact_total += dt
            F_peak = max(F_peak, Fc)
            if not in_contact:
                in_contact = True
                contacts += 1
        elif in_contact:
            in_contact = False
            t_last_sep = t
            if t_first_sep is None:
                t_first_sep = t
                v_first_sep = v_h

        # velocity-Verlet
        q = q + dt * qd + 0.5 * dt * dt * a_q
        x_h = x_h + dt * v_h + 0.5 * dt * dt * a_h
        qd_pred = qd + dt * a_q
        v_h_pred = v_h + dt * a_h
        a_q_new, a_h_new, Fc, w, wd = accel(q, qd_pred, x_h, v_h_pred)
        qd = qd + 0.5 * dt * (a_q + a_q_new)
        v_h = v_h + 0.5 * dt * (a_h + a_h_new)
        a_q, a_h = a_q_new, a_h_new

    rec = slice(0, j)
    E_in = 0.5 * hammer.mass * v_impact ** 2
    # La velocidad de rebote es la que tiene el martillo cuando se despide
    # DEFINITIVAMENTE, no la de la primera separación: una cuña bien asentada
    # rebota, vuelve y da un segundo empujón que casi triplica la velocidad de
    # salida. Tomar la primera separación invierte el orden de los estados.
    v_rebound = v_h
    if in_contact:
        raise RuntimeError("la simulación terminó en contacto: alargar t_end")
    E_out = 0.5 * hammer.mass * v_rebound ** 2
    E_modal = 0.5 * float(qd @ qd) + 0.5 * float(q @ (w2 * q))

    return {
        "t": rec_t[rec], "x_h": rec_xh[rec], "v_h": rec_vh[rec],
        "F": rec_F[rec], "w_palp": rec_wp[rec], "a_palp": rec_ap[rec],
        "w_strike": rec_ws[rec], "frac_seated": rec_seat[rec],
        "dt_rec": cfg.dt * cfg.decimate,
        "v_impact": v_impact,
        "v_rebound": float(abs(v_rebound)),
        "restitution": float(abs(v_rebound) / v_impact),
        "leeb": 1000.0 * float(abs(v_rebound)) / v_impact,
        "E_in_mJ": E_in * 1e3,
        "E_out_mJ": E_out * 1e3,
        "E_absorbed_mJ": (E_in - E_out) * 1e3,
        "eta_absorbed": (E_in - E_out) / E_in,
        "E_modal_end_mJ": E_modal * 1e3,
        "F_peak_N": F_peak,
        "t_contact_us": t_contact_total * 1e6,
        "t_first_sep_us": (t_first_sep or 0.0) * 1e6,
        "t_last_sep_us": (t_last_sep or 0.0) * 1e6,
        "v_first_sep_ms": float(v_first_sep) if v_first_sep is not None else 0.0,
        "n_contacts": contacts,
        "modal_f": model.f.tolist(),
        "f1_Hz": float(model.f[0]) if model.f[0] > 1.0 else
                 float(model.f[model.f > 1.0][0]) if np.any(model.f > 1.0)
                 else 0.0,
        "model": model,
    }


# --------------------------------------------------------------------------
# Extracción de características
# --------------------------------------------------------------------------

def highpass(sig: np.ndarray, dt: float, fc: float = 300.0) -> np.ndarray:
    """Pasa-altos de un polo. Modela el acoplamiento AC del acelerómetro y
    elimina la deriva de cuerpo rígido de la cuña suelta, que si no domina el
    espectro con una componente que ningún sensor real mediría."""
    a = math.exp(-2.0 * math.pi * fc * dt)
    y = np.empty_like(sig)
    prev_x = sig[0]
    prev_y = 0.0
    for i, x in enumerate(sig):
        prev_y = a * (prev_y + x - prev_x)
        prev_x = x
        y[i] = prev_y
    return y


def spectrum(sig: np.ndarray, dt: float, nfft: int | None = None):
    sig = sig - sig.mean()
    win = np.hanning(len(sig))
    n = nfft or int(2 ** math.ceil(math.log2(len(sig))))
    S = np.abs(np.fft.rfft(sig * win, n=n))
    f = np.fft.rfftfreq(n, dt)
    return f, S


def envelope_decay(sig: np.ndarray, dt: float, f0: float,
                   t_start: float = 0.3e-3) -> dict:
    """Ajuste exponencial del envolvente -> zeta efectivo."""
    i0 = int(t_start / dt)
    s = np.abs(sig[i0:])
    if len(s) < 50:
        return {"zeta_eff": float("nan"), "tau_ms": float("nan")}
    # envolvente por máximos móviles
    win = max(8, int(1.0 / max(f0, 1.0) / dt))
    nb = len(s) // win
    if nb < 4:
        return {"zeta_eff": float("nan"), "tau_ms": float("nan")}
    env = s[:nb * win].reshape(nb, win).max(axis=1)
    t = (np.arange(nb) + 0.5) * win * dt
    good = env > env.max() * 1e-3
    if good.sum() < 4:
        return {"zeta_eff": float("nan"), "tau_ms": float("nan")}
    p = np.polyfit(t[good], np.log(env[good]), 1)
    lam = -p[0]
    tau = 1.0 / lam if lam > 0 else float("inf")
    zeta = lam / (2.0 * math.pi * f0) if f0 > 0 else float("nan")
    return {"zeta_eff": float(zeta), "tau_ms": float(tau * 1e3),
            "lambda_1_s": float(lam)}


def extract_features(sim: dict, bands=((0, 1e3), (1e3, 3e3), (3e3, 8e3),
                                       (8e3, 20e3), (20e3, 60e3))) -> dict:
    dt = sim["dt_rec"]
    a = highpass(sim["a_palp"], dt, 300.0)
    f, S = spectrum(a, dt)
    P = S ** 2
    tot = P.sum() + 1e-30
    feats = {
        "f_peak_Hz": float(f[np.argmax(S)]),
        "centroid_Hz": float((f * P).sum() / tot),
        "restitution": sim["restitution"],
        "leeb": sim["leeb"],
        "eta_absorbed": sim["eta_absorbed"],
        "F_peak_N": sim["F_peak_N"],
        "t_contact_us": sim["t_contact_us"],
        "n_contacts": sim["n_contacts"],
        "a_rms": float(np.sqrt(np.mean(a ** 2))),
        "a_pk_g": float(np.abs(a).max() / 9.80665),
        "kurtosis": float(((a - a.mean()) ** 4).mean()
                          / max(((a - a.mean()) ** 2).mean() ** 2, 1e-30)),
        "frac_seated_min": float(sim["frac_seated"].min()),
        "frac_seated_end": float(sim["frac_seated"][-1]),
    }
    for lo, hi in bands:
        m = (f >= lo) & (f < hi)
        feats[f"band_{int(lo)}_{int(hi)}"] = float(P[m].sum() / tot)
    dec = envelope_decay(a, dt, feats["f_peak_Hz"])
    feats.update(dec)
    # Normalizados por energía de impacto: lo que hay que reportar si la
    # energía varía tiro a tiro.
    E = sim["E_in_mJ"]
    feats["a_rms_norm"] = feats["a_rms"] / E
    feats["a_pk_norm"] = feats["a_pk_g"] / E
    return feats
