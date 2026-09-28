---
titulo: Flex del conector M12
subtitulo: Memoria de diseño del tramo flexible entre la mainboard y la placa del conector
edicion: Rev. A · Layout del 27/9 · Plano de referencia FX-M12-S-03
fecha: 27 de septiembre de 2026
encabezado: Flex del conector M12 · Memoria de diseño
nota_portada: Memoria de diseño. Las formas del flex salen de la simulación de la elástica; el largo y las cotas del layout se confirman con una muestra física.
---

# Resumen

El conector M12 va en una placa rígida propia, unida a la mainboard por un tramo de flex de la misma rigid-flex. Para montar el equipo, esa placa tiene que **retroceder 12 mm** detrás del panel y después volver a su lugar. El flex tiene que acompañar ese movimiento sin doblarse por debajo del radio admisible y sin chocar con la placa de la cámara, que está al lado. Además, tiene que ocupar el menor espacio posible.

::: kpi
19,0 ± 0,25 || largo del flex entre cantos rígidos || con 1 mm recto en cada extremo
15,5 || separación entre cantos (Z) || entre la placa del conector y la pestaña fija
2,84 || R interior mínimo en la carrera || admisible: 2,5
1,43 || juego mínimo a la placa de cámara || peor caso con tolerancias
:::

::: nota clave | La solución en una frase
El flex forma una **S en el plano de las placas**, entre el canto de la placa del conector y una pestaña fija de la mainboard ubicada 5 mm por detrás de ella. Con **19,0 mm** de flex y 15,5 mm entre cantos, la S acompaña los 12 mm de carrera con un radio interior de al menos 2,84 mm y queda siempre a más de 1,4 mm de la placa de cámara. Para dibujarla alcanzan **tres arcos de R 3,5 unidos por rectas** (sección 4.1).
:::

# 1. El problema

## 1.1 Qué se tiene que mover

En posición nominal, la placa del conector apoya contra el panel frontal y el M12 asoma por él. Para montar el equipo a través del panel, esa placa tiene que poder retroceder 12 mm. La mainboard y su pestaña fija no se mueven. El flex que une las dos placas tiene que absorber esa carrera **dentro de su propio plano**, sin salirse de la altura disponible y sin tocar lo que tiene alrededor.

::: fig flex-problema | Figura 1 — Planta del conjunto como en Solid Edge, con el panel abajo. La placa del conector retrocede 12 mm y el flex pasa de la forma nominal (línea llena) a la retraída (línea de trazos). | Esquema del autor sobre el layout del 27/9. Escala aproximada.
:::

## 1.2 Condiciones de diseño

| Condición | Valor | De dónde sale |
|---|---|---|
| Flex | 0,2 mm, 2 capas, 11 mm de alto | Lleva 48 V / 10 A y Ethernet |
| Radio interior mínimo | **2,5 mm** | 12 × espesor (IPC-2223, 2 capas, curva que se mueve pocas veces) |
| Recto en cada transición rígido-flex | 1 mm | Regla de fabricación |
| Carrera de la placa del conector | 12 mm (se verifica con 12,5) | Montaje a través del panel |
| Altura disponible en nominal | 12 − 0,1 = 11,9 mm | Con cinta de 0,25 mm |
| Envolvente lateral | 52 mm, compartida con la cámara y el LED | Mecánica del equipo |
| Cantidad de flex | **uno solo** | Límite del fabricante (PCBWay) |
| Qué se minimiza | **Z**, la separación entre cantos | No el largo del flex |

La cámara (e-con e-CAM52A, MIPI de 2 lanes) va apoyada en el piso, con el lente centrado en los 52 mm y su propio flex recto. En la vista de planta, su placa queda al lado de la S, 2,5 mm por detrás de la línea del flex del conector. Ese es el obstáculo que la S no puede tocar.

# 2. Método

Cada forma del flex se calculó y no se supuso. El flex se modela como una **elástica**: una tira inextensible con los dos extremos empotrados, que adopta la forma de mínima energía de flexión. Las paredes y la placa de cámara entran al modelo como obstáculos. Cada forma se resuelve en milisegundos, así que se puede recorrer toda la carrera y todas las combinaciones de tolerancias.

::: tarjetas 3
::: tarjeta Toda la carrera, ida y vuelta | nominal → retraído → nominal
Se barre la carrera en los dos sentidos, arrancando desde la posición nominal. Así aparece cualquier salto de forma que un barrido en un solo sentido esconde.
:::
::: tarjeta Peor caso con tolerancias | 12 combinaciones por largo
Cuerpo del conector de 6,3 a 7 mm (± 0,35), carrera de 12 y 12,5 mm, largo del flex ± 0,25. Se informa siempre el peor resultado.
:::
::: tarjeta Criterios de aceptación | por forma
R interior ≥ 2,5 en todo el recorrido y juego ≥ 0,3 a la placa de cámara, en nominal y durante toda la carrera.
:::
:::

::: nota riesgo | Lo que enseñó la simulación
**Salto de forma (snap-through).** Cuando la S apoya contra una pared, en algún punto de la carrera salta de golpe a otra forma y el radio cae de repente. Esto no aparecía barriendo la carrera en un solo sentido. Por eso la S tiene que quedar **libre**, sin apoyar en nada, y centrada desde su propia pestaña.

**Largo mínimo.** Por debajo de un largo crítico el flex se tensa y se quiebra. Con este layout, eso ocurre bajo 18,5 mm (figura 5). El largo nominal se eligió lejos de ese borde, no pegado a él.
:::

# 3. Cómo llegamos acá

Cada paso respondió a una limitación del anterior. W es el ancho total que ocupa la solución en el sentido de la carrera. Z es la separación entre cantos de la S.

| # | Propuesta | Resultado | Qué se decidió |
|:--:|---|---|---|
| 1 | Omega libre en el plano vertical, con la placa del conector colgando (9,5 − R) | W ≈ 31–32 mm; con R 3 no entra en la altura | Buscar algo más angosto |
| 2 | Omega del primer boceto | W = 26,4 mm, R 2,7 | Admitir R 2,5 (12 × espesor): W = 25,7 mm |
| 3 | Placa del conector en el piso, flex hacia arriba | W ≈ 23–24 mm | Sigue ancho: pensar el flex en 3D |
| 4 | **S de canto, en el plano de las placas** | W ≈ 13 mm | **Camino elegido** |
| 5 | U rodante | Pide un canal libre de 7,6 mm | Descartada |
| 6 | Integrar la cámara: imagen horizontal | Dobla demasiado el flex de la cámara | Cámara centrada con el flex recto (imagen a 90°) y pared lateral |
| 7 | Cámara + S doble, islas de flex | Dos brazos de flex en una pieza | No fabricable: **un solo flex** |
| 8 | LED junto al lente, sin guía de luz | Tres variantes (A, B, C) | Placa LED con conector B2B delante del flex de cámara |
| 9 | Dimensionar la S | Z 15,5 con R 3, luego Z 14 con R 2,5; pestaña 5 mm atrás | Base del layout final |
| 10 | **Layout del 27/9**, con la placa de cámara como obstáculo | Z = 15,5; L = 19,0 ± 0,25 | **Solución de este informe** |

La galería de la sección 7 muestra cada alternativa en una imagen.

# 4. La solución

La S sale del canto de la pestaña fija, retrocede un poco alejándose del panel, cruza por detrás de la placa de cámara y baja hasta la línea del flex en la placa del conector. En los dos extremos el flex sale por la cara delantera de la placa, con 1 mm recto antes de empezar a doblar.

Coordenadas usadas en todo el informe:

- **z**: hacia la derecha, desde el extremo izquierdo de la placa del conector.
- **x**: hacia el panel, desde la línea del flex en la placa del conector (x = 0). Los valores negativos quedan detrás de esa línea.

| Referencia (nominal) | z | x |
|---|--:|--:|
| Canto de la placa del conector (salida del flex) | 16,50 | 0,00 |
| Canto de la pestaña fija (salida del flex) | 32,00 | −5,00 |
| Cara trasera de la placa de cámara | desde 22,0 | −2,50 |
| Inicio del módulo de cámara | 21,16 | — |

## 4.1 Geometría para dibujar

La forma real tiene radios variables. Para el modelo 3D no hace falta copiarla: alcanza con un perfil de **tres arcos del mismo radio, R 3,5, unidos por rectas**, con el mismo largo desarrollado y los mismos extremos y tangentes. En el equipo el flex va a tomar su forma natural, que es la simulada. El dibujo sirve para reservar el espacio y para obtener el largo desarrollado.

::: fig flex-geometria | Figura 2 — Perfil para dibujar, en posición nominal. La línea de trazos gris es la forma simulada; en ningún punto se aparta más de 0,11 mm del perfil de dibujo. Radios medidos en la línea media del flex. | Elaboración propia. geom_simple.py y s_layout.py.
:::

Recorrido desde la pestaña fija (T1) hasta la placa del conector (T8):

| Tramo | Elemento | Medida | Gira hacia | Punto final (z; x) | Centro del arco (z; x) |
|---|---|---|---|---|---|
| T1–T2 | Recta | 1,00 | — | 31,000; −5,000 | — |
| T2–T3 | Arco | R 3,5 · 21,5° | atrás (se aleja del panel) | 29,717; −5,244 | 31,000; −8,500 |
| T3–T4 | Recta | 3,39 | — | 26,566; −6,485 | — |
| T4–T5 | Arco | R 3,5 · 83,5° | adelante (hacia el panel) | 22,193; −4,871 | 25,284; −3,228 |
| T5–T6 | Recta | 3,41 | — | 20,590; −1,857 | — |
| T6–T7 | Arco | R 3,5 · 62,0° | atrás, hasta quedar paralelo | 17,500; 0,000 | 17,500; −3,500 |
| T7–T8 | Recta | 1,00 | — | 16,500; 0,000 | — |
| | **Total** | **19,00** | | | |

::: nota dato | Cómo trazarlo en Solid Edge
1. Dibujar el croquis como una cadena de rectas y arcos tangentes.
2. Fijar los dos extremos: T1 en (32; −5) y T8 en (16,5; 0). En los dos, el flex sale paralelo a la placa.
3. Acotar los tres radios en **3,5** y las rectas de los extremos en **1,00**.
4. Acotar dos ángulos: **21,5°** y **62°**. El arco central queda determinado, porque 21,5 + 62 = 83,5° y así el flex llega paralelo a la placa del conector.
5. Las dos rectas intermedias (3,39 y 3,41) salen solas al cerrar el croquis.
6. Crear una **pestaña por contorno** sobre ese croquis: espesor 0,2, alto 11, factor neutro 0,5. El largo desarrollado da 19,00.
:::

Chequeos del perfil de dibujo: largo 19,002 mm; juego a la placa de cámara 1,93 mm. El radio interior de dibujo es 3,4 mm y el real es menor, 2,84 mm como mínimo. Por eso el radio se verifica siempre con la simulación, nunca con el dibujo.

## 4.2 Especificación para fabricar

| Parámetro | Valor |
|---|---|
| Largo del flex entre cantos rígidos | **19,0 ± 0,25 mm** |
| Largo mínimo absoluto | 18,5 mm: por debajo, el flex se tensa y apoya en la placa de cámara |
| Rectos en las transiciones | 1,0 mm en cada extremo, sin cobre cruzando la línea de doblez |
| Espesor y capas | 0,2 mm, 2 capas |
| Alto del flex | 11 mm |
| Separación entre cantos (Z) | 15,5 mm |
| Salida del flex | Cara delantera de las dos placas |

::: detalle Perfil exacto de la forma simulada (referencia, desvío 0,02 mm)
Es el ajuste por arcos de la forma de equilibrio en nominal, el mismo que figura en el plano FX-M12-S-03 y en el DXF `S_conector_layout27_nominal.dxf`. No hace falta para dibujar; queda como registro.

| # | Elemento | Desde (z; x) | Medida |
|--:|---|---|---|
| 1 | Recta | 32,000; −5,000 | 1,000 |
| 2 | Arco antihorario | 31,000; −5,000 | R 3,677 · 23,2° |
| 3 | Recta | 29,549; −5,298 | 2,890 |
| 4 | Arco horario | 26,893; −6,439 | R 3,828 · 86,6° |
| 5 | Recta | 21,960; −4,635 | 2,659 |
| 6 | Arco antihorario | 20,769; −2,258 | R 4,376 · 35,7° |
| 7 | Arco antihorario | 18,890; −0,342 | R 2,990 · 27,7° |
| 8 | Recta | 17,500; 0,000 | 1,000 hasta 16,500; 0,000 |
:::

# 5. Verificación en toda la carrera

::: fig flex-carrera | Figura 3 — Forma del flex cada 2 mm de retracción, de 0 (nominal) a 12 mm. La S se abre hacia atrás y nunca toca la placa de cámara. | Simulación de la elástica. s_layout.py.
:::

::: fig flex-robustez | Figura 4 y 5 — Izquierda: R interior a lo largo de la carrera, con L = 19,0 y cotas nominales; el mínimo es 2,84 mm, cerca de los 5 mm de retracción. Centro y derecha: peor caso de R interior y de juego a la placa de cámara según el largo del flex. La banda marca 19,0 ± 0,25. | Simulación de la elástica. Peor caso sobre el cuerpo del conector de 6,3 a 7 mm y la carrera de 12 y 12,5 mm.
:::

| Largo del flex | R interior peor caso | Juego peor caso | Veredicto |
|--:|--:|--:|---|
| 18,25 | 1,77 | 0,30 | No: se tensa y apoya |
| 18,50 | 2,95 | 1,22 | Borde: sin margen para la tolerancia |
| **18,75** | **2,89** | **1,43** | Sí (tolerancia −) |
| **19,00** | **2,84** | **1,87** | **Sí (nominal)** |
| **19,25** | **2,79** | **2,05** | Sí (tolerancia +) |
| 20,00 | 2,69 | 2,40 | Sí, pero ocupa más |

Dentro de la tolerancia de fabricación, el peor caso es **R interior 2,79 mm** con L = 19,25 y **juego 1,43 mm** con L = 18,75. Los dos cumplen con margen.

# 6. Supuestos y puntos abiertos

::: nota inferencia | Supuestos de lectura del layout del 27/9
- La cota **2,5** es la distancia desde la cara trasera de la placa de cámara hasta la línea del flex en la placa del conector, medida hacia atrás.
- La placa de cámara empieza en z ≈ 22 y el módulo, 4,66 mm después del canto de la placa del conector.
- Juego mínimo exigido al flex: 0,3 mm.
- El flex se modela con rigidez uniforme. El cobre de las dos capas cambia la rigidez, pero no el largo ni la forma general.

Si alguna de estas cotas cambia, se vuelve a correr `s_layout.py` y se regeneran el plano y este informe.
:::

Queda por confirmar con una muestra: el largo real entre cantos después del fresado del rígido, y el comportamiento del flex con el cobre en el ciclo de montaje.

# 7. Alternativas evaluadas

Cada imagen es una de las propuestas que se simularon o modelaron en el camino. El resultado de cada una está en una línea; la marca verde indica que la idea sobrevivió, total o parcialmente, en la solución final.

::: fig flex-galeria-1 | Figura 6 — Primer grupo: formas en el plano vertical (omega) y la primera S en el plano de las placas. | Capturas de las páginas de simulación 2D.
:::

::: fig flex-galeria-2 | Figura 7 — Segundo grupo: arquitecturas en 3D e integración de la cámara. | Capturas del visor 3D de opciones.
:::

::: fig flex-galeria-3 | Figura 8 — Tercer grupo: cámara en la pared lateral y variantes del LED. | Capturas del visor 3D de opciones.
:::

# Anexo — Archivos

| Archivo (en `flex_omega/`) | Qué contiene |
|---|---|
| `s_layout.py` → `s_layout.json` | Modelo final: forma nominal, carrera, peor caso por largo y perfil ajustado |
| `plano_layout.py` → plano PDF en `planos/` | Plano FX-M12-S-03: planta 4:1, desarrollo de la tira, tangencias |
| `planos/…nominal.dxf` | Perfil exacto en nominal, para importar en Solid Edge |
| `informe/geom_simple.py` → `geom_simple.json` | Geometría para dibujar: tres arcos R 3,5 |
| `informe/figuras.py` | Figuras de este informe |
| `s_layout.html` | Animación 2D de la carrera con el layout final |
| `opciones3d.html` | Visor 3D de todas las alternativas |
