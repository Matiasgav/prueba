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
