# Eslabón de ancho regulable (doble Scott Russell) — v2 reforzada

Modelo 3D paramétrico en CadQuery de un eslabón de **190 × 13 mm** cuyo **ancho se regula a mano entre 35 y 105 mm**. Está pensado para mecanizar en **aluminio 7075-T651**, con pasadores templados en todas las articulaciones.

![Planta a W = 70 mm](img/planta_W70.png)

## Cuánto aguanta

Fuerza entre los ejes de acople hasta la primera fluencia, tanto en tracción como en compresión:

| W | 35 | 45 | 50 | 70 | 105 mm |
|---|---:|---:|---:|---:|---:|
| Carga a fluencia | 605 | 1.025 | 1.165 | 1.284 | 1.409 N |
| Carga de trabajo estática (÷ 1,5) | 400 | 680 | 780 | 860 | 940 N |
| Flexibilidad entre ejes | 20,5 | 10,5 | 8,5 | 5,1 | 3,5 mm/kN |

Estos valores son de la ronda de cálculo anterior a mover los agujeros de acople a 5 mm de la cara exterior; falta recalcular. La v1 patinaba en la traba con 25 a 100 N. El detalle (todas las piezas, hipótesis, por qué no da más y qué cambiar para subirla) está en **[ANALISIS.md](ANALISIS.md)**.

## Terminación

Pensada para quedar a la vista, sin quitar material de las zonas que trabajan:
- puntas de las barras redondeadas en planta (R 3);
- aristas exteriores con bisel de 0,3 mm, el mismo que dejaría un rebabado normal;
- eslabones y placas con contorno de arcos verdaderos y bisel de 0,3 mm (los agujeros de perno no se biselan);
- rebajes del eslabón corto alisados y unidos con la boca del canal del carro en las caras superior e inferior.

Comparado con la versión sin terminación, la sección de las barras y del carro en las zonas cargadas queda igual: el módulo resistente mínimo pasa de 127 a 127 mm³ en A, de 173 a 172 mm³ en B y de 168 a 167 mm³ en el carro. Las mejillas de los pernos quedan completas.

## Requisitos

| Requisito | Cómo se resolvió |
|---|---|
| Largo 190, espesor 13 | La envolvente es W × 190 × 13 en todo el recorrido. No sobresale nada. |
| Ancho 35 a 105 regulable | La barra B se traslada en X respecto de la barra A, sin girar. |
| 4 agujeros D5 × 10 | Dos por barra, uno en cada cara extrema. Cada par es coaxial, paralelo al largo, centrado en el espesor (z = 6,5) y a 5 mm de la cara exterior de su barra, igual en las dos. Distancia entre ejes: W − 10 (25 a 95 mm). Entrada avellanada 0,3 × 45°. |
| Doble Scott Russell | Paralelogramo de dos eslabones largos (2L = 88,4 mm): Q1 y Q2 en A, P1 y P2 en un carro que corre en B. Un eslabón corto (L = 44,2 mm, dos placas) une el pivote O de B con el punto medio C del eslabón 1. |
| Regulación manual | Se afloja el tornillo cónico M4 desde arriba del carro, se lleva el ancho a mano y se vuelve a apretar. El trinquete engrana en la cremallera de paso 0,5 mm de la columna de B (122 posiciones en todo el recorrido). Un diente equivale a un cambio de ancho de 3 mm a W = 35, 0,35 mm a W = 70 y 0,16 mm a W = 105, porque el Scott Russell amplifica más cerca del ancho mínimo. |

## Piezas (7075-T651 salvo indicación)

| Pieza | Cant. | Notas |
|---|---:|---|
| Barra A | 1 | 12,8 × 190 × 13. Horquillas en Q1 y Q2 (mejillas de 2,9 mm). |
| Barra B | 1 | 21,4 × 190 × 13. Columna maciza de 10,5 mm con cremallera y labios de retención, canal del carro y lengüeta del pivote O. |
| Carro | 1 | 10,9 mm de ancho + ganchos. Horquillas en P1 y P2 (52 mm entre centros) y alojamiento del trinquete. |
| Trinquete | 1 | 22 dientes de 60° y paso 0,5 mm. Se recomienda 7075 o acero. |
| Tornillo cónico | 1 | M4, prisionero 12.9 con punta cónica. |
| Eslabón 1 | 1 | 88,4 mm entre centros, 7 mm de espesor, ojos R 3,95, quilla de 11,4 mm hacia B. |
| Eslabón 2 | 1 | 88,4 mm entre centros, 7 mm de espesor, ojos R 3,95. |
| Placa corta | 2 | 44,2 mm entre centros, 2,8 mm de espesor, R 4. Van arriba y abajo del eslabón 1. |
| Pasador D4 × 13 | 6 | ISO 8734 4m6, templado. Ajuste m6/H7 en eslabones y placas. |

## Archivos

| Archivo | Contenido |
|---|---|
| `eslabon.py` | Modelo paramétrico. `configurar()` fija la geometría principal y los huecos salen de barrer los eslabones por todo el rango. |
| `analisis.py` | Estática y verificación de cada pieza en tracción y compresión a lo largo de todo el recorrido. |
| `secciones.py` | Propiedades de sección medidas sobre los sólidos del CAD. |
| `ANALISIS.md` | Informe de resistencia. |
| `visor.html` | Visor 3D con la carga admisible a cada ancho. Lo genera `eslabon.py`. |
| `salida/capacidad.json` | Capacidad por modo de falla cada 2,5 mm de ancho. |
| `salida/ensamble_W35.step`, `ensamble_W70.step`, `ensamble_W105.step` | Ensambles en tres posiciones. |
| `salida/piezas/*.step`, `*.stl` | Cada pieza suelta. |

Para regenerar todo: `pip install cadquery shapely` y después `python analisis.py && python eslabon.py`. El script verifica que no haya choques entre piezas cada 2,5 mm de ancho.
