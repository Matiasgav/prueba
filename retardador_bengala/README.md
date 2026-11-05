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

---

## 14. Producción de ~1000 unidades por año

### 14.1 La recomendación no cambia: micro + cristal

A 1000 u/año la diferencia de materiales entre opciones es de ~0,1–0,8 USD por
placa, es decir **100–800 USD por año**. No justifica:

- la versión sin cristal (§10): exige caracterización térmica, calibración por
  unidad y firmware más complejo, a cambio de ahorrar ~0,1–0,3 USD por placa;
- el analógico (§11): ajuste manual de cada placa;
- el discreto (§9): más grande y sin tiempo programable.

Sí conviene revisar el micro: ATtiny85 (~1 USD) o PIC12F1822 (~0,6–0,8 USD) están
bien. Si hay presión de costo, evaluar un micro de 0,10–0,20 USD con soporte de
cristal externo (CH32V003, PY32F002A; verificar pinout, disponibilidad y que se
pueda calificar el proveedor).

### 14.2 Fabricación

- PCB **ensamblado por el fabricante** (SMT) en paneles, 1 o 2 lotes por año, con
  piezas elegidas del catálogo del ensamblador para evitar faltantes.
- Todas las piezas en una cara; pads de pogo-pin para programar y probar.
- Costo orientativo por placa ensamblada: **~3–5 USD** (materiales 1,5–3 USD +
  PCB y montaje 1–2 USD). Costos únicos por lote: stencil y puesta a punto
  ~20–50 USD.

### 14.3 Banco de prueba (vale la pena a este volumen)

Una base con pogo-pins y un microcontrolador con cristal que, en una sola
operación de ~15 s por placa:

1. programa el firmware y el tiempo T;
2. aplica el pulso de 12 V real;
3. mide T sobre un resistor de 1,5 Ω (iniciador simulado) y la corriente de disparo;
4. marca aprobado/rechazado y registra número de serie, T medido y fecha.

Costo estimado del banco: 100–300 USD en materiales.

### 14.4 Calidad por lote

- 100 % de placas: ensayo del banco y barniz o resina.
- Muestra por lote: ciclado térmico (−40/+70 °C), vibración/choque, y disparo de
  iniciadores reales.
- Trazabilidad: número de serie en cada placa vinculado al registro de ensayo.

---

## 15. Diseño elegido: micro simple + cristal de 32 kHz, retención hasta 60 s

### 15.1 Micro: PIC12LF1822 (Microchip)

Barato por simple, no por calidad:

- 8 patas, núcleo de 8 bits, sin periféricos innecesarios. Fabricante de primera
  línea, familia madura (en producción desde hace más de 10 años), grado de
  temperatura extendido (−40 a +125 °C), EEPROM de datos, brown-out, watchdog.
- **Versión “LF” (bajo consumo, 1,8–3,6 V)**: duerme con ~1 µA mientras el
  Timer1 cuenta un cristal de reloj de 32,768 kHz.
- Precio orientativo a 1000 u: ~0,7–0,9 USD (confirmar con distribuidor).

**Por qué cristal de 32 kHz y no de MHz:** con un cristal de 4 MHz el micro gasta
~0,3–0,5 mA; en 60 s eso son ~25 mC, imposibles de juntar en un pulso de 1 ms
(serían ~25 A). Con 32 kHz el promedio baja a unos pocos µA.

**El problema del cristal de 32 kHz** es que tarda 0,5–3 s en arrancar. Solución
por firmware, sin perder precisión:

1. Al encender, el micro corre con su oscilador interno lento (LFINTOSC, 31 kHz)
   y cuenta sus ciclos mientras espera que el cristal arranque.
2. Cuando el cristal está estable, mide el oscilador interno contra el cristal
   durante ~0,25 s y corrige retroactivamente el tiempo transcurrido.
3. A partir de ahí cuenta con el cristal, durmiendo entre interrupciones.

Error resultante: cristal ±20 ppm + deriva térmica (≈ −100 ppm a −30 °C) +
corrección del arranque (~0,1 %·3 s) → **< 10 ms en 60 s**.

A verificar: resistencia a choque del cristal de diapasón de 32 kHz (son más
frágiles que los de MHz). Si no alcanza, existe la alternativa de oscilador
MEMS de 32 kHz de bajo consumo.

### 15.2 Asignación de patas

| Pata | Función |
|---|---|
| 1 VDD / 8 VSS | Alimentación 2,5–3,0 V |
| 2 RA5/T1OSI, 3 RA4/T1OSO | Cristal 32,768 kHz |
| 4 RA3 (solo entrada) | Detección de la línea (programación por los 2 cables) |
| 5 RA2 | FIRE_A → gate Q1 |
| 6 RA1/ICSPCLK | FIRE_B → gate Q2 (pull-down 100 k) |
| 7 RA0/ICSPDAT/AN0 | Medición de V(C_F) por divisor de 10 MΩ |

Programación por pogo-pins (ICSP) se hace con C_F descargado y sin iniciador:
el pulso de programación no puede disparar porque no hay energía en C_F.

### 15.3 Esquema de energía (un solo reservorio)

```
 Línea 12 V ─TVS─R_s─┬─D1─►─┬───────────── C_F (reservorio único) ── E-MATCH ── Q1 ── Q2 ── GND
                     │      │                │
                     │      R_bleed 4,7 MΩ   └─D2─►─ C_loc 10 µF MLCC ── LDO 2,5 V ── C 1 µF ── PIC
                     └── divisor ── RA3
```

- **C_F alimenta todo**: el disparo y, a través de D2 y el LDO, al micro. El consumo
  del micro es tan bajo que casi no le resta energía al disparo.
- **D2 + C_loc** aíslan al micro: durante los ~20 ms de disparo C_F cae, pero el
  micro sigue alimentado por C_loc (10 µF a 100 µA → caída < 0,2 V).
- **LDO** de entrada hasta 16–30 V y consumo propio ~1 µA (p. ej. TPS70925 o
  MCP1703A-2502).

### 15.4 Presupuesto de carga para 60 s

| Consumo | Corriente | Carga en 60 s |
|---|---|---|
| Arranque del cristal (micro despierto a 31 kHz, hasta 3 s) | ~15 µA | 45 µC |
| Sueño con Timer1 + cristal | ~1–2 µA | 120 µC |
| LDO | ~1 µA | 60 µC |
| Divisor de medición (10 MΩ) | ~1 µA | 60 µC |
| R_bleed 4,7 MΩ | ~2,4 µA | 140 µC |
| Fuga de C_F (polímero/tantalio a ≤ 50 % de su tensión) | ~2–5 µA | 120–300 µC |
| **Total** |  | **~0,6–0,7 mC** |

Con C_F = 330 µF eso es una caída de **~2 V en 60 s** (de 11,3 V a ~9,3 V).
El disparo se calcula con la tensión al final del tiempo.

### 15.5 Tamaño de C_F

`C_F ≥ 2 · R_puente · (I²t)_todo-fuego / V_final²`, con margen ×1,5–2.

| Iniciador (ejemplo) | C_F mínimo a 9 V | Recomendado |
|---|---|---|
| R = 1,5 Ω, I²t = 2 mA²·s (sensible) | 75 µF | 150 µF |
| R = 1,5 Ω, I²t = 10 mA²·s | 370 µF | 560 µF |

**Este dato del iniciador define todo el resto.**

### 15.6 ¿Alcanza un pulso de 1 ms o de 10 ms?

Para cargar C_F al ~95 % hace falta τ = R_total · C_F ≤ t_pulso / 3, donde
R_total es la resistencia de la fuente + cables + R_s + diodo.

| C_F | Pulso 1 ms: R_total máx | Corriente pico aprox. | Pulso 10 ms: R_total máx | Corriente pico aprox. |
|---|---|---|---|---|
| 150 µF | 2,2 Ω | ~5 A | 22 Ω | ~0,5 A |
| 330 µF | 1,0 Ω | ~11 A | 10 Ω | ~1,1 A |
| 560 µF | 0,6 Ω | ~19 A | 6 Ω | ~1,9 A |

- **Con 10 ms** cualquier fuente de 12 V decente y cableado normal alcanza.
- **Con 1 ms** hace falta una fuente muy rígida (batería, cables cortos y gruesos)
  y un iniciador sensible; si no, conviene un pulso de al menos 5–10 ms.
- D1 Schottky con corriente de pico alta (p. ej. SS34, I_FSM ≥ 80 A); R_s de
  0,1–0,5 Ω tipo pulso, o ninguna si el cable ya limita.
- Si la carga quedó incompleta, el micro lo detecta midiendo V(C_F) y aplica la
  política definida (abortar o disparar igual).

### 15.7 Elección de C_F

- **Tantalio-polímero o aluminio-polímero híbrido, 25 V** (trabajando a ≤ 50 %
  de su tensión): ESR bajo para cargar rápido, buen comportamiento en frío y
  fuga baja a tensión reducida.
- Fuga especificada ≤ 0,01·C·V; la real a la mitad de la tensión nominal es
  bastante menor, pero hay que **medirla** en el modelo elegido.
- Evitar electrolítico común (frío) y, si el C_F necesario es chico (≤ 100 µF),
  un banco de MLCC X7R es la opción más robusta (fuga despreciable).

---

## 16. Micro chico para ensamblado SMD en China (JLCPCB / LCSC)

Requisitos: fabricante de primera línea, encapsulado chico, **oscilador de
32,768 kHz con cristal externo (LSE / T1OSC)** que siga contando en bajo consumo,
ADC para medir C_F, brown-out, watchdog y memoria no volátil para T. Muchos
micros chinos muy baratos (CH32V003, PY32F002A) **no tienen oscilador de 32 kHz
con cristal**, así que no sirven para este diseño.

| Micro | Encapsulado más chico | Ventajas | A tener en cuenta |
|---|---|---|---|
| **STM32L011D4P6 / F4U6** (ST) | TSSOP-14 (5 × 6,4 mm) / UFQFPN-20 (3 × 3 mm) | Muy común en LCSC/JLC; LSE + LPTIM que cuenta en Stop (~1 µA); ADC 12 bits con sensor de temperatura; EEPROM de datos; programador ST-Link barato | Núcleo de 32 bits (no agrega riesgo, pero hay más configuración) |
| **PIC12LF1822** (Microchip) | DFN-8 (3 × 3 mm) / SOIC-8 | Lo más simple; Timer1 con cristal de 32 kHz en sueño (~1 µA); EEPROM | Menos stock en LCSC; programador PICkit |

**Recomendado: STM32L011** por disponibilidad en el ensamblador chino, herramientas
baratas y bajo consumo. Elegir TSSOP-14 si se quiere inspección visual simple;
UFQFPN-20 si se busca el mínimo tamaño. Precio orientativo ~0,7–1,0 USD.
**Verificar stock y asignación de patas (LSE en PC14/PC15) en LCSC y en la hoja
de datos antes de cerrar el esquemático.**

### 16.1 BOM SMD sugerida (todas piezas habituales en LCSC)

| Función | Pieza | Encapsulado |
|---|---|---|
| MCU | STM32L011D4P6 | TSSOP-14 |
| Cristal 32,768 kHz | 12,5 pF o 7 pF, ±20 ppm (verificar choque) | 2012 (2,0 × 1,2 mm) o 3215 |
| LDO 2,5 V, ≥ 16 V entrada, Iq ~1 µA | TPS70925 / MCP1703A | SOT-23-5 / SOT-23-3 |
| Q1, Q2 | AO3400A | SOT-23 |
| D1, D2 | SS34 (pico alto) / BAT54 (lógica) | SMA / SOD-323 |
| TVS | SMAJ15A | SMA |
| C_F | Tantalio-polímero 25 V (valor según iniciador) | Caja B/D |
| C_loc, desacople | MLCC 10 µF 25 V, 100 nF | 0805 / 0402 |
| Resistores | divisores 10 MΩ, pull-downs 100 k, bleed 4,7 MΩ | 0402 / 0603 |

### 16.2 Programación y prueba

El ensamblador entrega las placas sin programar. Se programan en el banco de
prueba (§14.3) por **pads de prueba SWD** (VDD, GND, SWDIO, SWCLK, NRST) con
pogo-pins: programa, graba T, aplica el pulso y mide el retardo en una sola
operación.

Tamaño estimado de la placa: **~10 × 15 mm**, definido sobre todo por C_F.

---

## 17. Precios LCSC/JLCPCB y costo de fabricación (consulta 04/11/2026)

Precios tomados del buscador de piezas de JLCPCB (mismos que LCSC), en USD por
unidad comprando 1000. Cambian a diario: **re-cotizar al hacer el pedido**.
"base" = pieza básica de JLC (sin cargo de carga); "ext" = extendida.

### 17.1 Lista de materiales

| Ref | Pieza | Código LCSC | Tipo | Cant. | USD c/u @1000 | Subtotal |
|---|---|---|---|---|---|---|
| U1 | STM32L010F4P6 (TSSOP-20) | C529415 | ext | 1 | 0,697 | 0,697 |
| (U1 alt.) | STM32L011F4U6TR (QFN-20 3×3) | C329283 | ext | (1) | (0,951) | — |
| Y1 | Cristal 32,768 kHz 7 pF ±20 ppm, 3215 (SC-32S) | C97604 | ext | 1 | 0,111 | 0,111 |
| C1, C2 | 10 pF C0G 0402 (carga del cristal) | C32949 | base | 2 | ~0,0015 | 0,003 |
| U2 | LDO HT7525S 2,5 V, 36 V máx., 2 µA (SOT-23) | C22466410 | ext | 1 | 0,029 | 0,029 |
| Q1, Q2 | AO3400A (SOT-23) | C20917 | base | 2 | 0,056 | 0,111 |
| Q3 | 2N7002 (respuesta al programador) | C8545 | base | 1 | 0,013 | 0,013 |
| D1 | SS34 (SMA) | C8678 | base | 1 | 0,025 | 0,025 |
| D2 | BAT54WS (SOD-323) | C191198 | ext | 1 | 0,010 | 0,010 |
| TVS | SMAJ15A (SMA) | C86819 | ext | 1 | 0,030 | 0,030 |
| C_F | Aluminio-polímero 330 µF 25 V, SMD 6,3 × 9 mm, 25 mΩ | C54321572 | ext | 1 | 0,125 | 0,125 |
| C_loc | 10 µF 25 V X5R 0805 | C15850 | base | 1 | 0,030 | 0,030 |
| C | 1 µF 25 V 0402 | C52923 | base | 2 | 0,005 | 0,010 |
| C | 100 nF 0402 | C1525 | base | 1 | 0,002 | 0,002 |
| R | 0402 varios (10 MΩ, 4,7 MΩ, 100 k, 22 k, 1 k) | C26082, C26091, C25741, … | base/ext | ~9 | ~0,0012 | 0,011 |
| | **Total materiales** | | | | | **≈ 1,21 USD** (con QFN: ≈ 1,46) |

Notas:
- C_F de aluminio-polímero: barato y bueno en frío; **medir su fuga** a 11 V
  durante 60 s. Alternativa de tantalio-polímero: KEMET T521D107M025 (100 µF
  25 V, C212710, 0,90 USD) si el iniciador es sensible.
- Con cristal de 7 pF el STM32L0 trabaja con su nivel de excitación bajo; los
  cristales de 12,5 pF piden más corriente.

### 17.2 Ensamblado y programación en JLCPCB (pedido de 1000 placas)

La programación del firmware la ofrece JLCPCB **solo en PCBA "Standard"**:
~8 USD de ingeniería + ~8 USD/hora de operario, después del montaje, con una
interfaz de programación en la placa (pads SWD).

| Concepto | Cálculo | USD |
|---|---|---|
| Setup Standard (una cara) | fijo | 25,6 |
| Stencil | fijo | 8,2 |
| Carga de alimentadores | ~16 piezas distintas × 1,53 | 24,5 |
| Soldaduras SMT | ~70 juntas × 1000 = 70 000 juntas | ~106 |
| Fixtures, embalaje, varios | estimado | ~15 |
| Programación | 8 + ~2–3 h × 8 | ~30 |
| **Subtotal ensamblado + programación** | | **≈ 210 → 0,21 USD/placa** |
| PCB 2 capas, ~10 × 15 mm, panelizado | estimado, cotizar en la web | 40–80 → 0,04–0,08/placa |

**Costo por placa terminada y programada: ≈ 1,5 USD** (≈ 1,75 con el micro QFN).
No incluye envío a Argentina ni impuestos de importación.

Prototipos (10 placas): conviene PCBA "Economic" (setup 8,2 + stencil 1,5 +
3,07 por pieza extendida) y programar uno mismo con un ST-Link (~5–10 USD):
**≈ 60–90 USD el lote** con piezas y PCB.

---

## 18. Cómo se programa el tiempo de cada retardador (después de armado)

Separación clara:

- **Firmware**: uno solo, igual para todas las placas, lo graba JLCPCB (o uno
  mismo por SWD). No contiene el tiempo.
- **Tiempo T**: es un dato que se guarda en la EEPROM interna, con CRC, **por los
  mismos 2 cables del iniciador**, en cualquier momento después del armado, aun
  con la placa encapsulada en resina. Se puede leer y reprogramar.

### 18.1 Programador de retardo (equipo de banco o de mano)

Cajita con pinzas a los 2 cables, perilla o teclado y pantalla (o conectada a
una PC). Basado en un Arduino/STM32 de desarrollo + 2 transistores: ~15–30 USD.

Operación (≈ 1 s por unidad):

1. Conectar las 2 pinzas.
2. Elegir el tiempo (p. ej. 9,0 s) — queda fijo para toda la tanda.
3. Apretar el botón: escribe, lee de vuelta y verifica.
4. LED verde "9,00 s OK" (o rojo si falla). Opcional: imprime etiqueta o
   registra número de serie.

También sirve para **leer** qué tiempo tiene cualquier unidad (control de calidad).

### 18.2 Cómo funciona por 2 cables

- El programador alimenta la línea con **5 V** (no 12 V). El firmware, al
  arrancar, mide la línea: si está por debajo de ~6 V entra en **modo
  programación, en el que los pines de disparo quedan bloqueados**. Solo con
  ≥ 9 V entra en modo retardo.
- Programador → placa: modula la línea entre 5 V y 3,5 V (C_F sigue cargado
  gracias a D1). La placa lo lee con un divisor 100 k / 22 k a una entrada ADC.
- Placa → programador: el micro prende Q3 (2N7002 + 1 kΩ) y consume ~5 mA en
  pulsos; el programador los detecta midiendo corriente.
- Se transmite T + CRC; la placa responde con lo que grabó; el programador compara.

### 18.3 Seguridad del proceso

- Flujo normal: **programar antes de conectar el iniciador**.
- Si hubiera que programar con el iniciador conectado: a 5 V la energía en C_F es
  ~20 % de la de 11 V, el firmware bloquea el disparo y hay dos MOSFET en serie
  apagados. Igualmente, evaluar con los datos de no-fuego del iniciador.
- Marcar el tiempo en el exterior de la bengala (etiqueta o color por tiempo).

---

## 19. Costo puesto en Argentina de un lote de 1000 (estimación 11/2026)

### 19.1 Precio en China (FOB)

| Concepto | USD |
|---|---|
| Piezas (1,21 × 1000) + ~3 % de merma que cobra JLC | ~1 250 |
| Ensamblado + programación del firmware (§17.2) | ~210 |
| PCB panelizado | ~60 |
| Comisión de pago (tarjeta/PayPal, ~0–4 %) | ~0–60 |
| **FOB** | **≈ 1 520–1 580** |

### 19.2 Envío

Peso estimado: ~1,4 g por placa + rieles de panel + embalaje → **2,5–3 kg**.
DHL Express desde JLCPCB a Argentina: **≈ 50–90 USD** (ver el valor exacto en
la página de cotización de JLCPCB con el peso real). → **CIF ≈ 1 600–1 650 USD**.

### 19.3 Aduana: es importación comercial

1000 unidades iguales **no entran como courier/pequeño envío** (el courier no
admite uso comercial ni más de 3 unidades de la misma especie). Va por el
**régimen general con despachante**, a nombre de la empresa (CUIT con alta de
importador).

Sobre CIF = 1 600 USD (la posición arancelaria la define el despachante; derecho
de importación supuesto 0–20 %):

| Concepto | Tasa | USD | ¿Se recupera? |
|---|---|---|---|
| Derecho de importación | 0–20 % (supuesto) | 0–320 | No |
| Tasa de estadística | 3 % | ~48 | No |
| Despachante + gastos de aduana/depósito del courier | — | 250–450 | No |
| IVA | 21 % | ~340–415 | Sí, crédito fiscal (responsable inscripto) |
| Percepción IVA adicional | 20 % | ~330–395 | Sí, a cuenta |
| Percepción Ganancias | 6 % | ~100–120 | Sí, a cuenta |
| Percepción IIBB | ~2,5 % | ~40–50 | Sí, a cuenta |

### 19.4 Resultado

| | Total USD | Por placa |
|---|---|---|
| **Costo real** (lo que no se recupera) | **≈ 1 900–2 420** | **≈ 1,9–2,4 USD** |
| Desembolso inicial (incluye impuestos recuperables) | ≈ 2 700–3 400 | ≈ 2,7–3,4 USD |

Estimación central (derecho del 16 %, despachante 350): **≈ 2 250 USD → 2,25 USD
por placa terminada, programada y nacionalizada.**

Lo que más mueve el número: la posición arancelaria (derecho de importación) y
el honorario mínimo del despachante, que pesa mucho en un envío chico. Pedir
cotización a un despachante con la factura proforma de JLCPCB.

### 19.5 Costos únicos (no por lote)

| Concepto | USD |
|---|---|
| Prototipos (10 placas, ensamblado Economic) | 60–90 + envío |
| Programador ST-Link | 5–10 |
| Programador de retardo por 2 cables | 15–30 |
| Banco de prueba con pogo-pins | 100–300 |

No incluido: diseño/firmware, barniz o resina y su aplicación, ensayos
(cámara térmica, vibración), mano de obra local.

### 19.6 Lotes siguientes

El costo de §19.4 ya no incluye costos únicos, así que un segundo lote de 1000
cuesta prácticamente lo mismo (≈ 2,2 USD/placa). Solo se ahorra el stencil
(~8 USD; JLC lo guarda por ~5 USD).

Separando fijos por pedido y variables por placa:

| | USD |
|---|---|
| Fijos por pedido: setup 25,6 + carga de piezas 24,5 + ingeniería de programación 8 + envío ~70 + despachante ~350 | **≈ 480 por pedido** |
| Variables por placa: piezas 1,25 + soldaduras 0,11 + PCB 0,06 + programación 0,02 + derechos y tasa (~19 % del CIF) 0,30 | **≈ 1,74 por placa** |

| Tamaño del pedido | Costo por placa |
|---|---|
| 1000 | ≈ 2,2 USD |
| 2000 | ≈ 2,0 USD |
| 5000 | ≈ 1,8 USD (más descuento por volumen en el micro) |

---

## 20. ¿Hay algo comercial que haga lo mismo?

| Opción | Qué es | Por qué sirve o no |
|---|---|---|
| Igniters electrónicos con retardo para fuegos artificiales (p. ej. MJG E-tek, EE. UU.; también fabricantes chinos de “electronic igniters” para shows) | E-match con chip de retardo integrado | Es lo más parecido. Pero funcionan con el sistema de disparo/programador propio de cada marca (no con un pulso de 12 V genérico), el E-tek cuesta ~5 USD c/u + programador de ~1 600 USD y no se vende online; al ser artículo pirotécnico, importarlo implica ANMaC y transporte de mercancía peligrosa. |
| Elemento de retardo pirotécnico (columna de composición) | Lo tradicional en bengalas eyectables | Barato y sin electrónica, pero la precisión típica es de varios % y varía con la temperatura: no asegura ±100 ms en 9 s. |
| Detonadores electrónicos de minería | Retardo electrónico autoalimentado | Son explosivos (detonadores), régimen legal distinto: no aplica. |
| Timers de cohetería / módulos de retardo con relé | Temporizadores genéricos | Necesitan batería o alimentación continua. |

Recomendación: consultar al proveedor de las bengalas si ofrece versión con
retardo integrado, y pedir cotización a fabricantes de igniters electrónicos
para fuegos artificiales indicando la interfaz (pulso de 12 V de 1–10 ms) y la
precisión requerida. Si no hay nada que acepte el pulso de 12 V y cumpla ±100 ms,
el diseño propio a ~2,2 USD/unidad sigue siendo competitivo.

---

## 21. Precio de venta sugerido

### 21.1 Referencia: cuánto cuesta una bengala

- Mendoza, licitación 2023–2024: **10 000 bengalas BIP** (burn-in-place, se
  queman en el ala del avión) por $456 250 000 → **$45 625 c/u**, ≈ **130 USD**
  al tipo de cambio oficial de octubre de 2023 (~350 $/USD). Proveedor:
  Stroyproject (Bulgaria).
- Mendoza 2008–2011 (expediente judicial): $141,12 por bengala y $92,40 por
  “cartucho de siembra” (probablemente eyectable) → ≈ 35 y 23 USD al cambio de
  entonces (~4 $/USD).
- Las eyectables (las que llevarían este retardador) son más chicas que las BIP:
  estimación **≈ 25–80 USD** hoy. No encontré precios publicados recientes:
  confirmar con proveedores.
- Ojo con el mercado: en junio de 2024 Mendoza anunció el fin de la siembra con
  aviones. Hay que identificar quién compra hoy (otras provincias, privados,
  exportación).

### 21.2 Costo completo por unidad (1000/año)

| Concepto | USD |
|---|---|
| Placa puesta en Argentina (§19) | 2,2 |
| Barniz/resina, etiqueta, ensayo y programación local | 0,3–0,6 |
| Rechazos y garantía (~5 %) | 0,15 |
| **Costo directo** | **≈ 2,7–3,0** |
| Amortización del desarrollo (p. ej. 10 000–20 000 USD en 3 años) | 3,3–6,7 |
| **Costo total** | **≈ 6–10** |

### 21.3 Precio

| Criterio | Precio por unidad |
|---|---|
| Costo directo × 2,5–3 (margen típico de electrónica B2B de bajo volumen) | 7–9 USD |
| Recuperar desarrollo + margen | 9–12 USD |
| Valor para el cliente: ≤ 10–15 % del precio de la bengala eyectable | 3–12 USD |

**Sugerido: lista ≈ 10 USD/unidad, 7–8 USD por volumen o contrato anual**, con el
programador de retardo vendido aparte (~150–300 USD) o incluido en la primera
compra. Es un componente de seguridad en un artículo pirotécnico: el precio debe
cubrir seguro de responsabilidad civil y ensayos de lote.

---

## 22. Mercado Mendoza: datos públicos (relevados 05/11/2026)

### 22.1 Consumo por temporada

| Temporada | Material usado | Fuente |
|---|---|---|
| 2022–23 (hasta enero) | 7 233 bengalas, 5 433 cartuchos, 566 h de vuelo | Contingencias Climáticas |
| 2024–25 (Sur, ADSAH) | 3 262 bengalas eyectables + 584 de quema directa, 61 vuelos | Municipalidad de Gral. Alvear |
| 2025–26 (Sur) | 4 889 bengalas + 4 414 cartuchos, 141 vuelos en 47 días, 3 aviones | MinutoYA |
| Año “normal” (declaración oficial) | ~10 000 bengalas + ~10 000 cartuchos | El Sol |

### 22.2 Compras y precios

| Fecha | Compra | Precio |
|---|---|---|
| 2008 (Decreto 3203/08) | 16 000 bengalas + 5 000 cartuchos, Stroyproject | $141,12 / $92,40 → ≈ 35 / 23 USD |
| 01/2023 | 3 000 bengalas | $50 M → $16 700 c/u (≈ 90 USD oficial) |
| 09/2023 (Decreto 1976/23) | 10 000 bengalas UVA-150, Stroyproject (única oferta) | $456,25 M → $45 625 c/u (≈ 130 USD oficial) |
| 2026–27 (licitación en curso) | 16 000 bengalas + 13 000 cartuchos | ofertas US$ 1,395–1,75 M → **≈ 48–60 USD promedio por unidad** |

Si en 2026–27 las bengalas valen 60–85 USD, los cartuchos quedarían en ≈ 20–40
USD (reparto no publicado: estimación).

### 22.3 Situación del programa

- La Provincia dejó de operar el sistema en 2024; lo operan **San Rafael y
  General Alvear** con aviones cedidos por la Provincia (Aviación San Rafael) y
  material de siembra comprado por la Provincia.
- Costo 2024–25 del sistema Sur: ~$1 500 M (San Rafael 70 %, Alvear 30 %).
- Para 2026–27 se discute un esquema plurianual; la cantidad de aviones (2 o 3)
  seguía sin definir en septiembre de 2026.
- Riesgo de contrato: en 2026 la Provincia rechazó el reclamo del proveedor por
  la devaluación de 2023 (contrato en pesos). → Cotizar en USD o con cláusula
  de ajuste.

### 22.4 Implicancias para el retardador

- Volumen potencial: **~10 000–16 000 unidades/año** solo en Mendoza, no 1000.
  A ese volumen el costo baja a ≈ 1,8 USD/placa (§19.6).
- Si va en el cartucho/bengala eyectable de ~20–40 USD, **10 USD es caro**:
  apuntar a **4–6 USD** por unidad (10–20 % del cartucho), que con 10 000+
  unidades deja buen margen y paga el desarrollo en la primera temporada.
- Calendario: la temporada arranca en noviembre y la licitación de material se
  define antes; un retardador nuevo tendría que estar ensayado y aceptado por
  el fabricante de la bengala con meses de anticipación.
