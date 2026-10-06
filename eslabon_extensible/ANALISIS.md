# Análisis de resistencia: eslabón regulable v7

Cuánta fuerza aguanta el eslabón entre sus ejes de acople y qué pieza falla primero, en todo el rango de ancho de 35 a 105 mm. El cálculo lo hace `analisis.py` sobre la geometría real del CAD (`eslabon.py`). Los resultados quedan en `salida/capacidad.json`.

> **La traba del carro no está definida todavía.** El cálculo supone una traba ideal **en el medio del carro, entre P1 y P2**, contra la columna de B, e informa la fuerza que tiene que aguantar. Esa ubicación es un requisito para la traba: en una punta del carro, el carro pasa a limitar (420 N a W = 35).

## Resultado

Carga entre ejes hasta la primera fluencia, sin coeficiente de seguridad. Es el mínimo entre tracción y compresión, que en este diseño dan igual.

| Ancho W [mm] | Carga a fluencia [N] | Carga de trabajo estática, ÷ 1,5 [N] | Limita | Flexibilidad entre ejes [mm/kN] | Fuerza sobre la traba [N por N] |
|---:|---:|---:|---|---:|---:|
| 35 | 480 | 320 | flexión del eslabón 1 | 10,7 | 7,48 |
| 45 | 653 | 435 | flexión del eslabón 1 | 5,0 | 3,88 |
| 50 | 716 | 477 | flexión del eslabón 1 | 4,1 | 3,09 |
| 60 | 831 | 554 | flexión del eslabón 1 | 3,1 | 2,13 |
| 70 | 955 | 637 | flexión del eslabón 1 | 2,6 | 1,55 |
| 90 | 1.078 | 719 | flexión de la barra A | 1,8 | 0,81 |
| 105 | 1.152 | 768 | flexión de la barra A | 1,5 | 0,32 |

Comparación:

| | W = 35 | W = 50 | W = 70 | W = 105 |
|---|---:|---:|---:|---:|
| v1 (traba por fricción) | ≈ 25 N | – | ≈ 100 N | – |
| v2 | 605 N | 1.165 N | 1.284 N | 1.409 N |
| v3 | 762 N | 1.227 N | 1.521 N | 1.634 N |
| v4 (lateral semicilíndrico) | 597 N* | 981 N* | 1.126 N* | 1.244 N* |
| v5 (riel en C, corto embutido, eslabón 1 engrosado) | 673 N | 1.004 N | 1.156 N | 1.256 N |
| v6 (eslabones largos iguales y planos, corto de 2,5) | 547 N | 804 N | 1.083 N | 1.256 N |
| **v7 (cable Ø4 oculto de largo fijo)** | **480 N** | **716 N** | **955 N** | **1.152 N** |

\* Las cifras de la v4 y anteriores se calcularon con un error en la lectura del contorno de las piezas (`contorno_capa` armaba el polígono con tramos en orden inconsistente). Afectaba sobre todo las mejillas del carro y de las barras. Está corregido en la v5; las versiones anteriores no se recalcularon.

Para cargas cíclicas (vibración, ciclos de arranque y parada), usá **menos de un tercio** de la carga a fluencia. El 7075 tiene baja resistencia a la fatiga con concentradores, y los agujeros de los pernos en ligamentos finos lo son.

## Qué cambió en la v7: cable Ø4 oculto

![Recorrido del cable](img/cable_recorrido.png)

- **Recorrido.** El cable entra por el lateral de B, rodea O, sigue el lado de afuera del eslabón corto, pasa por encima de C, baja por el lado de afuera del eslabón 1, rodea Q1 y sale por el lateral de A. Dentro de cada barra hace una curva fija de R 5.
- **Largo fijo.** En O, C y Q1 el cable gira siempre por el lado de afuera y al mismo radio (R 7 al eje del cable). Los tres giros suman siempre 180°, así que el largo no cambia: 124,8 mm entre laterales en todo el recorrido (verificado cada 0,25 mm de ancho). El radio mínimo de curvatura es 5 mm (curvas fijas en A y B); en los pivotes es 7.
- **Altura de la salida.** El cable rodea Q1 y O solo lo justo para W = 35 y enseguida dobla hacia el lateral, así sale a 16,6 mm de la punta. Se puede subir más corriendo O y Q1 hacia el centro, pero acorta el paralelogramo:

  | O y Q1 en y = | 20 (actual) | 23 | 25 |
  |---|---:|---:|---:|
  | Salida del cable a | 16,6 | 19,6 | 21,6 mm de la punta |
  | Capacidad a W = 35 / 50 / 70 | 480 / 716 / 955 | 447 / 668 / 892 | 427 / 640 / 854 N |

- **Por qué R 7.** El cable va en la capa del medio (z 4,3 a 8,7), la misma de los ojos de los eslabones (R 4,5). A R 7 le quedan 0,3 mm a cada ojo. Los ojos hacen de polea.
- **Lo que costó en geometría** (el ancho total y el espesor no cambian):
  - Q1 y Q2 a 10 mm de la cara exterior de A (antes 6,5), para que el cable rodee Q1 por dentro del semicilindro. A pasa a 14,2 mm y B a 20,0 mm (columna de 8,6). La relación s/p a W = 35 empeora un poco (s mínimo 11,3 en lugar de 12,9).
  - O y Q1 suben a y = 20 (antes 15) para que el cable pase por encima de los agujeros de acople. El paralelogramo baja de 77 a 73 mm entre pivotes.
  - Vientre de los eslabones largos de 9,9 mm (antes 10,6), lo que entra con la geometría nueva.
- **Túneles.** El cable pasa por dentro del eslabón 1 alrededor de C (del lado de P1) y por dentro de A y B alrededor de Q1 y O. Las secciones se midieron sobre el sólido real con esos huecos.
- **Costo:** entre 8 y 12 % menos que la v6 en todo el rango. A W = 35 limitan casi juntos el eslabón 1 (480 N), los ojos del corto (497 N) y la barra A (578 N): no queda una mejora geométrica barata. Si hace falta más, el paso siguiente es el material de los eslabones (acero inoxidable 17-4PH o titanio).

## Qué cambió en la v6

- **Eslabones largos iguales, espejados y planos.** Los dos tienen el mismo contorno, con vientre simétrico R 60 de 10,6 mm (lo máximo que entra sin tocar la columna de B ni comer la barra A), espejado respecto de su eje: el 1 hacia B y el 2 hacia A. Espesor constante de 7 mm, sin zonas gruesas. A y B ya no necesitan el hueco bajo piel de la v5.
- **Eslabón corto de 2,5 mm** (antes 4,6). Es una biela: solo trabaja a tracción o compresión. Pero a W = 35 lleva 6,7 veces la carga entre ejes, así que el espesor lo fijan el desgarro de sus ojos y el pandeo. Afinarlo deja más material en las alas de la embocadura del eslabón 1 (2,15 mm cada una):

  | Espesor del corto | 4,6 | 3,6 | 3,0 | **2,5** mm |
  |---|---:|---:|---:|---:|
  | Eslabón 1, flexión a W = 35 | 277 | 406 | 483 | **547 N** |
  | Ojos del corto, desgarro a W = 35 | – | 802 | 668 | **557 N** |
  | Corto, pandeo a W = 35 | – | – | – | **652 N** |

  En 2,5 mm las dos fallas quedan parejas. Más fino, mandan los ojos del corto.
- **Carro guiado por las alas.** Ya no hay ganchos ni bolsillos mecanizados en la columna. Las alas guían el carro en z; la cara de la columna lo apoya cuando lo empujan hacia B, y un labio de 1,5 × 0,9 mm en el borde interior de cada ala lo retiene cuando lo tiran hacia A. Los labios aguantan el equivalente a casi 10 kN entre ejes a W = 35. La columna recupera el material de los bolsillos.
- **Costo:** la capacidad baja respecto de la v5 hasta W = 75 (547 en lugar de 673 N a W = 35), porque el eslabón 1 ya no tiene la zona gruesa ni la gota hacia Q1. Desde W = 80 limita la barra A, igual que antes.

## Qué cambió en la v5

- **Riel en C con alas estructurales de 1,5 mm.** El carro corre entre las dos alas de B y queda oculto: la cara ancha de B es continua. Las alas trabajan con la columna y la barra B pasa de limitar a W = 35 (597 N en la v4) a aguantar unos 1.500 N. El canal se abre en la punta de y = 190 para meter el carro y se cierra con una **tapa**.
- **Eslabón corto de una pieza** (4,6 mm), embutido en una **embocadura** del eslabón 1 en C y en un alojamiento de B en O, los dos ocultos.
- **Eslabón 1 engrosado alrededor de C.** La embocadura le saca el centro justo donde el momento es máximo (F·p/2). Con el eslabón de 7 mm las alas de la embocadura quedaban de 1,1 mm y la capacidad a W = 35 caía a 324 N. En una zona de ±22 mm alrededor de C el eslabón pasa a 9,8 mm de espesor en todo su ancho, así que las alas quedan de 2,5 mm. A y B tienen el hueco correspondiente bajo sus alas.
- **Sin traba.** Se sacaron la cremallera, el trinquete, el tornillo cónico y la ranura del ala. Falta definir la traba (ver arriba).

## Qué cambió en la v4

- **Lateral exterior en semicilindro R 6,5** (la mitad del espesor) en las dos barras; las puntas (caras de 13 × ancho) quedan planas. La línea de pivotes de A se corrió de 5,5 a 6,5 mm de la cara exterior, así la nariz redonda queda maciza en Q1 y Q2.
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

Cálculo fuera del plano con `torsion.py` (emparrillado de vigas con secciones medidas sobre el CAD; resultados en `salida/torsion.json`). B empotrada en sus dos acoples y una cupla aplicada en los acoples de A:

- **Mx, alrededor del ancho:** una punta de A sube y la otra baja respecto de B. Es el alabeo típico del marco.
- **My, alrededor del largo:** A gira sobre su propio eje de acople respecto de B.

| W [mm] | Mx: rigidez [N·m/°] | Mx: capacidad a fluencia [N·m] | My: rigidez [N·m/°] | My: capacidad a fluencia [N·m] |
|---:|---:|---:|---:|---:|
| 35 | 24,1 | 77,8 (eslabón corto) | 2,9 | 8,3 (eslabón 1) |
| 50 | 21,7 | 44,9 (barra A) | 3,1 | 9,6 (eslabón 1) |
| 70 | 17,6 | 28,6 (barra A) | 3,5 | 11,2 (barra A) |
| 90 | 13,4 | 20,3 (barra A) | 4,0 | 11,2 (barra A) |
| 105 | 10,6 | 15,9 (barra A) | 4,7 | 11,2 (barra A) |

Las tensiones de los eslabones se evalúan fuera de los agujeros de los pasadores: ahí el momento lo toma el pasador. Verificación aparte de ojos y pasadores con 3 N·m: la peor articulación pasa unos 2,3 N·m, lo que da unos 490 N de cupla sobre el pasador. Eso es unos 80 MPa de flexión en el pasador templado, unos 45 MPa de aplastamiento en el ojo y unos 75 MPa en las mejillas del carro: todo con margen amplio.

- **Deformación.** Con Mx, a W = 70, cada N·m gira 0,057° (0,18 mm de desnivel entre las puntas de A, en 180 mm). Con My cada N·m gira 0,21° a 0,34°: es la dirección floja. Con 3 N·m gira 0,6° a 1,0°, más el juego de las articulaciones.
- **Qué cede.** Los eslabones largos, que son planos de 7 mm, a flexión fuera del plano y a torsión, sobre todo junto a los ojos. Las barras casi no participan. En My, a anchos chicos los eslabones quedan casi paralelos a las barras y trabajan a torsión: dos placas de 7 mm. Ahí está la flexibilidad.
- **Hipótesis que hay que tener presentes:**
  - Los pivotes se suponen rígidos fuera del plano. Eso vale con la arandela de precarga y el pasador ajustado.
  - Juego adicional sin carga, estimado: hasta unos 0,2° por articulación por el juego del pasador (H7/g6: 4 a 24 µm en 7 mm de ojo) y unos 0,13° del carro entre las alas (0,1 mm por lado). Se suma a lo de la tabla hasta que el juego se cierra.
  - La torsión de cada sección se aproxima como sección maciza (A⁴/40 Ip), con un error esperable de ±30 %.
  - No incluye pandeo lateral ni concentración de tensiones.
- **Qué la subiría:** eslabones más altos en z (hoy 7 mm; la rigidez fuera del plano crece con el cubo del espesor) o en material más rígido. Con acero, la rigidez sube unas 2,8 veces por el módulo, y la capacidad con la fluencia.

## Por qué no da más: la geometría manda

Fuerzas internas por cada newton entre ejes:

| W [mm] | Eslabón largo 1 (en Q1) | Eslabón largo 2 | Eslabón corto | Traba del carro |
|---:|---:|---:|---:|---:|
| 35 | 7,7 N | 7,8 N | 7,5 N | 7,5 N |
| 50 | 3,2 N | 3,3 N | 3,2 N | 3,1 N |
| 70 | 1,6 N | 1,9 N | 1,8 N | 1,5 N |
| 105 | 0,3 N | 1,1 N | 1,0 N | 0,3 N |

1. **A anchos chicos los eslabones largos quedan casi paralelos a las barras.** A W = 35 solo una fracción chica de su fuerza axial empuja en X, y el Scott Russell amplifica igual: el carro recibe p/s veces la carga. Esto viene del recorrido pedido (35 a 105) en 190 mm de largo.
2. **El paralelogramo se agarra de A solo en la mitad inferior** (Q1 a 20 mm, Q2 a 93 mm). La carga del acople de y = 185 recorre la barra como un voladizo. Por eso la barra A limita desde W = 75.
3. **Todo vive en 13 mm de espesor:** 7 mm de eslabón, 1,5 de ala y 1,3 de mejilla del carro. En C el eslabón 1 tiene dos alas de 2,15 mm alrededor del corto, y de 1,3 mm donde pasa el cable.

## Hipótesis

- **Carga:** F en la dirección del ancho (X), repartida mitad y mitad entre los dos agujeros de acople de cada barra (y = 5 y y = 185), sobre el eje de cada agujero (a 5 mm de la cara exterior).
- **Material:** 7075-T651, valores típicos: Sy = 503 MPa, Su = 572 MPa, E = 71,7 GPa, τy = 0,577 Sy. El admisible de aplastamiento es Sy·e/D, con un máximo de 1,5 Sy.
- **Pernos:** pasadores Ø5 templados (550 a 650 HV), rectificados g6. El corte doble de fluencia se toma como 0,75 × 30,8 kN, la rotura mínima de ISO 8734 para Ø5. A flexión se admiten 1500 MPa, con el momento de horquilla F/2·(t_mejilla/2 + juego + t_medio/4).
- **Mecanismo:** con el carro trabado es isostático, y la estática da todas las fuerzas. La traba se supone ideal, en el medio del carro.
- **Barras y carro:** vigas con secciones medidas cada 0,5 mm sobre el CAD. Se toma N/A + M·c/I con los dos términos del mismo signo, lo que es conservador.
- **Eslabón 1:** viga con la sección real medida sobre el sólido del CAD cada 0,25 mm (vientre, embocadura y agujeros).
- **Labios de las alas:** voladizos de 0,9 mm de alto y 1,5 mm de ancho, cargados a media altura, con la carga repartida a lo largo del carro.
- **Ojos y agujeros:** aplastamiento, desgarro (2·t·(e − d/2·cos 40°)·τy) y tracción neta. La distancia al borde se mide sobre el contorno real, en la dirección de la fuerza.
- **Pandeo:** Euler o Johnson para las piezas comprimidas, articulado en ambos extremos.
- **Rigidez:** energía de deformación (axial y flexión) de eslabones, barras y carro, sin el juego radial de los pernos (H7/g6: hasta unos 0,02 mm por articulación).
- **Qué no se analiza:**
  - Cargas fuera del plano y torsión: van aparte, en `torsion.py` (ver la sección «Torsión y alabeo entre ejes»).
  - Concentración de tensiones en los agujeros (Kt): no cambia la fluencia estática de un material dúctil, pero sí la fatiga.

## Todos los modos de falla

Carga entre ejes [N] que lleva cada modo a la fluencia, ordenados por W = 35. Es el menor entre tracción y compresión. El listado completo está en `salida/capacidad.json`.

| Modo de falla | W = 35 | W = 50 | W = 70 | W = 105 |
|---|---:|---:|---:|---:|
| eslabón 1: flexión + axial | 480 | 716 | 955 | 2.235 |
| eslabón corto ojo O: desgarro | 497 | 1.157 | 2.036 | 3.575 |
| eslabón corto ojo C: desgarro | 497 | 1.157 | 2.036 | 3.575 |
| barra A: flexión + axial | 578 | 833 | 984 | 1.152 |
| eslabón corto fuera del plano: pandeo | 604 | 1.406 | 2.475 | 4.345 |
| eslabón corto ojo O: tracción neta | 666 | 1.551 | 2.730 | 4.794 |
| eslabón corto ojo C: tracción neta | 666 | 1.551 | 2.730 | 4.794 |
| eslabón corto ojo O: aplastamiento | 750 | 1.745 | 3.072 | 5.393 |
| eslabón corto ojo C: aplastamiento | 750 | 1.745 | 3.072 | 5.393 |
| carro mejilla P2: tracción neta | 790 | 1.998 | 4.443 | 23.290 |
| carro: flexión + axial | 870 | 2.290 | 4.131 | 6.806 |
| carro mejilla P2: desgarro | 1.002 | 2.465 | 5.083 | 3.929 |
| carro mejilla P2: aplastamiento | 1.191 | 2.888 | 5.182 | 5.728 |
| eslabón 1 alas en C: aplastamiento | 1.299 | 3.024 | 3.504 | 9.349 |
| eslabón 2 ojo P2: desgarro | 1.353 | 3.149 | 5.544 | 9.735 |
| eslabón 2 ojo Q2: desgarro | 1.353 | 3.149 | 5.544 | 9.735 |
| eslabón 1 ojo Q1: desgarro | 1.365 | 3.311 | 6.601 | 32.078 |
| perno Q2: flexión | 1.438 | 3.348 | 5.894 | 10.350 |
| perno Q1: flexión | 1.451 | 3.519 | 7.017 | 34.078 |
| barra B: flexión + axial | 1.481 | 2.451 | 3.507 | 4.427 |
| perno O: flexión | 1.696 | 3.948 | 6.951 | 12.205 |
| eslabón 1 alas en C: tracción neta | 1.709 | 4.956 | 18.062 | 15.165 |

## Cómo subir más la capacidad

Cualquiera de estas opciones cambia algo de lo especificado, así que la decisión es tuya:

- **Eslabones en acero o titanio.** Con los dos largos y el corto en 17-4PH H900 (fluencia ≈ 1.170 MPa) dejan de limitar y manda la barra A: ≈ 578 N a W = 35. Escalado por fluencia, sin recalcular.

- **Ancho mínimo mayor (45 mm).** La peor posición pasa a ser la de hoy a W = 45 (≈ 0,9 kN). No lo calculé reoptimizado.
- **Más espesor (16 a 20 mm).** Permite eslabones dobles en caja, que es lo que más rigidez a torsión da. No lo calculé.
- **Barras de acero.** Por ejemplo 4140 bonificado (Sy ≈ 650 MPa): un 30 % más de resistencia en las barras y unas 2 a 3 veces más rigidez entre ejes, con el triple de peso en esas piezas.
