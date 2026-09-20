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
   el grupo asentado (S0–S2) y el suelto (S4–S6): ×16 a ×69 con la energía, ×1,8 a
   ×12,8 con el pico.
7. **Conviene golpear flojo, no fuerte.** La separación se degrada al subir la energía
   del golpe: a 1 mJ el salto S3→S4 es ×560, a 12 mJ es ×8,7. Con energía alta hasta la
   cuña ajustada despega del hombro y todas se parecen. Invierte el instinto de pegar
   más fuerte para tener más señal.

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
