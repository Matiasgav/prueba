# Análisis de resistencia: eslabón regulable v2

Cuánta fuerza aguanta el eslabón entre sus ejes de acople y qué pieza falla primero, en todo el rango de ancho de 35 a 105 mm. El cálculo lo hace `analisis.py` sobre la geometría real del CAD (`eslabon.py`). Los resultados quedan en `salida/capacidad.json`.

## Resultado

Carga entre ejes hasta la primera fluencia, sin coeficiente de seguridad. Es el mínimo entre tracción y compresión, que en este diseño dan igual.

| Ancho W [mm] | Carga a fluencia [N] | Carga de trabajo estática, ÷ 1,5 [N] | Limita | Flexibilidad entre ejes [mm/kN] |
|---:|---:|---:|---|---:|
| 35 | 605 | 400 | flexión del perno Q2 / P2 | 20,5 |
| 45 | 1.025 | 680 | flexión del perno Q2 / P2 | 10,5 |
| 50 | 1.165 | 780 | flexión de la barra A | 8,5 |
| 60 | 1.235 | 820 | flexión de la barra A | 6,3 |
| 70 | 1.284 | 860 | flexión de la barra A | 5,1 |
| 90 | 1.356 | 900 | flexión de la barra A | 3,6 |
| 105 | 1.409 | 940 | flexión de la barra A | 3,5 |

Comparación con la v1: la traba del carro de la v1 era un M4 de perilla que sujetaba por fricción. Retenía unos 150 N en el carro, y como el carro recibe p/s veces la carga entre ejes, el eslabón patinaba con **25 N a W = 35 y 100 N a W = 70**. Su eslabón largo de 7 × 3,5 mm fluía a flexión cerca de 300 N. La v2 aguanta **entre 6 y 24 veces más**, según el ancho.

Para cargas cíclicas (vibración, ciclos de arranque y parada), usá **menos de un tercio** de la carga a fluencia. El 7075 tiene baja resistencia a la fatiga con concentradores, y los agujeros de 4 mm en ligamentos de 2 mm lo son. Para un diseño a fatiga habría que conocer el espectro de cargas.

## Por qué no da más: la geometría manda

Las fuerzas internas por cada newton entre ejes dependen fuertemente del ancho:

| W [mm] | Eslabón largo 1 (en Q1) | Eslabón largo 2 | Eslabón corto | Traba del carro |
|---:|---:|---:|---:|---:|
| 35 | 9,3 N | 9,4 N | 6,1 N | 6,1 N |
| 50 | 4,4 N | 4,6 N | 3,0 N | 2,8 N |
| 70 | 2,4 N | 2,8 N | 1,8 N | 1,5 N |
| 105 | 0,7 N | 1,6 N | 1,1 N | 0,3 N |

1. **A anchos chicos los eslabones largos quedan casi paralelos a las barras.** A W = 35 forman 80° con la dirección de la carga. Solo un 17 % de su fuerza axial empuja en X, así que cargan 9 veces la fuerza entre ejes. El Scott Russell amplifica igual: el carro recibe p/s veces la carga. Esto viene del recorrido pedido (35 a 105) con 190 mm de largo, y ningún dimensionado lo cambia.
2. **El paralelogramo se agarra de A solo en la mitad de abajo** (Q1 a 15 mm y Q2 a 67 mm). La carga del agujero de acople de y = 185 tiene que bajar 118 mm por la barra, que trabaja como voladizo. Por eso la barra A limita desde W = 50 y por eso la unión es flexible (3,5 a 20 mm/kN). No se puede subir Q2: el carro necesita recorrer 61 mm y cargar P1 y P2 separados lo mismo que Q1 y Q2, y eso ocupa todo el largo.
3. **Todo vive en 13 mm de espesor.** Una horquilla en doble corte deja 7 mm para el eslabón y 2,9 mm por mejilla. Los pernos D4 son lo más grande que entra en ojos de 3,95 mm de radio, y ese radio lo fija la separación entre los dos eslabones largos a W = 35.

## Qué se cambió respecto de la v1 para maximizar

| Elemento | v1 | v2 |
|---|---|---|
| Traba del carro | M4 por fricción | Cremallera de 60° y paso 0,5 mm en la columna de B + trinquete de 22 dientes en el carro, apretado con un tornillo cónico M4 desde arriba. Es un bloqueo de forma, sin fricción. |
| Retención del carro | Canal con piel de 1,5 mm | Ganchos en L en las mejillas del carro que calzan detrás de un labio de la columna. Retienen en X en los dos sentidos. |
| Pernos | D3, corte simple | Pasadores templados ISO 8734 D4 m6, todos en **doble corte** (horquillas). |
| Eslabones largos | 7 × 3,5 | 7 mm de espesor. El eslabón 1 tiene una **quilla** de 11,4 mm hacia B, porque trabaja a flexión: el brazo Q1–C lleva un momento de F·p/2. |
| Eslabón corto | 1 placa de 3 mm | 2 placas de 2,8 mm que abrazan al eslabón 1 en C y a una lengüeta de B en O. |
| Barras | 14 + 14, con huecos rectangulares | A de 12,8 y B de 21,4 (columna maciza de 10,5). Los huecos salen del barrido de los eslabones en todo el rango, así que solo se quita el material imprescindible. |
| Geometría | s = W − 20, 2L = 92 | s = W − 20,6, 2L = 88,4. Elegida con un barrido de 12 combinaciones sobre el CAD. |

## Hipótesis

- **Carga:** F en la dirección del ancho (X), repartida mitad y mitad entre los dos agujeros de acople de cada barra (y = 5 y y = 185). Se analizan tracción y compresión.
- **Material:** 7075-T651, valores típicos: Sy = 503 MPa, Su = 572 MPa, E = 71,7 GPa, τy = 0,577 Sy. El admisible de aplastamiento es Sy·e/D, con un máximo de 1,5 Sy.
- **Pernos:** ISO 8734 4m6 templados (550 a 650 HV). El corte doble de fluencia se toma como 0,75 × 19,7 kN de rotura mínima normalizada. A flexión se admiten 1500 MPa, con el momento de horquilla F/2·(t_mejilla/2 + juego + t_medio/4).
- **Mecanismo:** con el carro trabado es isostático, y la estática da todas las fuerzas.
- **Barras y carro:** vigas con secciones medidas cada 0,5 mm sobre el CAD. Se toma N/A + M·c/I con los dos términos del mismo signo, lo que es conservador.
- **Eslabón 1:** viga con la sección real (quilla y agujeros) cada 0,25 mm.
- **Ojos y agujeros:** aplastamiento, desgarro (2·t·(e − d/2·cos 40°)·τy) y tracción neta. La distancia al borde se mide sobre el contorno real, en la dirección de la fuerza.
- **Pandeo:** Euler o Johnson para las piezas comprimidas, articulado en ambos extremos.
- **Rigidez:** energía de deformación (axial y flexión) de eslabones, barras y carro. **No incluye el juego de los pernos.** Con agujeros H7 y pernos m6 suma unos 0,01 a 0,02 mm por articulación.
- **Qué no se analiza:**
  - Cargas fuera del plano (en Z), momentos alrededor de los ejes de acople y carga a lo largo de los ejes (Y). El mecanismo es débil en Z: las horquillas resisten por contacto de caras.
  - Concentración de tensiones en los agujeros (Kt), que no cambia la fluencia estática de un material dúctil pero sí la fatiga.

## Todos los modos de falla

Carga entre ejes [N] que lleva cada modo a la fluencia, ordenados por W = 35. Se muestra el menor entre tracción y compresión. El listado completo, con los modos de las mejillas, los ganchos y la traba, está en `salida/capacidad.json`.

| Modo de falla | W = 35 | W = 50 | W = 70 | W = 105 |
|---|---:|---:|---:|---:|
| perno Q2 / P2: flexión | **605** | 1.235 | 2.075 | 3.545 |
| perno Q1: flexión | 612 | 1.299 | 2.435 | 7.924 |
| eslabón 1: flexión + axial | 784 | 1.192 | 1.650 | 3.626 |
| barra B: flexión + axial | 792 | 1.250 | 1.797 | 2.302 |
| perno C: flexión | 917 | 1.871 | 3.144 | 5.372 |
| perno O: flexión | 930 | 1.900 | 3.192 | 5.454 |
| barra A: flexión + axial | 953 | **1.165** | **1.284** | **1.409** |
| eslabón 2, ojos: desgarro | 1.040 | 2.124 | 3.569 | 6.097 |
| eslabón 1, ojo Q1: desgarro | 1.052 | 2.235 | 4.188 | 13.628 |
| placas cortas, ojos: desgarro | 1.307 | 2.668 | 4.483 | 7.659 |
| eslabón 2, ojos: tracción neta | 1.454 | 2.969 | 4.988 | 8.522 |
| pernos Q2 / P2: corte doble | 1.564 | 3.194 | 5.367 | 9.169 |
| perno P1: flexión | 1.584 | 2.635 | 3.295 | 3.691 |
| placa corta: pandeo fuera del plano | 1.727 | 3.526 | 5.925 | 10.122 |
| ganchos del carro: flexión | 1.777 | 2.060 | 2.207 | 2.354 |
| barra A, mejilla Q2: aplastamiento | 1.853 | 3.784 | 4.803 | 5.175 |
| carro, mejilla P2: aplastamiento | 1.853 | 3.412 | 4.055 | 4.847 |
| eslabón 2: pandeo fuera del plano | 1.944 | 3.968 | 6.668 | 11.392 |
| carro, mejilla P2: desgarro | 2.311 | 2.822 | 2.806 | 2.393 |
| traba: tornillo cónico | 2.431 | 5.192 | 9.921 | 47.263 |
| carro: flexión + axial | 2.521 | 5.778 | 6.495 | 6.402 |
| traba: corte de dientes | 2.588 | 5.527 | 10.561 | 50.313 |

La traba dentada ya no es el eslabón débil: con 22 dientes engranados aguanta unas 4 veces lo que limita el resto a W = 35. Su contra es la resolución: cerca de W = 35 un diente equivale a 3 mm de ancho. Si necesitás ajuste fino en esa zona, hay que agregar un nonio (dos trinquetes desfasados medio diente).

## Cómo subir más la capacidad

Cualquiera de estas opciones cambia algo de lo especificado, así que la decisión es tuya:

- **Ancho mínimo mayor.** Con el mínimo en 45 mm en vez de 35, la peor posición pasa a ser al menos la de hoy a W = 45 (1,0 kN). Reoptimizando la geometría para ese rango probablemente dé más, porque los eslabones dejan de estar casi paralelos y entra un perno D5. No lo calculé.
- **Más espesor.** Con 16 mm en vez de 13, las mejillas, los pernos y las barras crecen. Es una estimación gruesa, sin calcular: un 40 a 60 % más.
- **Barras de acero en vez de 7075.** A y B de acero bonificado (por ejemplo 4140, Sy ≈ 650 MPa) darían un 30 % más de resistencia en la barra A. Como las barras son la mayor parte de la flexibilidad, la rigidez entre ejes mejoraría unas 2 a 3 veces. Esas piezas pesarían el triple.
- **Otra topología.** Si la prioridad es rigidez, conviene un mecanismo que se agarre de las barras cerca de los dos extremos, no solo en la mitad de abajo, por ejemplo un pantógrafo de dos etapas o dos guías prismáticas cortas con bloqueo. El paralelogramo con Scott Russell es lo que limita.
