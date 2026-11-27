# Sistema de retardo electrónico autoalimentado

Documento técnico del sistema de retardo electrónico autoalimentado: función, núcleo conceptual, diseño, presupuesto de energía, firmware, programación, alternativas evaluadas y costos de fabricación.

## 1. Función

Sistema sin batería que:

1. Recibe **un único pulso de 12 V de 300–500 ms**.
2. Almacena esa energía en capacitores.
3. Espera un tiempo **T** (fijo de diseño o programable).
4. Activa una carga de baja resistencia (puente de 1–2 Ω) durante unos 20 ms, entregando la corriente de disparo desde el capacitor.

Objetivo de precisión típico: **±100 ms** sobre tiempos de varios segundos, hasta **60 s**.

Dos variantes sobre el mismo hardware:

| Variante | Cómo se fija T |
|---|---|
| **A – Fija de diseño** | Constante en el firmware, o resistor de código leído por ADC. |
| **B – Programable** | Valor guardado en EEPROM/Flash, programado por los mismos 2 cables de potencia o por pads de pogo-pin. |

## 2. Núcleo conceptual para el análisis

Este es el **core** del sistema: el modelo mínimo con el que conviene empezar el análisis de seguridad, precisión y arquitectura.

### 2.1 Bloques

```
                    t0  pulso 12 V · 300 ms
                    │
     ──energía──► [ ALMACENAMIENTO DE ENERGÍA ] ──energía──► [ DRIVER ] ──energía──► [ INICIADOR ]
                    │                                              ▲
                    │                                              │ señal
                    └──energía──► [ CONTADOR ] ────────────────────┘
                    ▲
                    └── señal desde la línea de entrada
```

Diagrama conceptual (equivalente al esquema visual del núcleo):

- **Entrada (t0):** pulso de 12 V, ~300 ms.
- **Rama de energía:** almacenamiento → driver → iniciador; y almacenamiento → contador.
- **Rama de señal:** entrada → contador → driver.
- **Notas de tiempo y fallos** (detalle en §2.2 y §2.3): t1 ≈ 4 s ±5 % (no activación); t2 programable 10–40 s ±5 % (activación); modos P1–P4.

| Bloque | Rol |
|---|---|
| **Almacenamiento de energía** | Captura el pulso de 12 V y sostiene al contador y al driver hasta el disparo. |
| **Contador** | Mide el tiempo desde t0 y autoriza el disparo. |
| **Driver** | Conmuta la energía del almacenamiento hacia el iniciador (en la implementación: dos MOSFET en serie). |
| **Iniciador** | Carga de baja resistencia (puente ~1–2 Ω) que debe recibir la corriente de activación. |

Flujo de **energía**: entrada → almacenamiento → driver → iniciador (y una derivación al contador).  
Flujo de **señal**: entrada → contador → driver.

### 2.2 Tiempos de referencia

| Símbolo | Significado | Valor de trabajo (orientativo) |
|---|---|---|
| **t0** | Instantánea de llegada del pulso de 12 V (inicio de la cuenta). | Pulso ≈ 300 ms (rango de diseño 300–500 ms). |
| **t1** | Tiempo de **no activación**: ventana en la que el sistema no debe disparar. Posible mecanismo de seguridad (p. ej. un retardo mínimo o un “armado” previo). | ~4 s ±5 %. |
| **t2** | Tiempo de **activación** programable: instante en que debe disparar el driver. | 10–40 s ±5 %. |

En la implementación electrónica recomendada (§4 en adelante), t1 y t2 se pueden materializar en firmware (no activar antes de t1; disparar en t2) o, en parte, en hardware (doble llave, umbral de tensión, CRC).

### 2.3 Modos de fallo a cuantificar

Cualquier diseño del núcleo debe acotar estas cuatro probabilidades (o demostrarlas despreciables por construcción):

| Código | Modo de fallo | Interpretación |
|---|---|---|
| **P1** | Activa **antes de t1** | Disparo prematuro en la ventana de no activación. El más crítico. |
| **P2** | Activa **entre t1 y t2** | Disparo anticipado respecto del tiempo programado, pero fuera de la ventana mínima. |
| **P3** | **No activa después de t2** | Fallo de no-disparo (energía insuficiente, driver abierto, iniciador fuera de especificación, aborto por tensión baja). |
| **P4** | Activa **después de t2** | Disparo tardío (reloj lento, reset intermedio, compensación de arranque mal hecha). |

Orden de severidad habitual para el análisis: **P1 ≫ P2 ≈ P4 > P3** (el prematuro suele ser peor que el silencio o el atraso). Hay que fijar la política de sistema si V(C_F) está baja en t2: intentar igual (riesgo de P3/P4) o abortar (aceptar P3).

### 2.4 Cómo se mapea el núcleo al hardware de este documento

| Bloque del núcleo | Implementación propuesta |
|---|---|
| Almacenamiento | C_F (polímero) + D1 + R_bleed; C_loc + LDO para el contador |
| Contador | MCU + cristal 32,768 kHz (o resonador / discreto / RC según alternativa) |
| Driver | Q1 y Q2 en serie, pines FIRE_A / FIRE_B, pull-downs 100 kΩ |
| Iniciador | Carga R ≈ 1–2 Ω; dimensión de C_F según I²t |
| t1 (no activación) | Firmware: no subir gates antes de t1; opcionalmente un bit de “armado” |
| t2 (activación) | EEPROM/constante T; secuencia FIRE_B → FIRE_A ≈ 20 ms |
| Mitigación de P1 | Doble llave, pins en bajo al reset, BOR/watchdog sin reiniciar cuenta, modo programación a 5 V bloqueado |
| Mitigación de P3 | Margen de energía en C_F, medición de V(C_F), banco de prueba 100 % |
| Mitigación de P2/P4 | Base de tiempo de cristal + corrección de arranque; ensayo térmico de T |

El resto del documento detalla el circuito, el presupuesto de energía, el firmware y los costos de esa implementación.

## 3. Por qué no un RC analógico simple

±100 ms en 9 s es **±1,1 %** en todo el rango térmico (fácilmente −30 °C en uso). Un RC + comparador sin ajuste no llega: los capacitores grandes derivan ±10–20 % y la fuga de un electrolítico a varios segundos pesa mucho.

Un microcontrolador chico con base de tiempo estable es más chico, más barato y más exacto que una solución analógica o con contadores CMOS discretos, salvo que se exija cero software.

Referencias de base de tiempo:

- Resonador cerámico (p. ej. Murata CSTNE 4–8 MHz con capacitores integrados): ~±0,5 % inicial, ~±0,2–0,3 % por temperatura → **≈ ±0,8 % peor caso ≈ ±70 ms en 9 s**. Arranca en < 1 ms.
- Cristal de 32,768 kHz: precisión holgada (< 10 ms en 60 s con la corrección de arranque de §7), a costa de un arranque lento (0,5–3 s) que el firmware corrige.
- Oscilador interno RC del micro: ±1–2 % en temperatura → **no garantiza** ±100 ms salvo calibración individual y compensación térmica.

## 4. Arquitectura recomendada

Un solo reservorio de energía. El micro se alimenta de ese mismo capacitor a través de un diodo y un LDO de muy bajo consumo. Dos MOSFET en serie conmutan la carga.

```
12 V pulso ──TVS──R_s─┬─D1─►─┬───────────── C_F ── CARGA ── Q1 ── Q2 ── GND
                      │      │                │
                      │      R_bleed          └─D2─►─ C_loc ── LDO 2,5 V ── MCU + cristal 32 kHz
                      └── divisor ── ADC / detección de modo
```

Reglas de hardware:

1. **Dos llaves en serie** (Q1 y Q2). Cada una tiene su pull-down de gate (100 kΩ) y la maneja un pin distinto. Un MOSFET en corto o un pin glitcheado no activa la carga.
2. **D2 + C_loc** aíslan al micro durante el disparo: C_F cae, pero el micro sigue alimentado por C_loc (10 µF a ~100 µA → caída < 0,2 V en los ~20 ms de disparo).
3. **R_bleed** descarga C_F en minutos si no hubo disparo. Con 4,7 MΩ y 330 µF, τ ≈ 26 min; la pérdida de carga en 60 s es del orden de 140 µC y entra en el presupuesto.
4. **TVS (SMAJ15A) + R_s + D1 Schottky** contra sobretensión, picos y polaridad invertida.
5. El firmware mantiene los pines de disparo en bajo desde la primera instrucción y solo los activa al cumplir T y las comprobaciones de tensión y CRC.

### Asignación de pines (PIC12LF1822, referencia)

| Pata | Función |
|---|---|
| 1 VDD / 8 VSS | Alimentación 2,5–3,0 V |
| 2 RA5/T1OSI, 3 RA4/T1OSO | Cristal 32,768 kHz |
| 4 RA3 (solo entrada) | Detección de la línea (modo programación por los 2 cables) |
| 5 RA2 | FIRE_A → gate Q1 |
| 6 RA1/ICSPCLK | FIRE_B → gate Q2 (pull-down 100 kΩ) |
| 7 RA0/ICSPDAT/AN0 | Medición de V(C_F) por divisor de alta impedancia |

En el STM32L0 equivalente, LSE va en PC14/PC15 y los pines de disparo y ADC se eligen libres de esas funciones. Verificar el pinout en la hoja de datos antes de cerrar el esquemático.

La programación por pogo-pins (ICSP/SWD) se hace con C_F descargado y sin la carga conectada.

## 5. Presupuesto de energía

### 5.1 Lo que pide la carga (valores típicos; hay que medirlos)

- Resistencia del puente: 1–2 Ω.
- Corriente de no-activación: ~0,2–0,25 A (umbral que no debe superarse fuera del disparo).
- Corriente de activación segura: ~0,6–1 A durante algunos milisegundos.
- Energía: unos pocos mJ.
- Dato que define C_F: constante de acción **I²t** del fabricante, junto con R.

### 5.2 Banco de disparo C_F

Energía almacenada con 1000 µF a 11,3 V:

\[
\frac{1}{2} C V^2 \approx 64\,\text{mJ}
\]

Es 10–20× lo típico. Con R total ≈ 2 Ω (puente + 2 MOSFET + ESR), τ ≈ 2 ms y la corriente inicial es de varios amperes, por encima de 1 A durante unos milisegundos. Margen amplio.

En frío (−30 °C) un electrolítico común pierde capacidad y su ESR sube 5–10×. Usar **aluminio-polímero, híbrido o tantalio-polímero**, tensión nominal **25 V**, trabajando a ≤ 50 % de esa tensión. Si el C_F necesario es ≤ 100 µF, un banco de MLCC X7R (descontando la pérdida por DC bias) es más robusto y tiene fuga despreciable.

Fórmula de dimensionado, con margen ×1,5–2:

\[
C_F \ge \frac{2 \cdot R_{\text{puente}} \cdot (I^2 t)}{V_{\text{final}}^2}
\]

| Carga de ejemplo | C_F mínimo a 9 V | Recomendado |
|---|---|---|
| R = 1,5 Ω, I²t = 2 mA²·s | 75 µF | 150 µF |
| R = 1,5 Ω, I²t = 10 mA²·s | 370 µF | 560 µF |

**Este dato eléctrico de la carga define el resto del diseño.**

### 5.3 Consumo de lógica hasta 60 s

Micro en sueño con Timer1 y cristal de 32,768 kHz (~1–2 µA). Un cristal de MHz gasta ~0,3–0,5 mA y en 60 s pediría ~25 mC, imposible de cargar con un pulso corto.

| Consumo | Corriente | Carga en 60 s |
|---|---|---|
| Arranque del cristal (despierto a ~31 kHz, hasta 3 s) | ~15 µA | 45 µC |
| Sueño con Timer1 + cristal | ~1–2 µA | 120 µC |
| LDO | ~1 µA | 60 µC |
| Divisor de medición (~10 MΩ) | ~1 µA | 60 µC |
| R_bleed 4,7 MΩ | ~2,4 µA | 140 µC |
| Fuga de C_F (polímero/tantalio a ≤ 50 % de Vnom) | ~2–5 µA | 120–300 µC |
| **Total** | | **~0,6–0,7 mC** |

Con C_F = 330 µF eso es una caída de **~2 V en 60 s** (de ~11,3 V a ~9,3 V). El disparo se calcula con la tensión al final del tiempo.

C_loc es 1–2 MLCC de 10 µF 25 V más desacople. No hace falta un segundo electrolítico de lógica: el consumo medio es de microamperes, no de miliamperes.

### 5.4 ¿Alcanza el pulso de 300–500 ms?

Sí, con margen. Para cargar C_F al ~95 % hace falta τ = R_total · C_F ≤ t_pulso / 3, donde R_total es fuente + cables + R_s + diodo.

Con 300 ms, incluso un C_F de 560 µF admite R_total de decenas de ohmios. La corriente de pico queda en el orden de cientos de miliamperes, no de decenas de amperes.

Referencia por si el pulso real fuera más corto de lo declarado:

| C_F | Pulso 1 ms: R_total máx | Pico aprox. | Pulso 10 ms: R_total máx | Pico aprox. |
|---|---|---|---|---|
| 150 µF | 2,2 Ω | ~5 A | 22 Ω | ~0,5 A |
| 330 µF | 1,0 Ω | ~11 A | 10 Ω | ~1,1 A |
| 560 µF | 0,6 Ω | ~19 A | 6 Ω | ~1,9 A |

- Con **300–500 ms** cualquier fuente de 12 V razonable alcanza.
- D1 Schottky de pico alto (SS34, I_FSM ≥ 80 A). R_s de 0,1–0,5 Ω tipo pulso, o ninguno si el cable ya limita.
- Si la carga quedó incompleta, el micro mide V(C_F) al arrancar y aplica la política definida: abortar o disparar igual. Esa política es de sistema (qué es peor: no activar, o activar tarde) y hay que fijarla antes del firmware definitivo.

## 6. BOM de producción (SMD, piezas habituales en LCSC)

Precios en USD por unidad a 1000, consulta de referencia 04/11/2026. "base" = pieza básica de JLCPCB (sin cargo de carga); "ext" = extendida. Re-cotizar al pedir.

| Ref | Pieza | Código LCSC | Tipo | Cant. | USD c/u @1000 | Subtotal |
|---|---|---|---|---|---|---|
| U1 | STM32L010F4P6 (TSSOP-20) | C529415 | ext | 1 | 0,697 | 0,697 |
| (U1 alt.) | STM32L011F4U6TR (QFN-20 3×3) | C329283 | ext | (1) | (0,951) | — |
| Y1 | Cristal 32,768 kHz 7 pF ±20 ppm, 3215 (SC-32S) | C97604 | ext | 1 | 0,111 | 0,111 |
| C1, C2 | 10 pF C0G 0402 (carga del cristal) | C32949 | base | 2 | ~0,0015 | 0,003 |
| U2 | LDO HT7525S 2,5 V, 36 V máx., ~2 µA (SOT-23) | C22466410 | ext | 1 | 0,029 | 0,029 |
| Q1, Q2 | AO3400A (SOT-23) | C20917 | base | 2 | 0,056 | 0,111 |
| Q3 | 2N7002 (respuesta de corriente al programador) | C8545 | base | 1 | 0,013 | 0,013 |
| D1 | SS34 (SMA) | C8678 | base | 1 | 0,025 | 0,025 |
| D2 | BAT54WS (SOD-323) | C191198 | ext | 1 | 0,010 | 0,010 |
| TVS | SMAJ15A (SMA) | C86819 | ext | 1 | 0,030 | 0,030 |
| C_F | Aluminio-polímero 330 µF 25 V, SMD 6,3×9 mm, ~25 mΩ | C54321572 | ext | 1 | 0,125 | 0,125 |
| C_loc | 10 µF 25 V X5R 0805 | C15850 | base | 1 | 0,030 | 0,030 |
| C | 1 µF 25 V 0402 | C52923 | base | 2 | 0,005 | 0,010 |
| C | 100 nF 0402 | C1525 | base | 1 | 0,002 | 0,002 |
| R | 0402 (10 MΩ, 4,7 MΩ, 100 k, 22 k, 1 k y afines) | varios | base/ext | ~9 | ~0,0012 | 0,011 |
| | **Total materiales** | | | | | **≈ 1,21 USD** (QFN ≈ 1,46) |

Notas de BOM:

- Medir la fuga real de C_F a ~11 V durante 60 s. Alternativa de marca si la china no pasa: tantalio-polímero (p. ej. KEMET T521, mucho más caro por µF) o Panasonic OS-CON (~1 USD el 330 µF 25 V en DigiKey). El delta es ≈ 0,9 USD/placa.
- Con cristal de 7 pF el STM32L0 puede usar el nivel de excitación bajo. Los de 12,5 pF piden más corriente.
- LDO alternativos: TPS70925, MCP1703A-2502. Requisitos: entrada ≥ 16 V, Iq ~1–2 µA, salida 2,5 V.
- Tamaño de placa estimado **~10 × 15 mm**, dominado por C_F. Una cara, para poder encapsular en resina.

### Cruce de precios (05/11/2026, 1000 u)

| Pieza | LCSC/JLC | DigiKey | Farnell |
|---|---|---|---|
| STM32L010F4P6 | 0,69 USD | ≈ 0,65 USD | ≈ 0,83 USD |
| Cristal Seiko SC-32S 7 pF ±20 ppm | 0,11 USD | ≈ 0,26 USD | — |
| AO3400A | 0,056 USD | ≈ 0,12 USD | — |
| C_F 330 µF 25 V polímero | 0,12 USD (marca china) | Panasonic 25SVF330M ≈ 1,0 USD | — |

LCSC es el piso real. Armar todo en distribuidores occidentales sube ≈ 0,3 USD sin cambiar C_F, o ≈ 1,2 USD con C_F de marca.

### Por qué este micro y no uno más barato

Requisitos: oscilador de 32,768 kHz con cristal externo que siga contando en bajo consumo (LSE / Timer1), ADC, brown-out, watchdog y memoria no volátil para T.

| Micro | Encapsulado | Notas |
|---|---|---|
| **STM32L010 / STM32L011** (recomendado) | TSSOP-14/20 o UFQFPN-20 3×3 | Stock en LCSC/JLC; LSE + temporizador en Stop ~1 µA; ADC; EEPROM de datos; ST-Link barato |
| **PIC12LF1822** | DFN-8 3×3 o SOIC-8 | Más simple; Timer1 + cristal en sueño ~1 µA; EEPROM. Menos stock en LCSC |
| CH32V003, PY32F002A | chicos y baratos | **No sirven para este diseño**: no tienen oscilador de 32 kHz con cristal |

ATtiny85 o PIC12F1822 (no LF) con cristal de MHz sirven para T cortos y series chicas, pero no para 60 s con un pulso de carga limitado: el consumo despierto es demasiado alto.

## 7. Firmware

```c
// Pseudocódigo — variantes A y B
main() {
    pins_fire_low();                       // Q1 y Q2 apagados desde la primera instrucción

    // Base de tiempo:
    // 1) corre con el oscilador interno lento mientras el cristal de 32 kHz arranca;
    // 2) cuando el cristal está estable, mide el interno contra el cristal (~0,25 s)
    //    y corrige retroactivamente el tiempo ya transcurrido;
    // 3) a partir de ahí cuenta con el cristal, durmiendo entre interrupciones.
    clock_init_con_correccion();
    if (cristal_no_arranzo) abortar_y_descargar();

    if (V_linea < umbral_programacion)     // ~5–6 V → nunca dispara
        return programar_T();

    T = leer_T_eeprom_con_CRC();           // variante A: constante
    if (!crc_ok || T fuera de rango) abortar_y_descargar();

    if (V_CF() < V_MIN_ARMADO) abortar_y_descargar();

    esperar_hasta(T - T_compensacion);

    FIRE_B = 1; delay_us(50);
    FIRE_A = 1; delay_ms(20);
    FIRE_A = 0; FIRE_B = 0;

    descargar_resto();                     // opcional
    sleep_forever();
}
```

Reglas:

- **Nunca activar antes de T.** Ante CRC malo, oscilador caído, tensión baja o watchdog: llaves abiertas y R_bleed descarga.
- Watchdog activo. Tras reset por watchdog o brown-out el micro **no reinicia la cuenta** (lee la causa de reset y aborta), para no producir una activación tardía.
- Error esperado con cristal ±20 ppm + deriva térmica (≈ −100 ppm a −30 °C) + corrección de arranque (~0,1 % de los primeros ~3 s): **< 10 ms en 60 s**.
- Verificar resistencia a choque del cristal de diapasón de 32 kHz. Si no alcanza, usar un oscilador MEMS de 32 kHz de bajo consumo.

## 8. Programación de T por los dos cables

Separación:

- **Firmware**: uno solo, igual para todas las placas. No contiene T. Se graba por SWD/ICSP (JLCPCB en PCBA Standard, o un ST-Link / PICkit).
- **T**: dato en EEPROM con CRC. Se escribe y se lee **por los mismos 2 cables**, después del armado, incluso con la placa encapsulada.

Protocolo:

- El programador alimenta a **5 V**, nunca a 12 V. Por debajo de ~6 V el firmware entra en modo programación y **bloquea los pines de disparo**. Solo con ≥ 9 V entra en modo retardo.
- Programador → placa: modula la línea entre 5 V y ~3,5 V. C_F se mantiene gracias a D1. La placa lo lee con un divisor (100 kΩ / 22 kΩ) en un ADC.
- Placa → programador: el micro enciende Q3 (2N7002 + 1 kΩ) y consume ~5 mA en pulsos, por debajo del umbral de no-activación. El programador mide corriente.
- Se transmite T + CRC; la placa responde con lo grabado; el programador compara.

Equipo de banco o de mano: Arduino o STM32 de desarrollo + 2 transistores, pinzas a los 2 cables, perilla o teclado y un LED de OK. Costo de materiales **15–30 USD**. Operación ≈ 1 s por unidad: escribe, lee y verifica.

Flujo normal: **programar antes de conectar la carga**. Si hubiera que hacerlo con la carga conectada, a 5 V la energía en C_F es ~20 % de la de 11 V, el firmware bloquea el disparo y hay dos MOSFET apagados en serie. Igual hay que contrastarlo con la corriente de no-activación de la carga.

## 9. Alternativas evaluadas (y por qué no)

### 9.1 Contadores discretos (cero software)

Cristal de **4,194304 MHz = 2²² Hz** en un **74HC4060** (oscilador + 14 etapas) en cascada con un **74HC4040** (12 etapas). Cada salida del 4040 es una potencia de 2 en segundos exactos (Q9 = 1 s, Q10 = 2 s, Q11 = 4 s, Q12 = 8 s). El disparo es la AND de los bits que suman T (9 s = Q12 · Q9). Durante el ripple de un contador asíncrono los estados transitorios solo tienen un subconjunto de los bits anteriores, así que la AND no se activa antes de tiempo.

| | Micro + cristal | Discreto 4060 + 4040 + AND |
|---|---|---|
| Costo de silicio | ~0,10–0,70 USD | ~0,25–0,40 USD |
| Área | 1 encapsulado chico | 2 × TSSOP-16 + SOT-23-5 |
| Precisión | cristal | igual |
| Resolución | 1 ms, cualquier T | pasos de 0,5–1 s |
| Programable | EEPROM por los 2 cables | solo puentes o DIP |
| Reset seguro | BOR + watchdog internos | depende de un POR externo RC+Schmitt; si no arranca en cero, el tiempo es aleatorio |

El discreto conviene solo si se exige **cero software** y alcanzan pasos de 0,5–1 s. Es más grande y el reset al encender es su punto débil.

### 9.2 RC de precisión + comparador

\[
T = R_T C_T \ln\frac{1}{1-k}
\]

Con k = 0,8, T = 1,609 · R_T · C_T. Ejemplo: C_T = 2 µF C0G, R_T = 2,80 MΩ → T ≈ 9,01 s. Es ratiométrico (umbral y carga salen de la misma referencia).

Presupuesto de error estimado: capacitor ±1 %, divisor × sensibilidad ~2,7, temperatura, offset y fugas → **±1,5–2 % sin ajuste** (no cumple ±100 ms) y **±0,5–0,8 % con ajuste unitario** (cumple). Los nodos de varios MΩ son sensibles a humedad y flux. No hay versión programable razonable. No conviene a ninguna escala para este requisito.

### 9.3 Micro sin cristal, solo oscilador interno

Menos piezas y nada frágil al choque. Cumple ±100 ms solo con **calibración individual** (el banco manda una referencia y el micro guarda el factor) más **compensación térmica** caracterizada por lote. El residual hay que medirlo en cámara antes de darlo por bueno. Ahorra ~0,1–0,3 USD/placa a cambio de firmware y proceso de calibración más complejos. No se justifica a 1000 u/año.

### 9.4 Serie corta (~10 unidades)

Micro de 8 patas + cristal de MHz (ATtiny85 o PIC12F1822), sin calibración. Precisión de sobra, se programa con Arduino o PICkit. Piezas minoristas ~3–6 USD/placa; PCB del lote ~10–30 USD. El analógico no conviene: hay que ajustar cada placa a mano.

## 10. Fabricación y costo

### 10.1 Ensamblado de 1000 placas (JLCPCB, referencia 04/11/2026)

La programación de firmware en JLCPCB existe solo en PCBA Standard: ~8 USD de ingeniería + ~8 USD/hora, con pads SWD.

| Concepto | USD |
|---|---|
| Setup Standard (una cara) | 25,6 |
| Stencil | 8,2 |
| Carga de alimentadores (~16 piezas × 1,53) | 24,5 |
| Soldaduras SMT (~70 juntas × 1000) | ~106 |
| Fixtures, embalaje, varios | ~15 |
| Programación de firmware | ~30 |
| **Subtotal ensamblado + programación** | **≈ 210 → 0,21 USD/placa** |
| PCB 2 capas, ~10 × 15 mm, panelizado | 40–80 → 0,04–0,08/placa |

**Costo por placa terminada y programada, FOB: ≈ 1,5 USD** (≈ 1,75 con el micro QFN). No incluye flete ni impuestos de destino.

Prototipos (10 placas): PCBA Economic y programar uno mismo con ST-Link. **≈ 60–90 USD** el lote con piezas y PCB.

### 10.2 Puesto en Argentina, lote de 1000 (estimación 11/2026)

| Concepto | USD |
|---|---|
| Piezas (1,21 × 1000) + ~3 % de merma | ~1 250 |
| Ensamblado + programación de firmware | ~210 |
| PCB | ~60 |
| Comisión de pago (0–4 %) | 0–60 |
| **FOB** | **≈ 1 520–1 580** |
| DHL, 2,5–3 kg | 50–90 |
| **CIF** | **≈ 1 600–1 650** |

Es importación comercial (no courier de uso personal): régimen general con despachante.

| Concepto | ¿Se recupera? | USD sobre CIF 1 600 |
|---|---|---|
| Derecho de importación 0–20 % (la posición la fija el despachante) | No | 0–320 |
| Tasa de estadística 3 % | No | ~48 |
| Despachante + depósito | No | 250–450 |
| IVA 21 % | Sí, crédito fiscal | ~340–415 |
| Percepción IVA adicional 20 % | Sí, a cuenta | ~330–395 |
| Percepción Ganancias 6 % | Sí, a cuenta | ~100–120 |
| Percepción IIBB ~2,5 % | Sí, a cuenta | ~40–50 |

| | Total USD | Por placa |
|---|---|---|
| **Costo real (no recuperable)** | **≈ 1 900–2 420** | **≈ 1,9–2,4** |
| Desembolso inicial (incluye impuestos recuperables) | ≈ 2 700–3 400 | ≈ 2,7–3,4 |

Central (derecho 16 %, despachante 350): **≈ 2 250 USD → 2,25 USD por placa** terminada, con firmware grabado y nacionalizada.

Desglose para otros tamaños de pedido (mismos supuestos):

| | USD |
|---|---|
| Fijos por pedido (setup, carga, ingeniería de programación, envío, despachante) | ≈ 480 |
| Variables por placa (piezas, soldadura, PCB, programación, derechos y tasa) | ≈ 1,74 |

| Pedido | Costo por placa |
|---|---|
| 1000 | ≈ 2,2 USD |
| 2000 | ≈ 2,0 USD |
| 5000 | ≈ 1,8 USD |

### 10.3 Lote de 10 000

| Concepto | USD |
|---|---|
| Piezas 1,206 × 10 000 + ~3 % merma | ~12 400 |
| Soldaduras SMT (~700 000 juntas) | ~865 |
| Setup + stencil + carga | ~60 |
| PCB (~250 paneles) | ~250 |
| Programación de firmware (~17 h) | ~140 |
| Embalaje y comisión | ~100–400 |
| **FOB** | **≈ 13 800–14 100** |
| DHL ~20–25 kg | ~300–450 |
| **CIF** | **≈ 14 300** |
| Derecho (central 16 %) + estadística 3 % + despachante | ~3 200 |
| **Puesto en Argentina, no recuperable** | **≈ 17 600** (rango 15 300–18 300) |
| IVA + percepciones a adelantar (recuperables) | ≈ 7 600–9 100 |

Por unidad: puesta en Argentina **1,53–1,83 USD** (central 1,76) + resina/etiqueta/ensayo/programación de T (~0,3) + rechazos (~0,05) → **costo directo ≈ 2,1 USD**.

Ahorro posible: comprar el micro a un distribuidor de ST a 10 000 u (~0,45–0,55 USD en lugar de 0,70) y consignarlo a JLC: −1 500 a −2 500 USD.

### 10.4 Banco de prueba

Base con pogo-pins y un microcontrolador con cristal. En ~15 s por placa:

1. Programa el firmware (si no lo hizo el ensamblador) y escribe T.
2. Aplica el pulso de 12 V real (300–500 ms).
3. Mide T sobre un resistor de 1,5 Ω que simula la carga, y la corriente de disparo.
4. Marca aprobado/rechazado y registra número de serie, T medido y fecha.

Costo de materiales del banco: **100–300 USD**.

### 10.5 Dónde fabricar

Pedir la misma cotización (Gerber, BOM, posiciones, .hex), para 1000 y 10 000, con programación y prueba funcional, a JLCPCB, PCBWay, NextPCB y, si se ensambla en Argentina, a ELTECH (u otro EMS local con SMT, programación y trazabilidad). El ensamblado es < 10 % del costo puesto en destino; el peso está en las piezas y en la importación. Para un componente de conmutación de energía, la trazabilidad del lote pesa tanto como el precio unitario.

JLCPCB es la base de estos números porque publica tarifas. PCBWay, Seeed, NextPCB y similares cotizan sobre archivos; no hay tarifa pública equivalente para comparar sin el diseño cerrado.

## 11. Checklist técnico antes de cerrar el esquemático

- [ ] R del puente, corriente de no-activación, corriente de activación, tiempo e I²t de la carga real.
- [ ] Tensión, duración y corriente disponible del pulso de 12 V, y rebotes.
- [ ] Política si V(C_F) está baja en el instante de disparar: abortar o disparar igual.
- [ ] Pull-down de 100 kΩ en cada gate; pines en bajo por defecto.
- [ ] Fuga medida de C_F a ~11 V y a −30 °C, en el modelo elegido.
- [ ] Arranque del cristal de 32 kHz en frío y resistencia a choque; plan B con MEMS si no pasa.
- [ ] Inmunidad del cable de la carga: corto, trenzado, plano de masa, TVS junto al conector.
- [ ] Ensayo térmico (−40 °C a +70 °C) de T en una muestra; verificar ±100 ms con margen.
- [ ] Ensayo de vibración y choque del conjunto.
- [ ] Barniz conformal o resina (humedad sobre los nodos de alta impedancia).
- [ ] 100 % de las placas en el banco, con carga simulada de 1,5 Ω, midiendo T y corriente.
- [ ] Stock y pinout de LSE (PC14/PC15) confirmados en LCSC y en la hoja de datos del STM32L0 elegido.

## 12. Datos eléctricos pendientes

Lo que todavía hay que cerrar con medición o hoja de datos:

1. Especificación de la carga: R e I²t (y corrientes de no-activación / activación).
2. Forma real del pulso de 12 V: tensión, duración, corriente disponible y rebotes.
3. Fuga real de C_F a ~11 V durante 60 s (y en frío).

Con el pulso declarado de 300–500 ms la carga del capacitor deja de ser el punto crítico; el punto crítico pasa a ser el tamaño de C_F que exija la carga y la fuga de ese capacitor a 60 s.
