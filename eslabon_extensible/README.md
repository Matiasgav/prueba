# Eslabón de ancho regulable (doble Scott Russell) — v3

Modelo 3D paramétrico en CadQuery de un eslabón de **190 × 13 mm** cuyo **ancho se regula a mano entre 35 y 105 mm**. Está pensado para mecanizar en **aluminio 7075-T651**, con pivotes templados y precargados.

![Isométrica a W = 35 mm](img/iso_W35.png)
![Planta a W = 70 mm](img/planta_W70.png)

## Cuánto aguanta

Fuerza entre los ejes de acople hasta la primera fluencia, tanto en tracción como en compresión:

| W | 35 | 45 | 50 | 70 | 105 mm |
|---|---:|---:|---:|---:|---:|
| Carga a fluencia | 762 | 1.089 | 1.227 | 1.413 | 1.520 N |
| Carga de trabajo estática (÷ 1,5) | 508 | 726 | 818 | 942 | 1.014 N |
| Flexibilidad entre ejes | 20,7 | 10,2 | 8,2 | 4,6 | 2,9 mm/kN |

El detalle (todas las piezas, hipótesis, torsión y qué cambiar para subirla) está en **[ANALISIS.md](ANALISIS.md)**.

## Diseño

- **Paralelogramo** de dos eslabones largos (88 mm entre centros), con pivotes separados 69 mm: Q1 y Q2 en la barra A, P1 y P2 en un carro que corre en la barra B.
- **Eslabón corto** del Scott Russell (44 mm, dos placas): une el pivote O de B con el punto medio C del eslabón 1. Así Q1 se mueve en línea recta perpendicular a B, y la barra A se traslada sin girar.
- **Eslabones largos con vientre en arco** (R 60, tangente a los ojos). El eslabón 1 tiene forma de gota hacia B, donde trabaja a flexión. El eslabón 2 es de la misma familia y tiene el vientre hacia A.
- **Pivotes Ø5 en doble corte, precargados.** Pasador rectificado g6, a presión en las dos mejillas. Una arandela ondulada de acero, en un rebaje de 0,15 mm del ojo, elimina el juego axial y mantiene las caras en contacto, lo que hace al conjunto firme contra el alabeo.
- **Traba de forma.** Cremallera de 60° y paso 0,5 mm en la columna de B, y trinquete de 11 dientes en el carro, que se aprieta con un tornillo cónico M4 desde arriba. El carro se retiene en X con ganchos en L detrás de un labio de la columna.
- **Terminación.**
  - Puntas R 4, el mismo radio que los ojos.
  - Bisel de 0,3 mm en las aristas exteriores (el de un rebabado normal).
  - Agujeros de acople avellanados.
  - Rebaje del pivote O con una curva continua hasta la boca del canal.

## Requisitos

| Requisito | Cómo se resolvió |
|---|---|
| Largo 190, espesor 13 | La envolvente es W × 190 × 13 en todo el recorrido. No sobresale nada. |
| Ancho 35 a 105 regulable | La barra B se traslada en X respecto de la barra A, sin girar. |
| 4 agujeros D5 × 10 | Dos por barra, uno en cada cara extrema. Cada par es coaxial, paralelo al largo, centrado en el espesor (z = 6,5) y a 5 mm de la cara exterior de su barra, igual en las dos. Distancia entre ejes: W − 10 (de 25 a 95 mm). |
| Regulación manual | Se afloja el tornillo cónico, se lleva el ancho a mano y se vuelve a apretar. Hay 122 posiciones en todo el recorrido. Un diente de la traba equivale a 3 mm de ancho a W = 35, 0,75 mm a W = 70 y 0,16 mm a W = 105. |

## Piezas (7075-T651 salvo indicación)

| Pieza | Cant. | Notas |
|---|---:|---|
| Barra A | 1 | 12,3 × 190 × 13. Horquillas en Q1 y Q2 (mejillas de 2,9 mm). |
| Barra B | 1 | 21,9 × 190 × 13. Columna maciza de 10,5 mm con cremallera y labio de retención, canal del carro y lengüeta del pivote O. |
| Carro | 1 | 11,4 mm de ancho + ganchos. Horquillas en P1 y P2 (69 mm entre centros) y alojamiento del trinquete. |
| Trinquete | 1 | 11 dientes de 60° y paso 0,5 mm. 7075 o acero. |
| Tornillo cónico | 1 | M4, prisionero 12.9 con punta cónica. |
| Eslabón 1 | 1 | 88 mm entre centros, 7 mm de espesor, ojos R 4,5, vientre de 13 mm hacia B. |
| Eslabón 2 | 1 | 88 mm entre centros, 7 mm de espesor, ojos R 4,5, vientre de 10,9 mm hacia A. |
| Placa corta | 2 | 44 mm entre centros, 2,8 mm de espesor, R 4,5. Van arriba y abajo del eslabón 1. |
| Pasador Ø5 × 13 | 6 | Templado 550 a 650 HV, rectificado g6, a presión en las mejillas. |
| Arandela ondulada | 6 | Acero inoxidable para resortes, Ø5,2 × 7,9, 0,25 mm comprimida. |

## Archivos

| Archivo | Contenido |
|---|---|
| `eslabon.py` | Modelo paramétrico. `configurar()` fija la geometría principal y los huecos salen de barrer los eslabones por todo el rango. |
| `analisis.py` | Estática y verificación de cada pieza en tracción y compresión, en todo el recorrido. |
| `secciones.py` | Propiedades de sección medidas sobre los sólidos del CAD. |
| `ajuste_vientres.py` | Busca la profundidad máxima de los vientres de los eslabones largos. |
| `ANALISIS.md` | Informe de resistencia. |
| `visor.html` | Visor 3D con la carga admisible a cada ancho. Lo genera `eslabon.py`. |
| `salida/capacidad.json` | Capacidad por modo de falla cada 2,5 mm de ancho. |
| `salida/ensamble_W35.step`, `ensamble_W70.step`, `ensamble_W105.step` | Ensambles en tres posiciones. |
| `salida/piezas/*.step`, `*.stl` | Cada pieza suelta. |

Para regenerar todo: `pip install cadquery shapely` y después `python analisis.py && python eslabon.py`. El script verifica que no haya choques entre piezas cada 2,5 mm de ancho.
