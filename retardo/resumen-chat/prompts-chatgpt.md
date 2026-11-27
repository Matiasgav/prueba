# Anexo: prompts para ChatGPT escritos durante el chat

## Buscar alternativas al temporizador TPL5110-Q1 (23/11)

```
Necesito que busques alternativas al integrado temporizador TPL5110-Q1 de Texas Instruments
para un circuito de retardo. Buscá en hojas de datos y documentos oficiales de fabricantes
(TI, Analog Devices/Maxim, Renesas, Microchip, ABLIC, Nexperia, onsemi, STMicroelectronics,
Toshiba, ROHM, Diodes Inc. y cualquier otro). Podés buscar en inglés.

CONTEXTO DE USO
- El circuito recibe energía una sola vez (un capacitor cargado) y tiene que esperar un tiempo
  fijo y después cambiar una salida que habilita la conmutación de una carga.
- No hay microcontrolador ni software: el tiempo lo fijan componentes externos.
- Las placas se almacenan 2–3 años antes de usarse y no se pueden probar justo antes del uso.

REQUISITOS DEL TEMPORIZADOR
1. Función
   - Empieza a contar solo al recibir alimentación (sin pulso de disparo externo), o con un
     disparo que pueda generarse de forma simple y confiable al encenderse.
   - Rango de tiempo que cubra 20 a 45 segundos.
   - Tiempo ajustable con componentes externos (resistor, capacitor o pines de configuración),
     sin programación.
   - Cambia la salida una sola vez (monoestable o modo de un solo pulso), sin repetirse
     mientras haya alimentación.
   - Mantiene la salida activa al menos 20 ms, o hasta que se corte la alimentación.
2. Precisión
   - Error total ≤ ±10 % entre −30 y +70 °C, incluyendo el componente externo de ajuste.
   - Indicá qué especificaciones son mínimo/máximo garantizado y cuáles son solo típicas.
3. Alimentación y consumo (crítico)
   - Funciona a 2,5 V (ideal 1,8–5,5 V).
   - Consumo en espera ≤ 1 µA (máximo aceptable 5 µA). Descartá los de decenas de µA o más.
   - Informá el pico de consumo al arrancar y su duración.
4. Comportamiento ante fallas
   - La salida debe estar en el nivel inactivo desde el encendido, sin pulsos espurios.
   - Si el fabricante publica análisis de fallas por pin (Pin FMA), indicá qué pasa con la
     salida si un pin queda en corto a masa, en corto a VDD o abierto, y si el componente de
     ajuste se abre o se pone en corto.
5. Ambiente y robustez
   - Temperatura de trabajo al menos −40 a +85 °C.
   - Sin resonador mecánico (sin cristal ni MEMS), por choque y vibración.
   - ESD HBM ≥ 2 kV.
6. Confiabilidad y datos (muy importante)
   - Preferentemente calificado AEC-Q100.
   - Tasa de falla publicada (FIT según IEC TR 62380, SN 29500 o ensayo de vida), reparto
     de modos de falla (FMD) y análisis por pin. Indicá el documento exacto donde aparecen.
7. Fabricación y precio
   - Encapsulado chico con patas visibles (SOT-23, SC-70, MSOP, SOIC); evitá QFN/BGA si hay opción.
   - Disponible en LCSC/JLCPCB o en distribuidores grandes (DigiKey, Mouser).
   - Precio objetivo ≤ 0,60 USD a 1000 unidades.
   - Estado de producción activo (no NRND ni obsoleto).

REFERENCIA (lo que ya tengo, para comparar)
TPL5110-Q1 (TI): 100 ms–7200 s con un resistor, 35 nA típ., 1,8–5,5 V, AEC-Q100 grado 1,
oscilador ±0,5 % a 25 °C garantizado, deriva 150 ppm/°C típica, 4 FIT (IEC TR 62380),
FMD 50 % sin salida / 50 % precisión degradada, Pin FMA publicado (SNAA343A),
SOT-23-6, ~0,35–0,51 USD a 1000 en LCSC.
Ya descarté: LTC6995/LTC6993 (consumo ~55–80 µA) y TLC555-Q1 (~180 µA).
No me propongas microcontroladores ni relojes de tiempo real con cristal.

QUÉ QUIERO COMO RESPUESTA
1. Una tabla con cada candidato: fabricante, número de parte, rango de tiempo, método de
   ajuste, consumo (típico y máximo), precisión (separando garantizado y típico), temperatura,
   AEC-Q100 sí/no, FIT/FMD/Pin FMA publicados sí/no, encapsulado, precio aproximado y
   disponibilidad en LCSC.
2. Para cada candidato, el enlace a la hoja de datos y a los documentos de confiabilidad.
3. Qué requisitos cumple, cuáles no y cuáles no se pueden verificar con la información pública.
4. Si no encontrás un dato, escribí "no encontrado". No lo estimes ni lo inventes.
5. Al final, un ranking de los 3 mejores para este uso y el motivo, y si alguno sirve como
   segunda fuente del TPL5110-Q1.
```

## Respuesta a ChatGPT corrigiendo sus candidatos de temporizador (23/11)

```
Gracias. Verifiqué tus candidatos contra las hojas de datos y encontré estos problemas:

1. ABLIC S-19100: no es un temporizador, es un supervisor de tensión con retardo por capacitor.
   - El ±15 % vale solo a 25 °C (CD = 4,7 nF). Según la hoja de datos (Tabla 11), el coeficiente de
     retardo va de 2,58 ms/nF (+105 °C, mín.) a 12,01 ms/nF (−40 °C, máx.): casi 5 veces de variación,
     más la tolerancia del capacitor. No cumple ±10 % para 30 s.
   - El consumo máximo es 1,1–1,2 µA (no 2,2 µA), y es AEC-Q100 grado 2, no grado 1.
   - ABLIC no publica FIT; lo calcula a pedido.
2. 74HC4538 / HCF4538 / MC14538: el consumo que citaste es el de reposo, no el de mientras temporiza
   (onsemi especifica aparte un "active state"). Para 30 s necesitan un RC con capacitores de decenas
   de µF (electrolíticos o tántalo, con fuga comparable a la corriente de carga), necesitan un flanco de
   disparo y el CD74HC4538-Q1 de TI figura como no recomendado para diseños nuevos. Descartados.
3. ICM7555: 40 µA típ. / 200 µA máx. Supera el límite de consumo. Descartado.

Ninguno reemplaza al TPL5110-Q1. Quiero que busques de nuevo con estos criterios más estrictos:

A) Solo temporizadores dedicados (no supervisores con retardo por capacitor, no monoestables RC,
   no 555) cuyo tiempo NO dependa de un capacitor externo grande: ajuste por resistor, por pines
   digitales o por oscilador interno con divisor.
B) Consumo máximo ≤ 1 µA durante la cuenta (no solo el de reposo).
C) Error total ≤ ±10 % entre −30 y +70 °C, con datos de la hoja de datos (indicá si son garantizados
   o típicos) y el coeficiente de temperatura del oscilador.
D) Rango que cubra 20–45 s.
E) Salida en nivel inactivo desde el encendido; si hay análisis de fallas por pin, citá qué hace la
   salida con un pin en corto a masa.
F) Prioridad a AEC-Q100 y a fabricantes que publiquen FIT y reparto de modos de falla
   (indicá el número de documento).

Buscá también:
- Segundas fuentes o equivalentes de la familia TPL5010 / TPL5110 / TPL5111 de otros fabricantes
  (por ejemplo "nano power timer", "system timer", "power gating timer", "wake-up timer" sin cristal).
- Temporizadores de bajo consumo de Renesas, Microchip, ABLIC, ROHM, Toshiba, Nisshinbo, Torex,
  Diodes Inc., Nexperia y onsemi.

Mismo formato que antes: tabla, enlaces a la hoja de datos y a los documentos de confiabilidad,
"no encontrado" cuando no esté el dato, y al final un ranking con el motivo. Si no existe ninguna
alternativa que cumpla A–D, decilo directamente.
```

## Buscar osciloscopio y multímetro en MercadoLibre (24/11)

```
Necesito que busques en MercadoLibre Argentina (mercadolibre.com.ar) las opciones más convenientes, nuevas y con stock, para armar un banco de medición simple. Usá precios actuales en pesos y dame los enlaces directos a las publicaciones.

USO: medir un pulso de descarga de un capacitor de ~1–5 ms (corriente sobre un shunt de 0,1 Ω, hasta ~10 A), medir tensiones de continua de 0 a 30 V y medir fugas de µA como tensión sobre un resistor de 100 kΩ (milivolts).

1) OSCILOSCOPIO (presupuesto objetivo: lo más barato que cumpla)
Requisitos obligatorios:
- Disparo único (modo "Single" / "Single shot").
- Exportar los datos de la forma de onda a la PC (CSV o texto). Si no exporta, que tenga cursores de medición de tiempo y tensión.
Deseable, pero no obligatorio: 2 canales; 20 MHz o más; punta x10 incluida.
Puede ser USB (por ejemplo Hantek 6022BE, si funciona con el software libre OpenHantek6022), portátil (FNIRSI 2C53P/2C53T) o de mesa.
Para cada opción indicá: modelo exacto, precio, cuotas, envío, reputación del vendedor y cantidad de vendidos, si es tienda oficial, y si la descripción confirma el disparo único y la exportación de datos.

2) MULTÍMETRO (presupuesto objetivo: económico)
Requisito obligatorio:
- En tensión continua, el rango más bajo (200, 400 o 600 mV) tiene que mostrar 0,1 mV de resolución (multímetro de 2000, 4000 o 6000 cuentas o más). Verificá ese dato en la especificación de la publicación o del fabricante; si no está claro, aclaralo.
Deseable: precisión en continua de ±0,5 % a ±1 %; impedancia de entrada de 10 MΩ; medición de capacidad.
Marcas de referencia: UNI-T, ANENG, Owon, Brymen, Zotek (no es obligatorio que sea una de estas).

3) FUENTE DE LABORATORIO (opcional, si encontrás algo conveniente)
0–30 V, 3–5 A, regulable, con límite de corriente ajustable (modo CC) y display digital.

QUÉ DESCARTAR O MARCAR COMO SOSPECHOSO:
- Precios muy por debajo del resto del mismo modelo (posible copia, error de carga o modelo distinto).
- Vendedores con poca reputación o sin ventas.
- Publicaciones que no aclaran el modelo exacto.

FORMATO DE RESPUESTA:
- Una tabla por instrumento con: modelo, precio (ARS), ¿cumple los obligatorios? (sí/no/dudoso y por qué), vendedor y reputación, enlace.
- Al final, tu recomendación: la combinación más barata que cumpla todos los obligatorios, con el total en pesos, y una segunda opción "un poco mejor" si la diferencia de precio es chica.
```

## Buscar capacitores de polímero en MercadoLibre (24/11)

```
Buscá en MercadoLibre Argentina (mercadolibre.com.ar) capacitores de aluminio de POLÍMERO SÓLIDO (también llamados "capacitor sólido", "estado sólido", "polymer", "OS-CON", "POSCAP", "low ESR polímero"), nuevos y con stock. Dame enlaces directos y precios actuales en pesos.

Los necesito para un ensayo de descarga rápida: la resistencia serie (ESR) tiene que ser baja, por eso NO sirven los electrolíticos comunes, aunque el título diga "sólido".

QUÉ BUSCO (3 de cada uno):
1) 470 a 560 µF, 25 V (aceptable 16 V si no hay de 25 V). Prioridad máxima.
2) 220 a 270 µF, 16 a 25 V.
3) 820 a 1000 µF, 16 a 25 V.

REQUISITOS OBLIGATORIOS:
- Tecnología: aluminio de polímero sólido (no electrolítico líquido, no tantalio, no supercapacitor).
- Nuevos (no recuperados de placas madre).
- Tensión nominal 16 V o más (preferible 25 V).

CÓMO VERIFICAR QUE SEA POLÍMERO DE VERDAD (indicalo en cada resultado):
- Marca y serie identificables, por ejemplo: Nichicon LF/LE, Panasonic OS-CON (SVP, SEP, SVPF), Nippon Chemi-Con PSA/PSC, Rubycon PZ-CAP, Lelon OCR, Apaq, CapXon (serie sólida), Fujitsu FP, Elite, Jianghai (serie polímero).
- ESR del orden de 10 a 40 mΩ si la publicación o la hoja de datos de esa serie la indica.
- En las fotos: tapa de aluminio lisa SIN la cruz de venteo grabada.
- Si el anuncio no dice marca ni serie, o la foto muestra la cruz de venteo en la tapa, marcalo como "dudoso".

QUÉ DESCARTAR:
- Electrolíticos comunes con la palabra "sólido" en el título.
- Packs muy baratos sin marca.
- Vendedores sin reputación o sin ventas.

FORMATO DE RESPUESTA:
- Una tabla por cada grupo de valores (470–560 µF / 220–270 µF / 820–1000 µF) con: capacidad, tensión, marca y serie, ESR si figura, ¿es polímero? (sí / dudoso / no y por qué), precio por unidad, cantidad mínima de compra, vendedor y reputación, enlace.
- Al final, tu recomendación: qué comprar de cada grupo (3 unidades), el total en pesos y alternativas si algún grupo no tiene opciones confiables.
```

## Buscar materiales del banco de I²t en MercadoLibre (25/11)

```
Necesito que busques en MercadoLibre Argentina (mercadolibre.com.ar) los materiales para un banco de medición de pulsos de corriente. Para cada ítem dame el link directo a una publicación activa (no a una búsqueda), el precio actual, el vendedor y su reputación, si el envío es local o internacional y el plazo de entrega. Si hay varias opciones, elegí la mejor relación calidad/precio con vendedor confiable y envío local, y mencioná una alternativa. Verificá en la publicación que el producto cumpla la especificación; si no estás seguro, decilo.

ADQUISICIÓN
1. Módulo ADC AD7606 de 8 canales, 16 bits, 200 kSPS, alimentación 5 V. Tiene que ser un MÓDULO (placa), no el integrado suelto AD7606BSTZ. Si la publicación lo muestra, confirmá que tiene accesibles los pines VIO (o VDRIVE), PAR/SER, RANGE, OS0-OS2, CONVST, BUSY, CS, SCLK, DOUTA y RESET.
2. Placa Black Pill STM32F411CEU6 (WeAct o equivalente, USB-C). Que sea F411CEU6, no F401. Evitá las de precio sospechosamente bajo.
3. Aislador USB con chip ADuM3160 (USB full speed 12 Mbps alcanza).

CIRCUITO DE DESCARGA
4. Resistencia shunt 0,1 Ω, 1 %, SMD 2512, 2 W (pack de 5). Alternativa: 0,1 Ω cerámica de 5 W.
5. Capacitor electrolítico 680 µF 25 V, 105 °C (pack de 10 o 20).
6. MOSFET IRLZ44N (2 o 3 unidades). OJO: tiene que ser IRLZ44N, NO IRFZ44N.
7. Resistencia 2,2 Ω 1 % de 5 W (para validar el banco).
8. Resistencia 100 Ω 5 W (2 unidades).
9. Resistencias de 1/4 W al 1 %: 20 kΩ, 10 kΩ, 1 kΩ y 470 Ω (packs chicos o kit surtido de resistencias al 1 %).
10. Pulsador normal abierto para panel.
11. Dos interruptores de palanca (2 A o más).
12. Interruptor con llave física (cerradura) de 2 contactos.
13. Broche para pila de 9 V.
14. Borneras para placa paso 5 mm, placa perforada experimental y cables dupont macho-hembra.
15. Cable de cobre de 1 mm² (unos metros, rojo y negro).

INSTRUMENTOS
16. Fuente de laboratorio regulable 0–30 V, 0–5 A con límite de corriente y display de 2 decimales debajo de 10 V. Comparar Etheos FLI-3005, Korad KA3005D y otras de marca conocida.
17. Multímetro UNI-T UT61E+ (o equivalente de 22.000 cuentas con rango de mV y mA).

Al final armá una tabla con: ítem, link, precio, vendedor, envío, y el total sumado. Indicá aparte qué ítems conviene comprar en una casa de electrónica local en vez de MercadoLibre (por ejemplo, resistencias sueltas que en MercadoLibre solo vienen en packs grandes).
```

## Buscar materiales originales: MercadoLibre, distribuidores y DigiKey/Mouser (25/11)

```
Necesito que busques los materiales para un banco de medición de pulsos de corriente. Quiero componentes ORIGINALES, no clones. Buscá primero en MercadoLibre Argentina (tiendas oficiales o vendedores que sean distribuidores con factura), después en distribuidores argentinos (por ejemplo Electrocomponentes) y por último en DigiKey o Mouser con envío a Argentina, aclarando costo de flete e impuestos estimados.

Para cada ítem dame: link directo a una publicación o página de producto (no búsquedas), precio, vendedor, cómo se confirma que es original (tienda oficial, distribuidor autorizado, marca y número de parte del fabricante en la publicación, garantía, factura), envío y plazo. Si no podés confirmar que es original, decilo y proponé dónde conseguirlo original.

ADQUISICIÓN
1. Módulo ADC AD7606 de 8 canales, 16 bits, 200 kSPS, 5 V, con chip original de Analog Devices (pedir o buscar fotos del integrado). Tiene que ser un MÓDULO, no el integrado suelto. Confirmá que tiene accesibles VIO/VDRIVE, PAR/SER, RANGE, OS0-OS2, CONVST, BUSY, CS, SCLK, DOUTA, RESET. Alternativa: placa de evaluación oficial de Analog Devices (EVAL-AD7606), con su precio.
2. Placa Black Pill STM32F411CEU6 original de WeAct Studio (tienda oficial WeAct o vendedor que la identifique como WeAct con fotos de la serigrafía). No F401.
3. Aislador USB con chip ADuM3160 original de Analog Devices.

CIRCUITO DE DESCARGA (marcas: Vishay, Yageo, Bourns, Ohmite, KOA, TE para resistencias; Panasonic, Nichicon, Rubycon, Nippon Chemi-Con para capacitores; Infineon para el MOSFET)
4. Resistencia shunt 0,1 Ω, 1 %, SMD 2512, 2 W o más, de baja inductancia (5 unidades).
5. Capacitor electrolítico de aluminio 680 µF 25 V, 105 °C, baja ESR (5 unidades).
6. MOSFET IRLZ44N de Infineon (3 unidades). NO IRFZ44N.
7. Resistencia 2,2 Ω 1 % de 5 W o más.
8. Resistencia 100 Ω 5 W (2 unidades).
9. Resistencias de 1/4 W al 1 % metal film: 20 kΩ, 10 kΩ, 1 kΩ, 470 Ω (5 de cada una).
10. Pulsador normal abierto para panel; dos interruptores de palanca de 2 A o más; interruptor con llave física (cerradura). Marcas tipo C&K, APEM, E-Switch o equivalentes de calidad.
11. Broche para pila de 9 V, borneras paso 5 mm (Phoenix Contact, Würth o similar), placa perforada FR4, cable de cobre de 1 mm².

INSTRUMENTOS
12. Fuente de laboratorio regulable 0–30 V, 0–5 A, con límite de corriente y display de 2 decimales debajo de 10 V, de marca reconocida con garantía en Argentina (Korad KA3005D, UNI-T, Owon u otra de calidad similar).
13. Multímetro UNI-T UT61E+ original (tienda oficial UNI-T o importador autorizado), o equivalente de 22.000 cuentas.

Al final armá una tabla con: ítem, link, marca y número de parte, precio, dónde se compra, cómo se confirma que es original, envío, y el total. Agrupá los ítems por proveedor para minimizar envíos, y decime si conviene hacer un solo pedido a DigiKey/Mouser para los componentes chicos.
```

## Buscar materiales originales solo en MercadoLibre, con ST-Link (25/11)

```
Necesito que busques SOLO en MercadoLibre Argentina (mercadolibre.com.ar) los materiales para un banco de medición de pulsos de corriente. Quiero componentes ORIGINALES, no clones. Priorizá tiendas oficiales, MercadoLíderes que sean distribuidores o importadores con factura, y publicaciones que indiquen marca y número de parte del fabricante.

Para cada ítem dame: link directo a una publicación activa (no a una búsqueda), precio, vendedor y reputación, cómo se confirma que es original (tienda oficial, distribuidor, marca y número de parte, fotos del producto, garantía, factura), envío local o internacional y plazo. Si en MercadoLibre no hay una opción que se pueda confirmar como original, decilo claramente y dame la mejor alternativa disponible indicando el riesgo.

PROGRAMACIÓN
1. Programador ST-Link original de STMicroelectronics: STLINK-V3MINIE o ST-LINK/V2 original (caja y etiqueta de ST). No clones "ST-Link V2 mini" de aluminio.

ADQUISICIÓN
2. Módulo ADC AD7606 de 8 canales, 16 bits, 200 kSPS, 5 V, con chip original de Analog Devices (buscar fotos del integrado). Tiene que ser un MÓDULO, no el integrado suelto. Confirmá que tiene accesibles VIO/VDRIVE, PAR/SER, RANGE, OS0-OS2, CONVST, BUSY, CS, SCLK, DOUTA, RESET.
3. Placa Black Pill STM32F411CEU6 original de WeAct Studio (que la publicación diga WeAct y muestre la serigrafía). No F401.
4. Aislador USB con chip ADuM3160 original de Analog Devices.

CIRCUITO DE DESCARGA (marcas: Vishay, Yageo, Bourns, Ohmite o KOA para resistencias; Panasonic, Nichicon, Rubycon o Nippon Chemi-Con para capacitores; Infineon para el MOSFET)
5. Resistencia shunt 0,1 Ω, 1 %, SMD 2512, 2 W o más (5 unidades). Alternativa: 0,1 Ω 1 % de potencia, no bobinada.
6. Capacitor electrolítico de aluminio 680 µF 25 V, 105 °C, baja ESR (5 unidades).
7. MOSFET IRLZ44N de Infineon (3 unidades). NO IRFZ44N.
8. Resistencia 2,2 Ω 1 % de 5 W o más.
9. Resistencia 100 Ω 5 W (2 unidades).
10. Resistencias de 1/4 W al 1 % metal film: 20 kΩ, 10 kΩ, 1 kΩ y 470 Ω (o un kit surtido al 1 % de marca).
11. Pulsador normal abierto para panel; dos interruptores de palanca de 2 A o más; interruptor con llave física (cerradura).
12. Broche para pila de 9 V, borneras paso 5 mm, placa perforada FR4, cables dupont macho-hembra, cable de cobre de 1 mm² rojo y negro.

INSTRUMENTOS
13. Fuente de laboratorio regulable 0–30 V, 0–5 A, con límite de corriente y display de 2 decimales debajo de 10 V, de marca reconocida con garantía en Argentina (Korad KA3005D, UNI-T, Owon u otra similar).
14. Multímetro UNI-T UT61E+ original (tienda oficial UNI-T o importador autorizado).

Al final armá una tabla con: ítem, link, marca y número de parte, precio, vendedor, cómo se confirma que es original, envío, y el total. Agrupá por vendedor para ahorrar envíos y marcá en rojo los ítems que no pudiste confirmar como originales.
```
