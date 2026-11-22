# Retardo autoalimentado: probabilidad de los modos de fallo P1–P4

Estudio de la probabilidad de cada modo de fallo del núcleo (almacenamiento → contador → driver → iniciador) del diseño de `sistema-retardo-autoalimentado.md`. No hay una gravedad asignada a cada modo, así que acá **no se ponderan**: se estima la probabilidad de cada uno por separado y qué la domina.

| Código | Evento |
|---|---|
| **P1** | Activa antes de t1 (≈ 4 s) |
| **P2** | Activa entre t1 y t2 (antes de t2 − 5 %) |
| **P3** | No activa |
| **P4** | Activa después de t2 + 5 % |

## 1. Resumen

Valores por unidad y por uso (una demanda), con placa aprobada en el banco 100 % y **2 años de almacenamiento** antes del uso. Son órdenes de magnitud con los supuestos de §2; sirven para comparar y para decidir dónde poner esfuerzo, no como valor certificable.

| Modo | Probabilidad estimada | Qué la domina | Con las mejoras de §7 |
|---|---|---|---|
| **P1** | **~10⁻⁷** (10⁻⁸ a 10⁻⁶) | Falla de causa común que cierra Q1 y Q2 a la vez: sobretensión en VDD (LDO en corto) y acople dV/dt en las gates al llegar el pulso | < 10⁻⁹ en hardware |
| **P2** | **10⁻⁵ a 10⁻⁴** con T programable · ~10⁻⁹ con T fija | Error humano al programar un T más corto. El hardware casi no aporta | 10⁻⁶ a 10⁻⁵ |
| **P3** | **~2 × 10⁻⁴** sin contar el iniciador (5 × 10⁻⁵ a 10⁻³) | Fallas latentes en almacenamiento (casi todas terminan en "no dispara"), escapes de fabricación y margen de energía de C_F | ~10⁻⁴ |
| **P4** | **10⁻⁵ a 10⁻⁴** con T programable · ~10⁻⁹ con T fija | El mismo error de programación que P2 (T más largo) | 10⁻⁶ a 10⁻⁵ |

Conclusiones:

1. **El diseño falla hacia P3.** Casi cualquier componente que se abre, se cae o se corta termina en "no dispara", porque el firmware aborta ante cualquier anomalía y las dos llaves en serie tienen que cerrarse juntas. Es la consecuencia esperada de la política "ante la duda, abortar".
2. **P2 y P4 no los produce la electrónica.** Con tolerancia de ±5 % el error de tiempo del cristal queda en ~0,3 % en el peor caso (§4). Lo que puede llevar a un disparo fuera de ventana es **un T mal elegido o mal cargado**. Con T fija en firmware (variante A) ese término casi desaparece.
3. **P1 no depende de fallas simples.** Hay dos caminos de causa común que hay que cerrar en el esquemático: sobretensión en el micro y acople capacitivo en las gates (§3.1).
4. **P3 depende fuertemente del I²t real del iniciador.** Con C_F = 330 µF y t2 = 40 s, el peor caso entrega ~3 A²·ms. Si el iniciador pide 5 A²·ms, P3 sube a ~4 % (§5.3). Es el dato que falta y el que más mueve los números.

## 2. Método y supuestos

Una sola demanda dura como máximo 40 s. Con tasas de falla típicas de componentes (≈ 100 FIT en total), la probabilidad de que algo se rompa **durante** esos 40 s es ~10⁻¹². Lo que importa es lo que ya está mal al momento de usarla:

| Fuente | Cómo se estima |
|---|---|
| **A. Fallas latentes en almacenamiento** | λ · k_d · t_alm, con k_d = 0,1 (tasa en reposo ≈ 10 % de la de operación), t_alm = 2 años = 17 520 h |
| **B. Escapes de fabricación** | Defectos que pasan el banco 100 % (juntas marginales, daño por ESD) |
| **C. Paramétrica** | Monte Carlo de energía y tiempo con tolerancias de componentes (§4, §5.3) |
| **D. Causa común y ambiente** | Análisis de peor caso: sobretensión, dV/dt, choque, frío, EMI |
| **E. Sistemáticas y humanas** | Errores de firmware y de programación de T. No tienen tasa: se acotan con proceso y verificación |

Tasas de falla de referencia (orden de magnitud, estilo SN 29500 / MIL-HDBK-217F a ~40 °C):

| Ref | Pieza | FIT | Reparto de modos de falla (supuesto) | Efecto |
|---|---|---|---|---|
| U1 | MCU | 15 | Muerto / no arranca 80 % · salida trabada 10 % · comportamiento errático 10 % | P3 · latente para P1 · P3 (aborta) |
| Y1 | Cristal 32 kHz | 10 | No arranca / abierto ≈ 100 % | P3 (el firmware aborta) |
| U2 | LDO | 8 | Sin salida 60 % · salida alta (corto IN-OUT) 25 % · otros 15 % | P3 · **causa común P1** |
| Q1, Q2 | AO3400A | 5 c/u | Corto D-S 50 % · abierto 30 % · fuga de gate 20 % | Latente para P1 · P3 · P3/P1 |
| D1 | SS34 | 3 | Abierto 50 % · corto 50 % | P3 · P3 (C_F se descarga hacia la línea) |
| D2 | BAT54WS | 2 | Abierto · corto | P3 · posible brown-out durante el disparo (P3) |
| D3 | SMAJ15A | 5 | Corto ≈ 80 % · abierto 20 % | P3 · latente (sin protección) |
| C_F | Polímero 330 µF | 15 | Corto 40 % · abierto 30 % · pérdida de capacidad / suba de ESR 30 % | P3 |
| C_loc | MLCC 10 µF | 2 | Corto (fisura por flexión) | P3 |
| R | 9 resistores | 0,5 c/u | Abierto ≈ 100 % | Según cuál (§3.4) |
| — | ~70 juntas de soldadura | 0,2 c/u | Abierto | P3 |

Total ≈ 100 FIT. En reposo durante 2 años: 100 × 10⁻⁹ × 0,1 × 17 520 ≈ **1,8 × 10⁻⁴**, que se escala linealmente con el tiempo de almacenamiento y con k_d (0,03–0,3 según la fuente da 5 × 10⁻⁵ a 5 × 10⁻⁴).

## 3. P1 — Activa antes de t1

El disparo requiere que Q1 **y** Q2 conduzcan a la vez. El firmware no sube ninguna gate antes de T. Por lo tanto P1 necesita una de estas tres cosas: dos fallas independientes, una sola falla que afecte a las dos llaves (causa común), o un error de firmware.

### 3.1 Árbol de P1

| Camino | Cálculo | Probabilidad |
|---|---|---|
| Q1 y Q2 en corto, independientes (latentes en almacenamiento) | (5 × 10⁻⁹ · 0,1 · 17 520 · 0,5)² = (4,4 × 10⁻⁶)² | ~2 × 10⁻¹¹ |
| Un MOSFET en corto de fábrica no detectado × el otro en corto en almacenamiento | 10⁻⁵ × 4,4 × 10⁻⁶ | ~4 × 10⁻¹¹ (≈ 0 si el banco prueba cada llave por separado) |
| Un MOSFET en corto × pin del MCU trabado en alto | 4,4 × 10⁻⁶ × 1,3 × 10⁻⁶ | ~6 × 10⁻¹² |
| **Causa común: LDO en corto IN-OUT** → VDD sube a ~11 V, el MCU se daña y sus salidas pueden quedar en alto (o conducir a través de los diodos de protección a VDD) → las dos gates en alto | 8 × 10⁻⁹ · 0,1 · 17 520 · 0,25 = 3,5 × 10⁻⁶, × 0,01–0,1 de que el MCU dañado suba ambas salidas | **3 × 10⁻⁸ a 3 × 10⁻⁷** |
| **Causa común: acople dV/dt (Miller) en las gates** al cargar C_F | Determinístico: pasa o no pasa según el flanco (ver abajo) | 0 o ~1 según el diseño |
| **Causa común: ESD/EOS por la línea** que pasa la TVS y daña el MCU | Depende del ambiente. Misma consecuencia que el LDO en corto | sin dato: 10⁻⁸ a 10⁻⁶ |
| Error de firmware (overflow del timer, prescaler mal, lectura de T sin CRC) | Sistemático, sin tasa | Se acota con revisión, prueba y un enclavamiento independiente (§7) |
| EMI/RF inducida en los cables del iniciador con las llaves abiertas | Depende del ambiente: la corriente RF puede cerrar por las capacidades C_oss de Q1/Q2 | a evaluar con el ambiente EM real |

**El término dominante de P1 es la sobretensión de VDD**, una sola falla que puede encender las dos llaves. El diseño actual no tiene ninguna defensa contra ella: los pull-downs de 100 kΩ no alcanzan si el pin del MCU queda en alto.

**Acople dV/dt.** Cuando llega el pulso, el drain de Q1 sube de 0 a ~11 V con una constante τ = R_carga · C_F. La capacidad C_rss (≈ 77 pF en el AO3400A) inyecta corriente en la gate y el pull-down la convierte en tensión: V_g ≈ C_rss · dV/dt · R_pd. El V_th mínimo del AO3400A es 0,65 V y baja ~3 mV/°C (≈ 0,52 V a 70 °C).

| R_s | dV/dt | V_g con R_pd = 100 kΩ | V_g con R_pd = 10 kΩ |
|---|---|---|---|
| 0 Ω (fuente rígida) | 171 V/ms | **1,32 V → conduce** | 0,13 V |
| 0,1 Ω | 114 V/ms | **0,88 V → conduce** | 0,09 V |
| 0,5 Ω | 49 V/ms | 0,38 V (margen chico) | 0,04 V |

Es una estimación cuasi estática (la constante de gate R_pd · C_iss ≈ 63 µs es parecida a la del flanco, así que el valor real es algo menor). Igual muestra que **con 100 kΩ y R_s bajo, las gates pueden superar V_th en el flanco**. El encendido es breve (decenas de µs) y probablemente no alcance el I²t de disparo, pero sí puede superar la corriente de no-activación. Hay que medirlo con osciloscopio y con la fuente real. La corrección es barata (§7).

**P1 estimado: ~10⁻⁷** (dominado por la sobretensión de VDD), siempre que el acople dV/dt se elimine por diseño.

### 3.2 Por qué P1 y P2 son casi el mismo problema

Una falla de hardware presente al llegar el pulso dispara en t0, o sea P1. Una falla que aparece durante la cuenta (entre 4 y 40 s) tiene probabilidad ~10⁻¹³. Por eso, del lado del hardware, **lo que no es P1 no llega a ser P2**: P2 queda para los errores de T y de la base de tiempo.

## 4. P2 y P4 — Activa fuera de la ventana t2 ± 5 %

### 4.1 Error de tiempo paramétrico (Monte Carlo, 2 × 10⁶ casos)

| Término | Rango supuesto |
|---|---|
| Cristal: tolerancia inicial | ±20 ppm |
| Cristal: temperatura (−30 a +70 °C, parábola −0,034 ppm/°C²) | 0 a −103 ppm |
| Cristal: envejecimiento | ±5 ppm |
| Corrección de arranque (oscilador interno medido contra el cristal) | ±0,1 % de los primeros 0,5–3 s |
| Latencia de t0 (carga de C_loc, LDO, POR, arranque) no compensada | 5–50 ms, compensando 20 ms |
| T programado | 10–40 s |

Resultado: **error máximo 33 ms, máximo relativo 0,32 %** contra una tolerancia de ±5 % (±500 ms a 10 s). El margen es de más de 15×. La probabilidad paramétrica de P2 o P4 es **cero en la práctica**.

Esto cambia una conclusión del documento original: con ±5 % **el cristal no es necesario para la precisión**. Un oscilador interno calibrado periódicamente contra el HSI16 (supuesto ±3 % peor caso, a confirmar en la hoja de datos del STM32L0) da un error máximo de 3,3 % en el Monte Carlo, dentro de la ventana. Ver §7, punto 6.

### 4.2 Causas gruesas de P2 / P4

| Causa | Resultado | Probabilidad |
|---|---|---|
| **T mal elegido o mal cargado por el operador** (variante B) | P2 si es más corto, P4 si es más largo | 10⁻⁴ a 10⁻³ por operación sin control cruzado; **10⁻⁵ a 10⁻⁴** con relectura y verificación contra la orden. Se reparte entre P2 y P4 |
| Valor de T en el rango permitido pero equivocado | P2 o P4: el CRC no lo detecta porque el dato es válido | Incluido arriba |
| EEPROM corrupta | El CRC lo detecta → aborta → P3 | Fuga del CRC-16: 1,5 × 10⁻⁵ × P(corrupción) ≈ 10⁻¹² |
| El cristal (LSE) falla durante la cuenta y el micro pasa al LSI sin avisar | El LSI del STM32L0 varía entre 26 y 56 kHz → error de −30 % a +50 % → P2 o P4 | ~10⁻¹² en hardware, **pero sistemático si el firmware no lo maneja**: el detector de falla del LSE tiene que abortar, no seguir contando con el LSI |
| Reset por watchdog o brown-out a mitad de la cuenta | Con la política del documento (aborta) → P3. Si reiniciara la cuenta → P4 | Pasa a P3 |
| Energía baja → el iniciador tarda más en funcionar | Retardo de milisegundos, no llega al ±5 % | ≈ 0 |

**P2 ≈ P4 ≈ 10⁻⁵ a 10⁻⁴** con T programable, y ~10⁻⁹ con T fija en firmware. Son términos del proceso, no de la electrónica.

## 5. P3 — No activa

### 5.1 Contribuciones

| Fuente | Probabilidad | Comentario |
|---|---|---|
| A. Fallas latentes en almacenamiento (2 años) | **~1,5 × 10⁻⁴** | ~85 % de las fallas de §2 terminan en P3 |
| B. Escapes de fabricación (después del banco) | 10⁻⁵ a 10⁻⁴ | Juntas marginales que pasan la prueba pero se abren por choque o ciclos térmicos |
| C. Energía insuficiente (paramétrica) | **depende del I²t del iniciador** (§5.3) | 5 × 10⁻⁷ si pide 2 A²·ms; 4 × 10⁻² si pide 5 A²·ms |
| D. Cristal que no arranca en frío o dañado por choque | a medir | Si el choque del lanzamiento supera lo especificado para el cristal de diapasón, puede ser el término dominante |
| D. Aborto en falso (umbral de V_CF muy alto, brown-out durante el disparo, watchdog mal ajustado) | sistemático | Se acota por ensayo en temperatura |
| Iniciador mismo | según su hoja de datos | Típicamente se especifica el all-fire al 99,9 % con 95 % de confianza; con 1,5–2× de margen sobre esa corriente la probabilidad baja varios órdenes |
| Pulso de 12 V ausente, corto o débil | fuera del alcance | Es del sistema que entrega t0 |

**P3 estimado (electrónica): ~2 × 10⁻⁴**, o sea confiabilidad ≈ 0,9998 a 2 años de almacenamiento. Se le suma la del iniciador y la del pulso de entrada.

### 5.2 Fallas de resistores: la mayoría son seguras

| Resistor abierto | Efecto |
|---|---|
| R1 (100 k, LINE_SENSE alto) | La línea se lee como 0 V → entra en modo programación → nunca dispara (P3, seguro) |
| R2 (22 k, LINE_SENSE bajo) | La línea se lee alta → modo retardo normal (sin efecto) |
| R3 / R4 (divisor de V_CF) | Lectura de V_CF en 0 o en tope → aborta (P3) o dispara sin medir energía |
| **R5 / R6 (pull-down de gate)** | Gate flotante: **falla latente de P1**. Sola no dispara, pero elimina la defensa contra el acople dV/dt y contra el estado indefinido del pin en el arranque |
| R_bleed | Sin efecto en la demanda. Latente: C_F queda cargado si no hubo disparo |

### 5.3 Margen de energía (Monte Carlo, peor caso t2 = 40 s)

Supuestos: pulso de 10,8–13,2 V, caída de D1 de 0,35–0,5 V, C_F = 330 µF ±20 % (3σ) × 0,88–1,0 por frío, consumo + fuga de 5–25 µA, puente de 1–2 Ω, 2 × R_DS(on) de 35–60 mΩ, ESR de 25–100 mΩ (frío). I²t entregado = V_f² · C / (2 · R_total).

| Resultado | Valor |
|---|---|
| V(C_F) a 40 s: mediana / percentil 0,1 % | 9,6 V / 7,0 V |
| I²t entregado: mediana | 8,6 A²·ms |
| I²t entregado: percentil 1 % / 0,1 % / mínimo | 4,2 / 3,5 / ~3,0 A²·ms |
| Corriente de pico mínima | 2,9 A |

| I²t que pide el iniciador | P3 por energía |
|---|---|
| 2 A²·ms | 5 × 10⁻⁷ |
| 3 A²·ms | 1,3 × 10⁻⁴ |
| 5 A²·ms | 3,9 × 10⁻² |
| 8 A²·ms | 0,40 |
| 10 A²·ms | 0,69 |

**C_F = 330 µF solo sirve si el iniciador pide ≤ 2 A²·ms.** Para 10 A²·ms hacen falta ~1000 µF (el §5.2 del documento recomienda 560 µF; con frío, tolerancia y la caída a 40 s, no alcanza).

Nota de unidades: la tabla del §5.2 del documento original escribe "mA²·s", pero los valores de C_F que da (75 µF para 2, 370 µF para 10) corresponden a **A²·ms** (= 10⁻³ A²·s). Conviene corregirlo antes de pedirle el dato al fabricante.

## 6. Sensibilidad: qué mueve los números

| Si cambia… | Efecto |
|---|---|
| Tiempo de almacenamiento de 2 a 10 años | P3 latente × 5 (~7 × 10⁻⁴); P1 por LDO × 5 |
| I²t del iniciador de 2 a 5 A²·ms | P3 pasa de ~2 × 10⁻⁴ a ~4 × 10⁻²: domina todo |
| T fija en lugar de programable | P2 y P4 bajan de 10⁻⁵–10⁻⁴ a ~10⁻⁹ |
| El banco prueba cada llave por separado | Elimina el camino "corto de fábrica + corto en almacenamiento" de P1 |
| Choque del lanzamiento por encima de lo que aguanta el cristal | P3 puede subir a valores de 10⁻³ o más: hay que ensayarlo |

## 7. Mejoras que bajan las probabilidades

En orden de impacto por costo:

1. **Clamp de VDD** (zener o TVS de 3,6 V en VDD, o LDO con protección) y **resistor serie de 1 kΩ + zener de 5,1 V en cada gate.** Corta el camino dominante de P1: aunque el MCU se dañe, las gates no ven 11 V. Costo < 0,02 USD.
2. **Pull-downs de gate de 10 kΩ** en lugar de 100 kΩ, o un capacitor de 4,7 nF entre gate y source. Baja el acople dV/dt de 1,3 V a 0,13 V. Consumo extra solo durante los 20 ms del disparo (2,5 V / 10 kΩ = 250 µA). Medir el flanco real con osciloscopio.
3. **Enclavamiento de t1 por hardware, independiente del MCU.** Por ejemplo, la alimentación de la gate de Q2 pasa por una red RC + comparador (o un supervisor con retardo) que no habilita antes de ~6 s ±30 % (4,2–7,8 s). Nunca bloquea un disparo legítimo (t2 ≥ 10 s) y hace que P1 requiera dos fallas independientes también para los errores de firmware. Es la mejora estructural más importante si P1 se quiere demostrar < 10⁻⁹.
4. **Banco de prueba con cada llave por separado**: un comando de firmware de prueba enciende solo FIRE_A, después solo FIRE_B (no debe circular corriente por la carga de 1,5 Ω), y después las dos. Detecta MOSFET en corto latentes. Hacerlo siempre sin el iniciador conectado.
5. **Control cruzado de T** (variante B): el valor viene de la orden de trabajo en forma legible por máquina, el programador lo graba, lo relee y lo compara, y se registra junto al número de serie. Si la aplicación lo permite, limitar el rango de T aceptado por el firmware al uso concreto.
6. **Evaluar quitar el cristal.** Con ±5 % alcanza un oscilador interno calibrado periódicamente contra el HSI16 (despertando unos milisegundos cada segundo). Desaparecen los modos de falla del cristal (no arranque en frío, choque, arranque lento de 0,5–3 s), que son una parte importante de P3. Hay que confirmar la deriva del HSI16 en la hoja de datos y el consumo de los despertares en el presupuesto de carga.
7. **Dimensionar C_F con el I²t real**, con t2 = 40 s, frío y tolerancia, y apuntar a ≥ 1,5–2× del all-fire del iniciador.
8. **Firmware: la falla de LSE aborta**, nunca pasa a contar con el LSI.

## 8. Datos que faltan para cerrar los números

| Dato | Afecta |
|---|---|
| I²t de all-fire del iniciador (con media y desvío, o el dato probit del fabricante) y corriente de no-activación | P3 (dominante), y si el acople dV/dt llega a ser P1 |
| Tiempo de almacenamiento esperado y temperatura de almacenamiento | P3 y P1 latentes (lineal) |
| Perfil de choque y vibración en el uso | Cristal y juntas → P3 |
| Forma real del pulso de 12 V: flanco, impedancia de la fuente, rebotes | Acople dV/dt → P1; carga de C_F → P3 |
| Ambiente electromagnético (RF, ESD, descargas) | P1 por EMI/EOS |
| Si T se programa en campo o en fábrica, y quién lo elige | P2 y P4 |

## 9. Ensayos recomendados para validar el análisis

| Ensayo | Muestra | Qué valida |
|---|---|---|
| Flanco de carga con fuente rígida, midiendo V_gs de Q1 y Q2 y la corriente por la carga simulada | 5 placas, −30 / 25 / 70 °C | Acople dV/dt (P1) |
| Sobretensión forzada en VDD (simular LDO en corto) y ESD en la línea según IEC 61000-4-2 | 5 placas (destructivo) | Causa común de P1 |
| T medido en cámara de −40 a +70 °C, en los extremos de T | 30 placas | Error temporal (P2 / P4) |
| Disparo con t2 = 40 s, a −30 °C, con el C_F de menor capacidad del lote | 30 placas | Margen de energía (P3) |
| Choque y vibración según el perfil de uso, y después la prueba funcional | 30 placas | Cristal y juntas (P3) |
| Envejecimiento acelerado (85 °C / 85 % HR, 1000 h) y prueba funcional | 30 placas | Fallas latentes (P3) |

Con 30 placas sin fallas solo se demuestra P < 10 % con 95 % de confianza (regla de 3/n). Los ensayos validan mecanismos y márgenes; las probabilidades bajas (10⁻⁴ y menores) salen del análisis, no del ensayo.

---

El script del Monte Carlo usado en §4.1 y §5.3 está en `retardo/montecarlo_fallos.py`.
