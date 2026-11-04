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
