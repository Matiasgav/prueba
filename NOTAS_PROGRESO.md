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
