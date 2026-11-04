# Cable 3.5 mm en hueco 42.62 x 24.57 mm — simulación de elástica

- `rod.py`: modelo del cable como viga elástica inextensible (elástica plana), empotrado en la soldadura y en el canal de salida (arriba a la izquierda, hacia arriba), con contacto contra las paredes y sin cruzarse consigo mismo.
- `simulate.py x y phi L_ext L_ret out.json`: recorrido cuasiestático de extracción y de retracción.
- `sweep_test.py x y phi`: barrido rápido de radio mínimo vs largo interno para una pose de soldadura.
- `plot.py in.json out.png`: figura de formas + radio mínimo vs recorrido.

Resultado (`sim_35p5.json`, `resultado_soldadura.png`): soldadura con el eje del cable en x = 35.5 mm (desde la pared izquierda), y = 22.8 mm (pegado al borde superior) y el cable saliendo hacia abajo.
Con R >= 12.5 mm se obtienen ~13 mm de recorrido (largo interno de 63 a 50 mm); con R >= 14 mm, ~11 mm (62 a 51 mm).
Límite geométrico: un lazo en U solo puede subir H - D - R, y el recorrido es el doble: 2 x (24.57 - 3.5 - 12.5) = 17 mm. 60 mm de recorrido no entran en el plano.

## Revisión 2 — salida hacia la izquierda, 60 mm de carrera

Salida arriba a la izquierda **hacia -x**; se exige poder extraer 60 mm, aceptando menor radio.
`omega_sweep.py` (variable de entorno `PHI` = ángulo del cable en la soldadura), `plot_omega.py`.

| Soldadura (eje del cable) | Sale hacia | R mín. en la carrera | Carrera |
|---|---|---|---|
| esquina inf. izq. (1.75, 1.75) | derecha (0°) | ~8.8 mm (7 en los extremos) | 60 mm (L int 91 -> 31) |
| (4, 1.75) | derecha (0°) | ~8.7 mm | 57 mm con R >= 7 |
| (4–10, 1.75) | arriba (90°, "omega") | 5.3–5.7 mm | — (radio mucho menor) |

Lazo rodante: rama inferior soldada, rama superior hacia la salida, la curva de 180° rueda de x≈40 a x≈11.
Límite: con ramas en y=1.75 e y=22.82 el radio geométrico máximo es 10.5 mm; la elástica da ~8.8.
