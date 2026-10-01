"""Cálculos de la nota 02489-00-MC010: evaluación de la cámara ams OSRAM NanEyeC RGB.

Calcula:
  1. Campo visual nominal y densidad de píxeles a 4, 5, 6, 8 y 12 mm, a partir del
     FOV diagonal de 120° y la matriz de 320 x 320 px (hoja de datos DS000503 v2-00).
     Modelo de cámara estenopeica, sin distorsión: es una cota nominal.
  2. Comparación con el campo medido para la NanEyeM (misma óptica FOV120 F4) en
     PMC13417079, Fig. 17: ejes de ±5,6 mm a 4 mm y ±7,12 mm a 6 mm (leídos de la figura).
  3. Duración del cuadro en modo SEIM según la estructura de la hoja de datos:
     648 PP de interfaz + 656 PP de sincronismo + retardo mínimo 2·328 PP
     + 320 filas de (8 + 320) PP + 8 PP de fin de cuadro; 1 PP = 12 ciclos de SCLK.
     Se contrasta con las tasas que muestra el visor de github.com/phili-b/teensy_naneyeC
     (12,375 MHz → «~8 fps» en el selector; 24,75 MHz → «≤ 19,3 fps»).
  4. Caudal de datos en SEIM.

Escribe resultados.json en la misma carpeta.
"""
import json
import math
from pathlib import Path

# --- datos de la hoja de datos DS000503 v2-00 --------------------------------
N_PX = 320              # píxeles por lado
PITCH_UM = 2.4          # paso de píxel
FOV_DIAG_DEG = 120.0    # FOV diagonal (NEC_RGB_SGA_FOV120_F4.0 / NEC_HLBX-00)
BITS_PP = 12            # bits por palabra (inicio + 10 datos + parada)
PP_INTERFAZ = 648
PP_SYNC = 656
PP_DELAY_MIN = 2 * 328
PP_FILA = 8 + 320
PP_EOF = 8

# --- campo medido NanEyeM (PMC13417079, Fig. 17, ejes de la figura) -----------
MEDIDO = {4.0: 2 * 5.6, 6.0: 2 * 7.12}   # ancho del campo [mm]

DISTANCIAS = [4.0, 5.0, 6.0, 8.0, 12.0]


def campo_nominal(d_mm: float) -> float:
    """Ancho del campo cuadrado [mm] a la distancia d, FOV diagonal 120°."""
    diag = 2 * d_mm * math.tan(math.radians(FOV_DIAG_DEG / 2))
    return diag / math.sqrt(2)


def tiempo_cuadro(f_sclk_hz: float) -> float:
    pp = PP_INTERFAZ + PP_SYNC + PP_DELAY_MIN + N_PX * PP_FILA + PP_EOF
    return pp * BITS_PP / f_sclk_hz


res = {"campo": [], "seim": [], "medido_naneyem": []}
for d in DISTANCIAS:
    w = campo_nominal(d)
    res["campo"].append({"d_mm": d, "ancho_mm": round(w, 2),
                         "px_por_mm": round(N_PX / w, 1),
                         "mm_por_px": round(w / N_PX, 3)})
for d, w in MEDIDO.items():
    res["medido_naneyem"].append({"d_mm": d, "ancho_mm": round(w, 2),
                                  "px_por_mm": round(N_PX / w, 1),
                                  "nominal_mm": round(campo_nominal(d), 2)})
for f in [12.375e6, 24.75e6, 60e6, 75e6]:
    t = tiempo_cuadro(f)
    res["seim"].append({"sclk_MHz": f / 1e6, "cuadro_ms": round(t * 1e3, 1),
                        "fps": round(1 / t, 1), "Mbit_s": round(f / 1e6, 2)})
res["caudal_util_Mbit_s_58fps"] = round(N_PX**2 * 10 * 58 / 1e6, 1)

Path(__file__).with_name("resultados.json").write_text(
    json.dumps(res, indent=2, ensure_ascii=False))
print(json.dumps(res, indent=2, ensure_ascii=False))
