#!/usr/bin/env python3
"""Corre todos los estudios y vuelca resultados a results/*.json."""

from __future__ import annotations

import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wtd import actuator, catalog, coupling, launcher, lever, montecarlo
from wtd import reliability, sensing, springs, surge
from wtd.beam import BeamSection, euler_bernoulli_clamped, timoshenko_clamped
from wtd.beam import solve_kappa_for_frequency
from wtd.hertz import (hertz_impact, indentation_fatigue_cycles,
                       max_energy_for_pressure, hertz_plastic_correction)
from wtd.impact_sim import HammerSpec, SimConfig, extract_features, simulate
from wtd.materials import (G11_BEAM, G11_HERTZ, SI3N4, STEEL, TUNGSTEN_CARBIDE,
                           TUNGSTEN_HEAVY)
from wtd.module_design import (design_barrel_spring, design_torsion_accumulator,
                               transmission_efficiency)
from wtd.wedge import SupportSpec, WedgeModel, WedgeSpec, standard_states

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "results")
os.makedirs(OUT, exist_ok=True)
SEC = BeamSection(0.030, 0.008, 24e9, 1900.0, 5.7e9, 5.0 / 6.0)


def dump(name: str, obj) -> None:
    path = os.path.join(OUT, name + ".json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1,
                  default=lambda o: (o.tolist() if isinstance(o, np.ndarray)
                                     else float(o)))
    print(f"  -> {name}.json ({os.path.getsize(path)/1024:.0f} kB)")


def t(label):
    print(f"[{time.strftime('%H:%M:%S')}] {label}")


# ==========================================================================
def study_anchors():
    t("anclas")
    rows = []

    def add(name, got, obj, unit, tol_pct):
        err = 100.0 * (got - obj) / obj if obj else 0.0
        rows.append({"caso": name, "obtenido": got, "objetivo": obj,
                     "unidad": unit, "error_pct": err,
                     "ok": abs(err) <= tol_pct})

    v = math.sqrt(2 * 5e-3 / 4e-3)
    add("Cinemática: E=5 mJ, m=4 g → v", v, 1.5811, "m/s", 0.1)
    add("Cinemática: → p", 4e-3 * v * 1e3, 6.3246, "mN·s", 0.1)
    for L, f in ((0.050, 11691.0), (0.100, 2922.7)):
        m = euler_bernoulli_clamped(SEC, L, 80)
        add(f"Euler-Bernoulli f1, vano {L*1e3:.0f} mm", m.modes(1)[0][0], f,
            "Hz", 0.1)
    m = euler_bernoulli_clamped(SEC, 0.050, 80)
    add("Rigidez estática 192EI/L³ (50 mm)",
        m.static_stiffness_at(0.025) / 1e6, 47.19, "MN/m", 0.1)
    add("Masa modal EB / masa total",
        m.first_mode_at(0.025)["m_eff_kg"] / m.total_mass, 0.39648, "-", 0.1)
    for L, f, mm, kk in ((0.050, 9376.0, 9.77, 33.90),
                         (0.100, 2738.0, 18.56, 5.493)):
        mo = timoshenko_clamped(SEC, L, 80)
        p = mo.first_mode_at(L / 2)
        add(f"Timoshenko f1, vano {L*1e3:.0f} mm", mo.modes(1)[0][0], f, "Hz",
            0.1)
        add(f"Timoshenko m_eff, vano {L*1e3:.0f} mm", p["m_eff_kg"] * 1e3, mm,
            "g", 0.3)
        add(f"Timoshenko k_eff, vano {L*1e3:.0f} mm",
            p["k_eff_N_m"] / 1e6, kk, "MN/m", 0.3)
    for w, o in ((3.0e-3, 5.39), (3.5e-3, 6.16), (4.0e-3, 6.85)):
        add(f"Trabajo EM, ventana {w*1e3:.1f} mm",
            actuator.work_over_window(w) * 1e3, o, "mJ", 0.2)
    add("K_F desde constante de actuador",
        actuator.force_constant_from_datasheet(), 1.897, "N/A", 0.1)
    R = 4e-3
    mb = STEEL.rho * (4 / 3) * math.pi * R ** 3
    vb = math.sqrt(2 * 9.80665 * 0.070)
    Eb = 0.5 * mb * vb ** 2
    h = hertz_impact(Eb, mb, R, STEEL, G11_HERTZ)
    add("Bola ⌀8 mm: masa", mb * 1e3, 2.105, "g", 0.3)
    add("Bola ⌀8 mm: v desde 70 mm", vb, 1.172, "m/s", 0.2)
    add("Bola ⌀8 mm: energía", Eb * 1e3, 1.45, "mJ", 0.5)
    add("Bola ⌀8 mm: impulso", mb * vb * 1e3, 2.47, "mN·s", 0.5)
    add("Bola ⌀8 mm: fuerza de contacto", h.F, 165.0, "N", 1.0)
    add("Bola ⌀8 mm: presión hertziana", h.p_max / 1e6, 900.0, "MPa", 1.0)
    add("Bola ⌀8 mm: duración de contacto", h.t_c * 1e6, 55.0, "µs", 5.0)
    add("Leeb D: energía", 0.5 * 5.45e-3 * 2.05 ** 2 * 1e3, 11.5, "mJ", 0.5)
    add("Leeb D: impulso", 5.45e-3 * 2.05 * 1e3, 11.2, "mN·s", 0.5)
    W = actuator.work_over_window(3.0e-3)
    for r in lever.sweep_contact_height(W):
        y = r["y_contact_mm"]
        obj = {5.05: (3.55, 48.4, 17.8), 7.0: (5.5, 31.3, 13.6),
               8.0: (6.5, 26.4, 11.9)}[y]
        add(f"Palanca y={y}: brazo efectivo", r["r_eff_mm"], obj[0], "mm", 0.5)
        add(f"Palanca y={y}: giro", r["theta_deg"], obj[1], "°", 0.5)
        add(f"Palanca y={y}: oblicuidad", r["alpha_deg"], obj[2], "°", 1.5)
    k50 = solve_kappa_for_frequency(SEC, 0.050, 9376.0, 80)
    k100 = solve_kappa_for_frequency(SEC, 0.100, 2738.0, 80)
    dump("anchors", {"filas": rows,
                     "n_ok": sum(1 for r in rows if r["ok"]),
                     "n_total": len(rows),
                     "kappa_implicito_50mm": k50,
                     "kappa_implicito_100mm": k100,
                     "kappa_estandar": 5.0 / 6.0})


# ==========================================================================
def study_damage():
    t("límite de daño en G11")
    m = 8e-3
    rows = []
    for R_mm in [2, 3, 4, 5, 6, 8, 10, 12, 15, 20]:
        R = R_mm * 1e-3
        row = {"R_mm": R_mm}
        for label, p in (("elastico_640", 640e6), ("shakedown_1024", 1024e6),
                         ("visible_1800", 1800e6)):
            row["E_" + label + "_mJ"] = max_energy_for_pressure(
                p, m, R, STEEL, G11_HERTZ) * 1e3
        rows.append(row)
    # severidad constante: cuánta energía admite cada radio al p_max del
    # ensayo ancla de Matías (900 MPa, que se sabe que no marca)
    anchor_p = 900e6
    equiv = []
    for R_mm in [4, 6, 8, 10, 12, 15, 20]:
        E = max_energy_for_pressure(anchor_p, m, R_mm * 1e-3, STEEL,
                                    G11_HERTZ)
        equiv.append({"R_mm": R_mm, "E_mJ": E * 1e3, "factor_vs_ancla":
                      E / 1.4457e-3})
    # material de punta: casi no importa
    tips = []
    for name, mat in (("Acero", STEEL), ("Carburo de tungsteno",
                                         TUNGSTEN_CARBIDE),
                      ("Nitruro de silicio", SI3N4),
                      ("Aleación pesada W", TUNGSTEN_HEAVY)):
        hh = hertz_impact(60e-3, m, 12e-3, mat, G11_HERTZ)
        tips.append({"material": name, "E_star_GPa": hh.E_star / 1e9,
                     "p_max_MPa": hh.p_max / 1e6, "t_c_us": hh.t_c * 1e6,
                     "F_N": hh.F})
    ref = tips[0]["E_star_GPa"]
    for x in tips:
        x["delta_E_star_pct"] = 100.0 * (x["E_star_GPa"] / ref - 1.0)
    # shakedown / vida
    fat = [indentation_fatigue_cycles(p * 1e6, G11_HERTZ)
           for p in (500, 700, 900, 1100, 1400, 1800, 2200)]
    # corrección plástica
    plastic = []
    for E in (5e-3, 20e-3, 60e-3, 150e-3):
        hh = hertz_impact(E, m, 12e-3, STEEL, G11_HERTZ)
        pc = hertz_plastic_correction(hh, G11_HERTZ)
        plastic.append({"E_mJ": E * 1e3, "p_max_MPa": hh.p_max / 1e6, **pc})
    dump("damage", {"limites": rows, "severidad_constante": equiv,
                    "puntas": tips, "fatiga": fat,
                    "correccion_plastica": plastic,
                    "ancla": {"E_mJ": 1.4457, "p_max_MPa": 900.0,
                              "R_mm": 4.0}})


# ==========================================================================
def study_mass_optimum():
    t("masa óptima del proyectil")
    out = {}
    for span_mm in (50, 100):
        wedge = WedgeSpec(span=span_mm * 1e-3)
        sup = standard_states()[0]
        model = WedgeModel(wedge, sup, n_modes=6)
        f_seated = model.bounding_frequencies(1)["seated_Hz"][0]
        beam = timoshenko_clamped(SEC, span_mm * 1e-3, 80)
        p = beam.first_mode_at(span_mm * 1e-3 / 2)
        rows_by_E = {}
        for E_mJ in (10, 30, 60, 120):
            for label, f1, meff in (("empotrada (brief)", p["f_Hz"],
                                     p["m_eff_kg"]),
                                    ("asentada (modelo real)", f_seated,
                                     p["m_eff_kg"])):
                res = coupling.optimal_hammer_mass(
                    meff, f1, 12e-3, E_mJ * 1e-3, STEEL, G11_HERTZ,
                    m_grid=np.geomspace(0.3e-3, 60e-3, 260))
                key = f"{E_mJ}mJ_{label}"
                rows_by_E[key] = {"best": res["best"],
                                  "curve": res["curve"][::4],
                                  "f1_Hz": f1, "m_eff_g": meff * 1e3}
        out[f"vano_{span_mm}mm"] = {"f1_empotrada_Hz": p["f_Hz"],
                                    "f1_asentada_Hz": f_seated,
                                    "m_eff_g": p["m_eff_kg"] * 1e3,
                                    "casos": rows_by_E}
    dump("mass_optimum", out)


# ==========================================================================
def study_accumulators():
    t("acumuladores")
    barrel = []
    for E in (30, 60, 100, 150, 200):
        for s in (18, 22, 26, 30):
            r = design_barrel_spring(s * 1e-3, E * 1e-3, 8e-3,
                                     L_available=42e-3)
            if r:
                r["E_objetivo_mJ"] = E
                barrel.append(r)
    tors = []
    for rc in (3.0, 3.5, 4.0, 4.5, 5.0):
        for nf in (1, 2, 3):
            for Lm in (50, 60):
                r = design_torsion_accumulator(4.5e-3, rc * 1e-3, Lm * 1e-3,
                                               n_folds=nf)
                if r.get("feasible"):
                    r["L_modulo_mm"] = Lm
                    tors.append(r)
    # surge
    sp = design_barrel_spring(22e-3, 150e-3, 8e-3, L_available=42e-3)
    k = (sp["F2_N"] - sp["F1_N"]) / (sp["stroke_mm"] * 1e-3)
    sg = surge.surge_study(k, sp["mass_g"] * 1e-3, 8e-3,
                           sp["F2_N"] / k, N_list=(10, 20, 40, 80, 160))
    dump("accumulators", {"canon": barrel, "torsion": tors,
                          "densidad_especifica":
                              springs.specific_energy_comparison(),
                          "surge": sg, "resorte_referencia": sp,
                          "transmision": [
                              {"i": i,
                               "eff": transmission_efficiency(8e-3, 2e-3, i)}
                              for i in (0.1, 0.2, 0.364, 0.5, 0.7, 1.0, 1.5,
                                        2.0)]})


# ==========================================================================
def study_freeflight():
    t("vuelo libre")
    m = 8e-3
    W = m * 9.80665
    sen = sensing.InductiveSensor()
    forces = launcher.FreeFlightForces(
        weight=W, gravity_component=W,
        residual_magnetic=0.0,
        sensor_eddy_drag=sen.force_on_target(),
        aero_drag=launcher.aero_drag_force(4.0, 8e-3))
    magnet = launcher.magnet_wall_force(1.2, math.pi * (2e-3) ** 2, 1e-3,
                                        2e-3)
    sol = [{"t_us": tt * 1e6,
            "F_N": launcher.solenoid_residual_force(3.0, 200e-6, tt, 5e-3),
            "rel_peso": launcher.solenoid_residual_force(3.0, 200e-6, tt,
                                                         5e-3) / W}
           for tt in np.linspace(0, 1.5e-3, 25)]
    clock = launcher.clock_sensitivity(4.0, 3e-3, m, 22e-3, n=37)
    clockB = launcher.clock_sensitivity(4.0, 3e-3, m, 4.5e-3, n=37)
    vent = [launcher.size_vent(8e-3, vv, 10.0, frac_allowed=0.01)
            for vv in (3, 4, 5, 6, 8)]
    piston = []
    for c_um in (100, 150, 250, 400, 600, 1000):
        for L_mm, tag in ((2.5, "esfera ⌀8 (brief §7.1)"),
                          (14.0, "proyectil cilíndrico")):
            r = launcher.piston_effect_check(8e-3, c_um * 1e-6, 1.172,
                                             L_mm * 1e-3, 2.105e-3 * 9.80665)
            r["caso"] = tag
            r["L_engrane_mm"] = L_mm
            piston.append(r)
    flights = []
    for gap_mm in (2, 3, 4):
        for cl in (0, 90, 180):
            r = launcher.free_flight(4.0, gap_mm * 1e-3, m, clock_deg=cl)
            r["clock_deg"] = cl
            flights.append(r)
    dump("freeflight", {"fuerzas": forces.as_dict(),
                        "iman_permanente_N": magnet,
                        "iman_veces_peso": magnet / W,
                        "solenoide_residual": sol,
                        "hora_familiaA": clock, "hora_familiaB": clockB,
                        "venteo": vent, "piston": piston, "vuelos": flights})


# ==========================================================================
def study_sensing():
    t("sensado y adquisición")
    sen = sensing.InductiveSensor()
    ev = []
    for v in (1.5, 2.5, 3.5, 5.0):
        for gap in (2e-3, 3e-3, 4e-3):
            r = sen.evaluate(v, gap, 8e-3)
            r["v_ms"] = v
            r["gap_mm"] = gap * 1e3
            ev.append(r)
    res = []
    for fs_k in (100, 200, 500, 1000):
        for sx_um in (0.2, 0.5, 1.0, 2.0):
            s2 = sensing.InductiveSensor(fs=fs_k * 1e3,
                                         resolution_m=sx_um * 1e-6)
            r = s2.evaluate(4.0, 3e-3, 8e-3)
            r["fs_kHz"] = fs_k
            r["sigma_x_um"] = sx_um
            res.append(r)
    h = hertz_impact(60e-3, 8e-3, 12e-3, STEEL, G11_HERTZ)
    ring = coupling.ring_down(6094.0, 0.015)
    daq = sensing.daq_spec(30e3, h.t_c, ring["tau_s"] / 1e3 * 1e3
                           if False else ring["tau_s"])
    acc = sensing.accelerometer_spec(15000.0, 30e3)
    mic = sensing.microphone_spec(6094.0)
    f = np.geomspace(100, 100e3, 200)
    tr = sensing.palpator_transfer(0.5e-3, 5e6, f)
    dump("sensing", {"sensor": ev, "resolucion": res, "daq": daq,
                     "acelerometro": acc, "microfono": mic,
                     "ringdown": ring,
                     "t_c_us": h.t_c * 1e6,
                     "palpador": {"f_Hz": f.tolist(), "H": tr.tolist()}})


# ==========================================================================
def study_montecarlo():
    t("Monte Carlo de repetibilidad")
    pt = montecarlo.LauncherPoint()
    escenarios = {}
    for name, kw in (("traba mecánica (sear)", {"release_rel": 0.02}),
                     ("traba magnética", {"release_rel": 0.005}),
                     ("traba magnética + resorte clase 1",
                      {"release_rel": 0.005, "k_rel": 0.01,
                       "preload_rel": 0.01})):
        tol = montecarlo.ToleranceSpec(**kw)
        escenarios[name] = montecarlo.run(pt, tol, n=200_000)
    targets = montecarlo.tolerance_targets(pt, montecarlo.ToleranceSpec(),
                                           n=80_000)
    dump("montecarlo", {"escenarios": escenarios, "objetivos": targets})


# ==========================================================================
def study_reliability():
    t("confiabilidad")
    duty = reliability.duty_estimate()
    wear = [reliability.guide_wear(reliability.DESIGN_CYCLES, 0.05, F, 700.0)
            for F in (0.08, 0.3, 1.0)]
    rec = reliability.recoil_analysis(8e-3, 4.0, 2.0,
                                      hertz_impact(64e-3, 8e-3, 12e-3, STEEL,
                                                   G11_HERTZ).t_c, 50.0)
    lr = reliability.launch_reaction(64e-3, 22e-3, 8e-3, 0.6e-3)
    lrB = reliability.launch_reaction(64e-3, 4.5e-3, 8e-3, 0.01e-3)
    dump("reliability", {"duty": duty, "desgaste_guia": wear,
                         "punta": reliability.tip_wear_note(),
                         "retroceso": rec, "reaccion_lanzamiento_A": lr,
                         "reaccion_lanzamiento_B": lrB,
                         "fmea": reliability.fmea()})


# ==========================================================================
def study_catalog():
    t("catálogo de arquitecturas")
    dump("catalog", catalog.build_catalog())


# ==========================================================================
def study_wedge_states(quick: bool = False):
    t("estados de ajuste de la cuña (simulación no lineal)")
    cfg = SimConfig(t_end=3.0e-3, dt=5e-8, n_modes=24, decimate=20)
    energies = (5, 20, 60, 120) if not quick else (60,)
    out = {}
    waveforms = {}
    for span_mm in (50, 100):
        wedge = WedgeSpec(span=span_mm * 1e-3)
        rows = []
        for m_g in (4.0, 8.0):
          hammer = HammerSpec(mass=m_g * 1e-3, R_tip=12e-3)
          for st in standard_states():
            for E_mJ in energies:
                v = math.sqrt(2 * E_mJ * 1e-3 / hammer.mass)
                sim = simulate(wedge, st, hammer, v, cfg)
                fe = extract_features(sim)
                rows.append({"estado": st.label, "E_mJ": E_mJ, "m_g": m_g,
                             "precarga_N": st.preload,
                             "gap_um": st.gap * 1e6, **fe})
                if E_mJ == 60 and span_mm == 50 and m_g == 4.0:
                    n = len(sim["t"])
                    step = max(1, n // 1500)
                    waveforms[st.label] = {
                        "t_us": (sim["t"][::step] * 1e6).tolist(),
                        "a_palp_g": (sim["a_palp"][::step] / 9.80665).tolist(),
                        "F_N": (sim["F"][::step]).tolist(),
                        "w_palp_um": (sim["w_palp"][::step] * 1e6).tolist(),
                        "seated": (sim["frac_seated"][::step]).tolist(),
                    }
        out[f"vano_{span_mm}mm"] = rows
        print(f"    vano {span_mm} mm: {len(rows)} simulaciones")
    dump("wedge_states", out)
    dump("waveforms", waveforms)


# ==========================================================================
def study_separability(n_rep: int = 24):
    t(f"separabilidad de clases ({n_rep} repeticiones por estado)")
    rng = np.random.default_rng(7)
    # Maza del punto de diseño (4 g): es la que da restitución monótona.
    hammer = HammerSpec(mass=4e-3, R_tip=12e-3)
    cfg = SimConfig(t_end=2.5e-3, dt=5e-8, n_modes=20, decimate=20)
    wedge = WedgeSpec(span=0.050)
    states = standard_states()
    data = {}
    for st in states:
        feats = []
        for _ in range(n_rep):
            s2 = SupportSpec(
                preload=max(0.0, st.preload * (1 + 0.10 * rng.standard_normal())),
                k_ripple=3.0e7 * (1 + 0.20 * rng.standard_normal()),
                k_shoulder=2.0e10 * (1 + 0.30 * rng.standard_normal()),
                gap=max(0.0, st.gap * (1 + 0.15 * rng.standard_normal())),
                support_mode="ends",
                land_width=5e-3 * (1 + 0.10 * rng.standard_normal()),
                zeta=st.zeta * (1 + 0.20 * rng.standard_normal()),
                c_slide=st.c_slide * (1 + 0.25 * rng.standard_normal()),
                label=st.label)
            E = 60e-3 * (1 + 0.03 * rng.standard_normal())
            v = math.sqrt(2 * E / hammer.mass)
            xs = 0.050 * (0.5 + 0.06 * rng.standard_normal())
            c2 = SimConfig(t_end=cfg.t_end, dt=cfg.dt, n_modes=cfg.n_modes,
                           decimate=cfg.decimate, x_strike=xs)
            try:
                sim = simulate(wedge, s2, hammer, v, c2)
            except Exception as exc:      # noqa: BLE001
                print("      fallo:", exc)
                continue
            fe = extract_features(sim)
            fe["E_mJ"] = E * 1e3
            feats.append(fe)
        data[st.label] = feats
        print(f"    {st.label}: {len(feats)} ok")

    keys = ["restitution", "leeb", "eta_absorbed", "centroid_Hz",
            "f_peak_Hz", "t_c1_us", "t_contact_us", "n_contacts",
            "a_pk_norm", "zeta_eff",
            "band_3000_8000", "band_8000_20000", "kurtosis"]
    labels = list(data.keys())
    stats = {}
    for k in keys:
        stats[k] = {}
        for lab in labels:
            vals = np.array([f[k] for f in data[lab]
                             if np.isfinite(f.get(k, np.nan))])
            if vals.size:
                stats[k][lab] = {"media": float(vals.mean()),
                                 "sigma": float(vals.std()),
                                 "n": int(vals.size)}
    # d' entre estados adyacentes
    dprime = {}
    for k in keys:
        row = []
        for a, b in zip(labels[:-1], labels[1:]):
            sa, sb = stats[k].get(a), stats[k].get(b)
            if not sa or not sb:
                continue
            pooled = math.sqrt(0.5 * (sa["sigma"] ** 2 + sb["sigma"] ** 2))
            d = abs(sa["media"] - sb["media"]) / pooled if pooled > 0 else \
                float("inf")
            row.append({"par": f"{a[:2]}→{b[:2]}", "d_prime": d})
        dprime[k] = row
    # d' extremos
    dext = {}
    for k in keys:
        sa, sb = stats[k].get(labels[0]), stats[k].get(labels[-1])
        if sa and sb:
            pooled = math.sqrt(0.5 * (sa["sigma"] ** 2 + sb["sigma"] ** 2))
            dext[k] = (abs(sa["media"] - sb["media"]) / pooled
                       if pooled > 0 else float("inf"))
    dump("separability", {"stats": stats, "dprime_adyacentes": dprime,
                          "dprime_extremos": dext, "labels": labels,
                          "n_rep": n_rep,
                          "raw": {k: [{kk: v[kk] for kk in keys + ["E_mJ"]}
                                      for v in vs]
                                  for k, vs in data.items()}})


# ==========================================================================
def study_lever_baseline():
    t("línea base: palanca en L del informe")
    W3 = actuator.work_over_window(3.0e-3)
    W4 = actuator.work_over_window(4.0e-3)
    dump("lever_baseline", {
        "altura_contacto": lever.sweep_contact_height(W3),
        "diametro_bola": lever.sweep_ball_diameter(W3),
        "W_3mm_mJ": W3 * 1e3, "W_4mm_mJ": W4 * 1e3,
        "curva_KF": {"x_mm": (actuator.LAH04_CURVE_X * 1e3).tolist(),
                     "F_N": actuator.LAH04_CURVE_F.tolist()},
        "termico": actuator.thermal_budget(1.5, 6.6e-3, 5.0),
    })


# ==========================================================================
def study_mechanisms():
    """Separa los DOS mecanismos que compiten en el índice de rebote.

    (1) Transferencia elástica a los modos de la cuña. Crece cuando la cuña
        está bien acoplada (ajustada) -> la cuña AJUSTADA absorbe MÁS.
    (2) Disipación en la junta por micro-deslizamiento. Es cero con la junta
        totalmente pegada (no desliza) y cero con la junta totalmente suelta
        (no hay fuerza normal): tiene un MÁXIMO a precarga intermedia.

    Los dos empujan el índice de rebote en sentidos distintos, y por eso el
    índice solo no es monótono con el ajuste. Se corre la escalera de estados
    con c_slide = 0 para aislar (1).
    """
    t("mecanismos que compiten en el rebote")
    hammer = HammerSpec(mass=4e-3, R_tip=12e-3)
    cfg = SimConfig(t_end=3.0e-3, dt=5e-8, n_modes=24, decimate=20)
    out = {}
    for span_mm in (50, 100):
        wedge = WedgeSpec(span=span_mm * 1e-3)
        rows = []
        for st in standard_states():
            for tag, cs, zt in (("completo", st.c_slide, st.zeta),
                                ("sin fricción de junta", 0.0, 0.012),
                                ("solo fricción (contacto rígido)",
                                 st.c_slide, 0.012)):
                s2 = SupportSpec(preload=st.preload, k_ripple=3.0e7,
                                 k_shoulder=(2.0e12 if tag.startswith("solo")
                                             else 2.0e10),
                                 gap=st.gap, support_mode="ends",
                                 zeta=zt, c_slide=cs, label=st.label)
                v = math.sqrt(2 * 60e-3 / hammer.mass)
                sim = simulate(wedge, s2, hammer, v, cfg)
                fe = extract_features(sim)
                rows.append({"estado": st.label, "variante": tag,
                             "precarga_N": st.preload,
                             "restitution": sim["restitution"],
                             "eta_absorbida": sim["eta_absorbed"],
                             "f_peak_Hz": fe["f_peak_Hz"],
                             "centroid_Hz": fe["centroid_Hz"],
                             "t_c_us": sim["t_contact_us"],
                             "n_contacts": sim["n_contacts"]})
        out[f"vano_{span_mm}mm"] = rows
        print(f"    vano {span_mm} mm: {len(rows)} simulaciones")

    # cruce con la fórmula cerrada del brief §4.6
    cross = []
    for span_mm in (50, 100):
        wedge = WedgeSpec(span=span_mm * 1e-3)
        st = standard_states()[0]
        model = WedgeModel(wedge, st, n_modes=6)
        f_seated = model.bounding_frequencies(1)["seated_Hz"][0]
        beam = timoshenko_clamped(SEC, span_mm * 1e-3, 80)
        p = beam.first_mode_at(span_mm * 1e-3 / 2)
        for E_mJ in (5, 20, 60, 120):
            for m_g in (2, 4, 8, 16):
                v = math.sqrt(2 * E_mJ * 1e-3 / (m_g * 1e-3))
                h = HammerSpec(mass=m_g * 1e-3, R_tip=12e-3)
                sim = simulate(wedge, st, h, v, cfg)
                hz = hertz_impact(E_mJ * 1e-3, m_g * 1e-3, 12e-3, STEEL,
                                  G11_HERTZ)
                cf = coupling.modal_response(E_mJ * 1e-3, m_g * 1e-3,
                                             p["m_eff_kg"], f_seated, hz.t_c)
                cross.append({
                    "vano_mm": span_mm, "E_mJ": E_mJ, "m_g": m_g,
                    "eta_cerrada": cf["eta"],
                    "eta_simulada": sim["eta_absorbed"],
                    "e_cerrada": cf["restitution_from_eta"],
                    "e_simulada": sim["restitution"],
                    "t_c_hertz_us": hz.t_c * 1e6,
                    "t_c_sim_us": sim["t_contact_us"],
                    "f1_Hz": f_seated})
    out["cruce_formula_cerrada"] = cross
    dump("mechanisms", out)


# ==========================================================================
def study_wave_return():
    """¿Puede el rebote VER el estado del apoyo?

    El martillo sólo se entera de cómo está apoyada la cuña si la onda de
    flexión llega al apoyo y vuelve ANTES de que termine el contacto:

        t_c  >=  2 * L_al_apoyo / c_flexion(f)

    con c_flexion = sqrt(omega) * (EI/rhoA)^(1/4). Si no vuelve a tiempo, el
    impacto es indistinguible del de una cuña infinita y el índice de rebote
    NO discrimina, por más limpia que sea la medición.
    """
    t("tiempo de retorno de la onda vs duración del contacto")
    import numpy as _np
    EI = SEC.EI
    rhoA = SEC.rhoA
    rows = []
    for span_mm in (50, 100):
        for x_rel in (0.5, 0.3, 0.15, 0.08):
            L_sup = span_mm * 1e-3 * min(x_rel, 1 - x_rel)
            for m_g, R_mm in ((2, 12), (4, 12), (8, 12), (8, 20), (16, 20)):
                h = hertz_impact(60e-3, m_g * 1e-3, R_mm * 1e-3, STEEL,
                                 G11_HERTZ)
                f_dom = 0.5 / h.t_c
                c_flex = math.sqrt(2 * math.pi * f_dom) * (EI / rhoA) ** 0.25
                t_ret = 2.0 * L_sup / c_flex
                rows.append({"vano_mm": span_mm, "x_rel": x_rel,
                             "L_apoyo_mm": L_sup * 1e3, "m_g": m_g,
                             "R_mm": R_mm, "t_c_us": h.t_c * 1e6,
                             "f_dom_kHz": f_dom / 1e3,
                             "c_flex_ms": c_flex,
                             "t_retorno_us": t_ret * 1e6,
                             "ratio": h.t_c / t_ret,
                             "discrimina": h.t_c >= t_ret})
    dump("wave_return", rows)


# ==========================================================================
def study_mass_sim():
    """Masa óptima del proyectil, medida CON LA SIMULACIÓN.

    La fórmula cerrada del brief §4.6 predice que el óptimo está en
    m = m_eff. La simulación muestra que a esa masa la propia fórmula ya no
    vale: el contacto dura más que la respuesta de la cuña, la cuña devuelve
    la energía y la transferencia se derrumba.
    """
    t("masa óptima por simulación")
    cfg = SimConfig(t_end=3.0e-3, dt=5e-8, n_modes=24, decimate=20)
    masses = [1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0, 24.0]
    out = {}
    for span_mm in (50, 100):
        wedge = WedgeSpec(span=span_mm * 1e-3)
        rows = []
        for st_i in (0, 5):
            st = standard_states()[st_i]
            for E_mJ in (20, 60):
                for m_g in masses:
                    h = HammerSpec(mass=m_g * 1e-3, R_tip=12e-3)
                    v = math.sqrt(2 * E_mJ * 1e-3 / h.mass)
                    sim = simulate(wedge, st, h, v, cfg)
                    fe = extract_features(sim)
                    rows.append({
                        "estado": st.label, "E_mJ": E_mJ, "m_g": m_g,
                        "v_ms": v,
                        "eta": sim["eta_absorbed"],
                        "E_abs_mJ": sim["E_absorbed_mJ"],
                        "restitution": sim["restitution"],
                        "t_c1_us": fe["t_c1_us"],
                        "a_pk_g": fe["a_pk_g"],
                        "p_max_MPa": hertz_impact(E_mJ * 1e-3, m_g * 1e-3,
                                                  12e-3, STEEL,
                                                  G11_HERTZ).p_max / 1e6,
                        "f_knee_kHz": 0.5 / (fe["t_c1_us"] * 1e-6) / 1e3,
                    })
        out[f"vano_{span_mm}mm"] = rows
        print(f"    vano {span_mm} mm: {len(rows)} simulaciones")
    dump("mass_sim", out)


# ==========================================================================
def study_strike_position():
    t("posición del golpe a lo largo del vano")
    cfg = SimConfig(t_end=3.0e-3, dt=5e-8, n_modes=24, decimate=20)
    out = {}
    for span_mm in (50, 100):
        wedge = WedgeSpec(span=span_mm * 1e-3)
        rows = []
        for x_rel in (0.5, 0.4, 0.3, 0.2, 0.12):
            for st_i in (0, 3, 6):
                st = standard_states()[st_i]
                for m_g in (4.0, 8.0):
                    h = HammerSpec(mass=m_g * 1e-3, R_tip=12e-3)
                    v = math.sqrt(2 * 60e-3 / h.mass)
                    c2 = SimConfig(t_end=cfg.t_end, dt=cfg.dt,
                                   n_modes=cfg.n_modes,
                                   decimate=cfg.decimate,
                                   x_strike=span_mm * 1e-3 * x_rel,
                                   x_palpator=span_mm * 1e-3 * 0.5)
                    sim = simulate(wedge, st, h, v, c2)
                    fe = extract_features(sim)
                    rows.append({"x_rel": x_rel, "estado": st.label,
                                 "m_g": m_g,
                                 "restitution": sim["restitution"],
                                 "eta": sim["eta_absorbed"],
                                 "t_c1_us": fe["t_c1_us"],
                                 "kurtosis": fe["kurtosis"],
                                 "f_peak_Hz": fe["f_peak_Hz"]})
        out[f"vano_{span_mm}mm"] = rows
        print(f"    vano {span_mm} mm: {len(rows)} simulaciones")
    dump("strike_position", out)



# ==========================================================================
def study_wave_return_sim():
    """Calibra el criterio de retorno de onda CONTRA la simulación.

    Para cada combinación se corre la cuña ajustada y la floja con la
    fricción de junta ANULADA, de modo que la única diferencia posible sea
    elástica. La separación que quede es lo que el índice de rebote puede
    ver por mecánica pura.
    """
    t("criterio de retorno de onda, calibrado por simulación")
    cfg = SimConfig(t_end=3.0e-3, dt=5e-8, n_modes=24, decimate=20)
    EI, rhoA = SEC.EI, SEC.rhoA
    rows = []
    combos = []
    for span_mm in (30, 50, 70, 100, 140):
        for m_g, R_mm in ((2, 12), (4, 12), (8, 12), (16, 20), (24, 20)):
            combos.append((span_mm, m_g, R_mm, 0.5))
    for span_mm in (100,):
        for x_rel in (0.3, 0.2, 0.12):
            for m_g, R_mm in ((4, 12), (16, 20)):
                combos.append((span_mm, m_g, R_mm, x_rel))
    for span_mm, m_g, R_mm, x_rel in combos:
        wedge = WedgeSpec(span=span_mm * 1e-3)
        h = HammerSpec(mass=m_g * 1e-3, R_tip=R_mm * 1e-3)
        v = math.sqrt(2 * 60e-3 / h.mass)
        es = []
        for st_i in (0, 6):
            st = standard_states()[st_i]
            s2 = SupportSpec(preload=st.preload, k_ripple=3.0e7,
                             k_shoulder=2.0e10, gap=st.gap,
                             support_mode="ends", zeta=0.012, c_slide=0.0,
                             label=st.label)
            c2 = SimConfig(t_end=cfg.t_end, dt=cfg.dt, n_modes=cfg.n_modes,
                           decimate=cfg.decimate,
                           x_strike=span_mm * 1e-3 * x_rel)
            sim = simulate(wedge, s2, h, v, c2)
            es.append((sim["restitution"], sim["t_c1_us"]))
        t_c = es[0][1] * 1e-6
        f_dom = 0.5 / t_c
        c_flex = math.sqrt(2 * math.pi * f_dom) * (EI / rhoA) ** 0.25
        L_sup = span_mm * 1e-3 * min(x_rel, 1 - x_rel)
        t_ret = 2.0 * L_sup / c_flex
        rows.append({"vano_mm": span_mm, "m_g": m_g, "R_mm": R_mm,
                     "x_rel": x_rel, "t_c_us": t_c * 1e6,
                     "t_ret_us": t_ret * 1e6, "ratio": t_c / t_ret,
                     "e_ajustada": es[0][0], "e_floja": es[1][0],
                     "delta_e": abs(es[0][0] - es[1][0]),
                     "c_flex_ms": c_flex})
    rows.sort(key=lambda r: r["ratio"])
    dump("wave_return_sim", rows)


# ==========================================================================
def study_sensitivity():
    """¿Sobreviven las conclusiones a los parámetros que están estimados?

    Las tres conclusiones del lado medición descansan sobre parámetros [E]:
        k_ripple    rigidez del resorte ripple      (supuesta 3e7 N/m^2)
        k_shoulder  rigidez de contacto del hombro  (supuesta 2e10 N/m^2)
        c_slide     fricción de junta               (supuesta 0 a 3e4)
        land_width  ancho del apoyo                 (supuesto 5 mm)
    Se barre cada uno sobre un rango amplio y se comprueba si:
      (a) t_c1 sigue siendo monótona creciente con la soltura,
      (b) la curtosis sigue siendo monótona creciente,
      (c) la restitución sigue siendo NO monótona.
    Una conclusión que no sobrevive al barrido no es una conclusión.
    """
    t("sensibilidad de las conclusiones a los parámetros estimados")
    hammer = HammerSpec(mass=4e-3, R_tip=12e-3)
    cfg = SimConfig(t_end=3.0e-3, dt=5e-8, n_modes=24, decimate=20)
    wedge = WedgeSpec(span=0.050)
    base = standard_states()

    variantes = []
    for v in (0.5e7, 1e7, 3e7, 1e8, 3e8):
        variantes.append(("k_ripple", v, {"k_ripple": v}))
    for v in (2e9, 6e9, 2e10, 6e10, 2e11):
        variantes.append(("k_shoulder", v, {"k_shoulder": v}))
    for v in (0.0, 0.25, 1.0, 4.0):
        variantes.append(("c_slide x", v, {"_cs": v}))
    for v in (2e-3, 3.5e-3, 5e-3, 8e-3, 12e-3):
        variantes.append(("land_width", v, {"land_width": v}))
    for v in (0.005, 0.012, 0.03, 0.06):
        variantes.append(("zeta", v, {"_z": v}))

    out = []
    for nombre, val, kw in variantes:
        serie = []
        for st in base:
            kwargs = dict(preload=st.preload, k_ripple=3.0e7,
                          k_shoulder=2.0e10, gap=st.gap,
                          support_mode="ends", land_width=5e-3,
                          zeta=st.zeta, c_slide=st.c_slide, label=st.label)
            for k, v2 in kw.items():
                if k == "_cs":
                    kwargs["c_slide"] = st.c_slide * v2
                elif k == "_z":
                    kwargs["zeta"] = v2
                else:
                    kwargs[k] = v2
            s2 = SupportSpec(**kwargs)
            v_imp = math.sqrt(2 * 60e-3 / hammer.mass)
            sim = simulate(wedge, s2, hammer, v_imp, cfg)
            fe = extract_features(sim)
            serie.append({"estado": st.label, "e": sim["restitution"],
                          "t_c1": fe["t_c1_us"], "kurt": fe["kurtosis"],
                          "eta": sim["eta_absorbed"],
                          "f_peak": fe["f_peak_Hz"]})

        def mono(key, sign=+1):
            v = [r[key] for r in serie]
            d = [sign * (v[i + 1] - v[i]) for i in range(len(v) - 1)]
            # se admite una violación chica (menos del 3 % del rango total)
            rango = max(v) - min(v)
            tol = 0.03 * rango
            return all(x >= -tol for x in d)

        out.append({
            "parametro": nombre, "valor": val,
            "serie": serie,
            "tc1_monotona": mono("t_c1"),
            "kurt_monotona": mono("kurt"),
            "e_monotona": mono("e") or mono("e", -1),
            "tc1_rango_us": max(r["t_c1"] for r in serie) - min(r["t_c1"] for r in serie),
            "kurt_rango": max(r["kurt"] for r in serie) - min(r["kurt"] for r in serie),
            "e_rango": max(r["e"] for r in serie) - min(r["e"] for r in serie),
        })
        print(f"    {nombre}={val:<10.4g} tc1_mon={out[-1]['tc1_monotona']} "
              f"kurt_mon={out[-1]['kurt_monotona']} e_mon={out[-1]['e_monotona']} "
              f"(rangos: tc1 {out[-1]['tc1_rango_us']:.1f} us, kurt {out[-1]['kurt_rango']:.0f}, "
              f"e {out[-1]['e_rango']:.3f})")
    dump("sensitivity", out)


# ==========================================================================
def study_low_energy():
    """¿Alcanza un golpe de 5 mJ con la palanca en L y el voice coil?

    Compara la configuración que el usuario ya tiene en mente (bola de
    2.105 g de la palanca en L, 5 mJ) contra el punto de diseño de vuelo
    libre (4 g, 60 mJ), y contra la misma bola con punta de radio grande.

    La pregunta de fondo es si la separación entre clases depende de la
    ENERGÍA ABSOLUTA del golpe o no. Resultado: no depende — 5 mJ separa
    tanto como 60 mJ.
    """
    t("¿alcanza 5 mJ? separabilidad a baja energía")
    rng = np.random.default_rng(11)
    cfg = SimConfig(t_end=2.5e-3, dt=5e-8, n_modes=20, decimate=20)
    wedge = WedgeSpec(span=0.050)
    casos = [
        ("Palanca en L · bola 2.1 g · 5 mJ · R=4mm", 2.105e-3, 4e-3, 5e-3),
        ("Palanca en L · bola 2.1 g · 5 mJ · R=12mm", 2.105e-3, 12e-3, 5e-3),
        ("Vuelo libre · 4 g · 60 mJ · R=12mm", 4.0e-3, 12e-3, 60e-3),
    ]
    keys = ("restitution", "kurtosis", "t_c1_us", "eta_absorbed")
    out = {}
    for nombre, m, R, E in casos:
        h = HammerSpec(mass=m, R_tip=R)
        data = {}
        for st in standard_states():
            feats = []
            for _ in range(20):
                s2 = SupportSpec(
                    preload=max(0.0, st.preload * (1 + 0.10 * rng.standard_normal())),
                    k_ripple=3.0e7 * (1 + 0.20 * rng.standard_normal()),
                    k_shoulder=2.0e10 * (1 + 0.30 * rng.standard_normal()),
                    gap=max(0.0, st.gap * (1 + 0.15 * rng.standard_normal())),
                    support_mode="ends",
                    land_width=5e-3 * (1 + 0.10 * rng.standard_normal()),
                    zeta=st.zeta * (1 + 0.20 * rng.standard_normal()),
                    c_slide=st.c_slide * (1 + 0.25 * rng.standard_normal()),
                    label=st.label)
                Ei = E * (1 + 0.03 * rng.standard_normal())
                c2 = SimConfig(t_end=cfg.t_end, dt=cfg.dt, n_modes=cfg.n_modes,
                               decimate=cfg.decimate,
                               x_strike=0.050 * (0.5 + 0.06 * rng.standard_normal()))
                sim = simulate(wedge, s2, h, math.sqrt(2 * Ei / h.mass), c2)
                feats.append(extract_features(sim))
            data[st.label] = feats
        labs = list(data.keys())
        res = {}
        for k in keys:
            stt = {}
            for l in labs:
                v = np.array([f[k] for f in data[l]
                              if np.isfinite(f.get(k, np.nan))])
                stt[l] = {"media": float(v.mean()), "sigma": float(v.std())}
            adj = []
            for a, b in zip(labs[:-1], labs[1:]):
                pool = math.sqrt(0.5 * (stt[a]["sigma"] ** 2 + stt[b]["sigma"] ** 2))
                adj.append(abs(stt[a]["media"] - stt[b]["media"]) / pool
                           if pool > 0 else float("inf"))
            pool = math.sqrt(0.5 * (stt[labs[0]]["sigma"] ** 2
                                    + stt[labs[-1]]["sigma"] ** 2))
            res[k] = {"stats": stt, "adj": adj,
                      "ext": (abs(stt[labs[0]]["media"] - stt[labs[-1]]["media"])
                              / pool if pool > 0 else float("inf"))}
        res["comb"] = [math.sqrt(sum(res[k]["adj"][i] ** 2
                                     for k in ("restitution", "kurtosis", "t_c1_us")))
                       for i in range(len(labs) - 1)]
        res["m_g"] = m * 1e3
        res["R_mm"] = R * 1e3
        res["E_mJ"] = E * 1e3
        out[nombre] = res
        print(f"    {nombre}: d'ext(e)={res['restitution']['ext']:.2f} "
              f"d'ext(kurt)={res['kurtosis']['ext']:.1f}")

    # Umbral de despegue: ¿a partir de qué energía la cuña AJUSTADA despega?
    umbral = []
    for E_mJ in (2, 5, 10, 20, 40, 80):
        h = HammerSpec(mass=2.105e-3, R_tip=12e-3)
        sim = simulate(wedge, standard_states()[0], h,
                       math.sqrt(2 * E_mJ * 1e-3 / h.mass),
                       SimConfig(t_end=2e-3, dt=5e-8, n_modes=24, decimate=20))
        s0 = float(sim["frac_seated"][0])
        sm = float(sim["frac_seated"].min())
        umbral.append({"E_mJ": E_mJ, "v_ms": sim["v_impact"],
                       "F_peak_N": sim["F_peak_N"], "seat_ini": s0,
                       "seat_min": sm, "despega": sm < s0 - 0.01})
    out["_umbral_despegue"] = umbral
    print("    umbral de despegue de la cuña ajustada: entre "
          + str([u["E_mJ"] for u in umbral if not u["despega"]][-1])
          + " y " + str([u["E_mJ"] for u in umbral if u["despega"]][0]) + " mJ")

    # Corriente necesaria en la palanca en L para cada energía
    W1 = actuator.work_over_window(3.0e-3)
    d = lever.LeverDesign(y_contact=5.05e-3)
    corriente = []
    for I in (1.0, 1.5, 1.7, 2.0, 2.5, 3.0):
        r = d.solve(W1 * I)
        th = actuator.thermal_budget(I, 6.6e-3, 5.0)
        corriente.append({"I_A": I, "W_em_mJ": W1 * I * 1e3,
                          "E_maza_mJ": r["E_hammer_mJ"], "v_ms": r["v_ms"],
                          "p_normal_mNs": r["p_normal_mNs"],
                          "frac_actuador": r["frac_actuator"],
                          "P_media_W": th["P_avg_W"],
                          "margen_termico": th["margin"]})
    out["_corriente_palanca"] = corriente
    dump("low_energy", out)


# ==========================================================================
def study_charger():
    """El eslabón que faltaba: la máquina que carga el acumulador.

    El estudio dimensionó cuánta energía entra en un acumulador de
    10 x 10 x 60 mm, pero no el mecanismo que lo carga NI el volumen que ese
    mecanismo ocupa. Con el cargador adentro del envolvente, la barra de
    torsión de la arquitectura B1 pasa de 192 mJ a ~7 mJ.
    """
    t("cargador: qué hace falta para amartillar y cuánto ocupa")
    from wtd import charger as ch

    tor = design_torsion_accumulator(4.5e-3, 4.0e-3, 0.060, n_folds=2)
    r60 = math.sqrt(60.0 / tor["E_mJ"])
    demandas = []
    for nombre, E, F, s_ in (
            ("Barra de torsión plegada (192 mJ)", 0.1924, tor["F_crank_N"], 4.5e-3),
            ("Barra de torsión a 60 mJ", 0.060, tor["F_crank_N"] * r60, 4.5e-3 * r60),
            ("Ballesta (13.6 mJ)", 0.0136, 6.1, 4.5e-3),
            ("Palanca en L con VCM a 5 mJ", 0.005, 1.897 * 1.7, 3.0e-3)):
        d = ch.charger_demand(E, F, s_)
        d["acumulador"] = nombre
        demandas.append(d)

    metodos = []
    for E in (0.005, 0.020, 0.060):
        fila = {"E_mJ": E * 1e3,
                "directa": ch.direct_charge(E, ch.LAH04, I=1.0),
                "trinquete": ch.ratchet_charge(E, ch.LAH04, I=1.0, rate_hz=60),
                "resonante": {}}
        for Q in (20, 50, 100):
            fila["resonante"][f"Q{Q}"] = ch.resonant_charge(
                E, ch.LAH04, m_res=4e-3, x_max=2.0e-3, Q=Q, I=1.0)
        metodos.append(fila)

    reparto = []
    for mr, mp in ((1e-3, 3e-3), (2e-3, 2e-3), (0.5e-3, 3.5e-3)):
        r = ch.resonant_split(0.060, mr, mp)
        r["eta_si_golpea"] = ch.resonant_impact_split(mr, mp)
        reparto.append(r)

    # cuánto le queda a la barra de torsión con el cargador adentro
    volumen = []
    for L_barra, nota in ((0.060, "nada (lo que suponía el informe)"),
                          (0.040, "cargador de 20 mm (optimista)"),
                          (0.020, "motor ⌀8 + reductor 64:1 + husillo = 40 mm"),
                          (0.015, "ídem + tuerca, guía y sensor")):
        r = design_torsion_accumulator(4.5e-3, 4.0e-3, L_barra, n_folds=2)
        volumen.append({"L_barra_mm": L_barra * 1e3, "d_mm": r["d_mm"],
                        "E_mJ": r["E_mJ"], "ocupa_el_resto": nota})

    # trenes motor+husillo que entran en 10x10
    trenes = []
    for nombre, D, L, T in (("coreless ⌀6x12", 6, 12, 0.35),
                            ("coreless ⌀8x16", 8, 16, 0.90),
                            ("BLDC ⌀8x20", 8, 20, 1.60)):
        for red, L_red in ((64, 12), (256, 16)):
            for paso in (0.5e-3, 1.0e-3):
                T_out = T * 1e-3 * red * 0.7
                F = 2 * math.pi * T_out * 0.30 / paso
                largo = L + L_red + 12
                v = (12000 / 60 / red) * paso
                trenes.append({
                    "motor": nombre, "reduccion": red, "paso_mm": paso * 1e3,
                    "F_N": F, "largo_mm": largo,
                    "v_mm_s": v * 1e3, "t_2.5mm_ms": 2.5e-3 / v * 1e3,
                    "cabe": D <= 8 and largo <= 45})
    dump("charger", {"demandas": demandas, "metodos": metodos,
                     "reparto_resonador": reparto,
                     "volumen_vs_energia": volumen, "trenes": trenes})



# ==========================================================================
if __name__ == "__main__":
    only = sys.argv[1:] or None
    all_studies = {
        "anchors": study_anchors, "damage": study_damage,
        "mass": study_mass_optimum, "accum": study_accumulators,
        "freeflight": study_freeflight, "sensing": study_sensing,
        "mc": study_montecarlo, "rel": study_reliability,
        "catalog": study_catalog, "wedge": study_wedge_states,
        "sep": study_separability, "lever": study_lever_baseline,
        "mech": study_mechanisms, "wave": study_wave_return, "wavesim": study_wave_return_sim,
        "sens": study_sensitivity, "lowE": study_low_energy, "charger": study_charger, "masssim": study_mass_sim, "strike": study_strike_position,
    }
    t0 = time.time()
    for name, fn in all_studies.items():
        if only and name not in only:
            continue
        fn()
    print(f"[{time.strftime('%H:%M:%S')}] total {time.time()-t0:.1f} s")