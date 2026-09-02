# Módulo de impacto para el Wedge Tightness Test (GRIS)

Estudio de diseño mecánico de un módulo de **10 × 10 × 50–60 mm** que acelera una masa dentro de
su volumen, la suelta en vuelo libre y mide la energía que le entrega a la cuña de ranura.

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
masssim strike`.

## Verificación

34 de 34 casos ancla del brief §9 se reproducen dentro de tolerancia, incluidos los tres que el
informe original no permitía verificar por falta de parámetros declarados.

## Resultados principales

1. **El límite de energía lo pone el daño en el G11, no el actuador.** A la misma severidad de
   contacto del ensayo de la bola de ⌀8 mm (900 MPa, que no deja marca), una punta de R = 12 mm
   admite 39 mJ y una de R = 20 mm, 181 mJ: 27 y 125 veces más energía.
2. **Un acumulador elástico llega a 190 mJ dentro de 10 × 10 × 60 mm.** La restricción de 10 mm de
   altura no es la que limita la energía; lo que limita es la carrera lineal, y la barra de torsión
   la esquiva porque su carrera es un ángulo.
3. **Toda transmisión que convierta dirección paga cuadráticamente** en inercia reflejada
   (1/i²). Es la misma ley que explica el 43 % de pérdida de la palanca en L.
4. **El vuelo libre es alcanzable** (fuerzas parásitas del 0,56 % del peso) siempre que el blanco
   del sensor no sea un imán permanente: un imán daría 23 veces el peso del proyectil.
5. **Medir la velocidad convierte la repetibilidad en un requisito de sensado**: el lanzador
   dispersa 3 % y la magnitud reportada queda con 0,30 % de error.
6. **La masa de la maza decide si la medición significa algo.** Con 4 g la restitución es monótona
   con el ajuste (0,474 ajustada → 0,642 floja, d′ = 6,1); con 8 g se invierte y una cuña ajustada
   da casi el mismo número que una floja. Ocho gramos es la masa que pasa el acantilado de
   transferencia de energía: el mismo fenómeno arruina las dos cosas.
7. **Cuatro de los cinco parámetros estimados del modelo de la cuña no mueven el resultado**
   (la rigidez del ripple puede variar 60 veces y la del hombro 100), pero el quinto —la disipación
   por micro-deslizamiento en la junta— lo explica casi todo: anularla colapsa el rango de
   restitución de 0,168 a 0,005. El orden de la escalera es seguro; su magnitud es una hipótesis.
   Medirla es el ensayo de prioridad 1.
8. **La curtosis es el discriminante más robusto**: d′ = 16,6 entre extremos, y sigue ordenando
   los estados aun con la disipación de junta anulada, porque mide impulsividad y no disipación.

## Incógnitas y correcciones al informe previo

- **Cerrada** — incógnita #5: κ = 5/6 (los dos vanos lo dan de forma independiente).
- **Reconstruida** — incógnita #2: J_L compatible con barra de acero 3 × 8 mm (±1,1 %).
- **Corregida** — §4.6: la fórmula cerrada de acoplamiento modal se rompe justo en la masa que
  ella misma recomienda; verificado contra simulación no lineal.
- **Corregida** — §4.7: los 9376 Hz son el caso ideal empotrado; con un apoyo de cola de milano
  realista de 5 mm la frecuencia es 6094 Hz.
- **Abiertas** — módulo transversal del G11, rigidez y precarga del ripple, geometría del apoyo,
  umbral de daño real, y la separación entre clases requerida (que es una decisión, no un dato).

La lista completa, con impacto y forma de resolverla, está en la §17 del informe.
