# El modelo integrado, por partes

Este documento es la puerta de entrada al trabajo. Reemplaza la lectura
cronológica (rev. A → G de `NOTAS_PROGRESO.md`, que cuenta cómo se llegó) por
una lectura **estructural**: qué partes tiene el modelo, qué hace cada una, y
cómo se enganchan.

La estructura está declarada en código en `wtd/modelo.py` y anclada en
`tests/test_modelo.py`. No es un resumen escrito a mano: los números del
palpador se recalculan desde `wtd.softprobe`, y un test falla si el relato y
el código se separan.

```
$ python -m wtd.modelo
```

---

## La cadena en una línea

> **B1** la cuña se mueve → **B2** se mueve en **dos bandas** distintas según
> el ajuste → **B3** el palpador es un filtro que planta su corte en el medio
> → **B4** la lectura integra esa energía y la convierte en un número → **B5**
> el golpe que la excita se mide a sí mismo → **B6** los dos números deciden.

```
  afuera            B1            B2             B3            B4         B5          B6
 ────────        ────────     ──────────     ──────────     ────────    ───────    ─────────
 geometría   →   w(t)     →   f_asentada  →  f0           → rasgo    →            → veredicto
 apoyo           escalera     f_suelta       ζ              separación   E_golpe
 k_hombro  ⚠     x_pico       hueco          a_despegue     despegue?    v_maza
 F = 1 N   →                              →  m_punta      →           →  e, η    →
 d = 12.5 mm                                 k_precarga
 LAH04     ───────────────────────────────────────────────────────────→
```

Seis bloques, 32 magnitudes, una sola marcada `PENDIENTE`. La cadena **cierra**:
ningún bloque consume un símbolo que nadie produce.

### Dónde está el riesgo

| | |
|---|---|
| **Único bloque abierto** | B6, el clasificador conjunto. Falta ajustarlo con datos de banco. No es un riesgo: la separación de ×112 deja muchísimo margen. |
| **Único bloque que puede tumbar todo** | B2, y por un solo parámetro: `k_hombro`, estimado, nunca medido. |

Todo lo demás está cerrado y anclado en tests.

---

## B1 — La cuña y su apoyo

**Pregunta:** cuando el golpe entra, ¿cómo se mueve la cuña, y qué cambia con
el ajuste?

**Entra:** geometría (G11 50×30×8 mm, 22,8 g), tipo de apoyo, `k_hombro`,
distancia del palpador.
**Sale:** `w(t)`, la escalera S0–S6, `x_pico`, `a_pico`, `deriva`.

**Ecuación:**

```
M q'' + C q' + K q = f(t),   con contacto unilateral en el hombro:
    F_hombro = k_hombro · max(0, penetración)        (sólo empuja)
```

Viga de Timoshenko libre-libre, 20 modos, velocity-Verlet, dt = 50 ns.

### Lo que hay que entender

El golpe entra **radialmente hacia adentro**, o sea que *desasienta* la cuña de
los hombros. Lo que cambia entre una cuña ajustada y una suelta no es la cuña
— es su **condición de borde**:

- ripple precargado → hombros cerrados → la cuña está acoplada al núcleo en
  toda su longitud;
- sin precarga → hombros abiertos → la cuña queda colgada del ripple.

La escalera S0–S6 no es un cambio gradual de rigidez: es un cambio de
condición de borde. La frontera asentada|suelta cae entre S3 (25 % de
precarga) y S4 (5 %).

### El resultado que mata la idea ingenua

A 5 mJ y 12,5 mm del golpe:

| estado | x_pico [µm] | a_pico [g] | lectura del palpador [g] |
|---|---|---|---|
| S0 ajustada | 0,31 | 830 | 2,4 |
| S1 · 75 % | 0,30 | 756 | 2,3 |
| S2 · 50 % | 0,40 | 1545 | 2,9 |
| S3 · 25 % | 2,39 | **4808** | 16,2 |
| S4 residual | 7,12 | 1544 | 45,6 |
| S5 · juego 50 µm | 6,89 | 1073 | 44,4 |
| S6 · juego 200 µm | 6,90 | 1062 | 44,5 |

**El pico de aceleración no es monótono con la soltura.** Sube hasta S3 y
después baja, así que **1545 g corresponde tanto a S2 (cuña al 50 %) como a S4
(precarga residual)**: un acelerómetro rígido no puede distinguirlas. El de
desplazamiento sí es monótono, y la lectura del palpador lo sigue.

Medir la aceleración cruda de la cuña no sirve — y eso es independiente de
cuánta precarga haya disponible.

### Hipótesis

| hipótesis | origen | si es falsa |
|---|---|---|
| El apoyo es distribuido a lo largo del hombro, no en los extremos | dato de campo | cambia todas las frecuencias modales; de ahí salía el falso «6,1 kHz» de la rev. A |
| `k_hombro` = 2·10¹⁰ N/m por metro | **estimado** | la hipótesis más cara del proyecto → ver B2 |
| La disipación de junta crece al aflojarse (ζ 0,012 → 0,055) | estimado | de los cinco parámetros estimados de la cuña es el único que mueve el resultado |

**Verificación:** ensayo de banco **A**.
**Si falla:** si el aflojamiento real fuera gradual y no un cambio de apoyo, no
hay hueco espectral y el método entero se cae.

---

## B2 — El hueco espectral · *el fundamento del método*

**Pregunta:** ¿en qué se distingue, medible, una cuña asentada de una suelta?

**Entra:** `w(t)`, la escalera, `k_hombro`.
**Sale:** `f_asentada` = 33 350 Hz, `f_suelta` = 175 Hz (techo de banda), y el
reparto de energía contra el corte del palpador.

### La frecuencia sube con el apriete, y sube muchísimo

Una versión anterior de este trabajo afirmaba lo contrario, apoyada en un
6,1 kHz que venía del modelo de apoyo viejo. Estaba mal.

Modelo linealizado:

```
hombro CERRADO  →  32,9 / 33,4 / 33,6 / 40,0 kHz
hombro ABIERTO  →   1,28 / 1,29 kHz   (cuerpo rígido sobre el ripple)
                    y recién después 10,6 / 24,9 kHz de flexión
```

El mecanismo es simple una vez visto: la cuña asentada está pegada al núcleo,
que es una masa prácticamente infinita, así que responde con sus modos de
flexión contra un apoyo rigidísimo. La cuña suelta queda montada sobre el
ripple, que es blando, y responde con sus dos modos de **cuerpo rígido** sobre
ese resorte. No son el mismo modo corrido: son familias de modos distintas.

### El reparto de energía es total, no parcial

Espectro del **desplazamiento** (12,5 mm, 5 mJ, resolución 25 Hz):

| estado | qué hace | 90 % de la energía | por debajo de 1273 Hz |
|---|---|---|---|
| S0 ajustada | ráfaga de 33 kHz, se apaga en 0,06 ms | 33 325 – 33 375 Hz | **0,0 %** |
| S3 · 25 % | las dos cosas | 13 375 – 34 625 Hz | 1,5 % |
| S6 floja | una excursión de 6,9 µm, 2,4 ms | continua – 175 Hz | **100,0 %** |

El filtro no las atenúa distinto: **las separa enteras**.

**Tres trampas ya pisadas.** (1) El espectro que importa es el del
desplazamiento, porque es lo que excita al palpador; el de la aceleración pesa
las altas por ω⁴ y da otra cosa. (2) La ventana tiene que ser larga: con 8 ms
el bin vale 125 Hz y el «pico» de la cuña suelta aparece en 125 Hz por puro
artefacto. (3) Y la de fondo: **la cuña suelta no tiene pico espectral, porque
no oscila.** Cruza su propia media dos veces en 5 ms — es *una* excursión, y su
espectro es el de un transitorio, no el de un modo. Por eso ya no se cita un
«×670 entre los picos»: ese cociente dependía de la ventana, que era la misma
trampa de los 125 Hz vista de más lejos. Lo robusto es el reparto: 0,0 % contra
100,0 %.

### Aquí es donde duele: la sensibilidad a `k_hombro`

| `k_hombro` | 1er modo asentada | separación |
|---|---|---|
| ÷100 | 3 530 Hz | ×0,08 *(invertida)* |
| ÷10 | 10 487 Hz | ×0,34 *(invertida)* |
| ÷3,3 | 18 067 Hz | ×8,3 |
| **2·10¹⁰ (nominal)** | **32 874 Hz** | **×150** |
| ×3 | 55 493 Hz | ×176 |

El diseño está sentado en la rodilla de esta curva. Con el hombro diez veces
más blando, el primer modo asentado entra en la banda del palpador y la
separación **se invierte**. Ningún diseño de palpador sobrevive a eso, porque
no es un problema de palpador: es que el hueco deja de existir.

**Verificación:** ensayo **A**, que no necesita palpador y puede invalidar el
enfoque en un día. Por eso va primero.

---

## B3 — El palpador: un pasa-bajos plantado en el hueco

**Pregunta:** ¿cómo se mide eso con 1 N de precarga y a 12,5 mm del golpe?

**Entra:** las dos bandas de B2, `F_precarga` = 1 N, `d` = 12,5 mm.
**Sale:** el palpador entero.

| magnitud | valor | origen |
|---|---|---|
| masa móvil (carro + acelerómetro) | 0,68 g | elegida — sale en 0,33 g, hay que **lastrarla** con 0,35 g |
| rigidez de medición (flexura) | 43,5 N/mm | modelo |
| f₀ (corte del filtro) | 1273 Hz | modelo — banda útil 700–1700 Hz |
| ζ (amortiguamiento) | 0,02 | elegido — tiene piso **y** techo |
| a_despegue (fondo de escala) | 150 g | **= F/m, el invariante** |
| masa del lado punta | ≤ 20 mg | modelo — techo duro |
| rigidez del resorte de precarga | 0,30 N/mm | la fija el posicionamiento, no la medición |

### La topología

```
cuña ── punta ──[ resorte k ]── carro ──[ precarga F ]── cuerpo
                                  │
                            acelerómetro
```

La compliancia tiene que estar **en el camino de carga**, entre lo que toca y
lo que mide. Con un vástago rígido punta→carro y la flexura carro→cuerpo se
obtiene el palpador **rígido con pasos de más**: el carro sigue a la cuña y el
acelerómetro lee los miles de g.

### Ecuaciones

```
m x'' + c (x' − w') + k (x − w) = 0                    (en contacto)

F_contacto = F_precarga − k(x−w) − c(x'−w') + m_punta · w''

despegue  ⟺  F_contacto ≤ 0  ⟺  a_leída = F / m
```

El tercer término de `F_contacto` es lo que fija el techo de masa de la punta:
la punta queda del lado de la cuña, que la arrastra **cinemáticamente** a
miles de g. Seguirla cuesta `m_punta · a_cuña`, y esa fuerza sale del contacto,
que no puede dar más que la precarga:

```
m_punta ≤ F / a_cuña_max = 1 N / 4800 g ≈ 21 mg
```

### Tres resultados que ordenan el diseño

**1. El fondo de escala de cualquier palpador apoyado vale F/m, y no depende
del resorte.** Ablandar el acople no cuesta rango: cambia *qué parte* del
movimiento de la cuña cae adentro de ese fondo de escala. Con acople rígido se
gasta en los picos de alta frecuencia, que no llevan información; con acople
blando se gasta en el desplazamiento, que sí.

El límite es **de un solo lado**: acota la semionda que *descarga* el contacto.
Por eso el margen se calcula contra el pico de descarga (73,5 g) y no contra el
de compresión (85,9 g), que es el que dimensiona el acelerómetro. Margen real
**2,04**.

**2. f₀ elige la calidad, la masa elige si sobrevivís — y son independientes.**
La separación y el pico leído resultaron función de f₀ (y ζ) sola. Por eso el
diseño se hace en dos pasos y no resolviendo un compromiso.

| f₀ | a_max leída | separación | masa máx. (1 N, margen 1,4) |
|---|---|---|---|
| 600 Hz | 17,9 g | ×91 | 4,06 g |
| 1000 Hz | 49,0 g | ×139 | 1,49 g |
| **1273 Hz** | **78,4 g** | **×150** | **0,93 g** |
| 1600 Hz | 137,5 g | ×114 | 0,53 g |
| 2000 Hz | 235,4 g | ×80 | 0,31 g |

**3. ζ es el parámetro más sensible de todo el trabajo, y tiene piso y techo.**

| ζ | a_max [g] | separación | ring-down al 1 % |
|---|---|---|---|
| 0,005 (flexura de acero) | 78,4 | ×150 | 115 ms |
| **0,020 (recomendado)** | **78,8** | **×112** | **29 ms** |
| 0,050 | 86,6 | ×40 | 12 ms |
| 0,080 | 99,6 | ×14 | 7 ms |
| 0,150 (elastómero) | 135,6 | ×3 | 4 ms |
| 0,300 | 215,7 | ×0,7 | 2 ms — y **despega** |

- **Techo:** con elastómero el rechazo de alta frecuencia cae de 1/r² a 1/r y
  la separación se desploma. «Flexura metálica y no elastómero» no es una
  recomendación de segundo orden: es **la** decisión de construcción.
- **Piso:** con ζ muy bajo, Q es alto y una excitación **sostenida** a f₀
  (máquina girando, motores del crawler, ring-down del tiro anterior) despega
  el palpador con apenas 0,23 µm. Lo que protege es el **tiempo de
  crecimiento** — llegar a Q pide ~Q ciclos y el impacto dura ~1,3 — pero el
  margen es de 16 ms.

ζ = 0,02 cuesta ×150 → ×112 de separación y compra 4× de inmunidad, además de
bajar el ring-down de 115 a 29 ms, que es lo que fija el ritmo máximo de
disparo.

### La coincidencia que nadie eligió

f₀ salió de optimizar la separación: **1273 Hz**. El modo de cuerpo rígido de la
cuña *suelta* sobre el ripple sale de su masa y de la rigidez del resorte:

```
f = √(k_ripple · L / m) / 2π = √(3·10⁷ · 0,05 / 0,0228) / 2π = 1291 Hz
```

Coinciden dentro del **1,4 %**, y son cálculos independientes. Importa porque el
palpador es vulnerable justo ahí: una excitación *sostenida* a f₀ lo despega con
0,92 µm, y la excursión de la cuña suelta es 6,9 µm — **7,5 veces más**.

| seno sostenido a 1273 Hz | pico leído | ¿despega? |
|---|---|---|
| 0,5 µm | 52,8 g | no |
| 1,0 µm | 105,6 g | no |
| 3,0 µm | 246,0 g | **sí**, 16,5 % de las muestras |
| 6,9 µm — la excursión real | 306,9 g | **sí**, 21,8 % |

En el modelo no pasa, y la razón es comprobable: **la cuña suelta no oscila**,
hace una excursión y el ripple la reasienta (B2). Lo que llega al palpador es un
escalón, y un escalón no construye la resonancia.

Pero eso es una hipótesis sobre la cuña, no sobre el palpador, y descansa en
`k_ripple`, que es estimado. Un barrido anterior concluyó que `k_ripple` podía
variar 60 veces sin mover el resultado un 2 %: sigue siendo cierto *para la
separación*, y es falso para esto — `k_ripple` es exactamente lo que decide
dónde cae ese modo respecto de f₀.

Tres cosas, por costo: (1) el **detector de despegue de B4 ya cubre este modo de
falla**; (2) el **ensayo A lo responde de una**, porque el acelerómetro pegado a
la cuña muestra si la suelta suena o hace una excursión; (3) si sonara, mover f₀
cuesta poco — a 1000 Hz la separación baja de ×150 a ×139 (7 %), a 800 Hz a ×119
(21 %). No hay que decidirlo ahora: hay que medirlo.

### Construcción

- **Flexura de medición:** 2 láminas de acero de resorte 2 × 0,15 mm, luz
  10 mm, empotradas en ambos extremos, masa al centro. k = 43,5 N/mm, 83 MPa
  contra ~1000 de límite elástico → **vida infinita**. Pone 17,4 mg del lado
  punta.
- **Punta:** formar el resalto en la propia lámina; una bolilla ⌀1 mm agrega
  4,1 mg y deja el total en 21,6 mg, apenas por encima del techo.
- **Lastre:** 0,35 g del lado del carro. Sin lastre f₀ se va a 1829 Hz y la
  separación cae a ~×105. **Agregar masa mejora la medición.**
- **Cuerpo:** ≥ 7 g (10× la masa móvil). Con 3× el efecto de masa reducida
  corre f₀ un 15 %.
- **Flexura de precarga:** 0,30 N/mm, además **guía** el carro en el eje de
  medición. Es 145× más blanda que la de medición, así que suma ~1 % a la
  rigidez que fija f₀. Da el **rango de 3 mm** (F de 0,70 a 1,60 N) — y la
  ganancia varía 0,7 % entre 0,5 y 1,5 N, porque la precarga sólo entra por el
  término de Hertz.

### Hipótesis

| hipótesis | origen | si es falsa |
|---|---|---|
| **La cuña suelta no queda sonando a ~1,29 kHz sobre el ripple** | **estimado** | **lo más frágil después de `k_hombro`** — ver abajo |
| La flexura metálica da ζ ≈ 0,005–0,02 | estimado | el ensayo es inservible con elastómero; se mide en un ping |
| La resonancia parásita del lado punta (~7,4 kHz) no molesta | **estimado** | cae entre las dos bandas, así que en principio no interfiere, pero **no está en el modelo** — la punta se trata como masa pura. **Pendiente** |
| El cuerpo pesa ≥ 7 g | elegido | f₀ se corre |

**Verificación:** ensayos **B**, **C**, **D**.

---

## B4 — La lectura: de la señal a un número

**Pregunta:** ¿qué número se saca del registro, y cuánto separa?

**Entra:** f₀, ζ, a_despegue, masa móvil.
**Sale:** el rasgo de decisión y su poder de separación.

```
rasgo = ∫ a(t)² dt   sobre 3 ms, sobre la señal SIN filtrar
```

> **Los 5 kHz nunca se aplicaron al cálculo.** Son una especificación de la
> cadena de adquisición y entran en el presupuesto de ruido del acelerómetro,
> pero el rasgo se integra sobre la señal cruda. Aplicando un pasa-bajos real de
> 5 kHz la separación **mejora**: ×579 → ×4608 a 5 mJ, y ×112 → ×210 en la peor
> energía. O sea que todas las cifras de este documento son conservadoras.
>
> **Y la ventana de 3 ms es un parámetro libre que mueve el número.** Separación
> en la peor energía: ×45 con 0,5 ms, ×68 con 1 ms, ×98 con 2 ms, ×112 con 3 ms,
> ×127 con 5 ms. Los 3 ms son heredados, no óptimos; alargar a 5 ms es gratis
> (el ritmo de disparo es de 125 ms). Falta barrer ventana y filtro juntos.

| magnitud | valor |
|---|---|
| separación asentada \| suelta | **×112** (ζ = 0,02); ×150 con ζ = 0,005 |
| ventaja sobre el pico | ×14 a ×58 |
| rango de lectura sobre 126 casos | 0,9 a 109 g, **cero despegues** |
| acelerómetro | ADXL1005 ±100 g, 0,1 g de masa, 44 dB de SNR peor caso |

### Lo que el palpador mide no es desplazamiento ni velocidad limpios

Por regresión sobre los 126 casos simulados: ω²x da R² = 0,92 con 40 % de error
mediano, ωv da R² = 0,84 con 26 %. La cuña no lo excita con un impulso sino con
una ráfaga, así que la lectura es un valor de **espectro de respuesta al
choque** a f₀. Hay que calibrarla; no se invierte con fórmula cerrada. No es un
problema para este ensayo, que clasifica y no mide una magnitud física.

### Por qué la energía de la señal le gana al pico

Promedia sobre toda la ráfaga en vez de quedarse con un instante — y el
instante del pico está dominado por el transitorio rápido del impacto, que es
justamente la parte que **no** sigue al estado de ajuste.

### La detección de despegue sale gratis y es binaria

En vuelo la única fuerza sobre el carro es la precarga, así que la lectura se
clava **exactamente** en −F/m. Se cuentan las muestras con |a + F/m| < 1 % de
F/m:

```
contacto limpio →    0 muestras
despegue        →  110 muestras (3,67 %)
```

No hace falta calibrar nada para usarlo y no tiene falsos positivos.

### Límite honesto del ensayo

Resuelve bien la **transición** asentada/suelta (entre S3 y S4), **no el grado
de apriete**. Dentro del grupo asentado la lectura no es monótona, y S4/S5/S6
saturan todos en el mismo valor. Es un ensayo de dos clases, no un medidor de
precarga.

---

## B5 — El golpe, y cómo se mide a sí mismo

**Pregunta:** ¿con cuánta energía hay que golpear, y cómo se sabe cuánta fue?

**Entra:** la escalera, el rasgo, el voice coil LAH04.
**Sale:** energía de golpe, ritmo, velocidad de la maza y el error del cociente.

| magnitud | valor |
|---|---|
| energía de golpe | **3 a 5 mJ** (tiene óptimo) |
| ritmo máximo | 8 tiros/s (lo fija el ring-down del palpador) |
| error del cociente de velocidades | **0,145 %** por back-EMF (0,291 % el inductivo) |
| error de la energía absoluta | 4 % sistemático y calibrable; repetibilidad 0,17 % |
| τ_e de la bobina | 43,1 µs |

### La energía del golpe tiene óptimo, y no es el mínimo

- **Límite de arriba** (ya conocido): con el golpe fuerte hasta la cuña
  ajustada despega del hombro y la escalera se aplana.
- **Límite de abajo** (menos obvio): a 1 mJ la cuña ajustada S0 devuelve *más*
  señal que S1 y S2, o sea que la escalera deja de ordenar en el extremo
  apretado.

El máximo es ancho: 3–5 mJ da ×380 a ×579, contra ×230 a 1 mJ y ×112 a 12 mJ. Para resolver fino la frontera S3|S4 sí conviene lo más flojo
posible: ese salto vale ×459 a 1 mJ.

### Medir la velocidad con la propia bobina

```
u = R·i + L·di/dt + K_F·v          →      con el drive abierto:   u = K_F(x)·v
```

No agrega ningún sensor. El problema es que la escala K_F(x) varía 31 % a lo
largo de la carrera, lo que da 4 % de error en la **energía absoluta**.

### Pero si se miden las dos velocidades, el error de escala se cancela exacto

El discriminante es un **cociente** (índice tipo Leeb, o η = 1 − e²), y en un
cociente K se va:

```
e = v_rebote / v_incidente = (K·v_r) / (K·v_i) = v_r / v_i
```

Lo que **no** se cancela es la *variación* de K entre los dos instantes, o sea
dK/dx. Y ahí hay un regalo geométrico: la curva del LAH04 tiene su máximo en el
centro de carrera, donde **dK/dx = 0**. Haciendo caer el impacto en el centro el
residuo es 0,04 %, contra 0,41 % a 1,5 mm del centro.

| fuente | contribución al cociente |
|---|---|
| variación de K_F (impacto al centro) | 0,04 % |
| ruido | 0,138 % |
| offset | 0,011 % |
| **total sobre e / Leeb** | **0,145 %** |
| total sobre η = 1 − e² | 0,48 % |

Comparación justa contra el sensor inductivo del proyectil: **0,145 % contra
0,291 %** — el back-EMF es 2× mejor, 138 niveles Leeb distinguibles contra 69.
(Para la energía *absoluta* el inductivo gana; el veredicto opuesto de una nota
anterior comparaba esa magnitud, que no es la que usa el discriminante.)

### Cuidado con la arquitectura

- Si el lanzador **separa** la maza (resorte, vuelo libre), la bobina sólo ve
  la velocidad de separación y **no el rebote** → la cancelación no aplica.
- Con **palanca** no se separa, y el back-EMF ve las dos — pero entonces el
  49 % de la masa equivalente *es* el actuador.
- τ_e = 43 µs es comparable al contacto (60 µs): hay que abrir el drive ~5τ_e
  antes del impacto, o sea 265 µm antes.

---

## B6 — La decisión: asentada o suelta · **bloque abierto**

**Pregunta:** ¿cómo se combinan el rasgo y la energía del golpe en un veredicto?

**Entra:** rasgo, separación, energía del golpe, error del cociente, detector de
despegue.
**Sale:** veredicto de dos clases, descarte de tiros, y el clasificador —
`PENDIENTE`.

Este es el **único bloque que no está cerrado**. El rasgo de B4 separa ×112,
pero depende también de con cuánta energía se golpeó, y esa energía varía tiro a
tiro. B5 la mide con 0,145 % de error, más que suficiente para usarla como
covariable — pero la función que combina las dos cosas todavía no está
ajustada, porque ajustarla pide datos de banco, no de simulación.

Lo que **sí** está definido es el orden de operaciones:

1. el detector de despegue descarta el tiro (binario, sin calibración);
2. se normaliza el rasgo por la energía entregada;
3. recién ahí se compara contra el umbral.

El umbral se **calibra** contra cuñas de estado conocido; no se deriva del
modelo, porque derivarlo sería confiar en `k_hombro`.

También queda afuera del modelo el montaje del palpador en el brazo del crawler
y su dinámica propia.

**Si falla:** es trabajo pendiente, no un riesgo. La separación de ×112 deja
muchísimo margen para cualquier clasificador razonable.

---

## Los cuatro ensayos de banco, atados a lo que matan

Ordenados por cuánto ahorran si fallan.

### A — ¿Existe el hueco espectral? → B1, B2

- **Mata:** la hipótesis `k_hombro`, la única que puede tumbar el método.
- **Instrumentos:** acelerómetro de choque pegado a la cuña, ≥50 kHz, ±5000 g,
  200 kS/s. **No necesita palpador.**
- **Criterio:** la cuña asentada responde arriba de 20 kHz y la suelta abajo de
  1 kHz. **Y la suelta hace *una* excursión que se apaga en pocos ms, no un tren
  sostenido cerca de 1,3 kHz** — de eso depende que el palpador no despegue.

### B — Ping test del palpador construido → B3

- **Mata:** la hipótesis ζ, el parámetro más sensible del diseño.
- **Instrumentos:** un golpecito y el registro del decaimiento. Da ζ **y** f₀
  de una sola medición.
- **Criterio:** ζ ≤ 0,02 y f₀ entre 700 y 1700 Hz.

### C — Palpador contra referencia, barriendo precarga → B3, B4, B6

- **Mata:** que la separación simulada exista en fierro.
- **Criterio:** separación > ×100 entre 25 % y 5 % de precarga.

### D — Robustez → B3, B4, B5, B6

- **Mata:** los supuestos de operación del crawler.
- **Criterio:** ganancia insensible a la precarga (±20 % → <1 %), umbral de
  despegue donde lo predice F/m, repetibilidad dentro del presupuesto de ruido.

---

## Cómo leer el resto del repositorio

| quiero… | voy a |
|---|---|
| la estructura (esto) | `docs/MODELO.md`, `wtd/modelo.py` |
| **las trece figuras** | el artefacto publicado, https://claude.ai/artifact/XpcvS45VapBXWZUqwFvvpP |
| regenerar los datos de esas figuras | `python studies/figuras_modelo.py` → `results/figuras_modelo.json` |
| el orden de magnitud de todo, ejecutable | `python -m wtd.modelo` |
| la física del palpador | `wtd/softprobe.py` (el docstring es el argumento completo) |
| la velocidad por back-EMF | `wtd/backemf.py` |
| la cuña y la escalera | `wtd/wedge.py`, `wtd/beam.py`, `wtd/coupling.py` |
| reproducir los barridos | `python studies/soft_probe.py` → `results/softprobe.json` |
| las anclas | `python -m pytest tests/ -q` (54 tests) |
| **cómo se llegó** hasta acá, y qué se corrigió | `NOTAS_PROGRESO.md`, rev. A → G |
| el informe para revisión por pares | artefacto publicado, ver `NOTAS_PROGRESO.md` |

### Marcas de procedencia

Las mismas en todo el trabajo:

| | |
|---|---|
| **D** | dato del usuario o de campo — no se discute |
| **V** | de catálogo / hoja de datos — verificable en papel |
| **M** | calculado por el modelo — reproducible corriendo el código |
| **S** | medido sobre la simulación — reproducible corriendo el estudio |
| **E** | **estimado** — el riesgo vive acá |
| **X** | elegido por diseño — es una decisión, no un hallazgo |
