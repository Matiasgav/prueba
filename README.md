# Módulo de impacto para el Wedge Tightness Test (GRIS)

Evaluación de desempeño de un módulo de **10 × 10 × 50 mm acostado** que golpea la cuña de ranura
con 5 mJ y mide, con dos canales independientes, si la cuña está ajustada o floja.

La pregunta que contesta es una sola: **¿esta cadena distingue una cuña floja de una ajustada, con
cuánto margen, y de qué depende ese margen?**

**El informe completo, interactivo, está en [`docs/index.html`](docs/index.html).**

---

## Qué hay acá

```
wtd/                 paquete de modelado (numpy + scipy, nada más)
  materials.py       propiedades con trazabilidad V / E / ?
  hertz.py           contacto esfera-plano, umbrales de daño, shakedown
  beam.py            viga de Timoshenko FE con fundación y apoyos elásticos
  wedge.py           cuña con apoyo bilineal unilateral (hombro + ripple)
  impact_sim.py      simulación no lineal del impacto y extracción de features
  coupling.py        acoplamiento modal cerrado (fórmula del brief §4.6)
  actuator.py        LAH04 de catálogo + escalados de VCA plano y reluctancia
  springs.py         acumuladores con verificación de fatiga (Goodman/Zimmerli)
  surge.py           modelo distribuido del resorte
  launcher.py        lanzamiento, separación, vuelo libre, venteo del cañón
  lever.py           palanca en L del informe original (línea base)
  module_design.py   dimensionado de las dos familias de módulo
  catalog.py         catálogo de 14 arquitecturas con números
  sensing.py         sensor inductivo, acelerómetro, micrófono, adquisición
  palpator.py        palpador con masa y precarga: f0 de contacto y despegue
  charger.py         la máquina que carga un acumulador, y cuánto volumen come
  montecarlo.py      presupuesto de repetibilidad
  reliability.py     vida, desgaste, retroceso, AMFE

tests/               19 casos ancla del brief §9
studies/             corredor de estudios y constructor del informe
results/             salidas en JSON (las que consume el HTML)
docs/                informe HTML interactivo
```

## Cómo correrlo

```bash
pip install numpy scipy pytest
python3 -m pytest                 # 19 casos ancla
python3 studies/run_all.py        # todos los estudios -> results/*.json
python3 studies/build_report.py   # regenera docs/index.html
```

`run_all.py` acepta nombres de estudio para correr sólo algunos:
`anchors damage mass accum freeflight sensing mc rel catalog lever wedge sep mech wave wavesim
sens masssim strike lowE charger palp sig`.

## Verificación

El informe está estructurado alrededor de cinco niveles de verificación, cada uno capaz de
refutar al anterior:

1. **Casos ancla** — 34 de 34 valores publicados del informe previo se reproducen dentro de
   tolerancia, incluidos los tres que el original no permitía verificar por falta de parámetros
   declarados. Corren como regresión en `tests/test_anclas.py`.
2. **Convergencia numérica** — paso de integración, modos retenidos y número de elementos.
3. **Cruce entre métodos** — fórmula cerrada de acoplamiento modal contra simulación no lineal
   en el tiempo. Encontró que la fórmula recomienda como óptima una masa a la cual ella misma es
   inválida.
4. **Contraste contra dato empírico** — el modelo tiene que dar Leeb *menor* con la cuña floja.
   **Este nivel refutó el modelo**: la cuña estaba apoyada sólo en sus dos extremos y el signo
   salía al revés. Se corrigió a apoyo distribuido a lo largo de toda la cola de milano.
5. **Sensibilidad** — 23 variantes de los cinco parámetros estimados, a dos energías de golpe.
   Es el nivel que descartó la duración de contacto y encontró el techo de energía.

Los errores que estos niveles encontraron están listados en el informe (§2), con su consecuencia.

## Configuración evaluada

Voice coil LAH04 accionando la palanca en L existente: maza de 2,105 g con calota de R = 12 mm,
5 mJ, **sin acumulador ni amartillado**. Sensor inductivo sobre la maza (da v_i, v_r, energía y
t_c) y MEMS de 0,05 g con 0,5 N de precarga como palpador sobre la cuña, a 10 mm del golpe.

## Resultados principales

1. **El voice coil directo alcanza.** Con 5 mJ el índice Leeb va de 986 (ajustada) a 782 (floja) y
   la energía que la cuña se queda pasa de 2,7 % a 39 %. No hace falta acumulador — que además no
   entra: dimensionado *con su cargador adentro*, la barra de torsión de 192 mJ queda en 7 mJ.
2. **El sentido lo produce la impedancia, no la fricción.** Con la disipación de junta anulada la
   restitución sigue bajando monótonamente con la soltura (0,986 → 0,680). Es el mecanismo que
   explica el dato de campo del usuario (cuña floja → Leeb menor); la fricción de flancos empuja
   al revés.
3. **Hay un techo de energía, y no es el daño de la cuña.** A 5 mJ el índice Leeb ordena la
   escalera en las 23 variantes del barrido de sensibilidad; a 60 mJ, en 3 de 23. Con el golpe
   fuerte la cuña ajustada también despega, la disipación de junta pasa a dominar y la curva se
   pliega. Subir la energía «para tener más señal» rompe el ensayo.
4. **La duración de contacto hay que descartarla.** No ordena la escalera en ninguna de las 23
   variantes: se mueve 2,1 µs en total y cambia de signo en el medio. El vector de decisión son
   dos características, no tres: índice Leeb y curtosis.
5. **La curtosis es el discriminante más robusto**, porque mide impulsividad y no disipación:
   ×1,8 → ×79 a lo largo de la escalera, y sigue ordenando aun con la disipación de junta anulada.
6. **Lo que fija la magnitud de la separación es la rigidez del asiento de la cola de milano.** La
   rigidez del ripple puede variar 60 veces, el ancho del apoyo 6 y el amortiguamiento del material
   12 sin mover el resultado un 2 %; pero un hombro diez veces más blando baja el rango de
   restitución de 0,205 a 0,040. Medirlo es el ensayo de prioridad 1.
7. **La escalera satura.** A partir del 5 % de precarga las características dejan de moverse: una
   partición en tres clases (ajustada / intermedia / floja) es cómoda, una escala continua de
   soltura no lo es. Es un límite estructural del principio de medición, no de esta implementación.
8. **El daño no es limitante con la punta correcta.** Con R = 12 mm el golpe de 5 mJ da 596 MPa,
   por debajo de los 640 MPa del límite elástico del G11; con la bola de ⌀8 mm daría 1153 MPa, por
   encima del shakedown.
9. **El retroceso es un problema estructural, no de adherencia.** El impulso transferido es
   4,6 mN·s: 2,3 mm/s en un crawler de 2 kg, que un imán de 50 N frena en 92 µs recorriendo
   0,1 µm. Lo que hay que dimensionar son los 371 N de pico sobre el montaje.

## Incógnitas y correcciones al informe previo

- **Cerrada** — incógnita #5: κ = 5/6 (los dos vanos lo dan de forma independiente).
- **Reconstruida** — incógnita #2: J_L compatible con barra de acero 3 × 8 mm (±1,1 %).
- **Corregida** — §4.6: la fórmula cerrada de acoplamiento modal se rompe justo en la masa que
  ella misma recomienda; verificado contra simulación no lineal.
- **Corregida** — §4.7: los 9376 Hz son el caso ideal empotrado; con un apoyo de cola de milano
  realista de 5 mm la frecuencia es 6094 Hz.
- **Corregida por dato de campo** — el apoyo de la cuña se modelaba en dos puntos, y el índice
  Leeb salía creciente con la soltura. Con apoyo distribuido el signo se invierte y coincide con
  lo medido. Los dos modelos dan idéntico resultado en los estados flojos: difieren sólo en la
  impedancia de la cuña ajustada, que es justo lo que el dato resuelve.
- **Abiertas** — **rigidez del asiento de la cola de milano** (la que fija la magnitud de la
  separación), módulo transversal del G11, rigidez y precarga del ripple, umbral de daño real, y
  la separación entre clases requerida (que es una decisión, no un dato).

La lista completa, con impacto y forma de resolverla, está en la §17 del informe.
