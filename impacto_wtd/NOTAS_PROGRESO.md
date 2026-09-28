# Notas de progreso — módulo de impacto WTD

Sesión nocturna 2026-09-01/02. Deadline 08:00 (UTC-3).

## Plan de trabajo

- [x] P0 — Núcleo físico (`wtd/`): materiales, Hertz, actuadores, resortes, palanca,
      viga Timoshenko FE, acoplamiento modal.
- [x] P1 — Test suite contra los casos ancla del brief (§9).
- [x] P2 — Arquitectura del módulo 10×10×(50–60): concepto, presupuesto energético,
      vuelo libre, separación, sensor inductivo.
- [x] P3 — Alternativas de mecanismo (≥8), cada una con números y diagrama.
- [x] P4 — Dinámica de la cuña: estados de ajuste/soltura, modal lineal + no lineal
      (rattle), features discriminantes, separabilidad.
- [x] P5 — Barridos / Pareto de energía entregada, límite de daño, ancho de banda.
- [x] P6 — Monte Carlo de repetibilidad + confiabilidad (fatiga, desgaste, ciclos).
- [x] P7 — Cadena de adquisición y sensado.
- [x] P8 — HTML interactivo profesional (`docs/index.html`).
- [x] P9 — Lista de incógnitas abiertas / decisiones del usuario.

## Estado

Arranque: 2026-09-01 22:13 (UTC-3).

## Rev. A completa — 2026-09-02 01:05 (UTC-3)

Todo el plan P0–P9 hecho. 34/34 anclas, 19/19 tests, informe HTML de 1,4 MB con 17 secciones,
7 diagramas SVG y 10 herramientas interactivas.

### Pendiente para las horas que quedan
- [ ] Verificar hipótesis marcadas [E] que más pesan (k_ripple, k_shoulder, c_slide).
- [ ] Barrido de sensibilidad de la escalera de estados a esos parámetros.
- [ ] Buscar más alternativas de mecanismo.
- [ ] Revisión de cálculos: unidades, escalados, coherencia entre secciones.

## Rev. B — 2026-09-02 07:45 (UTC-3), cierre

Correcciones aplicadas sobre la rev. A tras el barrido de sensibilidad:
- La monotonía del índice de rebote depende de la masa de la maza (4 g sí, 8 g no).
- De los cinco parámetros estimados de la cuña, sólo la disipación de junta mueve el resultado.
- Bug corregido en hertz_plastic_correction (energía de fluencia 2,5x baja).

### Lo que quedó sin hacer (orden de valor)
1. Cuatro arquitecturas más, ya identificadas y sin modelar:
   - Resonador accionado por voice coil ("swing-up"): reusa el LAH04, acumula energía en
     ~50 ms a resonancia y libera en el paso por cero, donde la velocidad es máxima. Sin
     traba ni motor de amartillado. Probablemente la alternativa más interesante que falta.
   - Volante de inercia como acumulador + leva de disparo (~35 mJ en un volante de 8x5 mm
     a 20.000 rpm). Sin resorte que fatigar.
   - Bobina de Thomson (repulsión pulsada sobre disco de aluminio): sin contacto, sin
     desgaste, y el proyectil de aluminio sirve además de blanco del sensor. Hace falta
     una estimación honesta de rendimiento antes de recomendarla o descartarla.
   - Viga bi-estable con snap-through: la biestabilidad hace de traba.
2. Los números de las arquitecturas A3 (VCA tubular) y B4 (VCA plano) del catálogo están
   cargados a mano, no calculados con wtd.actuator.FlatVoiceCoil. Hay que atarlos al modelo.
3. Diseño de detalle del amartillado y cálculo magnético de la traba.
4. Verificación de la longitud media de espira en FlatVoiceCoil.power (usa h_coil donde
   debería ir el ancho de la sección).

## Rev. C — 2026-09-20: palpador de acople blando (1 N de precarga)

Restricción nueva del usuario: la precarga disponible es 1 N como máximo, el palpador
va a 10–15 mm del golpe, e interesa la energía transmitida más que la forma de onda.
Con esa precarga el palpador rígido de `wtd/palpator.py` es inviable: seguir los
miles de g de la cuña pediría una masa móvil de ~20 mg.

Módulo nuevo `wtd/softprobe.py`, estudio `studies/soft_probe.py`, resultados en
`results/softprobe.json`, 8 anclas en `tests/test_softprobe.py`.

### Lo que se estableció

1. **El fondo de escala de cualquier palpador apoyado vale F/m, y no depende del
   resorte.** Ablandar el acople no cuesta rango: cambia qué parte del movimiento de
   la cuña cae adentro de ese fondo de escala. Con acople rígido se gasta en los picos
   de aceleración de alta frecuencia, que no llevan información; con acople blando se
   gasta en el desplazamiento, que sí.
2. **El pico de aceleración de la cuña no es monótono con la soltura; el de
   desplazamiento sí.** A 5 mJ y 12,5 mm, S3 (25 % de precarga) da 4855 g y S6 (floja)
   1069 g: un mismo valor corresponde a dos estados opuestos. Es el argumento de fondo
   contra medir aceleración de la cuña, independiente de la precarga disponible.
3. Diseño resuelto: **m = 0,68 g, resorte de 45 N/mm, f0 = 1,27 kHz, precarga 1 N**.
   126 casos simulados (7 estados × 6 energías × 3 distancias), **cero despegues**,
   lectura de 0,9 a 109 g. El resorte se lleva el 97 % de la flexibilidad y diluye la
   no linealidad hertziana a ~3 %: el acople queda lineal y calibrable.
4. **La ganancia es insensible a la precarga**: varía 0,7 % entre 0,5 y 1,5 N, porque
   la precarga sólo entra por el término de Hertz. El crawler no necesita sostener la
   precarga con precisión.
5. **Lo que el palpador mide no es desplazamiento ni velocidad limpios.** Por regresión
   sobre los 126 casos: ω_n²·x da R²=0,92 con 40 % de error mediano, ω_n·v da R²=0,84
   con 26 %. La cuña no lo excita con un impulso sino con una ráfaga de ~2 ms a 6 kHz,
   así que la lectura es un valor de espectro de respuesta al choque a f0 y **hay que
   calibrarla**; no se invierte con fórmula cerrada.
6. **La mejor lectura es la energía de la señal (∫a²dt), no el pico.** Separación entre
   el grupo asentado (S0–S2) y el suelto (S4–S6), sobre las seis energías de golpe:
   **×14 a ×36 con la energía de la señal, ×1,6 a ×11,8 con el pico**.
7. **La energía del golpe tiene óptimo, y no es el mínimo.** Las dos lecturas no piden
   lo mismo: el pico se degrada monótonamente al subir la energía (×11,8 a 2 mJ, ×1,6 a
   12 mJ), mientras que la energía de la señal tiene un máximo ancho en **3–5 mJ**
   (×25 a ×36) y cae a ×23 en 1 mJ y a ×14 en 12 mJ. El límite de arriba es el ya
   conocido de la rev. A (con el golpe fuerte hasta la cuña ajustada despega del hombro).
   El de abajo es nuevo: a 1 mJ la cuña ajustada S0 devuelve más señal que S1 y S2, la
   escalera deja de ordenar en el extremo apretado y es S0 el que limita la separación.
   Para resolver fino la frontera S3|S4 sí conviene lo más flojo posible: ese salto vale
   ×459 a 1 mJ y ×7,2 a 12 mJ.

### Límites y pendientes de la rev. C

- El ensayo resuelve bien la **transición asentada/suelta** (entre S3 y S4), no el grado
  de apriete: dentro del grupo asentado la lectura no es monótona, y S4/S5/S6 saturan
  todos en el mismo valor.
- El palpador es ciego por debajo de su resonancia: no mide la deriva de cuerpo rígido
  de la cuña suelta.
- Falta diseño de detalle del resorte de 45 N/mm con f0 = 1,27 kHz y masa móvil 0,68 g,
  y verificar que su amortiguamiento propio queda bajo (ζ ≲ 0,05): con elastómero el
  rechazo de alta frecuencia cae de 1/r² a 1/r y la ganancia se ensucia.
- Falta cerrar la cadena con el sensor inductivo del proyectil: la clasificación usa la
  energía del golpe como covariable y todavía no está hecho el clasificador conjunto.
- No se modeló el montaje del palpador en el crawler ni su propia dinámica de brazo.

## Rev. D — 2026-09-20: corrección del mecanismo y espacio de diseño

### Error encontrado: el «primer modo de la cuña está en 6,1 kHz» es falso

La rev. C construía el argumento del acople blando sobre esa frecuencia. Los 6094 Hz
salen del modelo de apoyo en **extremos**, que la rev. B ya había reemplazado por apoyo
**distribuido** tras el dato de campo del usuario. Medido sobre el espectro de la
simulación vigente (12,5 mm, 5 mJ):

| estado | pico espectral | reparto de energía |
|---|---|---|
| S0 ajustada | 33 375 Hz | 100 % en 28–45 kHz |
| S2 · 50 % | — | 88 % en 0,1–0,8 kHz, 12 % en 33 kHz |
| S3 a S6 | 125 Hz | ~100 % en 0,1–0,8 kHz |

Modelo linealizado: hombro **cerrado** → 32,9 / 33,4 / 33,6 / 40,0 kHz; hombro
**abierto** (sólo ripple) → 1,28 / 1,29 kHz (los dos modos de cuerpo rígido sobre el
resorte) y recién después 10,6 y 24,9 kHz de flexión. Viga libre-libre pura: 0, 0,
10,6, 24,9, 41,4 kHz.

**La frecuencia sube con el apriete, factor ~270 entre asentada y suelta.** Eso es el
verdadero fundamento del método, y es más robusto que el argumento viejo: el palpador
planta su f₀ en el hueco entre los dos estados. Es un **pasa-bajos discriminante** —
la intuición original del usuario — y no un cambio de régimen para medir desplazamiento.

Corregido en `wtd/softprobe.py`. **Pendiente: el mismo 6094 Hz aparece en
`wtd/palpator.py:13`, `wtd/sensing.py:172` y `studies/run_all.py:308,312`
(ring_down y microphone_spec), y en `README.md:130`.** Son análisis de la rev. A que no
revisé; hay que verificar si sus conclusiones sobreviven al cambio de modelo.

### La deriva de cuerpo rígido resultó despreciable

Se midió: la posición media al final del transitorio vale 0,00–0,01 µm contra picos de
0,3 a 6,9 µm, o sea <0,2 % en los tres estados probados. El ripple reasienta la cuña.
El caveat de la rev. C queda rebajado a un efecto real que este modelo no reproduce
(una cuña que migre axialmente tiro a tiro), no a una limitación de la medición.

### Los 150 g de despegue son una consecuencia, no una elección

`design_space()` en `wtd/softprobe.py`. Los dos parámetros son independientes: **f₀
decide la calidad de la medición, la masa decide si sobrevivís**. La lectura pico y la
separación resultaron función de f₀ sola, no de la masa.

| a_despegue | masa | f₀ | separación |
|---|---|---|---|
| 48 g | 2,14 g | 600 Hz | ×3,2 |
| 97 g | 1,05 g | 1000 Hz | ×9,9 |
| 139 g | 0,73 g | 1273 Hz | ×14,1 |
| 200 g | 0,51 g | 1600 Hz | ×16,0 |
| 287 g | 0,36 g | 2000 Hz | ×16,9 (óptimo) |

La separación crece con f₀ hasta ~2 kHz, pero la lectura crece más rápido (a_max ~ f₀^1,7)
y obliga a bajar la masa. Con 0,68 g —lo más liviano construible— se llega a ×14,1 de
×16,9 alcanzables: 83 % del máximo. Subir la precarga a 2 N compraría ×16,9, un 20 %:
no vale la pena pelear por el segundo newton.

## Rev. E — 2026-09-20: el amortiguamiento manda, y el diseño queda confirmado

Barrido de ζ del acople con m = 0,68 g, f₀ = 1273 Hz, 1 N. Es **el parámetro más
sensible de todo el diseño**, por lejos:

| ζ | a_max [g] | separación | ring-down al 1 % |
|---|---|---|---|
| 0,002 | 78,5 | ×155 | 288 ms |
| **0,005** (flexura de acero) | **78,4** | **×150** | 115 ms |
| 0,010 | 78,4 | ×140 | 58 ms |
| 0,020 | 78,8 | ×112 | 29 ms |
| 0,050 | 86,6 | ×40 | 12 ms |
| 0,080 (lo que suponía la rev. C) | 99,6 | ×14 | 7 ms |
| 0,150 (elastómero blando) | 135,6 | ×3 | 4 ms |
| 0,300 | 215,7 | ×0,7 | 2 ms — y **despega** |

«Flexura metálica y no elastómero» deja de ser una recomendación de segundo orden y
pasa a ser **LA decisión de construcción**: entre ζ = 0,005 y ζ = 0,15 el ensayo va de
excelente a inservible sin que cambie ningún otro número.

### Consecuencias

1. **Todo lo que reportó la rev. C está calculado con ζ = 0,08, una suposición
   pesimista.** Los números reales de una flexura de acero son ~10× mejores: la
   separación asentada|suelta no es ×14 sino **×150**.
2. **El óptimo de f₀ se corre de 2 kHz a 1,3 kHz** — justo donde ya estaba el diseño.
   Con ζ = 0,08 parecía que convenía subir f₀ y que 1273 Hz dejaba un 17 % sobre la
   mesa; con ζ real, 1273 Hz *es* el óptimo.

| f₀ | a_max | separación | masa máx. (1 N, margen 1,4) |
|---|---|---|---|
| 600 Hz | 17,9 g | ×91 | 4,06 g |
| 1000 Hz | 49,0 g | ×139 | 1,49 g |
| **1273 Hz** | **78,4 g** | **×150** | **0,93 g** |
| 1600 Hz | 137,5 g | ×114 | 0,53 g |
| 2000 Hz | 235,4 g | ×80 | 0,31 g |

3. **El margen contra el despegue mejora**: el pico leído baja de 99,6 a 78,4 g, así que
   con 0,68 g el margen sube de 1,51 a **1,91**.
4. El segundo newton de precarga ya no compra nada de separación (estamos en el óptimo),
   sólo margen. Confirma que el límite de 1 N no es el que manda.

Agregado `ZETA_SWEEP` y `design_space(zeta=...)` en `wtd/softprobe.py`; el default de
`SoftProbe.zeta` pasa de 0,08 a 0,005. Docstring del módulo unificado: tenía la
explicación vieja (cambio de régimen para medir desplazamiento) conviviendo con la
corregida (pasa-bajos discriminante).

### Pendiente de banco

`ζ` es ahora el primer número a medir sobre el palpador construido, antes que f₀ y que
la ganancia. Se mide con un ping y la tasa de decaimiento.

## Rev. F — 2026-09-20: el «125 Hz» era un artefacto, y el filtro separa entero

Con resolución de 25 Hz (ventana de 40 ms) en vez de 125 Hz (8 ms), el espectro del
**desplazamiento** de la cuña —que es lo que excita al palpador— queda así:

| estado | pico | 90 % de la energía | por debajo de f₀ del palpador |
|---|---|---|---|
| S0 ajustada | 33 350 Hz | 33 325 – 33 375 Hz | **0,0 %** |
| S3 · 25 % | 33 075 Hz | 13 375 – 34 625 Hz | 1,5 % |
| S6 floja | 50 Hz | 50 – 225 Hz | **100,0 %** |

Los «125 Hz» de la rev. D eran literalmente el primer bin de la ventana corta. La cifra
correcta es 50–225 Hz, y el factor entre picos es ~670, no 270.

**El resultado es más fuerte de lo que parecía:** la cuña asentada entrega el 0 % de su
energía por debajo del corte y la suelta el 100 %. El filtro no las atenúa distinto — las
separa enteras. Anclado en `test_el_filtro_separa_las_dos_bandas_enteras`.

Ojo con la distinción: el espectro de la **aceleración** da otra cosa (pesa las altas por
ω⁴ y el 90 % de S6 se extiende hasta 18 kHz). El que importa para el filtrado es el del
desplazamiento.

### Diseño de detalle del palpador (para banco)

- **Flexura:** 2 láminas de acero de resorte de 5 × 0,30 mm, luz 27,1 mm, empotradas en
  ambos extremos con la masa al centro. k = 43,5 N/mm, tensión máxima 23 MPa contra
  ~1000 MPa de límite elástico → **vida infinita, sin cálculo de fatiga**.
- **Presupuesto de masa:** 0,490 g de piezas (acelerómetro 0,100 + vástago 0,083 + punta
  0,020 + masa efectiva de las láminas 0,237 + adhesivo 0,050). Quedan **0,19 g para el
  cable** contra el objetivo de 0,68 g, y 0,44 g contra el máximo de 0,93 g.
- **El diseño es indulgente con la masa:** a 0,93 g, f₀ baja a 1089 Hz y la separación
  pasa de ×150 a ×139. No vale la pena perseguir el gramo.
- **Cuerpo del palpador ≥ 7 g** (10× la masa móvil): con un cuerpo de sólo 3× la masa
  móvil el efecto de masa reducida corre f₀ un 15 %.
- **Resorte de precarga separado de la flexura**, 0,5 N/mm comprimido 2 mm. Da ±0,4 mm de
  tolerancia de posicionamiento para ±20 % de precarga — que además casi no afecta la
  ganancia. Es 85× más blando que la flexura, así que no ensucia la dinámica.
- **Ritmo máximo de disparo ~8 tiros/s**: con ζ = 0,005 el palpador tarda 115 ms en
  apagarse al 1 %.

### Protocolo de banco

Cuatro ensayos, ordenados por cuánto ahorran si fallan:

- **A** — verificar el hueco espectral con un acelerómetro de choque pegado (≥50 kHz,
  ±5000 g, 200 kS/s). No necesita palpador y puede invalidar todo el enfoque. Mide
  además la rigidez del hombro, que sigue siendo la incógnita nº 1 del proyecto.
- **B** — ping test sobre el palpador construido: da ζ y f₀ de una sola medición.
  Criterio: ζ ≤ 0,02.
- **C** — palpador contra referencia sobre la ranura de prueba, barriendo precarga.
  Criterio: separación > ×100 con el salto entre 25 % y 5 %.
- **D** — insensibilidad a la precarga, umbral de despegue, repetibilidad, orientación.

Publicado en https://claude.ai/artifact/6M9VJaZK7TU8tyFQoRBuT5

## Rev. G — 2026-09-20: dónde va el resorte (lo encontró una pregunta del usuario)

El dibujo de la rev. F ponía un **vástago rígido** entre la punta y la masa, y la flexura
entre la masa y el cuerpo. **Eso es el palpador rígido con pasos de más:** con el vástago
rígido la masa sigue a la cuña sin filtrar nada y el acelerómetro lee los miles de g. La
compliancia tiene que estar **en el camino de carga**, entre lo que toca y lo que mide:

    cuña ── punta ──[ resorte k ]── carro ──[ precarga F ]── cuerpo

### La restricción nueva: la punta tiene que pesar ≤ 20 mg

Con esa topología la punta queda del lado de la cuña, que la arrastra **cinemáticamente**
a miles de g. Seguirla cuesta `m_punta · a_cuña`, y esa fuerza sale del contacto, que no
puede dar más que la precarga:

    m_punta ≤ F_precarga / a_cuña_max = 1 N / 4800 g = 21 mg

Modelado: `SoftProbe.tip_mass` y el tercer término de `F_contacto` en `apply_soft_probe`.
Verificado: **la masa de punta no cambia la lectura** (mientras hay contacto la ecuación
del carro es idéntica), sólo adelanta el despegue. Umbral simulado: 30–50 mg a 5 mJ,
20–30 mg a 12 mJ, algo más permisivo que la cota porque el pico de aceleración y el de
fuerza del resorte no coinciden en el tiempo.

**Firma útil:** cuando despega, la lectura se recorta plana exactamente en F/m = 150 g,
porque en vuelo la única fuerza sobre el carro es la precarga. Es reconocible en el banco.

### La flexura de la rev. F no sirve

Las láminas de 5 × 0,30 mm con luz 27,1 mm ponen **237 mg** del lado de la punta: 12 veces
por encima del límite. Geometría corregida (todas dan 43,5 N/mm, punta al centro):

| b × h | luz | tensión | masa lado punta | |
|---|---|---|---|---|
| 5 × 0,30 | 27,1 mm | 23 MPa | 237 mg | ✗ (la de la rev. F) |
| 3 × 0,20 | 15,2 mm | 48 MPa | 53 mg | ✗ |
| **2 × 0,15** | **10,0 mm** | **83 MPa** | **17,4 mg** | ✓ recomendada |
| 1,5 × 0,12 | 7,3 mm | 126 MPa | 7,6 mg | ✓ |

Sigue siendo vida infinita (83 MPa contra ~1000 de límite elástico). El costo es manipular
chapa de 0,15 mm.

### Los dos presupuestos de masa, con criterios opuestos

- **Lado punta — techo 20 mg.** Lámina al centro 17,5 mg + bolilla ⌀1 mm 4,1 mg = 21,6 mg,
  apenas por encima. Conviene **formar el resalto en la propia lámina** y ahorrarse la
  bolilla: 17,5 mg.
- **Lado carro — objetivo 0,68 g.** Sale naturalmente en 0,33 g (acelerómetro 0,100 +
  estructura 0,150 + lámina 0,030 + adhesivo 0,050), o sea que **hay que lastrarlo con
  0,35 g**. Sin lastre f₀ se va a 1829 Hz y la separación cae de ×150 a ~×105. Agregar
  masa mejora la medición.

### La flexura de precarga hace dos trabajos

Además de dar la precarga de 1 N, **guía el carro** para que sólo se mueva en el eje de
medición. Al ser 85× más blanda que la de medición sólo suma un 1 % a la rigidez que fija
f₀. Falta dimensionarla en detalle: 0,5 N/mm con 2 mm de carrera, y su masa cae del lado
del carro.

### Pendiente nuevo

La **resonancia parásita del lado punta** (20 mg sobre 43,5 N/mm ≈ 7,4 kHz) no está en el
modelo, que trata la punta como masa pura sin grado de libertad propio. Cae entre las dos
bandas de la cuña, así que en principio no molesta, pero hay que verificarlo.

## Rev. H — 2026-09-20: el modelo integrado, por partes

Pedido del usuario: «se está volviendo complejo; para entenderlo bien necesito que lo
organicemos en un modelo integrado por partes bien definidas, bien explicado y cada parte
bien explicada».

El trabajo había crecido por capas y la única lectura posible era la cronológica (rev. A →
G de este archivo), que cuenta **cómo se llegó** y por lo tanto arrastra todas las
correcciones. Faltaba la lectura **estructural**.

### Lo que se agregó

- **`wtd/modelo.py`** — la cadena declarada como código: seis bloques, cada uno con su
  pregunta, entradas, salidas (símbolo / valor / unidad / procedencia), ecuación,
  explicación, hipótesis con su consecuencia si son falsas, anclas de pytest, ensayos de
  banco y qué se cae si falla. Más `EXTERNAS` (lo que entra de afuera), `BANCO` (los cuatro
  ensayos atados a la hipótesis que matan), `verificar_cadena()`, `resumen()` y `riesgos()`.
- **`docs/MODELO.md`** — la versión narrativa, que es la puerta de entrada al repositorio.
- **`tests/test_modelo.py`** — 8 anclas. Suite en **54 tests**.

### La cadena

```
B1 la cuña se mueve → B2 se mueve en DOS BANDAS según el ajuste → B3 el palpador es un
filtro que planta su corte en el medio → B4 la lectura integra esa energía → B5 el golpe
que la excita se mide a sí mismo → B6 los dos números deciden
```

Seis bloques, 32 magnitudes. `verificar_cadena()` comprueba que **cierra**: ningún bloque
consume un símbolo que nadie produce, ninguno queda sin verificación, y todo ensayo de
banco le sirve a algún bloque.

### Lo que la reorganización hizo visible

1. **Hay exactamente un bloque abierto: B6**, el clasificador conjunto. Y no es un riesgo
   — con ×112 de separación cualquier clasificador razonable alcanza; lo que falta son
   datos de banco para ajustarlo.
2. **Hay exactamente un bloque que puede tumbar todo: B2**, y por un solo parámetro,
   `k_hombro`. El resto de las hipótesis estimadas degradan el diseño; ésta lo invalida.
   `riesgos()` lo lista primero.
3. **El orden de los ensayos de banco cae solo** de la estructura: A mata la hipótesis que
   invalida el método y no necesita palpador; B mata la que arruina la medición y se hace
   con un ping. No hay que argumentar la prioridad, se lee.
4. **Los tests ahora atan el relato al código.** `test_los_valores_del_palpador_salen_del_
   codigo_y_no_del_relato` recalcula B3 desde `softprobe.design()`, y
   `test_el_corte_del_palpador_cae_dentro_del_hueco_de_la_cuña` verifica la desigualdad
   `f_suelta < f0 < f_asentada` con más de un orden de magnitud de holgura a cada lado. Si
   alguien cambia un número en un lado y no en el otro, falla.

### Limpieza de arrastre

- README: el «6094 Hz» quedaba como corrección vigente cuando la rev. B ya lo había
  dejado obsoleto. Ahora dice las dos correcciones y nombra los tres archivos donde el
  número sigue apareciendo (`palpator.py`, `sensing.py`, `run_all.py`), que siguen
  pendientes.
- README: el resultado 10 seguía diciendo que el palpador «pasa a medir desplazamiento»
  (el mecanismo viejo). Ahora dice pasa-bajos discriminante.

Publicado en https://claude.ai/artifact/XpcvS45VapBXWZUqwFvvpP

## Rev. I — 2026-09-21: trece figuras, y el defecto que aparecieron al buscarlas

Pedido del usuario: el modelo integrado necesita más figuras para entenderse.

### El defecto que encontró juntar los datos

Al recalcular los barridos para dibujarlos, los números no cerraban con las tablas
publicadas. La causa: **`design()` con sus argumentos por defecto no devolvía el palpador
documentado.** El default `x_wedge_max = 7,5 µm` daba f₀ = 1820 Hz y k = 88,9 N/mm, no los
1273 Hz y 43,5 N/mm de todo el resto del trabajo. El estudio y los tests pasan el argumento
explícito (el estudio usa la mayor excursión medida, 13,32 µm × 1,15 = 15,32 µm), así que
`results/softprobe.json` y las tablas siempre estuvieron bien — pero **`wtd/modelo.py`
llamaba a `design()` pelado** y heredaba el palpador equivocado.

El test anti-deriva de la rev. H no lo vio porque era **circular**: comparaba B3 contra
`design()`, o sea `design()` contra sí mismo. Si el default se corre, las dos mitades se
corren juntas y el test sigue pasando.

- `wtd/softprobe.py`: el default pasa a `X_WEDGE_MAX`, una constante documentada con su
  procedencia.
- `tests/test_modelo.py`: además de la comparación contra el código van los **valores
  publicados escritos a mano** (0,680 g · 1273 Hz · 43,5 N/mm · 150 g). Eso rompe la
  circularidad.

Con el default corregido, `studies/figuras_modelo.py` reproduce **exactamente** las dos
tablas publicadas: `ZETA_SWEEP` (78,5 g / ×154,8 … 215,8 g / ×0,7) y `F0_SWEEP_FLEXURA`
(17,9/×91,3 … 869,3/×13,7). Quedó anotada la métrica, que las tablas usaban sin decirla:

    separación = mín(estados sueltos de ∫a²dt) / máx(estados asentados),
                 tomada en la PEOR de las seis energías, que siempre es 12 mJ.

### Lo que las figuras nuevas hicieron ver

1. **El palpador no «rechaza» a la cuña asentada: la convierte.** Arriba de su resonancia
   la lectura vale ω₀²·w, o sea el desplazamiento. Los 830 g de la cuña asentada llegan al
   carro como 2,4 g — un rechazo de ×346 contra lo que leería un palpador rígido. La
   discriminación en amplitud es entonces la de la **excursión**: 0,31 µm contra 6,90 µm.
2. **El límite de banda a 5 kHz es la segunda mitad del filtrado, no un detalle.** La
   amplitud separa ×19 y el cuadrado la lleva a ×346, pero el rasgo separa ×1230: el resto
   lo pone el filtro, que descarta el rizado de 33 kHz que domina la señal cruda de S0.
3. **El óptimo de energía y el salto S3|S4 tiran para lados opuestos.** La separación de
   grupos tiene máximo en 5 mJ (×579); el salto en la frontera cae monótonamente (×798 a
   1 mJ, ×13,5 a 12 mJ). Son dos objetivos distintos y hay que elegir cuál se prioriza.
4. **El riel de despegue son 13 muestras contiguas** clavadas en −150,00 g entre t = 48 y
   60 µs, con punta de 120 mg a 12 mJ. Con punta de 20 mg, cero.

### Agregado

- `studies/figuras_modelo.py` → `results/figuras_modelo.json`. Reusa las trazas de la cuña
  (que no dependen del palpador) para que un barrido de horas tarde minutos, y por eso
  además sirve de verificación de las tablas publicadas.
- Trece figuras en el artefacto: corte de la ranura, los dos estados de borde, la escalera,
  la transferencia del palpador, las trazas del acelerómetro, la firma del despegue con su
  ampliación, el óptimo de energía, K_F(x) y el flujo de decisión.

Publicado en https://claude.ai/artifact/XpcvS45VapBXWZUqwFvvpP

## Rev. J — 2026-09-21: el informe como archivo independiente, con verificación automática

Pedido: el modelo integrado como HTML descargable, verificado.

`docs/modelo-cunas.html` — 100 kB, un solo archivo, sin dependencias. Las trece figuras se
dibujan en el navegador y los datos van embebidos. Sólo las tipografías salen a la red; sin
conexión caen a las del sistema y se lee igual.

### Los dos verificadores

Se dejaron en el repositorio porque lo que comprueban se rompe callado:

- **`docs/verificar_modelo.js`** — el **render**, en tres anchos (1100 / 900 / 390 px) y en
  los dos temas: errores de consola, que los diez gráficos dibujen, NaN o `undefined` en
  atributos SVG, texto que se salga de su `viewBox`, `var()` que no resuelva a un color,
  `[object Object]`, scroll horizontal, enlaces rotos, fondo del `body`, y que las
  etiquetas que dibuja el JS estén en el DOM.
- **`docs/verificar_numeros.py`** — el **contenido**: que el bloque de datos embebido sea
  el que emite `studies/figuras_modelo.py`, que el palpador sea el de `design()`, que
  `ZETA_SWEEP` y `F0_SWEEP_FLEXURA` reproduzcan, que la cadena cierre, y que no hayan
  quedado rastros de los números que las revisiones anteriores corrigieron (6094, 4855,
  848 g, 1820 Hz, 88,9 N/mm, 3,67 %, «sismómetro»).

### Lo que encontraron

1. **Tres etiquetas se salían del gráfico a 390 px** — el eje derecho de f₀, el punto de
   diseño de ζ y las dos líneas de leyenda del despegue. Corregidas con variantes cortas a
   lo angosto.
2. **Un pie de figura desalineado**: la Fig. 3 decía «~1550 g» y «0,3 a 7,1 µm» mientras el
   gráfico anotaba 1545 g y la tabla 0,31 a 7,12 µm.

Tres «fallas» más resultaron ser del verificador, no de la página, y quedaron documentadas
en el código para que no vuelvan a confundir:

- el error de consola por las tipografías de Google es del proxy del entorno;
- `var(--lo)` en un **atributo de presentación** SVG sí resuelve en el navegador — hay que
  mirar el color calculado, no el atributo;
- comparar tablas con un decimal pide tolerancia: ×154,82 contra ×154,9 es el mismo número,
  y ×0,747 contra ×0,700 también imprime ×0,7. La tolerancia quedó en 1 % o un dígito de la
  precisión impresa, lo que sea mayor — un error real, como el default roto de `design()`,
  daba 40 %.

## Rev. K — 2026-09-21: auditoría hipótesis por hipótesis

Pedido: revisar paso a paso, hipótesis por hipótesis, conclusión por conclusión, que todo
esté bien razonado. Se recorrió la cadena entera comprobando cada afirmación contra el
modelo, no contra la memoria. Aparecieron **cinco errores** y **un riesgo que no estaba**.

### El riesgo nuevo: f₀ cae encima del modo de la cuña suelta

f₀ salió de optimizar la separación: 1273 Hz. El modo de cuerpo rígido de la cuña suelta
sobre el ripple sale de su masa y del resorte:

    f = √(k_ripple · L / m) / 2π = √(3·10⁷ · 0,05 / 0,0228) / 2π = 1291 Hz

**Coinciden dentro del 1,4 %, y son dos cálculos independientes.** Importa porque el
palpador es vulnerable justo ahí: una excitación sostenida a f₀ lo despega con 0,92 µm, y la
excursión de la cuña suelta es de 6,9 µm — 7,5 veces más. Comprobado con senos sostenidos:
a 3 µm despega en el 16,5 % de las muestras, a 6,9 µm en el 21,8 %.

En el modelo no pasa, y la razón es comprobable: **la cuña suelta no oscila**. Su
desplazamiento cruza su propia media dos veces en 5 ms — es una sola excursión, que llega al
máximo en 0,08 ms y cae al 10 % a los 2,4 ms. Lo que llega al palpador es un escalón, y un
escalón no construye la resonancia.

Pero eso es una hipótesis sobre la cuña, no sobre el palpador, y descansa en `k_ripple`, que
es estimado. **Un barrido anterior concluyó que `k_ripple` podía variar 60 veces sin mover
el resultado un 2 %: sigue siendo cierto para la separación, y es falso para esto** —
`k_ripple` es exactamente lo que decide dónde cae ese modo respecto de f₀. El ensayo A lo
responde de una; el detector de despegue de B4 ya cubre el modo de falla; y si hiciera falta
mover f₀, a 1000 Hz cuesta el 7 % de separación.

### Los cinco errores

1. **El rasgo nunca se filtró.** B4 declaraba «∫a²dt con a filtrada a 5 kHz». `probe_features`
   no filtra: los 5 kHz están sólo en el presupuesto de ruido del acelerómetro. Aplicando un
   pasa-bajos real la separación **mejora** ×579 → ×4608 a 5 mJ y ×112 → ×210 en la peor
   energía. Todas las cifras del documento eran conservadoras sin decirlo.
2. **El pie de la Fig. 9 inventaba el mecanismo.** Atribuía el ×1230 al límite de banda.
   Falso: crudo y filtrado dan idéntico. El factor es la *duración* — el rizado de S0 se
   apaga en 0,06 ms y S6 mantiene amplitud los 3 ms, así que en valor eficaz la diferencia
   es ×35, y ×35² = 1230.
3. **«∫a²dt le gana al pico ×3 a ×9»** venía de la época de ζ = 0,08. Con el diseño vigente
   es **×14 a ×58**.
4. **«5 τ_e = 215 µs = 265 µm»** no cerraba: 215 µs a 1,48 m/s son **318 µm**. Los 265 µm son
   4,15 τ_e.
5. **«La cuña suelta responde a 50 Hz» y «×670 entre los picos»** son la misma trampa de los
   125 Hz vista de más lejos: S6 no tiene pico espectral porque no oscila. Se reemplazó por
   el techo de banda (175 Hz) y por el reparto, que es lo robusto: 0,0 % contra 100,0 %.

### Correcciones menores

- El techo de 20 mg de la punta es una cota de **simultaneidad**, 5,7× conservadora: la
  simulación despega recién con 120 mg. La recomendación de ahorrarse la bolilla de 4,1 mg
  era innecesaria.
- La **ventana de 3 ms es un parámetro libre no declarado** que mueve el número: separación
  en la peor energía ×45 (0,5 ms), ×68 (1 ms), ×98 (2 ms), ×112 (3 ms), ×127 (5 ms). Es
  heredada, no óptima, y alargarla es gratis.
- La **respuesta propia del acelerómetro** no está en el modelo (un ADXL1005 rueda a ~20 kHz
  y atenuaría el rizado de 33 kHz de S0): otra vez, conservador.

### Lo que resistió la auditoría

- El invariante F/m, analíticamente y en el barrido.
- Que arriba de la resonancia el palpador lee ω₀²·w: predicho 45,01 g para S6, simulado
  44,46 g — **1,2 % de diferencia**.
- Que f₀ y la separación no dependen de la masa, sólo de f₀ y ζ.
- La no monotonía de la aceleración contra la monotonía de la excursión.
- Que la cuña asentada está a 33,1 kHz y se apaga en 0,06 ms.
- El riel de despegue exactamente en −F/m, 13 muestras contiguas entre t = 48 y 60 µs.
- La cancelación exacta del error de escala en el cociente.
- `ZETA_SWEEP` y `F0_SWEEP_FLEXURA`, que reproducen punto por punto.

`tests/test_modelo.py` gana `test_la_f0_cae_encima_del_modo_de_la_cuna_suelta_sobre_el_ripple`,
que ancla la coincidencia para que no se pierda de vista. Suite en **55 tests**.

## Rev. L — 2026-09-21: revisión externa. El detector de despegue era un artefacto

Una revisión externa (ChatGPT, a pedido del usuario) encontró un defecto que invalida el
detector de despegue y varias conclusiones asociadas. **Tenía razón, y el error es peor de
lo que podía ver desde el HTML.**

### El defecto central

El documento afirmaba que al despegar «la única fuerza sobre el carro es la precarga», así
que la lectura se clavaba en −F/m. El revisor planteó el diagrama de cuerpo libre correcto:

    m_carro·a_carro + m_punta·a_punta = F_precarga − N

Con N = 0 eso es *una* ecuación con dos aceleraciones: no obliga a a_carro = F/m, porque el
resorte de medición sigue conectado entre la punta y el carro.

En `apply_soft_probe` el riel **está escrito a mano**:

```python
if F <= 0.0:
    a = -probe.preload / probe.mass      # ← el "riel" es esta línea
```

y la punta ni siquiera es un grado de libertad: `tip_mass` sólo entra en el test de contacto.
Los 13 valores de −150,00 g de la Fig. 10 eran esa asignación.

Se escribió `apply_soft_probe_2dof`: dos masas, contacto unilateral, reenganche. Coincide
exactamente con el modelo viejo mientras hay contacto. Con él, sobre el mismo caso:

| | 1 GDL (publicado) | 2 GDL (correcto) |
|---|---|---|
| ¿pierde contacto? | sí | sí, 13 µs |
| separación de la punta | no modelada | **0,0000 µm** |
| mínimo de la lectura | −150,00 g (impuesto) | −18,2 g |
| muestras en el riel | 13 | **0** |
| pico leído | 68,1 g | 68,1 g, igual que sin despegue |

Barrido de punta (20–600 mg) y precarga (0,70 y 1,00 N): el contacto se pierde 13–32 µs, la
punta nunca se separa y el pico leído no cambia. **El detector no queda debilitado: no
existe.** Cae con él el paso 1 de B6 y la mitigación que la rev. K había ofrecido para el
riesgo de resonancia a f₀.

Lo bueno: perder el contacto brevemente **no ensucia la medición**, así que las separaciones
publicadas no dependían de esto. El código del riel nunca se ejecutó en los 126 casos.

### El margen de contacto era sólo del carro

F/m contra el pico leído reparte toda la precarga al carro. La condición correcta suma las
dos demandas: 0,68 g × 73,5 g = 0,490 N más 20 mg × 4808 g = 0,943 N, o sea **1,433 N contra
1 N disponible**. Calculando el mínimo de N(t):

| precarga | punta | 5 mJ | 12 mJ |
|---|---|---|---|
| 1,00 N | 0 mg (lo simulado) | 0,704 N | 0,527 N |
| 1,00 N | 20 mg (real) | 0,583 N | **0,029 N** |
| 0,70 N | 20 mg (real) | 0,283 N | **pierde contacto** |

Y hay que decirlo fuerte: **los 126 casos se corrieron con `tip_mass = 0`**, porque es el
default de `design()`. El «cero despegues» vale para una punta ideal.

### Lo demás que aceptó la revisión

1. **El rango de 3 mm violaba el límite de 1 N.** Con k_p = 0,30 N/mm la fuerza barre 0,90 N
   y llega a 1,60 N. Para quedarse en 0,70–1,00 N hace falta **k_p ≤ 0,10 N/mm**, y el
   contacto hay que verificarlo a 0,70 N. Los 3 mm siguen **sin demostrar** como rango de
   medición.
2. **La Fig. 6 no dibujaba su propia ecuación.** De m ẍ + c(ẋ−ẇ) + k(x−w) = 0 sale
   X/W = (k+jωc)/(k−mω²+jωc); la curva omitía el término viscoso del numerador. A r = 26 daba
   1,00 y el valor correcto es **1,45**. El rechazo de 1/472 del texto sí era el completo.
   La «meseta» sólo vale mientras 2ζr ≪ 1.
3. **El ADXL1005 (±100 g) no alcanza.** La lectura llega a 109 g y el nivel a detectar estaba
   en −150 g. El propio estudio marcaba `satura: True`. Pasa a ±200 g.
4. **El lastre estaba al revés.** Con 0,33 g y k = 21,1 N/mm se conserva f₀ = 1273 Hz, la
   lectura en g es idéntica y el fondo de escala F/m **se duplica** (309 g). No lastrar y
   ablandar es estrictamente mejor.
5. **«Vida infinita»** comparaba contra el límite elástico, no contra el de fatiga (400–500
   MPa). La conclusión probablemente aguanta; el cálculo hay que hacerlo.
6. **B6 mezclaba magnitudes**: la covariable es la energía *absoluta* (4 % sistemático,
   0,17 % repetible), no el cociente (0,145 %).
7. **η = 1 − e²** es la energía que pierde el impactador, no la que se vuelve vibración útil.
8. **«El modo de 10,5 kHz entra en la banda del palpador»** es falso: r = 8 sigue muy arriba
   de f₀. El mecanismo de la inversión queda **sin explicar**.
9. **La monotonía del desplazamiento no es estricta**: S1 baja a 0,30 y S5 a 6,89. El propio
   estudio contaba 3–4 inversiones. Ninguna cruza la frontera S3|S4, que es lo que importa.

### Lo que la revisión no toca

Las separaciones de los 126 casos (el código del riel nunca corrió), el hueco espectral, la
cancelación del error de escala en el cociente, el invariante F/m como umbral —que sigue
siendo correcto *en el instante* de separación— y la limitación reconocida de que el ensayo
clasifica dos clases y no mide grado de apriete.

Anclas nuevas: `test_el_riel_de_menos_F_sobre_m_es_un_artefacto_del_modelo_de_1_gdl` y
`test_el_margen_de_contacto_tiene_que_incluir_la_punta`. Suite en **57 tests**.
