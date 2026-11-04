"""Simulación cuasiestática de extracción / retracción para una pose de soldadura.

Uso: python3 simulate.py x y phi_deg L_ext L_ret salida.json
  L_ext : largo interno con el cable extraído (estirado)
  L_ret : largo interno con el cable retraído (guardado)
Recorre L_ret -> L_ext (extracción) y L_ext -> L_ret (retracción) por
continuación pura (cada estado parte del anterior), que es como se comporta el
cable real si se mueve despacio: si hay una bifurcación (pandeo) aparece como
salto/histéresis entre ambos recorridos.
"""
import sys, json
import numpy as np
from rod import Rod, best_state

x, y, phd, Le, Lr = map(float, sys.argv[1:6])
rod = Rod((x, y), np.deg2rad(phd))
step = 1.0


def run(Ls):
    out, prev = [], None
    for i, L in enumerate(Ls):
        if prev is None:
            b = best_state(rod, L)
        else:
            b = rod.solve(L, prev['c'] * prev['L'] / L, prev['target'])
            if not b['ok']:
                b2 = best_state(rod, L, prev)
                b = b2 if b2 is not None else b
        prev = b if b is not None and b['ok'] else prev
        out.append(dict(L=float(L), ok=bool(b and b['ok']), Rmin=float(b['Rmin']) if b else None,
                        E=float(b['E']) if b else None,
                        X=np.round(b['X'][::2], 2).tolist() if b else None,
                        kap=np.round(np.abs(b['kap'][::2]), 4).tolist() if b else None))
        print(f"L={L:5.1f}  Rmin={out[-1]['Rmin']:.1f}  ok={out[-1]['ok']}", flush=True)
    return out

Ls = np.arange(Le, Lr + 1e-9, step)
ext = run(Ls[::-1])     # extracción: de guardado a estirado
ret = run(Ls)           # retracción: de estirado a guardado
json.dump(dict(pose=dict(x=x, y=y, phi=phd), L_ext=Le, L_ret=Lr, extract=ext, retract=ret),
          open(sys.argv[6], 'w'))
