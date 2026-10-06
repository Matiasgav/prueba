# Eslabón de ancho regulable (doble Scott Russell) — v7

Modelo 3D paramétrico en CadQuery de un eslabón de **190 × 13 mm** cuyo **ancho se regula a mano entre 35 y 105 mm**. Está pensado para mecanizar en **aluminio 7075-T651**, con pivotes templados y precargados.

![Isométrica a W = 35 mm, barras transparentes](img/iso_W35.png)
![Cable a W = 70 mm](img/cable_W70.png)
![Planta a W = 70 mm, barras transparentes](img/planta_W70.png)

> **Pendiente: la traba del carro.** Esta versión no la incluye. El cálculo supone una traba ideal en el medio del carro (entre P1 y P2) e informa cuánta fuerza tiene que aguantar: 7,5 veces la carga entre ejes a W = 35, 1,6 veces a W = 70 y 0,3 veces a W = 105.

## Cuánto aguanta

Fuerza entre los ejes de acople hasta la primera fluencia, tanto en tracción como en compresión:

| W | 35 | 45 | 50 | 70 | 105 mm |
|---|---:|---:|---:|---:|---:|
| Carga a fluencia | 480 | 653 | 716 | 955 | 1.152 N |
| Carga de trabajo estática (÷ 1,5) | 320 | 435 | 477 | 637 | 768 N |
| Flexibilidad entre ejes | 10,7 | 5,0 | 4,1 | 2,6 | 1,5 mm/kN |

Alabeo entre ejes (cupla alrededor del ancho, Mx): rigidez de 24 a 11 N·m/° y capacidad de 27 a 8 N·m según el ancho. Alrededor del largo (My) es la dirección floja: unos 3 a 5 N·m/° y de 3 a 11 N·m.

El detalle (todas las piezas, hipótesis, torsión y qué cambiar para subirla) está en **[ANALISIS.md](ANALISIS.md)**.

## Diseño

- **Paralelogramo** de dos eslabones largos (85,3 mm entre centros), con pivotes separados 73 mm: Q1 y Q2 en la barra A, P1 y P2 en un carro que corre en la barra B.
- **Eslabón corto** del Scott Russell (42,7 mm, una pieza de 2,5 mm: es una biela, solo trabaja a tracción y compresión): une el pivote O de B con el punto medio C del eslabón 1. Así Q1 se mueve en línea recta perpendicular a B, y la barra A se traslada sin girar.
- **Embocadura en C.** El eslabón corto entra en una ranura central del eslabón 1, que queda con dos alas de 2,15 mm.
- **Riel en C oculto, guiado por las alas.** El carro corre en un canal de B cerrado arriba y abajo por alas de 1,5 mm que trabajan con la columna: la cara ancha es continua y no se ve el carro. Las alas lo guían en z; la columna lo apoya hacia B y un labio de 1,5 × 0,9 mm en el borde interior de cada ala lo retiene hacia A. No hay guía mecanizada en la columna. El canal se abre en la punta de y = 190 para armar y se cierra con una tapa.
- **Eslabones largos iguales, espejados y planos.** Mismo contorno con vientre simétrico en arco (R 60, tangente a los ojos, 9,9 mm de profundidad): el 1 hacia B y el 2 hacia A. Espesor constante de 7 mm.
- **Pivotes Ø5 en doble corte, precargados.** Pasador rectificado g6, a presión en las mejillas. Una arandela ondulada de acero, en un rebaje de 0,15 mm del ojo, elimina el juego axial y mantiene las caras en contacto, lo que hace al conjunto firme contra el alabeo.
- **Cable Ø4 oculto, de largo fijo.** Entra por el lateral de B, rodea O, sigue el lado de afuera del eslabón corto, pasa por encima de C, baja por el lado de afuera del eslabón 1, rodea Q1 y sale por el lateral de A. En los tres pivotes gira por afuera a R 7: los giros suman siempre 180°, así que el largo es 124,8 mm en todo el recorrido. Dentro de las barras hace curvas fijas de R 5. Los ojos de los eslabones hacen de polea. Ver [el esquema](img/cable_recorrido.png).
- **Lateral exterior en semicilindro R 6,5** a todo lo largo de las dos barras; las puntas (caras de 13 × ancho) son planas. Los pernos Q1 y Q2 quedan al ras de la superficie curva.
- **Terminación:** bisel de 0,3 mm en las aristas exteriores y agujeros de acople avellanados.

## Requisitos

| Requisito | Cómo se resolvió |
|---|---|
| Cable Ø4 de un lado al otro, oculto, largo fijo, R mín 5 | Entra y sale por los laterales de 190 de B y A, a 16,6 mm de la punta (3,4 mm por debajo de O y Q1). Largo 124,8 mm constante. Curvas de R 5 (fijas) y R 7 (en los pivotes). |
| Largo 190, espesor 13 | La envolvente es W × 190 × 13 en todo el recorrido. No sobresale nada. |
| Ancho 35 a 105 regulable | La barra B se traslada en X respecto de la barra A, sin girar. |
| 4 agujeros D5 × 10 | Dos por barra, uno en cada cara extrema. Cada par es coaxial, paralelo al largo, centrado en el espesor (z = 6,5) y a 5 mm de la cara exterior de su barra, igual en las dos. Distancia entre ejes: W − 10 (de 25 a 95 mm). |
| Regulación manual | El carro se mueve a mano. **La traba que fija la posición está pendiente.** |

## Piezas (7075-T651 salvo indicación)

| Pieza | Cant. | Notas |
|---|---:|---|
| Barra A | 1 | 14,2 × 190 × 13, lateral exterior en semicilindro R 6,5. Horquillas en Q1 y Q2, pivotes a 10 mm de la cara exterior. Túnel del cable alrededor de Q1. |
| Barra B | 1 | 20,0 × 190 × 13, lateral exterior en semicilindro R 6,5. Columna de 8,6 mm y riel en C con alas de 1,5 mm y labios, alojamiento oculto del eslabón corto y túnel del cable en O. |
| Tapa | 1 | Cierra la boca del riel en y = 190; entra como el carro, bajo los labios. |
| Carro | 1 | 11,4 mm de ancho, 9,8 mm de alto entre las alas, con el escalón de los labios. Horquillas en P1 y P2 (73 mm entre centros), mejillas de 1,3 mm. |
| Eslabón 1 | 1 | 85,3 mm entre centros, 7 mm de espesor, ojos R 4,5, vientre de 9,9 mm hacia B, embocadura de 2,7 mm en C y túnel del cable alrededor de C. |
| Eslabón 2 | 1 | Mismo contorno que el 1, espejado: vientre de 9,9 mm hacia A. Sin embocadura. |
| Eslabón corto | 1 | 42,7 mm entre centros, 2,5 mm de espesor, R 4,5. |
| Pasador Ø5 | 6 | Templado 550 a 650 HV, rectificado g6, a presión en las mejillas. Largos: 13 (Q1, Q2, O), 9,8 (P1, P2), 7 (C). |
| Arandela ondulada | 6 | Acero inoxidable para resortes, Ø5,2 × 7,9, 0,25 mm comprimida. |

## Archivos

| Archivo | Contenido |
|---|---|
| `eslabon.py` | Modelo paramétrico. `configurar()` fija la geometría principal y los huecos salen de barrer los eslabones por todo el rango. |
| `analisis.py` | Estática y verificación de cada pieza en tracción y compresión, en todo el recorrido. |
| `secciones.py` | Propiedades de sección medidas sobre los sólidos del CAD. |
| `torsion.py` | Rigidez y resistencia al alabeo entre ejes (fuera del plano), en `salida/torsion.json`. |
| `ajuste_vientres.py` | Busca la profundidad máxima de los vientres de los eslabones largos. |
| `ANALISIS.md` | Informe de resistencia. |
| `visor.html` | Visor 3D con la carga admisible a cada ancho. Lo genera `eslabon.py`. |
| `salida/capacidad.json` | Capacidad por modo de falla cada 2,5 mm de ancho. |
| `salida/ensamble_W35.step`, `ensamble_W70.step`, `ensamble_W105.step` | Ensambles en tres posiciones, con el cable. |
| `salida/piezas/*.step`, `*.stl` | Cada pieza suelta. |

Para regenerar todo: `pip install cadquery shapely` y después `python analisis.py && python eslabon.py`. El script verifica que no haya choques entre piezas, ni entre el cable y las piezas, cada 2,5 mm de ancho.
