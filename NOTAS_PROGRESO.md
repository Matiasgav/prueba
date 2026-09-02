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
