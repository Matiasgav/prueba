---
titulo: Selección del LED para el módulo de iluminación compacto
subtitulo: OSRAM OSLON SSL 80 · GW CS8PM1.PM, 5000 K, bin LUMQ — robot de almacenamiento de medicamentos para farmacia
edicion: Memoria técnica · Selección de componente
fecha: Datos técnicos y de distribuidores verificados el 27 de septiembre de 2026
encabezado: Memoria técnica — Selección del LED OSLON SSL 80 (GW CS8PM1.PM)
aviso: Memoria de selección de componente. Los valores de flujo de salida son estimaciones de cálculo con supuestos declarados; deben confirmarse con medición sobre prototipo antes de congelar el diseño. Precios y stock se verificaron el 27-09-2026 y deben revisarse antes de cada compra.
---

# Resumen ejecutivo

Para el módulo de iluminación compacto del robot de almacenamiento de medicamentos se selecciona el LED **ams OSRAM OSLON SSL 80, tipo GW CS8PM1.PM, variante 5000 K bin LUMQ** (códigos GW CS8PM1.PM-LUMQ-XX53-1 o -A333-1), que entrega **164 a 210 lm a 350 mA** con un consumo cercano a **1 W**.

La elección responde a la geometría: el LED queda al fondo de un conducto de aluminio fresado, a **7 mm** de una ventana de **Ø 5 mm**. En ese espacio, un encapsulado de 3,0 × 3,0 mm con cono preenfocado de **80°** entrega a la ventana casi el doble de luz directa que un LED típico de 120° (19,4 % contra 11,3 % del flujo total), con paquete cerámico, resistencia térmica de 3,7 K/W y rango industrial de −40 a +125 °C.

El objetivo de **100 lm útiles a la salida es alcanzable pero no está garantizado**. Solo con luz directa llegan a la ventana 32–41 lm. El resultado final depende sobre todo de cómo refleja la pared interna: con aluminio que conserve componente especular y un difusor de alta transmisión se obtienen **95–140 lm**; con una pared mate y difusa el rango cae a **40–80 lm**. La recomendación es prototipar y medir, y dejar previsto un tratamiento de la pared (pulido, inserto o recubrimiento reflectivo) como medida de recuperación.

::: kpi
164–210 lm || flujo del bin LUMQ a 350 mA || 5000 K, CRI ≥ 70
≈ 1,0 W || potencia eléctrica típica || 350 mA × 2,85 V
19,4 % || del flujo llega directo a la ventana || geometría Ø 5 mm a 7 mm
40–140 lm || rango estimado a la salida || según pared y difusor
:::

::: nota clave | Decisión
**Se recomienda el OSLON SSL 80 GW CS8PM1.PM-LUMQ-XX53-1 (5000 K), alimentado a 350 mA con fuente de corriente constante.** La decisión del componente es firme; lo que queda abierto es la **eficiencia del conducto**, que se resuelve con una medición sobre prototipo y no cambiando de LED.
:::

## Requisitos del sistema frente al LED seleccionado

| Requisito del sistema | Valor pedido | OSLON SSL 80, LUMQ 5000 K | Cumplimiento |
|---|---|---|:--:|
| Encapsulado compatible con alojamiento mecanizado | LED SMD compacto | 3,0 × 3,0 mm, altura 2,13–2,30 mm, cerámico | Cumple |
| Concentrar la luz hacia una ventana de Ø 5 mm a 7 mm | Cono estrecho | 2φ = 80° a 50 % de intensidad | Cumple |
| Flujo disponible en el LED | Muy superior a 100 lm, para cubrir pérdidas | 164–210 lm a 350 mA | Cumple |
| 100 lm útiles a la salida | ≈ 100 lm | 40–140 lm según pared y difusor | **A verificar** |
| Operación continua 24/7 | Robustez térmica | RthJS 3,7 K/W; Top −40 a +125 °C | Cumple con diseño térmico |
| Alimentación simple y controlable | Driver estándar | Corriente constante 350 mA, Vf 2,70–3,20 V | Cumple |
| Observación, cámara, detección | Luz blanca estable | 5000 K, CRI 70 mín. | Cumple (no colorimetría) |
| Industrialización | Montaje automático | SMD en carrete de 600, MSL 2 | Cumple |
| Abastecimiento | Disponible en distribución | Stock en Mouser Europa (1.669 u.) | Cumple, con importación |

# Parte I — El componente

## 1. Contexto y restricciones del sistema

El módulo ilumina el interior del robot para observación, cámara o detección. La mecánica impone condiciones que ordenan toda la selección:

- LED SMD de alta potencia dentro de un alojamiento mecanizado.
- Distancia aproximada entre el LED y la ventana o difusor: **7 mm**.
- Ventana circular de salida de **Ø 5 mm**, con difusor.
- Conducto interno de **aluminio mecanizado o fresado**, con buena terminación pero **no pulido**.
- Objetivo de salida: del orden de **100 lm útiles**.

::: fig led-geometria | Figura 1 — Geometría del módulo. El cono verde es la luz que llega a la ventana sin tocar la pared; todo lo que sale fuera de él depende de la pared para llegar. | Esquema del autor. | 0.9
:::

::: nota riesgo | La pared del conducto es la variable crítica
Un aluminio fresado sin pulir **no debe modelarse como espejo**. Puede conservar parte de la reflexión especular, pero la rugosidad, las marcas de fresa, la oxidación y la limpieza de la superficie pueden bajar mucho la eficiencia óptica. En este diseño, esa superficie pesa más en el resultado final que la elección entre bins del LED.
:::

## 2. LED seleccionado

| Campo | Valor |
|---|---|
| Fabricante | ams OSRAM |
| Familia | OSRAM OSLON SSL 80 |
| Tipo base | GW CS8PM1.PM |
| Variante preferida | **GW CS8PM1.PM-LUMQ-XX53-1** (Q65113A9964) o **GW CS8PM1.PM-LUMQ-A333-1** (Q65113A9963) |
| Temperatura de color | 5000 K |
| Flujo a 350 mA | 164 a 210 lm (grupos LU, MP y MQ) |
| Código en distribución | GW CS8PM1.PM-LUMQ-XX53-1-350-R18 (carrete de 600 unidades) |
| Estado | *Full production* según la página oficial del producto |

El bin **LUMQ** es el de mayor flujo listado para 5000 K en la versión vigente del datasheet (v1.10, 2026-03-05). Las dos variantes, XX53 y A333, comparten flujo y temperatura de color; solo difieren en la agrupación cromática del pedido, que el datasheet codifica en el sufijo.

::: fig led-ds-portada | Figura 2 — Resumen del componente: encapsulado cerámico con lente de silicona, radiación típica de 80°, CRI 70 mín. y aplicaciones previstas. | Fuente: ams OSRAM, datasheet GW CS8PM1.PM, versión 1.10, 2026-03-05, p. 2. | 0.72
:::

::: fig led-ds-pedido | Figura 3 — Tabla de pedido. Resaltadas, las dos variantes LUMQ de 5000 K con 164 a 210 lm a 350 mA. | Fuente: ams OSRAM, datasheet GW CS8PM1.PM, versión 1.10, 2026-03-05, p. 3. | 0.9
:::

## 3. Por qué este LED y no otro

::: tarjetas 3
::: tarjeta LED de 120° a 150° | Descartado
Es lo más común en LEDs blancos de potencia. Con una ventana tan chica, **desperdicia más luz contra las paredes**: en α = 19,65° un LED lambertiano de 120° entrega directo el 11,3 % de su flujo y uno de 150°, el 8,7 %. Todo lo demás queda a merced del aluminio.
:::
::: tarjeta LED o lente muy cerrados | Descartado
Un haz de 30° a 60° mete más luz directa, pero genera un **punto caliente más fuerte** sobre el difusor y vuelve el módulo **dependiente de la alineación** entre LED y conducto. Suma además una óptica secundaria que no entra en el alojamiento.
:::
::: tarjeta OSLON SSL 80 | Seleccionado
Es el **compromiso** entre tamaño, flujo, disponibilidad industrial y cono preenfocado: **19,4 %** de captura directa, 164–210 lm en 3 × 3 mm, paquete cerámico y una familia en producción plena con distribución internacional.
:::
:::

::: fig led-captura | Figura 4 — Fracción del flujo total que sale dentro de cada semiángulo. En el borde de la ventana (19,65°) el OSLON SSL 80 captura en directo 1,7 veces lo que un LED de 120° y 2,2 veces lo que uno de 150°. | Cálculo propio con modelo cosᵐθ; 2φ del OSLON SSL 80 según el datasheet ams OSRAM v1.10. | 0.9
:::

Frente a **LEDs genéricos** de encapsulado plástico (PLCC, 2835, 5050), el OSLON SSL 80 aporta un paquete cerámico con resistencia térmica baja, ficha técnica completa con curvas de derating, agrupación por flujo, tensión y color, trazabilidad de lote y gestión de cambios de producto. Para un equipo 24/7 en un entorno regulado, esa documentación es parte del valor del componente.

# Parte II — Características

## 4. Características eléctricas, ópticas, térmicas y mecánicas

Valores a IF = 350 mA y Tj = 85 °C, salvo indicación.

| Grupo | Parámetro | Valor | Nota |
|---|---|---|---|
| Eléctrico | Tensión directa Vf | 2,70 mín. · **2,85 típ.** · 3,20 máx. V | Grupos K2 a M2, de 0,10 V |
| Eléctrico | Corriente directa | 100 mA mín. · 1300 mA máx. | Punto de diseño: 350 mA |
| Eléctrico | Corriente de pico | 2000 mA | t ≤ 10 µs, D = 0,005 |
| Eléctrico | Potencia típica | ≈ 1,0 W | 0,35 A × 2,85 V |
| Eléctrico | Tensión inversa | 1,2 V máx. (IR = 20 mA) | No polarizar en inversa |
| Eléctrico | ESD | 8 kV HBM, clase 3B | Diodo de protección en paralelo al chip |
| Óptico | Ángulo de emisión 2φ | 80° a 50 % de intensidad | Semiángulo de 40° |
| Óptico | Flujo, bin LUMQ | 164–210 lm | Tolerancia de medición ±7 % |
| Óptico | Temperatura de color | 5000 K | |
| Óptico | CRI / R9 | 70 mín., 72 típ. / −40 mín. | |
| Térmico | RthJS eléctrica | 3,7 K/W típ. | Con eficiencia ηe = 30 % |
| Térmico | Temperatura de juntura | 135 °C máx. (160 °C absoluta) | |
| Térmico | Temperatura de operación | −40 a +125 °C | Igual para almacenamiento |
| Mecánico | Cuerpo | 3,0 × 3,0 mm (2,9–3,1) | |
| Mecánico | Altura total | 2,13–2,30 mm | Plano del datasheet, p. 16 |
| Mecánico | Peso | 22,3 mg | |
| Proceso | Sensibilidad a la humedad | MSL 2 (JEDEC J-STD-020E) | Reflow sin plomo, pico 245–250 °C |
| Proceso | Embalaje | Cinta, carrete Ø 180 mm, 600 unidades | |

::: nota dato | Corrección sobre la altura del encapsulado
El plano dimensional oficial acota la altura total entre **2,13 y 2,30 mm**. En la documentación de partida figuraba 2,21–2,30 mm; para el diseño mecánico del alojamiento debe usarse el rango completo del plano.
:::

::: fig led-ds-maximos | Figura 5 — Valores máximos: corriente directa de 100 a 1300 mA, juntura de 135 °C, operación de −40 a +125 °C y ESD de 8 kV. | Fuente: ams OSRAM, datasheet GW CS8PM1.PM, versión 1.10, 2026-03-05, p. 4. | 0.9
:::

::: fig led-ds-caracteristicas | Figura 6 — Características a 350 mA y 85 °C: 80°, Vf 2,70/2,85/3,20 V, CRI 70/72 y RthJS 3,7 K/W. | Fuente: ams OSRAM, datasheet GW CS8PM1.PM, versión 1.10, 2026-03-05, p. 5. | 0.9
:::

::: fig led-ds-grupos | Figura 7 — Grupos de flujo y de tensión directa. Resaltados, los grupos LU, MP y MQ que componen el bin LUMQ. | Fuente: ams OSRAM, datasheet GW CS8PM1.PM, versión 1.10, 2026-03-05, p. 6. | 0.85
:::

::: nota inferencia | Qué significa realmente «80 grados»
El ángulo de 80° **no** indica que toda la luz salga dentro de un cono de 80°. Indica que a ±40° del eje la intensidad cae al **50 %** de la del eje. Con el modelo de la sección 6, solo el **62 %** del flujo sale dentro de ±40°; el 38 % restante sale más abierto y, en este módulo, termina en la pared del conducto.
:::

::: fig led-ds-radiacion | Figura 8 — Diagrama de radiación. La intensidad relativa cae a 0,5 cerca de ±40° y conserva valores apreciables hasta ±70°. | Fuente: ams OSRAM, datasheet GW CS8PM1.PM, versión 1.10, 2026-03-05, p. 12. | 0.62
:::

## 5. Alimentación y driver recomendado

El LED se alimenta con **corriente constante, nunca con tensión fija**. Su tensión directa varía entre unidades (2,70–3,20 V) y baja con la temperatura; con una fuente de tensión, pequeñas diferencias de Vf se traducen en grandes diferencias de corriente y la unidad puede entrar en embalamiento térmico.

| Parámetro del driver | Recomendación | Justificación |
|---|---|---|
| Tipo | Fuente de corriente constante, preferentemente conmutada (*buck*) | Regula corriente con independencia del Vf de cada unidad |
| Corriente nominal | **350 mA** | Punto en que el datasheet especifica flujo, Vf y CRI |
| Tensión de *compliance* | ≥ 3,5 V en el LED más el margen propio del driver | Vf máx. 3,20 V a 85 °C, más ≈ 0,3 V de aumento a −40 °C según la curva ΔVf(Tj) |
| Alimentación de entrada | Bus de 12 V o 24 V del robot | Con un regulador lineal desde 5 V se disiparían ≈ 0,75 W en el regulador |
| Regulación de brillo | PWM sobre la entrada *enable*, con pulso de 350 mA | El datasheet prohíbe operar en continua por debajo de 100 mA |
| Frecuencia PWM | Alta frente al tiempo de exposición, o sincronizada con la cámara | Evita bandas y variaciones de brillo entre cuadros |
| Protecciones | Circuito abierto, cortocircuito y reducción de corriente por temperatura (NTC cerca del LED) | Operación 24/7 sin supervisión |

::: fig led-ds-corriente | Figura 9 — Corriente frente a tensión directa y flujo relativo frente a corriente a Tj = 85 °C. A 500 mA el flujo sube ≈ 36 % respecto de 350 mA; a 700 mA, ≈ 80 %. | Fuente: ams OSRAM, datasheet GW CS8PM1.PM, versión 1.10, 2026-03-05, p. 13.
:::

### Confiabilidad y diseño térmico

Con RthJS = 3,7 K/W y 1,0 W eléctrico, la juntura queda apenas **≈ 4 K por encima del punto de soldadura**. Por eso, en este diseño, el cuello de botella térmico **no es el LED**: es la trayectoria del calor desde la placa hacia el cuerpo de aluminio.

- Usar placa **MCPCB** o PCB con vías térmicas bajo el *pad* central, que según el plano no tiene conexión eléctrica, y acoplarla al cuerpo de aluminio con interfaz térmica.
- Medir la temperatura en el punto de soldadura, o lo más cerca posible del LED, durante un ensayo 24/7 en la peor condición ambiente.
- Mantener la juntura con margen amplio respecto de 135 °C. Como referencia de diseño, conviene no superar ≈ 85 °C de Ts en régimen, que es además la temperatura a la que el datasheet especifica el flujo.
- La curva de derating permite 1300 mA hasta Ts = 100 °C. Si se sube la corriente para recuperar flujo, hay que recalcular disipación, derating y vida útil, y confirmar la temperatura con medición.

::: fig led-ds-temperatura | Figura 10 — Variación de Vf y de flujo relativo con la temperatura de juntura a 350 mA. El flujo a 25 °C es ≈ 10 % mayor que a 85 °C, y a 120 °C cae ≈ 10 %. | Fuente: ams OSRAM, datasheet GW CS8PM1.PM, versión 1.10, 2026-03-05, p. 14.
:::

::: fig led-ds-derating | Figura 11 — Corriente máxima admisible frente a la temperatura del punto de soldadura. Plena corriente hasta Ts = 100 °C y prohibición de operar por debajo de 100 mA. | Fuente: ams OSRAM, datasheet GW CS8PM1.PM, versión 1.10, 2026-03-05, p. 15. | 0.5
:::

# Parte III — Cálculo óptico

## 6. Geometría y captura directa

La ventana tiene radio r = 2,5 mm y está a d = 7 mm del emisor. El semiángulo que la ventana subtiende desde el LED es:

- `α = atan(r / d) = atan(2,5 / 7) = 19,65°`

Para la distribución angular del LED se usa el modelo habitual `I(θ) = I0 · cos^m(θ)`. Como la intensidad cae al 50 % a 40°:

- `m = ln(0,5) / ln(cos 40°) = 2,60`

La fracción del flujo total que sale dentro de un semiángulo α es `F(α) = 1 − cos^(m+1)(α)`. Para la ventana:

- `F_directa = 1 − cos(19,65°)^3,60 ≈ 0,194`

| Flujo del LED (bin LUMQ) | Luz directa en la ventana, antes del difusor |
|---|--:|
| 164 lm (mínimo del bin) | **32 lm** |
| 187 lm (valor medio, usado en los cálculos) | **36 lm** |
| 210 lm (máximo del bin) | **41 lm** |

::: nota clave | Conclusión parcial
Sin recuperación de luz por reflexiones en el conducto, **no se llega a 100 lm**. Cuatro de cada cinco lúmenes del LED tocan la pared antes de poder llegar a la ventana, así que la eficiencia real depende de cuánto recupere el conducto de aluminio.
:::

## 7. Conducto de aluminio fresado: dos escenarios

El conducto se trata como una **guía óptica imperfecta**. Como su reflectividad y su especularidad no se conocen, se calculan dos escenarios que acotan el comportamiento real, cada uno con una reflectividad de pared entre 0,55 y 0,92.

El cálculo es una simulación Monte Carlo simplificada, reproducible con `tools/led_montecarlo.py`: fuente puntual con distribución cos^2,6 en el fondo de un cilindro de Ø 5 × 7 mm, fondo absorbente y toda la boca como ventana. Con 400.000 rayos, reproduce las tablas de partida con diferencias menores a 0,01 en eficiencia.

### Modelo conservador: pared difusa

Aluminio mecanizado sin pulir que refleja de manera mayormente difusa: cada rebote reparte la luz en todas direcciones, y parte vuelve hacia el fondo.

| Reflectividad de la pared | Eficiencia del conducto | Antes del difusor (187 lm) | Con difusor 75 % | Con difusor 90 % |
|--:|--:|--:|--:|--:|
| 0,55 | 0,29 | 55 lm | 41 lm | 49 lm |
| 0,65 | 0,33 | 62 lm | 46 lm | 56 lm |
| 0,75 | 0,37 | 70 lm | 52 lm | 63 lm |
| 0,85 | 0,44 | 82 lm | 62 lm | 74 lm |
| 0,92 | 0,50 | 93 lm | 70 lm | 83 lm |

### Modelo optimista: pared con componente especular apreciable

Aluminio limpio, con marcas de herramienta finas pero sin pulir, que conserva buena parte de la reflexión especular. El conducto funciona entonces como una guía de luz y conserva la componente axial.

| Reflectividad de la pared | Eficiencia del conducto | Antes del difusor (187 lm) | Con difusor 75 % | Con difusor 90 % |
|--:|--:|--:|--:|--:|
| 0,55 | 0,56 | 105 lm | 79 lm | 95 lm |
| 0,65 | 0,65 | 121 lm | 90 lm | 109 lm |
| 0,75 | 0,74 | 138 lm | 103 lm | 124 lm |
| 0,85 | 0,83 | 156 lm | 117 lm | 140 lm |
| 0,92 | 0,91 | 170 lm | 127 lm | 153 lm |

::: fig led-sensibilidad | Figura 12 — Flujo de salida estimado en función de la reflectividad de la pared, para los dos modelos. El ancho de cada banda es el efecto del difusor (75 % a 90 %). | Cálculo propio con tools/led_montecarlo.py. | 0.9
:::

## 8. Rango estimado de flujo real y condiciones para 100 lm

Para entregar 100 lm con el valor medio del bin (187 lm), el conjunto conducto + difusor debe tener una eficiencia de al menos **0,54**. Eso exige una eficiencia de conducto de **0,59 con difusor de 90 %** o de **0,71 con difusor de 75 %**.

| Situación | Flujo de salida probable a 350 mA | ¿Llega a 100 lm? |
|---|--:|:--:|
| Pared mate o difusa, difusor 75–90 % | 40–80 lm | No |
| Pared con componente especular, Rw ≥ 0,60, difusor 90 % | 100–155 lm | Sí |
| Pared con componente especular, Rw ≥ 0,73, difusor 75 % | 100–127 lm | Sí, con poco margen |
| Bin mínimo (164 lm), pared especular Rw 0,75, difusor 85 % | ≈ 103 lm | Justo |

::: nota inferencia | Conclusión óptica
- El objetivo de **100 lm a la salida es viable** si el conducto conserva una componente especular razonable y el difusor tiene transmisión alta.
- Con pared muy mate o difusa, el flujo probable cae a **40–80 lm** a 350 mA, aun con el bin LUMQ.
- Un aluminio fresado real queda **entre los dos modelos**, y dónde queda solo lo dice una medición.
:::

Para **garantizar** los 100 lm hay tres palancas, en orden de preferencia:

1. **Mejorar la pared**: pulido del conducto, inserto de aluminio reflectivo o film especular, recubrimiento blanco de alta reflectancia (> 0,95) o reflector metalizado. Es la palanca más efectiva, porque actúa sobre el 80 % del flujo que hoy depende de la pared.
2. **Difusor de alta transmisión**, 85–90 %, con la difusión justa para homogeneizar el punto caliente.
3. **Subir la corriente** solo si el diseño térmico lo permite. A 500 mA el flujo sube ≈ 36 % (Figura 9) con ≈ 1,5 W eléctricos. Por ejemplo, pared difusa de 0,85 con difusor de 90 % pasa de 74 lm a ≈ 100 lm.

También puede **revisarse la geometría**: acortar la distancia LED–ventana o ensanchar la ventana aumenta α, y con él la captura directa.

# Parte IV — Riesgos, industrialización y abastecimiento

## 9. Riesgos

| Riesgo | Efecto | Mitigación |
|---|---|---|
| Reflectividad incierta del aluminio fresado | Salida entre 40 y 140 lm según la pared | Medir sobre prototipo; tener definido un tratamiento de pared como plan B |
| Dispersión del bin (164–210 lm) | ±12 % sobre el valor medio | Diseñar con 164 lm; especificar el bin LUMQ en la orden de compra |
| Condición de medición del bin | La portada indica 155 lm típicos a 85 °C, mientras el bin se mide con pulso de 10 ms. Si el bin estuviera referido a 25 °C, en régimen el flujo sería ≈ 10 % menor | Confirmar con ams OSRAM la temperatura de referencia del bin; medir flujo en régimen térmico estable |
| Temperatura | ≈ −10 % de flujo a 120 °C de juntura respecto de 85 °C; degradación más rápida | Trayectoria térmica a la carcasa, NTC y reducción de corriente |
| Envejecimiento y contaminación de la lente de silicona | Pérdida de flujo y corrimiento de color | Evitar compuestos volátiles (adhesivos y juntas no compatibles) dentro del conducto cerrado |
| Materiales con plata en el LED | Decoloración ante atmósferas con azufre o agentes agresivos | Revisar compatibilidad con los productos de limpieza de la farmacia; sellar el módulo |
| CRI 70 | Reproducción de color limitada; R9 puede ser −40 | Suficiente para forma, presencia, bordes, contraste y lectura. Para medir color con precisión, evaluar una variante de CRI 80–90 |
| Deslumbramiento | Clasificación IEC 62471 de riesgo moderado (tiempo de exposición de 0,25 s) | El difusor reduce la luminancia; evitar la visión directa durante el mantenimiento |
| Aplicación médica o de seguridad | El fabricante no califica el componente para estos usos | Ver la nota siguiente |
| Disponibilidad y obsolescencia de subvariantes | El datasheet cambió la tabla de pedido en 2025 y 2026 | Aprobar XX53 y A333 como alternativas; evitar bins antiguos como LSLU |

::: nota riesgo | Advertencia regulatoria
El datasheet indica que estos componentes **no están desarrollados, construidos ni ensayados como componente de seguridad ni para dispositivos médicos**, y que no están calificados a nivel de módulo ni de sistema para esos usos. En el robot de farmacia el LED es válido como **componente de iluminación**. Si su función afecta la seguridad o la dispensación, por ejemplo cuando una cámara verifica el medicamento dispensado, el sistema completo debe evaluarse según la normativa aplicable, y el fabricante pide que se le informe ese uso.
:::

## 10. Calidad, robustez e industrialización

- Familia industrial de ams OSRAM, orientada a iluminación profesional, interior, exterior e industrial.
- Paquete cerámico con lente de silicona y baja resistencia térmica, una ventaja frente a LEDs plásticos de bajo costo.
- Compatible con montaje SMD automático: cinta y carrete de 600 unidades, MSL 2 y perfil de reflow sin plomo estándar. El fabricante recomienda soldar en atmósfera de nitrógeno.
- Apto para funcionamiento 24/7 siempre que el driver sea de corriente constante, haya disipación real hacia el cuerpo de aluminio, la juntura opere con margen y la lente no se contamine químicamente.

::: fig led-ds-dimensiones | Figura 13 — Plano dimensional: cuerpo de 2,9–3,1 mm, altura de 2,13–2,30 mm, ánodo, cátodo y pad central sin conexión eléctrica. | Fuente: ams OSRAM, datasheet GW CS8PM1.PM, versión 1.10, 2026-03-05, p. 16.
:::

::: fig led-ds-footprint | Figura 14 — Pads de soldadura recomendados. | Fuente: ams OSRAM, datasheet GW CS8PM1.PM, versión 1.10, 2026-03-05, p. 17.
:::

::: fig led-ds-reflow | Figura 15 — Perfil de reflow sin plomo: pico de 245 °C recomendado y 250 °C máximo; MSL 2 según JEDEC J-STD-020E. | Fuente: ams OSRAM, datasheet GW CS8PM1.PM, versión 1.10, 2026-03-05, p. 18. | 0.78
:::

## 11. Precio, stock y disponibilidad

Relevamiento del 27 de septiembre de 2026. Precios sin impuestos ni envío.

| Fuente | Parte | Estado / stock | Precio observado | Comentario |
|---|---|--:|--:|---|
| ams OSRAM oficial | GW CS8PM1.PM-LUMQ-A333-1 / XX53-1 | Producción plena | No publica precio | Fuente técnica primaria |
| Mouser Europa (Alemania) | GW CS8PM1.PM-LUMQ-XX53-1-350-R18 | 1.669 unidades | 1 u.: 1,33 EUR · 10: 0,937 EUR · 100: 0,698 EUR · carrete 600: 0,593 EUR | Referencia de costo real para compra baja y media |
| Mouser Brasil | GW CS8PM1.PM-LUMQ-XX53-1-350-R18 | 1.669 unidades | 1 u.: USD 1,55 · 100: USD 0,812 · carrete 600: USD 0,689 | Referencia regional |
| DigiKey | GW CS8PM1.PM-LUMQ-XX53-1-350-R18 | Activo, sin stock habitual; requiere cotización | Sin precio directo | Confirma parámetros eléctricos y mecánicos |
| Mouser Argentina | Variantes OSLON SSL 80 relacionadas | Variante LTMP 6500 K sin stock, mínimo 600 | ARS 1.128,58 c/u a 600 (variante relacionada) | No confirma disponibilidad local del LUMQ 5000 K |
| TME Argentina | Categoría LEDs blancos de potencia ams OSRAM | Verificar parte exacta | No confirmado | Posible canal alternativo |

::: nota clave | Conclusiones de compra
- Comprar la variante objetivo **LUMQ 5000 K** (XX53-1, o A333-1 como alternativa aprobada).
- No comprar variantes viejas u obsoletas como **LSLU**, salvo para prototipo o aceptando menor flujo.
- En Argentina es más realista **importar por Mouser, DigiKey o TME** que esperar stock local de la parte exacta.
- Confirmar pedido mínimo, carrete de 600 y plazos de entrega antes de congelar la lista de materiales.
- Costo del LED en volumen de carrete: **≈ 0,60 EUR por unidad**, irrelevante frente al costo del módulo.
:::

# Parte V — Validación

## 12. Recomendaciones de prototipo

1. **Medir el flujo real de salida** con esfera integradora o con un sensor calibrado, en régimen térmico estable a 350 mA. Es la medición que cierra la incógnita de este informe.
2. **Medir temperatura** en el punto de soldadura, o cerca del LED, durante un ensayo 24/7 a la máxima temperatura ambiente prevista.
3. **Comparar conductos**: mecanizado tal como sale de máquina, pulido, con inserto o film reflectivo y con recubrimiento blanco de alta reflectancia. Con los resultados se ajusta el modelo de la sección 7.
4. **Evaluar difusores** de transmisión conocida (75 %, 85 % y 90 %) y medir la uniformidad del punto de luz junto con el flujo.
5. **Validar con la cámara o el sensor real** del robot: contraste, uniformidad, ausencia de parpadeo con el PWM elegido y estabilidad del color en el tiempo.
6. **Verificar tolerancias**: centrado del LED en el conducto y distancia real LED–ventana, incluida la altura del encapsulado de 2,13–2,30 mm.

::: detalle Criterio de aceptación sugerido para el prototipo
- Flujo de salida ≥ 100 lm medido con un LED de bin LUMQ a 350 mA, en régimen térmico estable.
- Ts ≤ 85 °C en la peor condición ambiente, con ensayo continuo de al menos 72 h.
- Uniformidad y contraste aceptados por el equipo de visión artificial.
- Sin decoloración visible de la lente tras la exposición a los agentes de limpieza previstos.
:::

# Anexos

## Anexo A — Fuentes verificadas

- ams OSRAM, página de producto OSRAM OSLON SSL 80 GW CS8PM1.PM: https://ams-osram.com/products/leds/white-leds/osram-oslon-ssl-80-gw-cs8pm1-pm
- ams OSRAM, datasheet oficial GW CS8PM1.PM, versión 1.10, 2026-03-05: https://look.ams-osram.com/m/16996c4989af2a7d/original/GW-CS8PM1-PM.pdf
- Mouser Europa, GW CS8PM1.PM-LUMQ-XX53-1-350-R18: https://www.mouser.de/ProductDetail/ams-OSRAM/GW-CS8PM1.PM-LUMQ-XX53-1-350-R18
- Mouser Brasil, GW CS8PM1.PM-LUMQ-XX53-1-350-R18: https://br.mouser.com/ProductDetail/ams-OSRAM/GW-CS8PM1.PM-LUMQ-XX53-1-350-R18
- DigiKey, GW CS8PM1.PM-LUMQ-XX53-1-350-R18: https://www.digikey.com/en/products/detail/ams-osram-ag/GW-CS8PM1-PM-LUMQ-XX53-1-350-R18/26248732
- Mouser Argentina, variante relacionada OSLON SSL 80: https://ar.mouser.com/ProductDetail/ams-OSRAM/GW-CS8PM1.PMLTMPXX51
- TME Argentina, categoría LEDs de potencia blancos ams OSRAM: https://www.tme.com/ar/es/katalog/leds-de-potencia-blancos_113364/p%2Cams-osram_114/

::: nota dato | Alcance de la verificación
Los datos técnicos de este informe se contrastaron con el datasheet oficial v1.10: pedido, valores máximos, características, grupos, curvas, plano, reflow, notas y descargo. Los precios y el stock de distribuidores provienen del relevamiento del 27-09-2026 y pueden cambiar en días. Las cifras de flujo de salida son cálculos propios con los supuestos declarados en la sección 7.
:::

## Anexo B — Método de cálculo

- **Modelo angular del LED**: `I(θ) = I0·cos^m(θ)`, con m = 2,60 para 2φ = 80°. Para los LEDs de comparación, m = 1,00 (120°, lambertiano) y m = 0,51 (150°).
- **Captura directa**: `F(α) = 1 − cos^(m+1)(α)`, con α = 19,65°.
- **Conducto**: trazado de rayos Monte Carlo en un cilindro de Ø 5 × 7 mm con fuente puntual en el centro del fondo. La pared es difusa (lambertiana) o especular ideal, con reflectividad Rw por rebote; el fondo es absorbente y la salida es la boca completa.
- **Difusor**: transmisión aplicada como factor constante (0,75 a 0,90), sin retrorreflexión hacia el conducto.
- **Limitaciones**: la fuente real no es puntual (la lente mide ≈ 2,5 mm de diámetro); el fondo (PCB y cuerpo del LED) refleja parte de la luz; y el difusor devuelve luz al conducto. Con un emisor de 2,4 mm de diámetro la eficiencia cambia menos de 0,015. Con un fondo difuso de reflectividad 0,5, la pared difusa gana entre 0,01 y 0,08, y la especular no cambia. Los modelos acotan el problema; no reemplazan la medición.
- **Reproducción**: `python3 tools/led_montecarlo.py` imprime las tablas de la sección 7, y `python3 tools/led_montecarlo.py --fondo 0.5` calcula la variante con fondo reflectivo.
