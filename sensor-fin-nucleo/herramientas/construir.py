#!/usr/bin/env python3
"""Inyecta los datos digitalizados en la plantilla y escribe el HTML autocontenido.

    python3 herramientas/construir.py            # -> simulador_sensor_fin_nucleo.html
"""
import json
import pathlib

BASE = pathlib.Path(__file__).resolve().parent.parent
datos = BASE / "datos"
vcnl = json.loads((datos / "vcnl36829um_fig10_fig11.json").read_text())["curvas_mm_vs_cuentas"]
qre = json.loads((datos / "qre1113_fig2_papel_blanco.json").read_text())["distancia_mm_vs_IC_normalizada"]
temp = json.loads((datos / "vcnl36829um_temperatura_fig38.json").read_text())["temperatura_C_vs_relacion"]

html = (BASE / "herramientas" / "plantilla.html").read_text()
for marca, valor in (("/*__VCNL__*/null", vcnl), ("/*__QRE__*/null", qre), ("/*__TEMP__*/null", temp)):
    assert marca in html, marca
    html = html.replace(marca, json.dumps(valor, separators=(",", ":")))
(BASE / "simulador_sensor_fin_nucleo.html").write_text(html)
print("escrito", BASE / "simulador_sensor_fin_nucleo.html", len(html), "bytes")
