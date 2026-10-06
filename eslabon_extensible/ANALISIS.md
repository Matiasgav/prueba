# Análisis de resistencia: eslabón regulable v3

Cuánta fuerza aguanta el eslabón entre sus ejes de acople y qué pieza falla primero, en todo el rango de ancho de 35 a 105 mm. El cálculo lo hace `analisis.py` sobre la geometría real del CAD (`eslabon.py`). Los resultados quedan en `salida/capacidad.json`.

## Resultado

Carga entre ejes hasta la primera fluencia, sin coeficiente de seguridad. Es el mínimo entre tracción y compresión, que en este diseño dan igual.

| Ancho W [mm] | Carga a fluencia [N] | Carga de trabajo estática, ÷ 1,5 [N] | Limita | Flexibilidad entre ejes [mm/kN] |
|---:|---:|---:|---|---:|
| 35 | 762 | 508 | flexión de la barra B | 20,7 |
| 45 | 1.089 | 726 | flexión de la barra B | 10,2 |
| 50 | 1.227 | 818 | flexión de la barra B | 8,2 |
| 60 | 1.369 | 913 | flexión de la barra A | 5,9 |
| 70 | 1.413 | 942 | flexión de la barra A | 4,6 |
| 90 | 1.475 | 983 | flexión de la barra A | 3,1 |
| 105 | 1.520 | 1.014 | flexión de la barra A | 2,9 |

Comparación:

| | W = 35 | W = 50 | W = 70 | W = 105 |
|---|---:|---:|---:|---:|
| v1 (traba por fricción) | ≈ 25 N | – | ≈ 100 N | – |
| v2 | 605 N | 1.165 N | 1.284 N | 1.409 N |
| **v3** | **762 N** | **1.227 N** | **1.413 N** | **1.520 N** |

Para cargas cíclicas (vibración, ciclos de arranque y parada), usá **menos de un tercio** de la carga a fluencia. El 7075 tiene baja resistencia a la fatiga con concentradores, y los agujeros de los pernos en ligamentos de 2 mm lo son. Para un diseño a fatiga habría que conocer el espectro de cargas.

## Qué cambió de la v2 a la v3

- **Lados del paralelogramo más separados: 69 mm entre pivotes en lugar de 52.**
  - La cupla que equilibra el momento en A baja en la misma proporción: el eslabón 2 carga 7,3 F a W = 35, antes 9,4 F.
  - Q2 sube a y = 84, así que la barra A trabaja con 101 mm de voladizo en lugar de 118.
  - Para hacer lugar, el canal del carro llega hasta y = 185. Pasa por dentro del eje de acople, que ahora está en otra zona de la columna. El trinquete se acortó a 6 mm (11 dientes de paso 0,5).
- **Pernos Ø5 en lugar de Ø4.** Con más separación entran ojos de R 4,5. Los pernos dejaron de ser el límite: a flexión resisten el doble.
- **Pivotes precargados.** Una arandela ondulada de acero, alojada en un rebaje de 0,15 mm en la cara del ojo, empuja el eslabón contra la mejilla opuesta. Así no hay juego axial y las caras quedan siempre en contacto, que es lo que resiste el alabeo. Ocupa el juego de 0,1 mm que ya existía, así que no se le resta espesor a nada.
- **Eslabones largos con vientre ("gota").** El contorno está hecho de arcos tangentes reales (R 60 en el vientre). El eslabón 1 lo tiene hacia B, más lleno del lado de Q1, y llega a 13 mm de profundidad en C: tiene más módulo resistente que la quilla triangular. El eslabón 2 lo tiene hacia A, con 10,9 mm. Las profundidades salen de `ajuste_vientres.py`: son las máximas que no tocan la columna de B ni comen la barra A más allá del fondo que ya deja el ojo.
- **Terminación:** puntas redondeadas R 4 (el radio de los ojos), bisel de 0,3 mm en las aristas exteriores y el rebaje del pivote O con una curva continua hasta la boca del canal.

## Torsión y alabeo entre ejes

Entre A y B solo hay pivotes de eje vertical. Un giro relativo de los ejes (alabeo) lo resisten tres cosas: la flexión de los eslabones fuera del plano, el apoyo cara contra cara en cada horquilla y la separación entre los apoyos. La v3 mejora las tres:

- **Juego axial cero** gracias a la precarga. Con 0,05 mm de juego, cada articulación de la v2 podía inclinarse unos ±0,4° sin carga.
- **Eslabones más anchos en el plano.** Su rigidez fuera del plano crece con el ancho: el eslabón 2 pasa de 7,9 a 15,4 mm en el medio.
- **Base más ancha:** 69 mm entre los lados del paralelogramo, antes 52.

La rigidez a torsión **no está calculada todavía**: el análisis actual es en el plano. Si es un caso de carga relevante, conviene definir el momento esperado y verificarlo con un modelo 3D.

## Por qué no da más: la geometría manda

Fuerzas internas por cada newton entre ejes:

| W [mm] | Eslabón largo 1 (en Q1) | Eslabón largo 2 | Eslabón corto | Traba del carro |
|---:|---:|---:|---:|---:|
| 35 | 7,2 N | 7,3 N | 6,3 N | 6,2 N |
| 50 | 3,3 N | 3,5 N | 3,0 N | 2,9 N |
| 70 | 1,7 N | 2,1 N | 1,8 N | 1,5 N |
| 105 | 0,4 N | 1,2 N | 1,0 N | 0,3 N |

1. **A anchos chicos los eslabones largos quedan casi paralelos a las barras.** A W = 35 solo una fracción chica de su fuerza axial empuja en X, y el Scott Russell amplifica igual: el carro recibe p/s veces la carga. Esto viene del recorrido pedido (35 a 105) en 190 mm de largo.
2. **El paralelogramo se agarra de A solo en la mitad inferior** (Q1 a 15 mm, Q2 a 84 mm). La carga del acople de y = 185 recorre la barra como un voladizo. Por eso la barra A limita desde W = 55 y la unión es flexible (2,9 a 20,7 mm/kN).
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
| barra B: flexión + axial | 762 | 1.227 | 1.773 | 2.699 |
| eslabón 1: flexión + axial | 948 | 1.412 | 1.931 | 4.259 |
| barra A: flexión + axial | 1.056 | 1.305 | 1.413 | 1.520 |
| traba: corte de dientes | 1.255 | 2.728 | 5.246 | 25.080 |
| placas cortas ojo O: desgarro | 1.329 | 2.763 | 4.674 | 8.020 |
| placas cortas ojo C: desgarro | 1.329 | 2.763 | 4.674 | 8.020 |
| eslabón 2 ojo Q2: desgarro | 1.432 | 2.977 | 5.036 | 8.641 |
| eslabón 2 ojo P2: desgarro | 1.432 | 2.977 | 5.036 | 8.641 |
| eslabón 1 ojo Q1: desgarro | 1.450 | 3.148 | 6.036 | 26.522 |
| perno Q2: flexión | 1.522 | 3.164 | 5.353 | 9.184 |
| perno P2: flexión | 1.522 | 3.164 | 5.353 | 9.184 |
| perno Q1: flexión | 1.541 | 3.346 | 6.415 | 28.187 |
| perno C: flexión | 1.738 | 3.613 | 6.114 | 10.490 |
| perno O: flexión | 1.764 | 3.668 | 6.206 | 10.649 |
| placas cortas ojo O: tracción neta | 1.782 | 3.704 | 6.268 | 10.754 |
| placas cortas ojo C: tracción neta | 1.782 | 3.704 | 6.268 | 10.754 |
| placa corta fuera del plano: pandeo | 1.908 | 3.966 | 6.711 | 11.514 |
| eslabón 2 ojo Q2: tracción neta | 1.949 | 4.053 | 6.857 | 11.765 |
| eslabón 2 ojo P2: tracción neta | 1.949 | 4.053 | 6.857 | 11.765 |
| traba: aplastamiento de flancos | 1.957 | 4.255 | 8.183 | 39.120 |
| placas cortas ojo O: aplastamiento | 2.004 | 4.168 | 7.052 | 12.099 |
| placas cortas ojo C: aplastamiento | 2.004 | 4.168 | 7.052 | 12.099 |
| barra A mejilla Q2: tracción neta | 2.088 | 4.739 | 10.107 | 68.904 |
| eslabón 2 ojo Q2: aplastamiento | 2.160 | 4.491 | 7.600 | 13.039 |

## Cómo subir más la capacidad

Cualquiera de estas opciones cambia algo de lo especificado, así que la decisión es tuya:

- **Ancho mínimo mayor (45 mm).** La peor posición pasa a ser al menos la de hoy a W = 45 (≈ 1,1 kN). No lo calculé reoptimizado.
- **Más espesor (16 a 20 mm).** Permite eslabones dobles en caja, que es lo que más rigidez a torsión da. No lo calculé.
- **Barras de acero.** Por ejemplo 4140 bonificado (Sy ≈ 650 MPa): un 30 % más de resistencia en las barras y unas 2 a 3 veces más rigidez entre ejes, con el triple de peso en esas piezas.
