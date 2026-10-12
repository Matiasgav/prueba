# Prototipo impreso · corredera del captor ELCID

Piezas para imprimir en 3D y probar cómo se comporta el cable de 1 mm.
Se generan a partir del STEP original de Solid Edge (`fuente/…_original.stp`).

| Archivo | Qué es |
|---|---|
| `stl/chasis.stl`, `stl/tapa.stl`, `stl/bobina_bastidor.stl` | Listas para laminar, apoyadas en z = 0 |
| `step/*.step` | Las mismas piezas en posición de ensamble, para abrir en Solid Edge |
| `step/ensamble_prototipo.step` | Ensamble con el cable en la posición del STEP |
| `visor.html` | Visor 3D con simulación del lazo de cable |
| `fuente/build.py` | Script (CadQuery) que hace las modificaciones; los parámetros están arriba |
| `fuente/check.py` | Chequeo de interferencias a lo largo del recorrido |

Para regenerar: separar el STEP en `p0..p7.brep` (orden del árbol: chasis, tapa, M14002, M14001, inserto, M14005, M14004, M14003) y correr `python3 build.py`.

## Resultado del chequeo

Hay 0 mm³ de interferencia entre chasis, tapa, bobina y cable con el tornillo de la bobina en X = −17,35 / −11,7 / −5 / 0 / +5 / +6,4.

## Pasos del cable (como en el diseño original)

- Dentro de la bobina: agujero de Ø1,5 y muesca de 1 × 1 contra la pared del chasis.
- Salida entre chasis y tapa: 1 × 1 mm (x −7,25…−6,25, z 10,5…11,5).
- La falange del inserto (Ø5,5 × 0,58) queda en plástico sobre la lengüeta. Va dentro del bolsillo ovalado de la tapa, donde guía la bobina y hace de tope.

## Cable

- Largo libre recomendado: **27 mm** (de la salida de la muesca de la bobina a X = −1,25 en la tapa).
- Total desde la cavidad de la bobina hasta el borde del chasis: unos 58 mm.
- Con ese largo, el recorrido útil va de −17,3 a +6,4 (unos 24 mm). Más allá, la curva del lazo (R 3,75) toca el radio interior R1,5 de la pared del extremo.
