# Análisis de resistencia: eslabón regulable v4

Cuánta fuerza aguanta el eslabón entre sus ejes de acople y qué pieza falla primero, en todo el rango de ancho de 35 a 105 mm. El cálculo lo hace `analisis.py` sobre la geometría real del CAD (`eslabon.py`). Los resultados quedan en `salida/capacidad.json`.

## Resultado

Carga entre ejes hasta la primera fluencia, sin coeficiente de seguridad. Es el mínimo entre tracción y compresión, que en este diseño dan igual.

| Ancho W [mm] | Carga a fluencia [N] | Carga de trabajo estática, ÷ 1,5 [N] | Limita | Flexibilidad entre ejes [mm/kN] |
|---:|---:|---:|---|---:|
| 35 | 597 | 398 | flexión de la barra B | 21,3 |
| 45 | 869 | 579 | flexión de la barra B | 10,4 |
| 50 | 981 | 654 | flexión de la barra B | 8,4 |
| 60 | 1.079 | 719 | flexión de la barra A | 6,2 |
| 70 | 1.126 | 750 | flexión de la barra A | 4,8 |
| 90 | 1.193 | 796 | flexión de la barra A | 3,2 |
| 105 | 1.244 | 829 | flexión de la barra A | 3,2 |

Comparación:

| | W = 35 | W = 50 | W = 70 | W = 105 |
|---|---:|---:|---:|---:|
| v1 (traba por fricción) | ≈ 25 N | – | ≈ 100 N | – |
| v2 | 605 N | 1.165 N | 1.284 N | 1.409 N |
| **v3** | **762 N** | **1.227 N** | **1.521 N** | **1.634 N** |
| **v4 (lateral semicilíndrico)** | **597 N** | **981 N** | **1.126 N** | **1.244 N** |

Para cargas cíclicas (vibración, ciclos de arranque y parada), usá **menos de un tercio** de la carga a fluencia. El 7075 tiene baja resistencia a la fatiga con concentradores, y los agujeros de los pernos en ligamentos de 2 mm lo son. Para un diseño a fatiga habría que conocer el espectro de cargas.

## Qué cambió en la v4

- **Lateral exterior en semicilindro R 6,5** (la mitad del espesor) en las dos barras; las puntas (caras de 13 × ancho) quedan planas. Cuesta resistencia porque saca la fibra exterior, la que más trabaja a flexión: un 20 a 25 % respecto de la v3. Para limitar la pérdida, la línea de pivotes de A se corrió de 5,5 a 6,5 mm de la cara exterior, así la nariz redonda queda maciza en Q1 y Q2. Se probaron 5,5, 6,5, 7, 7,5, 8 y 9 mm; 6,5 es la mejor.
- **Caras continuas.** Las placas del eslabón corto quedan hundidas 0,6 mm (pasan de 2,8 a 2,2 mm). Las barras conservan una piel de 0,6 mm que tapa los rebajes de C en A y de O en B. Esos rebajes se mecanizan con fresa de disco desde la cara interior.
- **Pernos Q1 y Q2 al ras** de la superficie curva.

## Qué cambió de la v2 a la v3

- **Lados del paralelogramo más separados: 76 mm entre pivotes en lugar de 52.**
  - La cupla que equilibra el momento en A baja en la misma proporción: el eslabón 2 carga 6,7 F a W = 35, antes 9,4 F.
  - Q2 sube a y = 91, así que la barra A trabaja con 94 mm de voladizo en lugar de 118.
  - Para hacer lugar, el canal del carro llega hasta y = 185. Pasa por dentro del eje de acople, que ahora está en otra zona de la columna. El trinquete se acortó a 6 mm (11 dientes de paso 0,5) y pasó a estar entre P1 y P2, junto a P1, en una zona del carro que ningún eslabón barre. La cola del carro por encima de P2 solo cierra el ojo.
- **Pernos Ø5 en lugar de Ø4.** Con más separación entran ojos de R 4,5. Los pernos dejaron de ser el límite: a flexión resisten el doble.
- **Pivotes precargados.** Una arandela ondulada de acero, alojada en un rebaje de 0,15 mm en la cara del ojo, empuja el eslabón contra la mejilla opuesta. Así no hay juego axial y las caras quedan siempre en contacto, que es lo que resiste el alabeo. Ocupa el juego de 0,1 mm que ya existía, así que no se le resta espesor a nada.
- **Eslabones largos con vientre ("gota").** El contorno está hecho de arcos tangentes reales (R 60 en el vientre). El eslabón 1 lo tiene hacia B, más lleno del lado de Q1, y llega a 13 mm de profundidad en C: tiene más módulo resistente que la quilla triangular. El eslabón 2 lo tiene hacia A, con 10,9 mm. Las profundidades salen de `ajuste_vientres.py`: son las máximas que no tocan la columna de B ni comen la barra A más allá del fondo que ya deja el ojo.
- **Terminación:** puntas redondeadas R 4 (el radio de los ojos), bisel de 0,3 mm en las aristas exteriores y el rebaje del pivote O con una curva continua hasta la boca del canal.

## Torsión y alabeo entre ejes

Entre A y B solo hay pivotes de eje vertical. Un giro relativo de los ejes (alabeo) lo resisten tres cosas: la flexión de los eslabones fuera del plano, el apoyo cara contra cara en cada horquilla y la separación entre los apoyos. La v3 mejora las tres:

- **Juego axial cero** gracias a la precarga. Con 0,05 mm de juego, cada articulación de la v2 podía inclinarse unos ±0,4° sin carga.
- **Eslabones más anchos en el plano.** Su rigidez fuera del plano crece con el ancho: el eslabón 2 pasa de 7,9 a 15,4 mm en el medio.
- **Base más ancha:** 76 mm entre los lados del paralelogramo, antes 52.

La rigidez a torsión **no está calculada todavía**: el análisis actual es en el plano. Si es un caso de carga relevante, conviene definir el momento esperado y verificarlo con un modelo 3D.

## Por qué no da más: la geometría manda

Fuerzas internas por cada newton entre ejes:

| W [mm] | Eslabón largo 1 (en Q1) | Eslabón largo 2 | Eslabón corto | Traba del carro |
|---:|---:|---:|---:|---:|
| 35 | 6,6 N | 6,7 N | 6,3 N | 6,2 N |
| 50 | 3,0 N | 3,2 N | 3,0 N | 2,9 N |
| 70 | 1,6 N | 1,9 N | 1,8 N | 1,5 N |
| 105 | 0,3 N | 1,1 N | 1,0 N | 0,3 N |

1. **A anchos chicos los eslabones largos quedan casi paralelos a las barras.** A W = 35 solo una fracción chica de su fuerza axial empuja en X, y el Scott Russell amplifica igual: el carro recibe p/s veces la carga. Esto viene del recorrido pedido (35 a 105) en 190 mm de largo.
2. **El paralelogramo se agarra de A solo en la mitad inferior** (Q1 a 15 mm, Q2 a 92 mm). La carga del acople de y = 185 recorre la barra como un voladizo. Por eso la barra A limita desde W = 55 y la unión es flexible (3,2 a 21,3 mm/kN).
3. **Todo vive en 13 mm de espesor:** 7 mm de eslabón y 2,9 mm por mejilla.

## Hipótesis

- **Carga:** F en la dirección del ancho (X), repartida mitad y mitad entre los dos agujeros de acople de cada barra (y = 5 y y = 185), sobre el eje de cada agujero (a 5 mm de la cara exterior).
- **Material:** 7075-T651, valores típicos: Sy = 503 MPa, Su = 572 MPa, E = 71,7 GPa, τy = 0,577 Sy. El admisible de aplastamiento es Sy·e/D, con un máximo de 1,5 Sy.
- **Pernos:** pasadores Ø5 templados (550 a 650 HV), rectificados g6. El corte doble de fluencia se toma como 0,75 × 30,8 kN, la rotura mínima de ISO 8734 para Ø5. A flexión se admiten 1500 MPa, con el momento de horquilla F/2·(t_mejilla/2 + juego + t_medio/4).
- **Mecanismo:** con el carro trabado es isostático, y la estática da todas las fuerzas.
- **Barras y carro:** vigas con secciones medidas cada 0,5 mm sobre el CAD. Se toma N/A + M·c/I con los dos términos del mismo signo, lo que es conservador.
- **Eslabón 1:** viga con la sección real (vientre y agujeros) cada 0,25 mm.
- **Ojos y agujeros:** aplastamiento, desgarro (2·t·(e − d/2·cos 40°)·τy) y tracción neta. La distancia al borde se mide sobre el contorno real, en la dirección de la fuerza.
- **Pandeo:** Euler o Johnson para las piezas comprimidas, articulado en ambos extremos.
- **Rigidez:** energía de deformación (axial y flexión) de eslabones, barras y carro, sin el juego radial de los pernos (H7/g6: hasta unos 0,02 mm por articulación).
- **Qué no se analiza:**
  - Cargas fuera del plano y torsión (ver la sección anterior).
  - Concentración de tensiones en los agujeros (Kt): no cambia la fluencia estática de un material dúctil, pero sí la fatiga.

## Todos los modos de falla

Carga entre ejes [N] que lleva cada modo a la fluencia, ordenados por W = 35. Es el menor entre tracción y compresión. El listado completo está en `salida/capacidad.json`.

| Modo de falla | W = 35 | W = 50 | W = 70 | W = 105 |
|---|---:|---:|---:|---:|
| barra B: flexión + axial | 597 | 981 | 1.419 | 2.112 |
| barra A: flexión + axial | 797 | 1.010 | 1.126 | 1.244 |
| placa corta fuera del plano: pandeo | 889 | 1.922 | 3.300 | 5.711 |
| eslabón 1: flexión + axial | 947 | 1.412 | 1.919 | 4.309 |
| placas cortas ojo O: desgarro | 980 | 2.120 | 3.639 | 6.298 |
| placas cortas ojo C: desgarro | 980 | 2.120 | 3.639 | 6.298 |
| traba: corte de dientes | 1.176 | 2.657 | 5.177 | 24.927 |
| placas cortas ojo C: tracción neta | 1.314 | 2.842 | 4.880 | 8.445 |
| placas cortas ojo O: tracción neta | 1.314 | 2.842 | 4.880 | 8.445 |
| placas cortas ojo C: aplastamiento | 1.478 | 3.198 | 5.490 | 9.501 |
| placas cortas ojo O: aplastamiento | 1.478 | 3.198 | 5.490 | 9.501 |
| eslabón 2 ojo Q2: desgarro | 1.500 | 3.243 | 5.568 | 9.637 |
| eslabón 2 ojo P2: desgarro | 1.500 | 3.243 | 5.568 | 9.637 |
| eslabón 1 ojo Q1: desgarro | 1.517 | 3.425 | 6.675 | 31.920 |
| perno Q2: flexión | 1.594 | 3.447 | 5.919 | 10.244 |
| perno P2: flexión | 1.594 | 3.447 | 5.919 | 10.244 |
| perno Q1: flexión | 1.612 | 3.640 | 7.092 | 33.916 |
| perno C: flexión | 1.792 | 3.875 | 6.653 | 11.515 |
| perno O: flexión | 1.822 | 3.940 | 6.764 | 11.707 |
| traba: aplastamiento de flancos | 1.835 | 4.144 | 8.075 | 38.880 |
| eslabón 2 ojo P2: tracción neta | 2.040 | 4.411 | 7.574 | 13.107 |
| eslabón 2 ojo Q2: tracción neta | 2.040 | 4.411 | 7.574 | 13.107 |
| carro: flexión + axial | 2.062 | 4.280 | 7.297 | 16.845 |
| barra A mejilla Q1: tracción neta | 2.067 | 4.669 | 9.101 | 44.123 |

## Cómo subir más la capacidad

Cualquiera de estas opciones cambia algo de lo especificado, así que la decisión es tuya:

- **Ancho mínimo mayor (45 mm).** La peor posición pasa a ser al menos la de hoy a W = 45 (≈ 1,1 kN). No lo calculé reoptimizado.
- **Más espesor (16 a 20 mm).** Permite eslabones dobles en caja, que es lo que más rigidez a torsión da. No lo calculé.
- **Barras de acero.** Por ejemplo 4140 bonificado (Sy ≈ 650 MPa): un 30 % más de resistencia en las barras y unas 2 a 3 veces más rigidez entre ejes, con el triple de peso en esas piezas.
