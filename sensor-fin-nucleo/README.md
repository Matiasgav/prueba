# Sensor de fin de núcleo

Análisis y simulación de un sensor compacto sin contacto que detecte el final de la cara del núcleo del estator, montado en un carro que avanza sobre él.

| Archivo | Contenido |
|---|---|
| `simulador_sensor_fin_nucleo.html` | Página autocontenida, sin dependencias externas: conclusiones, simulación interactiva (borde y ranura), análisis de sensibilidad, tabla comparativa, supuestos, procedimiento de ensayo y fuentes. |
| `datos/*.json` | Curvas digitalizadas con fuente, método e incertidumbre. |
| `herramientas/extraer_curvas.py` | Extrae las curvas vectoriales de los PDF de Vishay. |
| `herramientas/plantilla.html`, `herramientas/construir.py` | Fuente de la página; `python3 herramientas/construir.py` la regenera. |

## Conclusión corta

- **VCNL36829UM**: entrega cuentas de intensidad reflejada, no milímetros. Según la curva de Vishay (tarjeta gris ≈18 % a 940 nm), la señal a 20 mm es ≈3,2 veces menor que a 10 mm. Una mancha que refleje 3,2 veces menos que la cara, o un fondo que refleje 3,2 veces más, da la misma lectura que el escalón. Con una sola lectura no se separan distancia y reflectividad.
- **Ranura de 5 mm**: produce un falso fin con cualquier sensor si el haz entra en ella y su profundidad se parece a la del escalón. Esto lo resuelve la lógica (persistencia a lo largo de un avance mayor que la ranura, o dos sensores separados en x), no la elección del sensor.
- **ToF (VL53L4CD)**: una mancha baja la señal y deja igual la distancia. Es más robusto frente al color, pero no inmune: con retorno débil puede dar un estado inválido, que hay que tratar como fin por seguridad y nunca convertir en una distancia. Su exactitud publicada es ±6–7 mm (1–100 mm, incluye offset y dispersión entre unidades). Para un escalón de 10 mm conviene comparar contra la línea base del mismo sensor.
- **Recomendación**: prototipar con ToF (distancia + estado + tasa de señal) o con un sensor industrial de supresión de fondo (Omron E3T-FL1, 1–15 mm, salida PNP/NPN). Decidir con el ensayo de la página, que mide la reflectividad real a 940 nm.

## Revisión de los datos que se habían dado

| Afirmación previa | Resultado de la verificación contra el fabricante |
|---|---|
| 1,6 × 1,0 × 0,35 mm, VCSEL ~940 nm, ±4,5°, fotodiodo ±60°, ADC 16 bit, hasta 50 mm | Correcto ([datasheet 80580 Rev. 1.1](https://www.vishay.com/docs/80580/vcnl36829um.pdf)). Matices: 940 nm típico (930–955); el fondo de escala es de 14 bit (16 383 cuentas) con PS_IT ≤ 175 µs y de 16 bit solo con PS_IT ≥ 200 µs ([AN 80581](https://www.vishay.com/docs/80581/designing_vcnl36829um_into_an_application.pdf), Tabla 10); los 50 mm se definen con tarjeta gris Kodak, PS_IT 200 µs, 18 mA, ≥960 cuentas delta y sin ventana. |
| Rango de proximidad «hasta 50 mm» | Es un criterio de detección, no una resolución en mm. El sensor no mide distancia. |
| — | Inconsistencias del propio datasheet: la Fig. 11 rotula «20 mA», pero el registro solo llega a 18 mA; las características hablan de I²C a 1 MHz, pero la tabla de tiempos solo llega a 400 kHz; V<sub>PULLUP</sub> mínima 1,08 V en una tabla y 1,2 V en otra. |
| — | No publicado: ruido, repetibilidad y respuesta a reflectividades distintas de la tarjeta gris. La nota de aplicación indica una tolerancia de «alrededor de ±20 %» y una caída a 0,63× a 85 °C. |
| VL53L4CD | Exactitud ±7 mm (blanco 88 %) y ±6 mm (gris 17 %) de 1 a 100 mm, con ≥90 % de los valores dentro ([DS13812 Rev. 3](https://www.st.com/resource/en/datasheet/vl53l4cd.pdf)). Sin datos por debajo del 17 %. El manual UM2931 asigna los estados 1 y 2 de forma contradictoria entre la sección 3.3 y la Tabla 7. |
| QRE1113 | Solo hay una curva de 0 a 5 mm, normalizada a su propio pico ([onsemi Rev. 9](https://www.onsemi.com/download/data-sheet/pdf/qre1113-d.pdf)). No sirve para alturas de 3 a 25 mm sin medirlo. |

La lista completa de fuentes, supuestos y el procedimiento de ensayo están en la propia página.
