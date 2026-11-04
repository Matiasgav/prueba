# Retardador electrónico autoalimentado para bengala antigranizo

Diseño conceptual de una placa que recibe **un único pulso de 12 V de pocos ms**,
guarda esa energía y, pasado un tiempo **T** (p. ej. 9,0 s ± 100 ms), dispara el
iniciador (puente/filamento del e-match). No tiene batería.

Dos variantes sobre **el mismo hardware**:

| Variante | Cómo se fija T |
|---|---|
| **A – Fija de diseño** | Constante en el firmware (o un resistor de código leído por ADC). |
| **B – Programable** | T guardado en EEPROM/Flash, programado por los mismos 2 cables o por pads de pogo-pin. |

---

## 1. Por qué no un RC analógico

±100 ms en 9 s es **±1,1 %**, en todo el rango térmico (en vuelo se ven fácilmente
−30 °C). Un RC + comparador no llega: los capacitores grandes derivan ±10–20 % y la
fuga de un electrolítico a 9 s pesa mucho. Un **microcontrolador chico con
resonador cerámico** es más barato, más chico y más exacto que cualquier solución
analógica o con contadores CMOS discretos.

- Resonador cerámico (p. ej. Murata CSTNE 4–8 MHz con capacitores integrados):
  ~±0,5 % inicial, ~±0,2–0,3 % por temperatura → **≈ ±0,8 % peor caso ≈ ±70 ms**.
  Arranca en < 1 ms (un cristal de 32 kHz tarda 0,3–2 s en arrancar y en frío más:
  no sirve aquí).
- Oscilador interno RC del micro: ±1–2 % en temperatura → **no garantiza** ±100 ms
  salvo calibración individual (ver §6). Se puede usar como opción de costo mínimo.

---

## 2. Diagrama de bloques

```
 12 V pulso ──┬─[F1/R_in]─┬─D1─►──────────┬──────────── C_F (banco de disparo, ~1000 µF)
              │           │               │                     │
           TVS 15 V       │               R_bleed 220k          E-MATCH (puente ~1–2 Ω)
              │           │               │                     │
             GND          └─D2─►─┬── C_L (lógica, ~470 µF)       Q1 (N-MOS, Vgs lógico)
                                 │                               │
                                 LDO 3,0 V (Iq < 2 µA)            Q2 (N-MOS en serie)
                                 │                               │
                                 MCU + resonador ── FIRE_A ──────┘ (gate de Q1)
                                     │           ── FIRE_B ─────── (gate de Q2)
                                     ├─ ADC: divisor de V(C_F) y V(entrada)
                                     └─ línea de programación (variante B)
```

Puntos clave:

1. **Dos reservorios separados por diodos** (D1, D2 Schottky): el disparo, que
   tira varios amperes, no puede “voltear” al micro.
2. **Dos llaves en serie** (Q1 y Q2), cada una con su pull-down de gate y manejada
   por un pin distinto: un solo MOSFET en corto o un pin glitcheado no dispara.
3. **R_bleed** descarga C_F en pocos minutos si algo falla y no hubo disparo
   (τ = 220 kΩ × 1000 µF ≈ 220 s; en 9 s solo pierde ~4 % de tensión).
4. **TVS + resistor/fusible de entrada** contra sobretensión y ESD; diodo serie
   protege contra polaridad invertida.

---

## 3. Presupuesto de energía (dimensionado)

### 3.1 Lo que pide el iniciador (valores típicos, **verificar con el fabricante**)

- Resistencia del puente: 1–2 Ω
- Corriente de no-fuego: ~0,2–0,25 A
- Corriente de todo-fuego: ~0,6–1 A durante algunos ms
- Energía: unos pocos mJ

### 3.2 Banco de disparo C_F

Con C_F = 1000 µF cargado a ~11,3 V (12 V − Schottky):

- Energía almacenada: ½·C·V² ≈ **64 mJ** (10–20× lo necesario).
- Con R total ≈ 2 Ω (puente + 2 MOSFET + ESR): τ = 2 ms, corriente inicial ≈ 5 A;
  supera 1 A durante ~3 ms. Margen amplio.
- En frío (−30 °C) un electrolítico común pierde capacidad y su ESR sube 5–10×:
  usar **aluminio-polímero o híbrido** (o banco de MLCC X7R contando la
  degradación por DC bias). Tensión nominal **25 V**.

### 3.3 Reservorio de lógica C_L

- Consumo del micro con resonador a 4 MHz y periféricos mínimos: ~0,3–0,6 mA.
- Carga necesaria: 9 s × 0,5 mA ≈ 4,5 mC (+ margen ×2 → 9 mC).
- Tensión útil: de 11,3 V hasta 3,3 V (dropout del LDO) → ΔV = 8 V.
- C_L = Q/ΔV ≈ 9 mC / 8 V ≈ **1100 µF**; con 470 µF alcanza si el micro duerme
  entre ticks (modo IDLE con timer corriendo, ~0,2 mA).

Para retardos más largos (30–60 s) escalar C_L o bajar el consumo.

### 3.4 ¿Alcanza un pulso de “pocos ms” para cargar todo?

**Este es el punto crítico del diseño.** La carga total es:

Q = (C_F + C_L) · V ≈ 1,5 mF × 11,3 V ≈ **17 mC**

Con un pulso de 5 ms hace falta una corriente media de ~3,4 A; con 2 ms, ~8,5 A.
Eso depende de la fuente y del cableado al lanzador. Recomendaciones:

- Medir/definir **duración del pulso y corriente que entrega la fuente**.
- Si es posible, estirar el pulso a **20–50 ms** (quita todo el estrés: 0,4–0,9 A).
- Poner un resistor de entrada de bajo valor (0,5–1 Ω, tipo pulso) para limitar el
  pico y proteger contactos.
- El firmware mide V(C_F) al arrancar y antes de disparar (ver §5).

---

## 4. Componentes sugeridos (orientativos)

| Ref | Función | Ejemplo | Costo aprox. (volumen) |
|---|---|---|---|
| U1 | MCU con osc. externo HS/XT y EEPROM | PIC12F1822 / PIC16F15313 (SOIC-8), o STM32C011 (SO-8) | 0,35–0,60 USD |
| Y1 | Resonador cerámico 4 MHz con caps integrados | Murata CSTNE4M00G55 | 0,10–0,15 |
| U2 | LDO 3,0 V, Iq bajo, entrada 16 V+ | MCP1700-3002 / TPS7A02 / HT7530 | 0,05–0,20 |
| Q1, Q2 | N-MOSFET Vgs(th) bajo, Rds < 50 mΩ a 2,5 V | AO3400A / SI2302 (SOT-23) | 2 × 0,03 |
| C_F | 1000 µF 25 V polímero/híbrido | — | 0,30–0,60 |
| C_L | 470–1000 µF 25 V polímero/híbrido | — | 0,20–0,40 |
| D1, D2, D3 | Schottky 1–3 A | SS14 / B340 | 3 × 0,02 |
| TVS | SMBJ15A | — | 0,05 |
| Varios | R, C 0402/0603, pull-downs 100 k de gate | — | 0,05 |

**Total BOM ≈ 1,5–2,5 USD** + PCB. Tamaño estimado **~15 × 30 mm**, dominado por
los capacitores (si el formato es cilíndrico, se puede hacer una placa angosta
con los capacitores acostados).

---

## 5. Firmware (lógica de seguridad)

```c
// Pseudocódigo – variante A y B
main() {
    t0 = 0;                          // el tiempo cuenta desde el reset por POR
    clock_init_resonator();          // si el resonador no arranca en X ms → NO disparar
    pins_fire_low();                 // Q1 y Q2 apagados desde la primera instrucción

    if (modo_programacion_detectado())   // variante B: Vin entre 4,5 y 6 V → nunca dispara
        return programar();

    T = leer_T_eeprom_con_CRC();     // variante A: constante
    if (!crc_ok || T fuera de rango) abortar_y_descargar();

    if (V_CF() < V_MIN_ARMADO) abortar_y_descargar();  // pulso insuficiente

    esperar_hasta(T - T_COMPENSACION);   // compensa arranque POR + tiempo de firmware

    // Disparo con secuencia: requiere dos pines y orden específico
    FIRE_B = 1; delay_us(50);
    FIRE_A = 1; delay_ms(20);        // 20 ms de corriente, sobrado para el puente
    FIRE_A = 0; FIRE_B = 0;

    descargar_resto();               // opcional: dejar C_F descargado
    sleep_forever();
}
```

Reglas:

- **Nunca disparar antes de T.** Ante cualquier anomalía (CRC, oscilador, tensión
  baja, watchdog) el sistema queda en estado seguro: llaves abiertas y R_bleed
  descarga.
- Watchdog activo; tras un reset por watchdog/brown-out el micro **no reinicia la
  cuenta** (detecta la causa de reset y aborta), para no producir un disparo tardío.
- Decidir qué hacer si V(C_F) está baja en el momento de disparar: intentarlo igual
  o abortar. Es una decisión de seguridad del sistema completo (¿qué es peor, una
  bengala que no enciende y cae, o una que enciende tarde?).

---

## 6. Variante B: cómo programar T sin agregar cables

Opción 1 – **pads de pogo-pin** (VDD, GND, DATA/ICSP): lo más simple y barato.
Se programa en fábrica antes de encapsular.

Opción 2 – **por los mismos 2 cables de disparo**:

- El programador alimenta con **5 V** (no 12 V). El firmware ve Vin < 6 V y entra
  en modo configuración, en el que **los pines de disparo nunca se activan**. Además,
  a 5 V la energía en C_F no alcanza para el todo-fuego si se elige bien el umbral.
  Aun así: **programar con el iniciador desconectado o con un puente simulado**
  siempre que se pueda.
- Datos programador→placa: modulando la tensión (5 V / 4 V).
- Datos placa→programador (lectura de verificación): modulación de consumo
  (el micro conecta una carga de ~10 mA, muy por debajo del no-fuego).
- Se guarda T + CRC en EEPROM y se lee de vuelta para verificar.

**Calibración en fábrica** (mejora la precisión o permite usar el oscilador interno):
el programador envía una referencia exacta (p. ej. un pulso de 1,000 s medido con
cristal); el micro mide cuántos ciclos propios caben y guarda el factor de
corrección. Queda solo la deriva térmica.

---

## 7. Confiabilidad y seguridad (checklist)

- [ ] Datos reales del iniciador: R del puente, no-fuego, todo-fuego, tiempo.
- [ ] Datos reales del pulso: tensión, duración, corriente disponible, rebotes.
- [ ] Gates de Q1/Q2 con pull-down a GND (100 k) y señal en LOW por defecto.
- [ ] Prueba de inmunidad RF/ESD: el cable al e-match corto y trenzado, plano
      de masa, TVS cerca del conector.
- [ ] Ensayo en cámara térmica (−40 °C a +70 °C) midiendo T real en cada unidad
      de una muestra; verificar ±100 ms con margen.
- [ ] Ensayo de vibración/choque (lanzamiento o eyección).
- [ ] Barnizado conformal (humedad/condensación en nube).
- [ ] Ensayo de 100 % de placas en línea con carga simulada (resistor 1,5 Ω) y
      medición de T y de la corriente de disparo.
- [ ] Verificar el marco regulatorio de artículos pirotécnicos aplicable
      (en Argentina: ANMaC) y los requisitos del cliente/operador aeronáutico.

---

## 8. Próximos pasos

1. Conseguir la hoja de datos del iniciador y medir el pulso real de 12 V.
2. Prototipo en placa de desarrollo con carga simulada; medir consumo y T.
3. Elegir MCU definitivo y hacer esquemático + PCB.
4. Ensayos térmicos y de lote.

---

## 9. Alternativa sin microcontrolador: lógica discreta (contadores)

### 9.1 Idea

Un cristal de **4,194304 MHz = 2²² Hz** (valor estándar, de “reloj”) alimenta un
**74HC4060** (oscilador + 14 etapas) en cascada con un **74HC4040** (12 etapas):
26 bits en total. Con esa frecuencia, cada salida del 4040 corresponde a una
potencia de 2 en **segundos exactos**:

| Salida | Pasa a 1 por primera vez a los | Peso |
|---|---|---|
| 4040 Q8  | 0,5 s | 0,5 s |
| 4040 Q9  | 1 s   | 1 s |
| 4040 Q10 | 2 s   | 2 s |
| 4040 Q11 | 4 s   | 4 s |
| 4040 Q12 | 8 s   | 8 s |

El disparo es la **AND** de los bits que suman el tiempo deseado. La primera vez
que todos están en 1 es exactamente T:

- 9 s = 8 + 1 → `FIRE = Q12 · Q9`
- 7 s = 4 + 2 + 1 → `FIRE = Q11 · Q10 · Q9`

Es libre de glitches aun siendo contador asincrónico: durante el “ripple” los
estados transitorios solo tienen un subconjunto de los bits del valor anterior,
así que la AND no puede activarse antes de tiempo.

### 9.2 Esquema

```
VDD 3,3V ─┬─ 74HC4060 ── Q14 ──► CLK 74HC4040 ── Q9..Q12 ──┐
          │   (XTAL 4,194304 MHz)                           │
          │                                               AND (74HC21 / 1G08)
   POR: RC + Schmitt ──► MR de ambos contadores             │
                                                     ┌──────┴──────┐
                                                   Gate Q1       Gate Q2
```

- **Variante fija:** una 74LVC1G08 (SOT-23-5) con dos bits → 9 s.
- **Variante “programable” sin micro:** 74HC21 (4 entradas) + DIP o puentes de
  soldadura. Cada entrada tiene pull-up a VDD y un puente al bit Qk: puente
  abierto = bit ignorado, cerrado = bit usado. Con Q9..Q12 → 1 a 15 s en pasos
  de 1 s; sumando Q8, pasos de 0,5 s.

### 9.3 Puntos delicados

1. **Reset al encender (crítico):** si los contadores no arrancan en cero el
   tiempo es aleatorio y puede disparar enseguida. El reset por RC + Schmitt
   tiene que funcionar con cualquier forma de pulso de entrada. Es el único punto
   donde la versión discreta es *menos* segura que el micro, que tiene reset
   interno con brown-out.
2. Consumo del 74HC4060 a 4 MHz: ~0,5–1 mA → C_L ≈ 1000 µF.
3. Dos llaves en serie: Q2 puede manejarse con Q12 (armado a los 8 s) y Q1 con
   la AND. No es independiente (mismo contador), pero evita disparos antes de 8 s
   por un solo fallo en la compuerta.

### 9.4 Comparación

| | Micro (p. ej. CH32V003 / PY32F002A + cristal) | Discreto (4060 + 4040 + AND) |
|---|---|---|
| Costo de silicio | ~0,10–0,40 USD | ~0,25–0,40 USD |
| Área | 1 SOP-8 / TSSOP-20 | 2 × TSSOP-16 + SOT-23-5 |
| Precisión con cristal | ±50 ppm (~0,5 ms en 9 s) | igual |
| Resolución | 1 ms, cualquier T | potencias de 2 (0,5 s con 5 bits) |
| Programable | por cables, EEPROM, CRC | solo puentes/DIP |
| Validación | requiere validar firmware | lógica fija, fácil de auditar |
| Reset / estado seguro | BOR interno, watchdog, autochequeos | depende del POR externo |

**Conclusión:** los micros modernos cuestan lo mismo o menos que dos contadores y
ocupan menos. El discreto conviene si se quiere **cero software** (certificación
más simple, sin riesgo de bug de firmware) y alcanza con tiempos en pasos de
0,5–1 s.

---

## 10. Versión mínima: un solo chip, sin cristal, sin electrolíticos

Objetivo: menos componentes, menos soldaduras y nada que sea sensible al frío o
al golpe de lanzamiento/eyección.

### 10.1 Qué se saca y por qué

| Se elimina | Motivo |
|---|---|
| Contadores discretos | 3 chips y 46 patas contra 1 chip de 6 patas. |
| Cristal o resonador | Es la pieza más sensible al choque mecánico y la que más tarda en arrancar. |
| Electrolíticos | En frío pierden capacidad y su ESR sube; envejecen. |
| LDO (si el micro tolera la tensión o se usa un zener + R) | Una pieza menos. |

### 10.2 Cómo se mantiene ±100 ms sin cristal

1. **Oscilador interno del micro**, que no tiene piezas móviles y aguanta
   cualquier choque.
2. **Calibración individual en fábrica**, por los mismos 2 cables: el equipo de
   prueba manda una referencia exacta y el micro guarda su factor de corrección.
   Queda la deriva térmica.
3. **Compensación de temperatura** con el sensor interno del micro: la curva
   frecuencia-temperatura se caracteriza por lote en cámara térmica y se guarda
   en el firmware. Residual esperado bastante por debajo de ±1 %.
4. Para gastar poco: el micro duerme con el oscilador lento interno y se despierta
   cada ~0,5 s para medirlo contra el rápido (ya corregido). Consumo medio de
   decenas de µA en lugar de cientos.

Todo esto **hay que validarlo en cámara térmica** con el micro elegido antes de
dar por cumplida la precisión.

### 10.3 Energía

- **Lógica:** ~10–30 µA × 9 s ≈ 0,1–0,3 mC → 1 o 2 MLCC de 22 µF 25 V (contando
  la pérdida por DC bias). Sin electrolítico.
- **Disparo:** lo fija el iniciador. Para un puente de resistencia R con constante
  de acción I²t (dato del fabricante), descargando un capacitor cargado a V:

  `C ≥ 2 · R · (I²t) / V²`  (más margen ×2–3)

  Ejemplo: R = 1,5 Ω, I²t = 10 mA²·s, V = 11 V → C ≥ 250 µF → **un tantalio-polímero**
  de 330–470 µF 16–25 V (7343). Si el iniciador es más sensible, alcanza con
  MLCC y desaparece el último capacitor “grande”.

### 10.4 Lista de componentes (≈ 10 piezas)

| Ref | Pieza |
|---|---|
| U1 | MCU en SOT-23-6 o DFN 2×2 con ADC, sensor de temperatura y EEPROM/Flash (p. ej. PIC10F322 o equivalente; **verificar** el oscilador interno) |
| Q1/Q2 | MOSFET N doble en un solo SOT-23-6 (dos llaves en serie) |
| C_F | Tantalio-polímero o banco de MLCC (según §10.3) |
| C_L | 1–2 MLCC 22 µF 25 V |
| D1, D2 | Schottky doble en SOT-23 |
| TVS | SOD-123 |
| R | Pull-downs de gate, descarga de C_F, divisor de medición, zener/regulación |

Tamaño estimado **~8 × 15 mm**, con todo en una cara para poder encapsular en
resina (potting), que es lo que más suma a la robustez mecánica.

---

## 11. Alternativa analógica: RC de precisión + comparador

### 11.1 Esquema

```
 C_L ── LDO 2,5 V (Vref, Iq < 1 µA) ──┬──────────────┬──────────────┐
                                      │              │              │
                                     R_T 2,80 MΩ    R_a 1 MΩ        (alimenta comparadores)
                                      │ 0,1 %        │
                                      ├── V_C        ├── 0,8·Vref (umbral de disparo)
                                      │              R_b 1 MΩ
                                     C_T 2 µF C0G    ├── 0,6·Vref (umbral de armado)
                                      │              R_c 3 MΩ
                                     GND             GND

 Comparador A: (+) V_C, (−) 0,8·Vref → gate Q1   (dispara a T)
 Comparador B: (+) V_C, (−) 0,6·Vref → gate Q2   (arma a ~0,57·T)
```

- Tiempo: `T = R_T · C_T · ln(1/(1−k))`, con k = 0,8 → `T = 1,609 · R_T · C_T`.
  Con C_T = 2 µF y R_T = 2,80 MΩ → **T ≈ 9,01 s**.
- Es **ratiométrico**: el umbral y la carga salen de la misma Vref, así que su
  valor absoluto no importa; solo tiene que mantenerse constante 9 s.
- Consumo total ~2–3 µA → la lógica se alimenta con 1–2 MLCC.
- Comparador doble nanopower con salida push-pull e histéresis interna
  (p. ej. familia TLV70xx; verificar corriente de entrada en caliente).

### 11.2 Presupuesto de error (estimado)

| Fuente | Error en T |
|---|---|
| C_T C0G ±1 % (o ±5 % sin trimar) | ±1 % (±5 %) |
| R_T 0,1 % | ±0,1 % |
| Divisor de umbral 0,1 % (sensibilidad ×2,7 con k = 0,8) | ±0,3 % |
| Temperatura: C0G ±30 ppm/°C, R ±25 ppm/°C, ±40 °C | ±0,2 % |
| Offset del comparador (mV sobre 2 V, ×2,7) | ±0,1–0,3 % |
| Fugas (bias del comparador, superficie de la placa) a ~1 µA de carga | ±0,1–0,5 % (crece con humedad y calor) |

- **Sin ajuste:** ~±1,5–2 % → **no garantiza** ±100 ms.
- **Con ajuste en fábrica** (medir T y elegir R_T de la serie E192 o un resistor
  serie de corrección): ~±0,5–0,8 % → **cumple**.

### 11.3 Riesgos propios

1. **Fugas a varios MΩ:** humedad o condensación (que en nube es lo normal) bajan
   la resistencia superficial y adelantan o atrasan el disparo. Exige anillo de
   guarda, barniz o resina de baja fuga y lavado de flux.
2. **C_T tiene que arrancar en 0 V:** si quedó carga de un pulso anterior, el
   tiempo se acorta. Hace falta un camino de descarga cuando no hay tensión.
3. **Arranque del comparador:** por debajo de su tensión mínima la salida no está
   definida. Usar MOSFET con Vgs(th) > 1,5 V y el segundo comparador como llave
   de armado.
4. **Solo tiempo fijo:** cambiar T implica cambiar R_T (o poner puentes que
   seleccionen resistores). No hay versión programable razonable.
5. Encontrar C0G de 1 µF a 25 V: existe en 1210/1812, verificar disponibilidad;
   la alternativa es film PPS, más grande.

### 11.4 Veredicto

| | Analógico (RC + comparador) | Micro de 6 patas |
|---|---|---|
| Software | ninguno | sí |
| Piezas | ~12 (2 chips) | ~10 (1 chip) |
| Precisión | cumple solo con ajuste por unidad | cumple con calibración por cables |
| Sensibilidad a humedad | alta (nodos de MΩ) | baja |
| Tiempo programable | no (solo cambiando resistor) | sí |
| Calibración en línea | cambiar/soldar un resistor | automática por los 2 cables |

Un CMOS 555 en monoestable también funciona con pocas piezas, pero su salida
puede pulsar al encender y su precisión inicial es peor: no recomendado como
única protección contra disparo prematuro.

---

## 12. Costo comparado del núcleo de temporización

Estimación orientativa a volumen (~10 000 u), **a confirmar con cotizaciones**.
Las piezas comunes a todas las versiones (capacitor de disparo, MOSFET, TVS,
diodos, PCB) no se cuentan porque son iguales.

| | Analógico (RC + comparador) | Micro de 6–8 patas |
|---|---|---|
| Chip | comparador doble CMOS nanopower: 0,15–0,40 USD | MCU: 0,10–0,50 USD |
| Capacitor de tiempo | 2 × C0G 1 µF 25 V tolerancia ±1 %: 0,30–0,80 USD | — |
| Resistores de precisión 0,1 % | 4 × 0,01–0,03 USD | — |
| LDO / referencia | 0,05–0,10 USD | 0,05–0,10 USD (o zener) |
| **Materiales** | **~0,55–1,40 USD** | **~0,15–0,60 USD** |
| Ajuste por unidad | medir T, elegir y soldar un resistor (manual) | calibración automática por los 2 cables, en paralelo |

El ensayo final de T al 100 % es necesario en ambos casos; la diferencia es que
el analógico agrega una operación manual de retrabajo por placa.

---

## 13. Recomendación para una serie corta (~10 unidades)

Con 10 placas el costo de piezas es irrelevante; lo que pesa es el esfuerzo de
desarrollo y de ajuste. Por eso cambia la recomendación respecto de §10:

**Micro de 8 patas + cristal, sin calibración ni compensación térmica.**

- El cristal (p. ej. 4 u 8 MHz, ±50 ppm) da la precisión de sobra en todo el
  rango térmico: no hay que calibrar cada placa ni caracterizar en cámara.
- Micro sugerido: **ATtiny85** (SOIC-8, se programa con un Arduino como
  programador) o **PIC12F1822** (SOIC-8, PICkit). Ambos admiten cristal externo,
  tienen brown-out, watchdog y EEPROM.
- Pines (ATtiny85): PB3/PB4 cristal · PB0 FIRE_A · PB1 FIRE_B · PB2 (ADC1)
  medición de C_F y línea de programación · PB5 reset.
- Mismo hardware para tiempo fijo y programable (el tiempo va en EEPROM).
- Capacitor de disparo: polímero o tantalio-polímero según §10.3.
- Ensayo de cada placa: osciloscopio + resistor de 1,5 Ω como iniciador simulado.

Alternativa sin software: contadores 74HC4060 + 74HC4040 + AND con cristal de
4,194304 MHz (§9). Tampoco requiere calibración, pero es más grande, solo da
tiempos en pasos de 0,5–1 s y depende de un reset externo al encender.

El analógico (§11) no conviene en ninguna escala para este requisito: exige
ajustar cada placa a mano y es sensible a la humedad.

Costo orientativo para 10 unidades: piezas ~3–6 USD por placa a precio
minorista, PCB de fabricante en lote ~10–30 USD, programador 5–60 USD una vez.
