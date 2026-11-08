# Paquete de arandelas de fricción: verificación

> **Actualización con FEA** (t = 0,5 mm confirmado, eslabones de Al 7075-T6): ver la sección "FEA" al final.
> La primera estimación manual era **optimista**: el FEA da la mitad de capacidad en la oreja de A.

Cálculo: `python3 calculo_arandelas.py` (solo usa la biblioteca estándar). Los supuestos están marcados en el código.

## Supuestos
- 6 arandelas intercaladas A-B-A-B-A-B (así se ve en el corte), con un espesor de **t ≈ 0,5 mm** medido sobre la imagen. Hay que confirmarlo.
- 5 interfaces A/B que deslizan. Las caras extremas se toman como solidarias.
- Tornillo de hombro Ø6/M5 inoxidable A2-70, hexágono de 3 mm (tipo ISO 7379), K = 0,25 (inox en seco). La cabeza mide Ø10 y aprieta una corona de Ø6 a Ø10, con r_eff = 4,08 mm.
- μ inox/inox entre 0,15 (lubricado) y 0,40 (seco). Para el criterio "desliza antes de deformar" se usa μ_máx.
- Se toma como fallo el inicio de la fluencia (Rp0,2) en el aplastamiento de los cantos.

## Resultados (t = 0,5 mm, AISI 304)
| Elemento | Carga con la Allen apretada (2,5 N·m → ~2000 N) | Capacidad | Estado |
|---|---|---|---|
| Tornillo (cuello de rosca) | 250 MPa von Mises | 450 MPa | OK hasta ~4 N·m |
| Compresión entre arandelas | 40 MPa | 215 MPa | OK |
| **Oreja A** (aplastamiento lateral, 1 mm × t, brazo 7 mm) | par de fricción por arandela 6,5 N·m | **0,75 N·m** | **FLUYE (×8,7)** |
| Caras de 11 mm de B (cantos) | 6,5 N·m | 1,38 N·m | FLUYE (×4,7) |

Con todo apretado, el paquete resiste bien la compresión. El problema aparece cuando se le aplica par a la articulación. Antes de deslizar, cada arandela intermedia tiene que transmitir la fricción de sus **dos** caras, 2·μ·F·r_eff. Ese par supera con creces lo que aguanta la oreja de A, que es el punto débil n.º 1, y también lo que aguantan los cantos de B, el n.º 2. En ese caso el sistema **no desliza: se deforman las orejas**.

## Conclusión clave
El par máximo de traba que se puede tener deslizando antes de deformar es

    T_traba,máx = (N_interfaces / 2) · T_cap,arandela

Este valor **no depende de μ ni de la precarga**. μ y F solo fijan el apriete al que se alcanza ese límite. Para subirlo hay tres palancas:
1. Más capacidad por arandela: más encastre de la oreja (pasar de 1 mm a toda la oreja), más espesor y un inox endurecido (301 1/2 duro, 17-7PH).
2. Más arandelas: el par crece de forma lineal con el número de interfaces.
3. Una precarga **controlada** que no dependa del par de apriete a mano.

Ejemplos con la tabla del script: con t = 1 mm de 17-7PH desliza antes de fluir incluso apretando a 2,5 N·m (~22 N·m de traba máxima). Con t = 0,5 mm de 304 hay que limitar la precarga a ~230 N (≈0,3 N·m de apriete, imposible de controlar a mano) y la traba queda en ~1,9 N·m.

## Recomendaciones
- **Oreja A**: encastrarla en toda su longitud (2–2,5 mm) en lugar de solo 1 mm. Mejor aún, usar dos orejas opuestas, que reparten la carga en un par de fuerzas y descargan el agujero contra el vástago.
- **Precarga definida**: dejar que el tornillo de hombro haga tope en su hombro y dar la carga con una arandela Belleville calibrada. Así F no depende de cuánto se apriete la Allen y se compensa el desgaste. Atención: si el hombro hace tope antes que el paquete, las arandelas quedan sin apriete.
- **Arandela en contacto con la cabeza**: tiene que ser del mismo tipo que el eslabón en el que rosca el tornillo. Si no, el giro de la articulación aplica par a la cabeza y afloja (o sobreaprieta) el tornillo.
- **Gripado inox/inox**: el 304 contra 304 en seco gripa. Lubricar (μ más bajo y estable) o alternar materiales/recubrimientos. Bajar μ no cambia la traba máxima, solo exige más F.
- **Eslabones**: el eslabón recibe la misma fuerza de aplastamiento que la oreja. Si es de aluminio o plástico, puede ser él el que se marque primero.


---

## FEA (tensión plana, `fea/`)

`cd fea && python3 fea_arandelas.py . && python3 graficos.py` (requiere `scikit-fem meshpy scipy matplotlib`).

**Modelo**
- Triángulos cuadráticos P2, unos 65 000 elementos de 0,07 mm. Inox con E = 193 GPa, t = 0,5 mm.
- Carga: fricción de las dos caras de una arandela intermedia, aplicada como tracción tangencial uniforme en la corona Ø6–Ø10 apretada por la cabeza.
- Apoyos de **contacto unilateral** (solo compresión, iterado) contra paredes rígidas: el costado de la oreja (A) o las caras de 11 mm (B), y el vástago Ø6.
- Comprobaciones: el momento de las reacciones es igual al par aplicado (1000,0 N·mm). La malla converge: el criterio promediado varía un ±5 % entre h = 0,07, 0,10 y 0,14 mm.
- Criterio de tensión: von Mises **promediado en r = 0,1 mm**. Los cantos vivos dan picos singulares que en la realidad se asientan con una marca local. Se usan dos niveles:
  - **Nivel 1 (sin marcas):** tensión local promediada < Rp0,2 en la arandela y presión en la pared < Rp0,2 del Al (460 MPa).
  - **Nivel 2 (sin deformación apreciable):** aplastamiento medio en el largo de contacto y tensión del cuerpo lejos del contacto (> 0,3 mm) < Rp0,2. Se aceptan marcas locales.

**Resultados por 1 N·m de par en una arandela** (todo escala de forma lineal)

| Caso | σvM local | σvM cuerpo | Fuerza en pared | Presión local en pared | Aplastamiento medio |
|---|---|---|---|---|---|
| A, oreja 1 mm (actual) | 573 MPa | 370 MPa | 146 N | 863 MPa | 292 MPa |
| A, oreja alargada a 8,5 mm, encastre 2 mm | 399 MPa | 366 MPa | 139 N | 616 MPa | 140 MPa |
| B, caras de 11 mm | 329 MPa | 190 MPa | 156 N por cara | 330 MPa | 86 MPa |

La fuerza en la pared coincide con el cálculo manual (146 N frente a 143 N). Lo que el cálculo manual no veía es que la presión **no es uniforme**: se concentra en el borde de entrada de la ranura del eslabón, que es la pared de Al. A eso se suma la concentración en el **canto vivo interior de la raíz de la oreja**, en (−5,5; ±2,5).

**Demanda.** Con la Allen a 2,5 N·m (unos 2000 N), cada arandela intermedia tiene que transmitir 2,5 N·m (μ 0,15), 4,9 N·m (μ 0,3) o 6,5 N·m (μ 0,4). **Con apriete libre a mano, ninguna combinación desliza antes de deformar.** La precarga hay que fijarla.

Ver `fea/tabla_capacidad.md` y los gráficos:
- `fea/fea_mapas_1Nm.png`
- `fea/fea_oreja_zoom.png`
- `fea/capacidad_vs_demanda.png`

### ¿Mejora alargar la oreja para encastrar 2 mm?
Sí. La pared tiene que seguir en r ≥ 6,5 para no rozar el R6 de las B, así que la oreja pasa de 7,5 a 8,5 mm.
- Nivel 1: la capacidad sube un **+40 %** (0,53 → 0,75 N·m, limita el Al).
- Nivel 2: **sube ×1,7 a ×2,1** (1,6 → 2,6–3,3 N·m), porque el aplastamiento medio sobre el Al se reduce a la mitad.

Aun así, A sigue siendo la arandela débil: B aguanta aproximadamente el doble. Además conviene **redondear con R0,3–0,5 la raíz de la oreja**, que es la segunda concentración.

### Materiales
- 304 recocido (215 MPa): **no sirve**. Fluye con menos de 0,6 N·m por arandela.
- Por encima de unos 900–1000 MPa, la que manda es la **pared de Al 7075** y no la arandela. Más dureza no aporta nada en la oreja de 1 mm.
- Con la oreja de 2 mm, el óptimo está entre 965 y 1350 MPa.
- Recomendación:
  - **A en AISI 301 duro** (full hard, ≥ 965 MPa) o **420 templado**. Las dos van cortadas por láser o por electroerosión de hilo, sin rebaba.
  - **B en un material distinto del de A**, por ejemplo 301 duro contra 420 templado, o 17-7PH. Así se evita el **gripado** inox/inox.
  - Montar con grasa (MoS₂ o PTFE).

### Ejemplo de dimensionado (oreja de 2 mm, A en 301 duro, nivel 2 con factor de seguridad 1,25)
- T_adm por arandela = 2,1 N·m.
- **Lubricado, μ de 0,12 a 0,18:** F ≤ 2100 / (2·0,18·4,08) ≈ **1400 N**. La traba con 6 arandelas queda entre 3,5 y 5,2 N·m.
- **En seco, μ de 0,2 a 0,4:** F ≤ 640 N. La traba queda entre solo 1,3 y 2,6 N·m.

Una banda de μ estrecha (lubricado) asegura **más** traba que en seco. La precarga de unos 1400 N se da mejor con una Belleville calibrada y el tornillo de hombro haciendo tope. Con llave dinamométrica serían unos 1,3 N·m, con K = 0,18 lubricado.

### Variante sin lubricar (pares de materiales distintos)
En seco, el inox contra inox **gripa**: μ sube con los ciclos (de 0,3 hasta más de 0,6), arranca material y termina superando la capacidad de las orejas. La alternativa sin grasa es un **par disímil**:

| Arandela | Material propuesto | Por qué |
|---|---|---|
| A (la débil, limita la oreja) | **AISI 301 duro** o **420 templado** | Resistencia de 965 a 1350 MPa, por encima de la cual manda el Al 7075 |
| B (le sobra capacidad) | **Bronce fosforoso CuSn8 duro** (Rp0,2 ≈ 600 MPa) o **CuBe2 templado** (≈ 1000 MPa, más caro) | No gripa contra inox, μ en seco más estable (≈ 0,20–0,35). B en CuSn8 aguanta 3,2 N·m en nivel 2, más que A |

Dimensionado en seco: oreja de 2 mm, nivel 2 / 1,25, 6 arandelas, K ≈ 0,3 en seco.

| A | Par | μ | F máx | Apriete | Traba |
|---|---|---|---|---|---|
| 301 duro | inox / CuSn8 | 0,20–0,35 | 740 N | ≈ 1,1 N·m | 3,0–5,3 N·m |
| 420 templado | inox / CuSn8 | 0,20–0,35 | 920 N | ≈ 1,4 N·m | 3,8–6,6 N·m |
| 420 templado | inox / inox (no recomendado) | 0,30–0,60 | 540 N | ≈ 0,8 N·m | 3,3–6,6 N·m al inicio, después impredecible |

La traba máxima la fija la capacidad de A, no μ. μ solo abre o cierra el rango. Para subir la traba mínima garantizada, la palanca es **agregar pares de arandelas**: cada par A+B suma unos 1,2–1,5 N·m. Los valores de μ en seco son bibliográficos y conviene medirlos con un ensayo simple (par de deslizamiento frente a apriete) antes de fijar la precarga.

### Especificación para el pedido (RapidDirect u otro proveedor)
| | Arandela A | Arandela B |
|---|---|---|
| Material | **SUS301-CSP H** (AISI 301 duro, HV ≥ 430, Rp0,2 ≥ 965 MPa), con certificado de material | **C5210-H/EH** (CuSn8 duro, JIS) o C5191-H (CuSn6), con certificado de material |
| Espesor | 0,50 ± 0,02 mm, planitud ≤ 0,05 mm | igual |
| Proceso | **Electroerosión por hilo** apilando chapas, o láser de fibra con N₂ y potencia baja. Sin temple posterior, porque el material ya viene duro | Electroerosión por hilo (el cobre refleja el láser y los bordes quedan peores) |
| Detalles críticos | Oreja de 8,5 mm, ancho 5 −0/+0,02, **radio R0,4 en la raíz** | Caras de 11 −0,02/−0,05 |
| Rebaba | ≤ 0,03 mm, sin rebaba en las caras de fricción. Sin tamboreo agresivo, que redondea el canto de la oreja | igual |

### ¿Se puede apretar más? Variante A con dos orejas opuestas (`fea/fea_dos_orejas.py`)
El par que tiene que aguantar cada arandela es 2·μ·F·r_eff y crece con el apriete. Agregar arandelas no lo reduce. Para apretar más hay que subir la capacidad de A.
- **Dos orejas opuestas** (encastre 2 mm cada una) forman un par de fuerzas. Por N·m: 70 N por oreja (antes 139), vástago casi descargado, σvM del cuerpo 178 MPa y aplastamiento medio en el Al de 70 MPa. **La capacidad se duplica.**
- **Espesor:** en tensión plana todas las tensiones escalan con 1/t, así que 0,8 mm da ×1,6.

Seco, μ 0,20–0,35, K = 0,3, nivel 2 / 1,25:

| A | Cap. [N·m] | F máx | Apriete Allen | Traba (6 arandelas) |
|---|---|---|---|---|
| 1 oreja, 420, 0,5 mm | 3,3 | 920 N | 1,4 N·m | 3,8–6,6 N·m |
| 2 orejas, 301 duro, 0,5 mm | 5,4 | 1500 N | 2,3 N·m | 6,1–10,8 N·m |
| 2 orejas, 420, 0,5 mm (limita el Al) | 6,6 | 1850 N | 2,8 N·m | 7,6–13,2 N·m |
| 2 orejas, 420, 0,8 mm | 10,5 | limita el tornillo, ≈ 2300 N | 3,5 N·m | 9,5–16,6 N·m |

### Materiales para la versión de dos orejas (apriete ≈ 2,3 N·m, F ≈ 1500 N, seco)
Con F = 1500 N y μ = 0,35, cada arandela intermedia tiene que transmitir **4,3 N·m**. Eso vale también para las **B**. Con este apriete, la B de bronce de 0,5 mm pasa a ser la débil: el cuerpo está a 190 MPa por N·m, lo que da unos 3,2 N·m de capacidad con CuSn8 (Rp0,2 ≈ 600 MPa).

| Arandela | Opción recomendada | Capacidad (nivel 2) | Admisible / 1,25 |
|---|---|---|---|
| A (2 orejas) | SUS301-CSP H, 0,5 mm | 5,4 N·m | 4,3 N·m ✔ (justo) |
| B | **CuBe2 (C17200) envejecido**, Rp0,2 ≈ 1000 MPa, 0,5 mm | ≈ 5,3 N·m (limita el Al) | 4,2 N·m ✔ (justo) |
| B (alternativa) | **CuSn8 C5210-H de 1,0 mm** | ≈ 6,3 N·m | 5,0 N·m ✔ |

### Tornillo: Accu SSHE-M5-6-xx-A2 (método Shigley, cap. 8)
Datos del fabricante: hombro Ø6 (+0/−0,025), M5×0,8, rosca de 6 mm, cabeza Ø10×5, **hexágono 3 mm**, acero A2 (304), "no estandarizado". **No declara la clase resistente.** Mecanizado desde barra, puede estar entre A2-50 y A2-70.

Par según Shigley, ec. 8-26: T = Fi·[dm/2·(l+πf·dm·secα)/(πdm−f·l·secα) + fc·dc/2]. Valores: dm = 4,48, dc = 8,1, α = 30°.
- f = 0,15 → K = 0,23. f = 0,20 (inox en seco) → **K = 0,29**. El 45 % del par va a la rosca y produce torsión en el vástago.
- Tensión combinada en el apriete (von Mises): σ = Fi/A, τ = 16·T_rosca/(π·d³).
- A = At = 14,2 mm². El cuello bajo el hombro (supuesto Ø3,9, no publicado) da 11,9 mm².

| Clase | Precarga Shigley 0,75·At·Sp | Par (K 0,29) | Fluencia en el cuello | Rotura aprox. (cuello) |
|---|---|---|---|---|
| A2-70 (Rp 450 / Rm 700) | 4070 N | 6,0 N·m | 5,1 N·m (3500 N) | ≈ 8 N·m |
| A2-50 (Rp 210 / Rm 500) | 1900 N | 2,8 N·m | 2,4 N·m (1640 N) | ≈ 5,7 N·m |

Llave hexagonal de 3 mm: par de prueba mínimo ≈ 7,6 N·m (ISO 2351-3:2002 / ISO 2936). El hexágono de un tornillo de 304 suele redondearse antes que la llave.
Rosca del eslabón de Al 7075 (6 mm de encastre, 7,5 hilos): cizalla τ ≈ 3F/(π·d·n·p) → aguanta más de 8000 N. No limita.
Fuerza axial: F = T/(K·d) ≈ **690 N por cada N·m** en seco (870 N/N·m con f = 0,15).

**Peor caso, A2-50.** El cuello de Ø3,9 empieza a fluir durante el apriete con unos 1640 N (2,4 N·m con K = 0,29). En seco, K varía entre 0,23 y 0,35. Con **1,8 N·m** en la Allen, la precarga queda entre 1030 y 1570 N, siempre por debajo de la fluencia. **Apriete máximo recomendado: 1,8 N·m (≈ 1500 N como máximo).**
Con ese apriete, el diseño de dos orejas (A 301 duro de 0,5 mm, B C5210 de 1,0 mm) da una demanda máxima de 4,5 N·m por arandela (μ 0,35), frente a 5,4 N·m de capacidad de A, así que desliza antes de deformar. Traba: entre 4,2 y 11,2 N·m.

### Alternativa: inox/inox, menos arandelas y más gruesas (F 1030–1570 N, μ seco 0,3–0,6)
La traba vale n_interfaces·μ·F·r_eff. Como F está limitada por el tornillo, **el espesor no aumenta la traba: solo permite soportar un μ más alto.** Sacar arandelas reduce la traba en la misma proporción.

| Paquete | Interfaces | Traba [N·m] | Demanda máx. por arandela | Capacidad (1,0 mm, 301 duro) |
|---|---|---|---|---|
| Bronce: 3 A de 0,5 + 3 B de 1,0 (4,5 mm) | 5 | 4,2–11,2 | 4,5 N·m | – |
| Inox 1,0 mm, A-B-A-B (4 mm) | 3 | 3,8–11,5 | 7,7 N·m | A 10,8 / B 10,2 ✔ |
| Inox 1,0 mm, A-B-A-B-A (5 mm) | 4 | 5,0–15,4 | 7,7 N·m | ✔ |

Estructuralmente funciona con 1,0 mm. El riesgo es el **gripado**: μ puede pasar de 0,6 con el uso y la articulación desliza a saltos. Para mitigarlo, usar durezas distintas (A en 301 duro, B en 420 templado o 17-4PH H900), granallar las caras y validar con un ensayo de ciclos.
