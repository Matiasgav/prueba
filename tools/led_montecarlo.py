#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Eficiencia optica del conducto LED -> ventana (informe OSLON SSL 80).

Modelo Monte Carlo simplificado:
    - Fuente puntual en el centro del fondo del conducto, I(theta) = I0 cos^m.
      m se ajusta para que la intensidad caiga al 50 % a 40 grados (2phi = 80).
    - Conducto cilindrico de radio R = 2.5 mm y largo L = 7 mm.
    - Ventana de salida = toda la boca superior (diametro 5 mm).
    - Fondo absorbente (caso conservador; se puede cambiar con --fondo).
    - Pared difusa (lambertiana) o especular ideal, con reflectividad Rw.

Uso:
    python3 tools/led_montecarlo.py            # tablas del informe
    python3 tools/led_montecarlo.py --fondo 0.5
"""
import argparse
import math

import numpy as np

R, L = 2.5, 7.0
M = math.log(0.5) / math.log(math.cos(math.radians(40)))


def _lambert(n, rng):
    u = rng.random(n)
    ct, st = np.sqrt(u), np.sqrt(1 - u)
    ph = 2 * np.pi * rng.random(n)
    return ct, st, ph


def eficiencia(rw, modo, fondo=0.0, n=400000, seed=1, max_rebotes=80):
    """Fraccion del flujo del LED que sale por la ventana (antes del difusor)."""
    rng = np.random.default_rng(seed)
    u = rng.random(n)
    ct = (1 - u) ** (1 / (M + 1))
    st = np.sqrt(1 - ct ** 2)
    ph = 2 * np.pi * rng.random(n)
    d = np.stack([st * np.cos(ph), st * np.sin(ph), ct], 1)
    p = np.zeros((n, 3))
    w = np.ones(n)
    salida = 0.0
    for _ in range(max_rebotes):
        if not len(w):
            break
        a = d[:, 0] ** 2 + d[:, 1] ** 2
        b = 2 * (p[:, 0] * d[:, 0] + p[:, 1] * d[:, 1])
        c = p[:, 0] ** 2 + p[:, 1] ** 2 - R ** 2
        with np.errstate(divide='ignore', invalid='ignore'):
            tc = np.where(a > 1e-12,
                          (-b + np.sqrt(np.maximum(b * b - 4 * a * c, 0))) / (2 * a),
                          np.inf)
            tz = np.where(d[:, 2] > 0, (L - p[:, 2]) / d[:, 2],
                          np.where(d[:, 2] < 0, -p[:, 2] / d[:, 2], np.inf))
        tc = np.where(tc > 1e-9, tc, np.inf)
        tapa = tz < tc
        arriba = tapa & (d[:, 2] > 0)
        abajo = tapa & (d[:, 2] < 0)
        pared = ~tapa
        salida += w[arriba].sum()
        np_, nd, nw = [], [], []
        if fondo > 0 and abajo.any():
            k = abajo.sum()
            ct, st, ph = _lambert(k, rng)
            np_.append(p[abajo] + d[abajo] * tz[abajo, None])
            nd.append(np.stack([st * np.cos(ph), st * np.sin(ph), ct], 1))
            nw.append(w[abajo] * fondo)
        if pared.any():
            k = pared.sum()
            pw = p[pared] + d[pared] * tc[pared, None]
            nrm = np.stack([-pw[:, 0] / R, -pw[:, 1] / R, np.zeros(k)], 1)
            if modo == 'especular':
                dw = d[pared]
                dn = dw - 2 * (dw * nrm).sum(1)[:, None] * nrm
            else:
                ct, st, ph = _lambert(k, rng)
                t1 = np.tile([0.0, 0.0, 1.0], (k, 1))
                t2 = np.cross(nrm, t1)
                dn = (ct[:, None] * nrm + st[:, None]
                      * (np.cos(ph)[:, None] * t1 + np.sin(ph)[:, None] * t2))
            np_.append(pw + nrm * 1e-7)
            nd.append(dn)
            nw.append(w[pared] * rw)
        if not np_:
            break
        p, d, w = np.concatenate(np_), np.concatenate(nd), np.concatenate(nw)
        viva = w > 1e-4
        p, d, w = p[viva], d[viva], w[viva]
    return salida / n


def captura_directa():
    alfa = math.atan(R / L)
    return 1 - math.cos(alfa) ** (M + 1), math.degrees(alfa)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fondo', type=float, default=0.0,
                    help='reflectividad difusa del fondo (0 = absorbente)')
    ap.add_argument('--flujo', type=float, default=187.0)
    args = ap.parse_args()
    f, alfa = captura_directa()
    print('m = %.2f   alfa = %.2f grados   captura directa = %.3f' % (M, alfa, f))
    print('%5s | %-22s | %-22s' % ('Rw', 'pared difusa', 'pared especular'))
    for rw in (0.55, 0.65, 0.75, 0.85, 0.92):
        ed = eficiencia(rw, 'difusa', args.fondo)
        ee = eficiencia(rw, 'especular', args.fondo)
        print('%5.2f | eta %.3f  %5.0f lm    | eta %.3f  %5.0f lm'
              % (rw, ed, ed * args.flujo, ee, ee * args.flujo))


if __name__ == '__main__':
    main()
