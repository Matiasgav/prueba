# Articulaciones: estudio de opciones sin tornillos

Estudio de cómo hacer las articulaciones del diseño en metal. Los números salen de `articulaciones_calc.py`.

## 1. Qué tiene que cumplir

| Requisito | Detalle |
|---|---|
| Fuerza | Hasta **5,5 kN por pivote** a W = 35 (con la carga que rompe la estructura: 733 N entre ejes) |
| Nada que se desprenda | **Sin tornillos ni roscas** (cualquier tornillo puede aflojarse) y sin piezas que puedan salir. Traba **de forma** y, si se puede, redundante |
| Sin juego | Radial y axial cero o casi cero. A W = 35 el mecanismo multiplica por 15 el juego del ojo entre los ejes de acople |
| Al ras | Nada sobresale de las caras de 190 × ancho |
| Fabricable | CNC normal (Rapid Direct) y armado con herramientas de taller razonables, sin máquinas caras |
| Espacio | 13 mm de espesor; mejillas de 2,9 (Q), 5,15 (O), 2,15 de acero (C) y 1,6 (P); pasador de Ø5 |

**P1 y P2 no necesitan traba:** las alas de B tapan las dos puntas del pasador, que para salir necesitaría sacar el carro del riel. Quedan **Q1, Q2, O y C**.

## 2. Qué hace una articulación, función por función

Separando las funciones se ve que solo una de ellas, la retención del pasador, quedaba sin resolver. Las demás ya están cubiertas y ninguna opción las cambia:

| Función | Cómo se resuelve (igual en todas las opciones) |
|---|---|
| Llevar la carga | Pasador macizo templado Ø5 en doble corte |
| Girar | El ojo (17-4PH H900, 44 HRC) gira sobre el pasador templado (440C, ≈ 58 HRC). Dureza distinta: no se engrana |
| Juego radial en el aluminio | Pasador **a presión** en las mejillas (7 a 20 µm): no se mueve ni se gasta el agujero blando |
| Juego radial en el ojo | Ojo apareado con el pasador (0 a 3 µm), o lapeado (0 a 1 µm). Ver sección 7 |
| Juego axial y cabeceo | Resorte de disco (Q, P) o arandela ondulada (O, C) |
| **Retención del pasador** | **Es lo que hay que elegir** |

Dato clave: **en servicio el pasador no tiene fuerza axial.** El resorte empuja entre las dos mejillas, que son la misma pieza, y los momentos fuera del plano flexionan el pasador, no lo empujan. Un golpe de 1.000 g sobre un pasador de 1,5 g son 15 N. La traba no tiene que aguantar una carga: tiene que hacer **imposible** que el pasador camine, aunque pasen años de vibración.

## 3. Todas las formas de trabar un pasador sin rosca

| Principio | Ejemplo | ¿Sirve? | Por qué |
|---|---|---|---|
| Cautivo por la arquitectura | P1 y P2 bajo las alas | Solo en P | En Q, O y C la punta queda en una cara a la vista. Taparla exige otra pieza fija, y el problema se repite |
| **Anillo elástico encerrado** | Anillo de alambre entre dos gargantas | **Sí (A)** | Forma, oculto y sin herramienta especial |
| **Deformar una pieza blanda agregada** | Virola estampada sobre una garganta del pasador | **Sí (B)** | Forma y visible; el pasador no se toca |
| Remache pasante en un tubo | Tubo templado + remache aeronáutico | Con riesgo (C) | El remache hincha el tubo y puede trabar el ojo |
| Deformar el alojamiento | Estampado del 7075 | Con riesgo (D) | El 7075 es poco dúctil; no sirve en C |
| Deformar el propio pasador | Remache radial | Con riesgo (E) | Pasador blando, margen ≈ 1 |
| Pasador fijo al ojo y giro en bujes en las mejillas | Muñones | No | Dos superficies que giran (el doble de juego), bujes en mejillas de 1,6 a 2,9 y el pasador no entra en la horquilla cerrada |
| Interferencia sola o por contracción | Ajuste a presión, nitrógeno líquido | Solo como redundancia | Es fricción, no forma |
| Pasador elástico (Spirol, Mecanindus) | Pasador partido | No | Es fricción; el ojo giraría sobre una ranura |
| Adhesivo | Loctite 648 | Solo como redundancia | Es química, no forma |
| Soldadura | Láser | No | El acero no se suelda al aluminio. En C (acero) el calor arruina el H900 y el temple del pasador |
| Anillo de retención a la vista | Seeger en la cara | No | Sobresale y se saca con una pinza |

Siguen cinco conceptos (A a E). Están desarrollados abajo con medidas, cálculo, proceso, modos de falla y control.

![Cinco conceptos](img/articulaciones_conceptos.png)

## 4. Los conceptos en detalle

Los márgenes son a W = 35, sobre la carga que rompe la estructura: margen 1 es igual a esa carga y por encima de 1 la articulación es más fuerte que la estructura. El modelo de flexión es el mismo de `analisis.py`.

### A · Pasador ciego + anillo elástico encerrado

**Geometría:**
- **Pasador:** 440C templado y rectificado Ø5 (m6, o apareado al ojo). Tiene la punta con chaflán de 30° para abrir el anillo y una **garganta de Ø4,4 × 0,7** a 1,3 mm de la punta.
- **Alojamiento:** el agujero de la mejilla de abajo es **ciego** (piso de 0,6 mm: la cara de abajo queda lisa) y tiene una **garganta interior de Ø6,35 × 0,75** a la altura de la del pasador.
- **Anillo:** alambre de resorte inoxidable (1.4568 / 17-7PH o 1.4310) de Ø0,6, con Ø interior libre de 4,7. Al pasar el pasador se abre a 5,05, con una tensión de 1.350 MPa, por debajo del límite del alambre (1.600 a 1.700). Ya cerrado, se mete 0,15 mm en la garganta del pasador y 0,45 mm en la del alojamiento.

**Traba:**
- **Hacia abajo:** de forma, por el fondo del agujero ciego.
- **Hacia arriba**, la única salida: de forma, por el anillo, que aguanta del orden de 0,5 a 1 kN (estimado: el anillo puede rodar en la garganta), y además la interferencia (0,4 a 1,1 kN).
- **Variante redundante:** un segundo anillo en la mejilla de arriba. Las gargantas del pasador llevan el flanco de arriba en rampa de 30°, para que el pasador pueda bajar a través del primer anillo, y el de abajo recto, que es el que traba. Así quedan dos trabas de forma independientes para el único sentido de salida.

**Resistencia:**

| Pivote | Flexión del pasador | Aplastamiento |
|---|---:|---:|
| Q | 2,6 | 3,7 |
| O | 2,2 | 6,2 |
| C | 4,4 | 4,9 |

La garganta queda donde el momento es el **1 %** del máximo (en C, el 7 %), así que no debilita el pasador.

**Fabricación y armado:**
1. La garganta interior se hace en el CNC con una fresa de ranurar de Ø4 y cuello de Ø2,5, que entra por el agujero de arriba (sin el eslabón puesto) e interpola el círculo. En C se hace en el ala antes del envejecido H900.
2. El anillo se baja comprimido con un empujador hasta que salta a su garganta.
3. Se pone el eslabón con su resorte.
4. Se prensa el pasador: al cerrarse el anillo se siente en la prensa.

**Control:** el pasador lleva un agujero central roscado M2 que solo usa el tirador del ensayo (no queda ningún tornillo). Se tira con 200 N: si no se mueve, el anillo está puesto.

**Modos de falla:**

| Falla | Qué la evita |
|---|---|
| Anillo mal asentado | El ensayo de 200 N, en todas las articulaciones |
| Anillo que se abre con el tiempo | Queda sin tensión, encerrado; no hay nada que lo abra |
| Corrosión | Inoxidable y grasa en el agujero |

**Aspecto:** arriba se ve solo el disco del pasador (Ø5) al ras; abajo, nada. **No se desarma:** hay que perforar el pasador.

![Armado de A y B](img/articulaciones_armado_AB.png)

### B · Pasador con cabeza + virola estampada (recomendada)

**Geometría:**
- **Pasador:** 440C templado y rectificado Ø5 con **cabeza de Ø6,5 × 1,0** (Ø6,5 × 0,7 en C), en una cajera de la cara de arriba. En la punta de abajo tiene una **garganta de Ø4,4 × 0,6**. Se consigue como pin de posicionamiento con brida para presión, configurable (Misumi lo ofrece en 440C), o a medida.
- **Virola:** anillo de **inox. 304 recocido** de Ø6,8 × Ø5,05 × 1,2 (0,8 en C), en una cajera de la cara de abajo.
- **Estampado:** un punzón hueco con tope de profundidad empuja el borde interior de la virola dentro de la garganta del pasador.

**Traba:**
- **Hacia abajo:** de forma, por la cabeza del pasador sobre su cajera.
- **Hacia arriba:** de forma, por la virola estampada sobre su cajera. Para sacarla hay que cortar el metal de la virola dentro de la garganta, unos **3,5 kN**.
- **Además:** la interferencia. Son dos trabas de forma independientes, una por sentido, más la fricción.

**Resistencia:**

| Pivote | Flexión del pasador | Aplastamiento |
|---|---:|---:|
| Q | 2,9 | 2,7 |
| O | 2,5 | 5,4 |
| C | 4,8 | 4,3 |

La cajera de Ø6,9 en Q deja 0,75 mm de pared hasta la cara interior de A; lo comprobé en el CAD. Ni las cajeras ni las gargantas tocan el túnel del cable.

**Por qué es la más controlable:**
- **Se deforma una pieza agregada, blanda y muy dúctil** (304 recocido, alargamiento de 40 %), no el pasador ni el 7075. Nada se abarrila.
- **La deformación la fija el tope del punzón**, no la fuerza: siempre queda igual.
- **Alcanza con una prensa de mano** (de cremallera, 1 a 2 t). El estampado pide del orden de 5 a 6 kN, que se descargan sobre la cabeza del pasador, apoyada en una base plana. La cajera de aluminio ve unos 250 MPa, por debajo del aplastamiento admisible.
- **Se ve si está bien hecho:** la marca del punzón queda en la virola.

**Armado:**
1. Pasador a presión desde arriba, hasta que la cabeza apoya.
2. Se da vuelta la pieza.
3. Virola a mano en su cajera.
4. Se estampa con la prensa hasta el tope.
5. Ensayo de 300 N empujando desde abajo.

**Modos de falla:**

| Falla | Qué la evita |
|---|---|
| Estampado incompleto | El tope y el ensayo de 300 N |
| Virola fisurada | El 304 recocido no se fisura con 0,3 mm de deformación |
| Corrosión | Inox. 304 en aluminio anodizado: sellar la cajera con grasa o barniz |

**Aspecto:** arriba, el disco de la cabeza (Ø6,5); abajo, la punta del pasador dentro de un anillo de inox. de Ø6,8, los dos al ras. **No se desarma:** hay que cortar la virola.

### C · Tubo templado + remache aeronáutico pasante

- **Cómo es:** el pasador es un **tubo de 440C** de Ø5 × Ø3,3, con las puntas avellanadas a 100° antes del temple. Por adentro pasa un **remache macizo de 1/8"** (MS20426, de aluminio 2117), con la cabeza avellanada arriba y la cabeza formada al ras en un avellanado abajo. Las dos cabezas pisan la mejilla (Ø5,72 > Ø5).
- **Traba:** de forma en los dos sentidos (4,6 kN, por aplastamiento de la cabeza sobre la mejilla).
- **Herramienta:** remachadora de mano «squeezer», la de los que construyen aviones caseros. Es barata, la altura queda fija por la matriz y no hay golpes.
- **Resistencia del tubo:**

  | Pivote | Margen |
  |---|---:|
  | Q | 2,3 |
  | O | 2,0 |
  | C | 4,3 |

- **El problema:** al remachar, el remache se hincha dentro del tubo y empuja hacia afuera. Con unos 250 MPa, **el tubo crece ~10 µm de diámetro**, más que la holgura del ojo (0 a 3 µm), y **el ojo quedaría trabado**. Habría que dejar el interior del tubo más grande en la zona del ojo, o aceptar más holgura. **Queda como alternativa, con prueba obligatoria.**

### D · Estampado del aluminio sobre el pasador

- **Cómo es:** como B, pero en lugar de la virola se empuja el **7075** del borde del agujero dentro de la garganta del pasador.
- **Traba:** de forma; unos 3,7 kN.
- **Problemas:**
  - El 7075-T6 tiene ~11 % de alargamiento y se puede **fisurar** en el borde.
  - El anodizado se rompe alrededor.
  - **No sirve en C**, porque las alas son de acero H900.
- **Conclusión:** B hace lo mismo con una pieza que sí se deja deformar, así que D queda descartada frente a B.

### E · Remache del propio pasador

- **Cómo es:** traba de forma, permanente.
- **Problemas:**
  - El pasador tiene que ser deformable (H1150), con **margen 1,0 a 1,2**.
  - Hay riesgo de abarrilar.
  - Necesita remachadora radial con tope, que es cara.
- **Conclusión:** queda por debajo de B en todo.

## 5. Cada concepto en cada articulación

| | Q1 / Q2 (7075, 2,9) | O (7075, 5,15) | C (acero H900, 2,15) | P1 / P2 |
|---|---|---|---|---|
| **A** anillo oculto | Sí | Sí | Sí (garganta antes del envejecido) | No hace falta |
| **B** cabeza + virola | Sí | Sí | Sí (cabeza de 0,7, virola de 0,8) | No hace falta |
| C tubo + remache | Sí, con riesgo de trabar el ojo | Ídem | Ídem | No hace falta |
| D estampado del aluminio | Riesgo de fisura | Riesgo de fisura | No | No hace falta |
| E remache del pasador | Margen 1,2 | Margen 1,0 | Margen 2,0 | No hace falta |

## 6. Comparación y recomendación

| Criterio | A · Anillo oculto | **B · Cabeza + virola** | C · Tubo + remache | D · Estampado Al | E · Remache |
|---|---|---|---|---|---|
| Traba de forma ↓ / ↑ | Ciego / anillo | Cabeza / virola | Cabeza / cabeza | Ciego / aluminio | Cabeza / cabeza |
| Redundancia | Interferencia (+ 2.º anillo) | Interferencia | Interferencia | Interferencia | Interferencia |
| Capacidad de la traba | 0,5 a 1 kN (estimado) | 3,5 kN | 4,6 kN | 3,7 kN | Alta |
| Margen del pasador (peor pivote) | 2,2 | 2,5 | 2,0 | 2,0 | 1,0 |
| Riesgo para el juego del ojo | Ninguno | Ninguno | **Alto** (hinchado) | Ninguno | Medio (pasador blando) |
| Control del proceso | Clic + ensayo con tirador | **Tope + marca visible + ensayo** | Matriz del squeezer | Tope (fisuras) | Máquina con tope |
| Herramientas | CNC (fresa de ranurar) + prensa | Prensa de mano + punzón | Squeezer + matrices | Prensa + punzón | Remachadora radial |
| Aspecto | **Arriba un disco, abajo nada** | Disco arriba, anillo inox. abajo | Remache en las dos caras | Disco + marca | Remache al ras |
| Se ve que está bien | No (hace falta el ensayo) | **Sí** | Sí | Sí | Sí |
| Desarme | Perforar | Cortar la virola | Perforar el remache | Perforar | Perforar |

**Recomendación: B (cabeza + virola estampada) en Q1, Q2, O y C**, y el pasador liso de siempre en P1 y P2.
- Traba por forma los dos sentidos con elementos independientes.
- No deforma ni el pasador ni el 7075.
- La deformación la controla un tope, así que no depende de la fuerza.
- Se inspecciona a la vista.
- Usa una prensa de mano.
- Deja el margen del pasador en 2,5 o más.

**Alternativa: A (anillo oculto)**, si importa más que **no se vea nada** en la cara de abajo y aceptás que la traba no se ve (control por ensayo). Con dos anillos es la más redundante en el único sentido de salida.

## 7. Juego: presupuesto por articulación

| Fuente | Valor | Cómo se elimina |
|---|---|---|
| Pasador en el aluminio | 0 | Interferencia de 7 a 20 µm; con +50 °C pierde 3 µm |
| Ojo sobre el pasador | 0 a 3 µm (apareado) o 0 a 1 µm (lapeado) | Medición y apareo; o lapeado de cada ojo con su pasador |
| Axial / cabeceo | 0 hasta ≈ 1 N·m por pivote | Resorte de disco de ≈ 250 N |
| Carro en el riel | Depende de la traba (pendiente) | Diseño de la traba |

**Juego entre ejes al invertir la carga:**

| Ajuste del ojo | W = 35 | W = 70 |
|---|---:|---:|
| Apareado | ≤ 0,09 mm | ≤ 0,02 mm |
| Lapeado | ≤ 0,03 mm | ≤ 0,01 mm |

Para comparar, el conjunto se deforma 0,09 mm con 13 N a W = 35. Si hiciera falta juego cero absoluto, el paso siguiente es un **pivote de conos precargados** (sección 8 de la ronda anterior). Sirve con A y con B.

## 8. Antes de decidir: muestras de prueba

En una tarde de taller se valida el concepto elegido antes de llevarlo al diseño:

1. **Probetas:**
   - Dos placas de 7075 de 2,9 mm con un separador de acero de 7 mm, que hace de ojo, para Q.
   - Una plaqueta de 17-4PH H900 de 2,15 para C.
   - Tres o cuatro pasadores de cada variante.
2. **Medir:**
   - El par de giro del ojo antes y después de trabar: no debe cambiar.
   - El empuje hasta que la traba cede (esperado: > 1 kN en B).
   - El aspecto de la cara.
3. **Cortar** una probeta al medio para ver cómo quedó la virola (B) o el anillo (A).

---

## Historial: rondas anteriores (descartadas)

- **Ronda 1:** pasador con cabeza + tornillo M2 solapado, y casquillo + tornillo avellanado. Descartadas porque usan tornillos ([dibujo](img/articulaciones_opciones.png)).
- **Ronda 2:** anillo oculto, estampado del aluminio y remache, en una versión preliminar ([dibujo](img/articulaciones_sin_tornillos.png)). Esta ronda 3 la reemplaza, con la virola estampada (B) y el tubo con remache (C) como conceptos nuevos.
