#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nota 02489-00-MC003 - Modelo 3D (STEP) del resorte de torsión Ø0,50.

Uso (desde esta carpeta, requiere CadQuery: pip install cadquery):
    python3 modelo_step.py      # escribe resorte_02489-00-MC003.step

Geometría en posición libre, igual que el plano:
  * eje del resorte = eje Z; la primera espira arranca en (D/2, 0, 0);
  * hélice a derechas de 9 + 60° espiras (Nb = 9,1667), diámetro medio 4,10 mm;
  * brazo 1 tangente hacia -Y desde el arranque; brazo 2 tangente al final de
    la hélice; ambos rectos de 8 mm y en la prolongación de la hélice (con su
    inclinación de 2,3°), así el barrido es continuo;
  * paso = d + 0,01 mm: las espiras quedan juntas pero sin tocarse, para que el
    sólido sea válido (el resorte real se enrolla con espiras en contacto).
Unidades: mm.
"""
import math
import os

import cadquery as cq

ROOT = os.path.dirname(os.path.abspath(__file__))

d = 0.50                 # mm, alambre
ID = 3.60                # mm, diámetro interior libre
Nb = 9 + 1 / 6           # espiras de cuerpo
l1 = l2 = 8.0            # mm, brazos
paso = d + 0.01          # mm

R = (ID + d) / 2
alto = paso * Nb
phi_f = 2 * math.pi * Nb

helice = cq.Wire.makeHelix(pitch=paso, height=alto, radius=R)   # a derechas, arranca en (R, 0, 0)
p0, pf = helice.startPoint(), helice.endPoint()
t0, tf = helice.tangentAt(0), helice.tangentAt(1)

# camino continuo en tangente: brazo 1 + hélice + brazo 2, y un único barrido de la sección
camino = cq.Wire.assembleEdges([cq.Edge.makeLine(p0 - t0 * l1, p0), *helice.Edges(),
                                cq.Edge.makeLine(pf, pf + tf * l2)])
perfil = cq.Wire.makeCircle(d / 2, p0 - t0 * l1, t0)
solido = cq.Solid.sweep(perfil, [], camino, makeSolid=True, isFrenet=True)

assert solido.isValid(), 'el sólido barrido no es válido'
vol = solido.Volume()
largo = camino.Length()
print(f'Largo de alambre: {largo:.1f} mm   Volumen: {vol:.2f} mm³   Masa: {vol * 7.85e-3:.3f} g')
bb = solido.BoundingBox()
print(f'Caja: X {bb.xmin:.2f}…{bb.xmax:.2f}  Y {bb.ymin:.2f}…{bb.ymax:.2f}  Z {bb.zmin:.2f}…{bb.zmax:.2f} mm')

salida = os.path.join(ROOT, 'resorte_02489-00-MC003.step')
cq.exporters.export(cq.Workplane().add(solido), salida)
print('Escrito', os.path.relpath(salida, ROOT))
