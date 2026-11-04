# Cable 3.5 mm en hueco 42.62 x 24.57 mm — simulación de elástica

- `rod.py`: modelo del cable como viga elástica inextensible (elástica plana), empotrado en la soldadura y en el canal de salida (arriba a la izquierda, hacia arriba), con contacto contra las paredes y sin cruzarse consigo mismo.
- `simulate.py x y phi L_ext L_ret out.json`: recorrido cuasiestático de extracción y de retracción.
- `sweep_test.py x y phi`: barrido rápido de radio mínimo vs largo interno para una pose de soldadura.
- `plot.py in.json out.png`: figura de formas + radio mínimo vs recorrido.

Resultado (`sim_35p5.json`, `resultado_soldadura.png`): soldadura con el eje del cable en x = 35.5 mm (desde la pared izquierda), y = 22.8 mm (pegado al borde superior) y el cable saliendo hacia abajo.
Con R >= 12.5 mm se obtienen ~13 mm de recorrido (largo interno de 63 a 50 mm); con R >= 14 mm, ~11 mm (62 a 51 mm).
Límite geométrico: un lazo en U solo puede subir H - D - R, y el recorrido es el doble: 2 x (24.57 - 3.5 - 12.5) = 17 mm. 60 mm de recorrido no entran en el plano.
