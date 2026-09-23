# Actuación del paralelogramo elevador

Gráficos para dimensionar la actuación del paralelogramo con un tornillo de avance
dentro de la viga, movido en línea por el motor, más una biela de empuje hacia una
de las bielas del paralelogramo.

**Los valores de `DATOS` en `tools/paralelogramo.py` son supuestos de ejemplo**
(W = 10 N, L = 100 mm, recorrido de 15° a 65°, enganche a = 25 mm, biela de empuje c = 60 mm).
Reemplazalos por los reales y regenerá con:

```bash
python3 tools/paralelogramo.py
```

| Figura | Contenido |
|---|---|
| `01_esquema` | Esquema de la solución propuesta |
| `02_torque_pivote` | Torque en el pivote T = W·L·cos θ |
| `03_fuerza_tuerca` | Fuerza axial en la tuerca según el punto de enganche |
| `04_angulo_transmision` | Ángulo de transmisión y zona de punto muerto |
| `05_torque_motor` | Torque del motor según el tornillo |
| `06_resorte` | Compensación del peso con resorte de torsión |
| `07_tiempo` | Tiempo de subida según la velocidad del motor |
