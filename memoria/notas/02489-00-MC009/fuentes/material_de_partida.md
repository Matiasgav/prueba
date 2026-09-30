# Especificación técnica para informe: geometría de ranuras estatóricas en generadores >20 MW

**Fecha de preparación:** 2026-09-30  
**Objetivo del documento:** servir como entrada técnica para generar un informe formal y trazable sobre la geometría de ranuras estatóricas en grandes generadores eléctricos, discriminando **hidrogeneradores** y **turbogeneradores**, con foco en el diseño de un equipo/robot que debe desplazarse o sensar sobre la superficie del estator.

---

# 1. Objetivo del informe a generar

El informe final debe responder, con evidencia verificable, las siguientes preguntas:

1. Para generadores de **20 MW o más**, ¿qué rango puede adoptar la relación entre:
   - ancho de ranura estatórica `b_s`
   - paso de ranura `τ_s`

   es decir:

   \[
   k_s=\frac{b_s}{\tau_s}
   \]

2. ¿Ese rango es diferente para:
   - **hidrogeneradores** de polos salientes;
   - **turbogeneradores** de rotor cilíndrico?

3. ¿Qué **ancho absoluto de ranura en mm** puede encontrarse?
   - valor típico;
   - mayor valor documentado;
   - envolvente conservadora para diseño mecánico/sensado.

4. ¿Qué **paso de ranura** puede encontrarse?

5. ¿Cuántas **ranuras estatóricas `Q_s`** puede tener una máquina grande?
   - rango observado en máquinas reales;
   - relación con el número de polos y las ranuras por polo y fase.

6. Determinar qué afirmaciones pueden considerarse:
   - **hechos de máquinas reales**;
   - **reglas de diseño**;
   - **envolventes de ingeniería recomendadas**;
   - y qué NO puede presentarse como un límite normativo garantizado.

---

# 2. Alcance

El estudio debe centrarse en máquinas síncronas industriales de potencia nominal igual o superior a aproximadamente **20 MW**.

Separar explícitamente:

## 2.1 Hidrogeneradores

Principalmente:

- generadores síncronos de polos salientes;
- turbinas Francis, Kaplan, Pelton y tubulares;
- generadores-motores de centrales reversibles cuando sean comparables;
- grandes velocidades bajas/medias;
- número elevado de polos.

## 2.2 Turbogeneradores

Principalmente:

- generadores síncronos de rotor cilíndrico;
- accionados por turbinas de vapor o gas;
- 2 polos o 4 polos en la mayoría de los casos;
- grandes potencias y alta velocidad;
- refrigeración por aire, hidrógeno y/o agua.

No mezclar ambos tipos en un único rango sin mostrar primero las diferencias.

---

# 3. Definiciones geométricas obligatorias

Debe usarse una nomenclatura consistente.

## 3.1 Paso de ranura

Para un estator de diámetro interior `D_i` y `Q_s` ranuras:

\[
\tau_s=\frac{\pi D_i}{Q_s}
\]

donde:

- `τ_s`: paso circunferencial de ranura [mm];
- `D_i`: diámetro interior del estator [mm];
- `Q_s`: número total de ranuras estatóricas.

Esta expresión es válida como aproximación del paso lineal en el diámetro interior.

---

## 3.2 Relación ranura/paso

Definir:

\[
k_s=\frac{b_s}{\tau_s}
\]

donde `b_s` debe ser el **ancho del cuerpo de la ranura medido circunferencialmente en un radio definido**, preferentemente cerca de la parte superior de la ranura.

Expresar también como porcentaje:

\[
k_s[\%]=100\frac{b_s}{\tau_s}
\]

---

## 3.3 Ancho de diente

Si `b_t` y `b_s` se miden al mismo radio y la geometría puede aproximarse localmente como recta:

\[
b_t+b_s\approx\tau_s
\]

por lo tanto:

\[
\frac{b_t}{\tau_s}+\frac{b_s}{\tau_s}\approx1
\]

Esta relación NO debe aplicarse sin aclaraciones a geometrías con:
- ranura trapezoidal;
- dientes no paralelos;
- tooth tips;
- wedge seats;
- boca de ranura estrecha.

---

# 4. Distinción crítica: ancho de ranura vs. boca de ranura

No confundir:

- `b_s`: ancho del cuerpo de la ranura;
- `b_so`: **slot opening**, boca de ranura visible desde el entrehierro;
- ancho del wedge;
- ancho superior/inferior de una ranura trapezoidal.

Una ranura puede tener un cuerpo de 20–70 mm y una abertura superficial sensiblemente menor.

Para el robot esto es crítico: si el sensor observa directamente la superficie del estator, puede estar midiendo la **slot opening** o el wedge, no necesariamente `b_s`.

El informe debe incluir un esquema como:

```text
                  ENTREHIERRO
   ──────────────────────────────────
        diente        diente
          │            │
          │<- b_so ->  │       <- boca visible
          └────┐  ┌────┘
               │  │
             ┌─┘  └─┐
             │      │
             │ b_s  │           <- cuerpo de ranura
             │      │
             └──────┘
```

Si las fuentes sólo dicen "slot width", indicar explícitamente que se está interpretando como ancho de cuerpo de ranura y no como abertura.

---

# 5. Relación entre polos, ranuras y ranuras/polo/fase

Para una máquina trifásica:

\[
Q_s=mPq
\]

donde:

- `m = 3`;
- `P`: número de polos;
- `q`: ranuras por polo y por fase.

Si `p` es el número de pares de polos:

\[
Q_s=2pmq=6pq
\]

Esto explica la diferencia estructural entre hidro y turbo:

- hydro: muchos polos → normalmente cientos de ranuras;
- turbo: 2 o 4 polos → normalmente decenas de ranuras, aunque el valor depende fuertemente del diseño.

Para devanados fraccionarios, `q` puede no ser entero.

---

# 6. Evidencia de HIDROGENERADORES

## 6.1 Máquina tubular específica de 34 MW

**Fuente:** Zhen et al., *Effect of different types of damping winding structures on the no-load magnetic field of a tubular hydro-generator*, Archives of Electrical Engineering, 2025.  
DOI: `10.24425/aee.2025.155959`

URL:
https://journals.pan.pl/Content/136333/06_2k.pdf

Parámetros publicados:

- potencia: 34 MW;
- 44 polos;
- 2 ranuras por polo y fase;
- 3 fases;
- diámetro interior de estator: 5620 mm;
- ancho de ranura estatórica: 28 mm.

Número de ranuras:

\[
Q_s=44\cdot3\cdot2=264
\]

Paso:

\[
\tau_s=\frac{\pi\cdot5620}{264}=66.88\text{ mm}
\]

Relación:

\[
k_s=\frac{28}{66.88}=0.4187
\]

\[
\boxed{k_s=41.9\%}
\]

**Clasificación de evidencia:** máquina específica publicada; geometría explícita.

---

## 6.2 Hydro-Québec Manic-2, 122.6 / 150.7 MVA

**Fuente:** Aguiar, Merkhouf, Al-Haddad, *Open-Circuit and Short-Circuit Core Losses Computation in a Large Hydro Generator*, IEEE IECON 2013.  
DOI: `10.1109/IECON.2013.7163454`

URL de acceso:
https://www.researchgate.net/publication/299446934_Open-Circuit_and_Short-Circuit_Core_Losses_Computation_in_a_Large_Hydro_Generator

Parámetros publicados:

- 122.6 / 150.7 MVA;
- 60 polos;
- 504 ranuras;
- `D_i = 10617.2 mm`;
- `b_s = 23.24 mm`;
- altura de ranura 159 mm;
- máquina de Hydro-Québec;
- estator rehabilitado en 2009;
- resultados comparados con datos reales.

Cálculo:

\[
\tau_s=\frac{\pi\cdot10617.2}{504}=66.18\text{ mm}
\]

\[
k_s=\frac{23.24}{66.18}=0.3512
\]

\[
\boxed{k_s=35.1\%}
\]

**Clasificación de evidencia:** máquina real; alta relevancia.

---

## 6.3 CB 870/300-28, hidrogenerador existente de 250 MW

**Fuente:** C. Carunaiselvane, T. R. Chelliah, D. Khare, *Temperature Distribution of 250 MW Hydro Turbine Synchronous Generator at Continuous Overloading Conditions*, IEEE PEDES 2018.  
DOI: `10.1109/PEDES.2018.8707684`

URL:
https://www.researchgate.net/publication/332982043_Temperature_Distribution_of_250_MW_Hydro_Turbine_Synchronous_Generator_at_Continuous_Overloading_Conditions

El artículo dice explícitamente que el modelo replica un generador **CB 870/300-28 existente**, empleado en grandes centrales hidroeléctricas de India.

Parámetros:

- potencia: 250 MW;
- 28 polos;
- 348 ranuras estatóricas;
- radio interior del estator: 7909.9 mm;
- por lo tanto `D_i = 15819.8 mm`;
- ancho de ranura: 27.9 mm;
- altura de ranura: 209.9 mm.

Paso:

\[
\tau_s=\frac{\pi\cdot15819.8}{348}=142.81\text{ mm}
\]

Relación:

\[
k_s=\frac{27.9}{142.81}=0.1954
\]

\[
\boxed{k_s=19.5\%}
\]

**Clasificación de evidencia:** máquina existente; artículo IEEE; validación con datos operativos.  
**Muy importante:** este caso demuestra que el paso puede ser mucho mayor que los rangos simplificados de algunos textos de diseño.

---

## 6.4 Generador-motor reversible de 145 MW / 170 MW

**Fuente:** Zhang et al., *Coupled Electromagnetic–Fluid–Thermal Analysis of a Fully Air-Cooled Pumped Storage Generator Motor*, Machines 2023, 11, 901.  
DOI: `10.3390/machines11090901`

URL:
https://www.mdpi.com/2075-1702/11/9/901

El trabajo declara que el modelo está basado en una **máquina real**.

Datos:

- generación: 145 MW;
- bombeo: 170 MW;
- 360 ranuras;
- 30 pares de polos / 30 polos según tabla del artículo; verificar terminología exacta al redactar;
- `D_i = 7240 mm`;
- ancho de ranura: 24.5 mm;
- altura de ranura: 159.5 mm.

Cálculo:

\[
\tau_s=\frac{\pi\cdot7240}{360}=63.18\text{ mm}
\]

\[
k_s=\frac{24.5}{63.18}=0.3878
\]

\[
\boxed{k_s=38.8\%}
\]

**Clasificación:** máquina real / modelo contrastado con mediciones.

---

## 6.5 Gezhouba, SF150-96/15600, 150 MW

**Fuente:** *Research on Non-destructive Intelligence Detection of Tightness of Stator Slot Wedges of Large Hydro-generator*.

URL de acceso:
https://www.researchgate.net/publication/369359836_Research_on_Non-destructive_Intelligence_Detection_of_Tightness_of_Stator_Slot_Wedges_of_Large_Hydro-generator

Datos publicados:

- modelo: SF150-96/15600;
- potencia: 150 MW;
- ancho de ranura: **30 mm**.

La fuente no entrega en la tabla citada todos los datos necesarios para calcular de forma inequívoca `τ_s`, por lo que:

- utilizarla como evidencia de **ancho absoluto**;
- NO utilizarla para calcular `b_s/τ_s` sin conseguir `Q_s` y `D_i` en otra fuente.

\[
\boxed{b_s=30\text{ mm}}
\]

Hasta el momento, es el mayor ancho de ranura hidro explícito encontrado en la muestra de máquinas reales consultada.

---

## 6.6 Hidrogenerador de 95.5 MVA – dos configuraciones publicadas

**Fuente:** *Electromagnetic Forces on Coils and Bars Inside the Slot of Hydro-Generator*.

URL:
https://us.v-cdn.net/6038102/uploads/attachments/d6c0d22e1b6ad0108017dc61ec4bcb83/Electromagnetic%20Forces%20on%20Coils%20and%20Bars%20inside%20the%20Slot%20of%20Hydro-Generator.pdf

Casos reportados:

### Caso 1
- 95.5 MVA;
- 432 ranuras;
- ancho de ranura: 24.76 mm.

### Caso 2
- 95.5 MVA;
- 576 ranuras;
- ancho de ranura: 23.19 mm.

No se dispone en el fragmento consultado de `D_i`, por lo cual usar sólo como evidencia de:
- ancho absoluto;
- número de ranuras.

---

## 6.7 Itaipú – 700 MW por unidad

Fuente técnica sobre descargas parciales en los generadores de Itaipú:

URL:
https://pt.scribd.com/document/357546540/DESCARGAS-PARCIAIS-EM-GERADORES-A-EXPERIE-NCIA-DE-ITAIPU1-pdf

Datos reportados:

- potencia: 700 MW por unidad;
- 504 ranuras;
- diámetro interior del estator: aproximadamente 16 m;
- 50 Hz: 66 polos;
- 60 Hz: 78 polos.

Paso aproximado:

\[
\tau_s=\frac{\pi\cdot16000}{504}=99.73\text{ mm}
\]

No se encontró en esta fuente el ancho de ranura, por lo que NO calcular `k_s`.

Usar como evidencia de:
- tamaño real;
- `Q_s`;
- paso de ranura del orden de 100 mm.

Fuente oficial de potencia de las unidades:
https://www.itaipu.gov.py/energia/generacion/casa-de-maquinas

---

## 6.8 Máquinas hidro de 1000 MW: evidencia de número de ranuras

### Caso A

**Fuente:** *Effect of Generator Rotor Radial Deviation on the Unbalanced Magnetic Pull of 1000 MW Hydro-Generator Unit*, Processes 2023.

URL:
https://www.mdpi.com/2227-9717/11/3/899

Datos:

- 1000 MW;
- 54 polos;
- 810 ranuras;
- diámetro interior reportado: aproximadamente 17.5 m.

Paso aproximado:

\[
\tau_s\approx67.9\text{ mm}
\]

### Caso B

**Fuente:** *Study of Unsymmetrical Magnetic Pulling Force and Magnetic Moment in 1000 MW Hydrogenerator Based on Finite Element Analysis*, 2024.

URL:
https://www.researchgate.net/publication/384860410_Study_of_Unsymmetrical_Magnetic_Pulling_Force_and_Magnetic_Moment_in_1000_MW_Hydrogenerator_Based_on_Finite_Element_Analysis

Datos:

- 1000 MW;
- 56 polos;
- 696 ranuras;
- `D_i = 16580 mm`.

Paso:

\[
\tau_s=\frac{\pi\cdot16580}{696}=74.84\text{ mm}
\]

Estas máquinas sirven principalmente para justificar que un gran hydro puede tener del orden de **700–800 ranuras**.

---

# 7. Conclusión preliminar para HIDRO

Máquinas para las cuales se pudo calcular de forma directa `b_s/τ_s`:

| Máquina | Potencia | Qs | Di [mm] | bs [mm] | τs [mm] | bs/τs |
|---|---:|---:|---:|---:|---:|---:|
| Tubular | 34 MW | 264 | 5620 | 28.0 | 66.88 | 41.9 % |
| Manic-2 | 122.6/150.7 MVA | 504 | 10617.2 | 23.24 | 66.18 | 35.1 % |
| Reversible | 145 MW | 360 | 7240 | 24.5 | 63.18 | 38.8 % |
| CB 870/300-28 | 250 MW | 348 | 15819.8 | 27.9 | 142.81 | 19.5 % |

Rango directamente observado en esta muestra:

\[
\boxed{0.195\leq b_s/\tau_s\leq0.419}
\]

o:

\[
\boxed{19.5\%-41.9\%}
\]

### Envolvente de ingeniería preliminar recomendada para Hydro

No presentarla como norma ni como garantía universal.

\[
\boxed{0.15\leq b_s/\tau_s\leq0.50}
\]

La intención del margen es cubrir variaciones no representadas en la muestra.

---

# 8. Anchos absolutos observados en HYDRO

Valores explícitos encontrados:

- 23.19 mm — 95.5 MVA;
- 23.24 mm — Manic-2;
- 24.5 mm — reversible 145 MW;
- 24.76 mm — 95.5 MVA;
- 27.9 mm — CB 870/300-28, 250 MW;
- 28 mm — tubular 34 MW;
- 30 mm — Gezhouba SF150-96/15600, 150 MW.

Por lo tanto, en la muestra consultada:

\[
\boxed{b_s\approx23-30\text{ mm}}
\]

es el rango **directamente observado** de ancho de ranura hidro.

Esto NO significa que 30 mm sea el máximo físico mundial.

### Mayor paso hidro directamente calculado en la muestra

CB 870/300-28:

\[
\boxed{\tau_s=142.8\text{ mm}}
\]

Combinando conservadoramente:

\[
b_s=k_s\tau_s
\]

con la envolvente propuesta `k_s ≤ 0.50` y `τ_s ≈ 150 mm`:

\[
b_{s,\text{env}}\approx75\text{ mm}
\]

Por ello puede considerarse, **sólo como envolvente mecánica preliminar para el robot**:

\[
\boxed{b_s\lesssim75\text{ mm para hydro}}
\]

Debe marcarse claramente:

- **30 mm:** máximo explícitamente encontrado hasta ahora en máquinas hydro consultadas;
- **75 mm:** límite derivado conservador, NO una ranura real observada.

---

# 9. Número de ranuras observado en HYDRO

Ejemplos publicados:

- 264 — tubular 34 MW;
- 348 — 250 MW;
- 360 — reversible 145 MW;
- 432 / 576 — máquina de 95.5 MVA, según configuración;
- 504 — Manic-2;
- 504 — Itaipú 700 MW;
- 696 — hydro 1000 MW;
- 810 — hydro 1000 MW.

Muestra observada:

\[
\boxed{264\leq Q_s\leq810}
\]

No presentarlo como mínimo/máximo universal.

La relación de diseño:

\[
Q_s=mPq
\]

permite que máquinas con muchos polos alcancen varios cientos de ranuras con facilidad.

---

# 10. Evidencia de TURBOGENERADORES

## 10.1 Familia de diseños de 250 MW con diferentes refrigeraciones

**Fuente:** Minko, A.; Shevchenko, V., *Turbogenerators of New Generation with Various Cooling Systems*, 2018.

DOI de registro:
`10.5281/zenodo.2636460`

PDF:
https://web.kpi.kharkov.ua/elmash/wp-content/uploads/sites/108/2019/02/2018_24.pdf

La publicación indica que los parámetros se basan en:
- estudios teóricos;
- experiencia práctica de diseño de turbogeneradores;
- análisis de literatura técnica.

Tres variantes, todas de 250 MW, 15.75 kV, cosφ=0.85, `p=1` par de polos.

### Variante A — aire / aire / aire

Datos:

- `Q_s = 72`;
- ancho de ranura: 27 mm;
- rotor: 1200 mm;
- entrehierro unilateral: 50 mm.

Aproximación:

\[
D_i\approx1200+2\cdot50=1300\text{ mm}
\]

Paso:

\[
\tau_s=\frac{\pi\cdot1300}{72}=56.72\text{ mm}
\]

Relación:

\[
k_s=27/56.72=0.476
\]

\[
\boxed{k_s=47.6\%}
\]

---

### Variante B — H₂ / H₂ / H₂

Datos:

- `Q_s = 60`;
- ancho: 38.6 mm;
- rotor: 1075 mm;
- gap unilateral: 100 mm.

\[
D_i\approx1275\text{ mm}
\]

\[
\tau_s=\frac{\pi\cdot1275}{60}=66.76\text{ mm}
\]

\[
k_s=\frac{38.6}{66.76}=0.578
\]

\[
\boxed{k_s=57.8\%}
\]

---

### Variante C — H₂ / agua / H₂

Datos:

- `Q_s = 30`;
- ancho: 50.8 mm;
- rotor: 1120 mm;
- gap unilateral: 77.5 mm.

\[
D_i\approx1120+2(77.5)=1275\text{ mm}
\]

\[
\tau_s=\frac{\pi\cdot1275}{30}=133.52\text{ mm}
\]

\[
k_s=\frac{50.8}{133.52}=0.380
\]

\[
\boxed{k_s=38.0\%}
\]

**Nota:** estos son diseños técnicos publicados, no deben describirse automáticamente como tres máquinas específicas instaladas.

---

## 10.2 QFSN-600-2YHG, 600 MW / 667 MVA

**Fuente:** Jiang et al., *Effect of Static Rotor Eccentricity on End Winding Forces and Vibration Wearing*, International Journal of Rotating Machinery, 2021.  
DOI: `10.1155/2021/5554914`

URL:
https://onlinelibrary.wiley.com/doi/10.1155/2021/5554914

Datos:

- 667 MVA;
- aproximadamente 600 MW;
- 3000 rpm;
- 2 polos;
- `Q_s = 42`;
- `D_i = 1316 mm`;
- dimensiones de ranura estatórica: `160 × 70 mm`.

Interpretación:

- el paso en el bore es:

\[
\tau_s=\frac{\pi\cdot1316}{42}=98.44\text{ mm}
\]

- por lo tanto la dimensión circunferencial NO puede ser 160 mm, porque sería mayor que el propio paso;
- se interpreta razonablemente:
  - profundidad radial ≈160 mm;
  - ancho circunferencial ≈70 mm.

Entonces:

\[
k_s=\frac{70}{98.44}=0.711
\]

\[
\boxed{k_s\approx71.1\%}
\]

Este es actualmente el **mayor cociente documentado** encontrado dentro de la búsqueda.

También es el mayor ancho estatórico explícito encontrado:

\[
\boxed{b_s=70\text{ mm}}
\]

El informe final debe intentar confirmar esta orientación de `160×70 mm` mediante:
- dibujo;
- segunda fuente;
- otra publicación del mismo modelo.

---

## 10.3 Turbogenerador de 30 MVA con relación impuesta de 0.15

**Fuente:** *Analysing the Impact of Frequency Bands on Partial Discharge Measurement Outcomes in Generators Through Model-Based Approach*, High Voltage, 2026.

URL:
https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/hve2.70118

El diseño adopta explícitamente:

\[
b_s=0.15\tau_s
\]

y obtiene:

\[
b_s=0.024\text{ m}=24\text{ mm}
\]

Por tanto:

\[
\boxed{k_s=15\%}
\]

Este caso es importante como evidencia de metodología de diseño, pero debe etiquetarse como:
- diseño publicado;
- no necesariamente máquina comercial instalada.

---

## 10.4 Turbogenerador de 247 MVA

**Fuente:** Hanic et al., *Computationally efficient finite-element-based methods for the calculation of symmetrical steady-state load conditions for synchronous generators*, IET Electric Power Applications, 2014.

URL:
https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/iet-epa.2014.0040

Datos del turbogenerador:

- 247 MVA;
- 2 polos;
- 3000 rpm;
- 60 ranuras estatóricas;
- stack 3700 mm;
- entrehierro 80 mm.

No se entrega ancho de ranura en la tabla citada.

Usar como evidencia de:

\[
\boxed{Q_s=60}
\]

para un turbogenerador industrial grande.

---

## 10.5 Turbogenerador de 1000 MW

**Fuente:** estudio de dinámica del núcleo estatórico de turbogenerador de 1000 MW.

URL:
https://www.wseas.org/multimedia/journals/mechanics/2015/a165711-205.pdf

Datos:

- 1000 MW;
- 36 ranuras estatóricas;
- `D_i = 1471 mm`;
- altura de ranura: 160 mm.

Paso:

\[
\tau_s=\frac{\pi\cdot1471}{36}=128.37\text{ mm}
\]

No se obtuvo el ancho de ranura, por lo cual NO calcular `k_s`.

Este caso prueba que en un turbo de muy gran potencia puede haber:

\[
\boxed{Q_s=36}
\]

y un paso superior a 120 mm.

---

# 11. Conclusión preliminar para TURBO

Puntos con relación `b_s/τ_s` disponible:

| Caso | Potencia | Qs | bs [mm] | τs [mm] | bs/τs |
|---|---:|---:|---:|---:|---:|
| Diseño publicado | 30 MVA | — | 24 | 160 | 15.0 % |
| 250 MW, aire | 250 MW | 72 | 27 | 56.72 | 47.6 % |
| 250 MW, H₂ | 250 MW | 60 | 38.6 | 66.76 | 57.8 % |
| 250 MW, H₂/agua/H₂ | 250 MW | 30 | 50.8 | 133.52 | 38.0 % |
| QFSN-600-2YHG | 600 MW | 42 | 70 | 98.44 | 71.1 % |

Rango respaldado por la evidencia recopilada:

\[
\boxed{0.15\leq b_s/\tau_s\leq0.711}
\]

o:

\[
\boxed{15\%-71.1\%}
\]

### Envolvente de ingeniería preliminar para turbo

\[
\boxed{0.12\leq b_s/\tau_s\leq0.75}
\]

No denominar este intervalo “límite normativo”.

---

# 12. Anchos absolutos observados en TURBO

Ejemplos:

- 24 mm — diseño 30 MVA;
- 27 mm — diseño 250 MW aire;
- 38.6 mm — diseño 250 MW H₂;
- 50.8 mm — diseño 250 MW H₂/agua/H₂;
- **70 mm — QFSN-600-2YHG, 600 MW**.

Actualmente:

\[
\boxed{b_{s,\max,\text{encontrado}}=70\text{ mm}}
\]

para un turbogenerador >20 MW de la evidencia recopilada.

Esto es un **máximo observado en la búsqueda**, no un máximo físico garantizado.

---

# 13. Paso de ranura en TURBO

Valores calculados:

- 56.7 mm — 250 MW, 72 slots;
- 66.8 mm — 250 MW, 60 slots;
- 98.4 mm — 600 MW, 42 slots;
- 128.4 mm — 1000 MW, 36 slots;
- 133.5 mm — 250 MW, 30 slots;
- 160 mm — diseño publicado de 30 MVA con `b_s/τ_s = 0.15`.

Por lo tanto, las reglas clásicas de “25–60 mm” o “75–90 mm en máquinas grandes” son útiles como orientación histórica, pero NO deben presentarse como límites duros para máquinas modernas.

---

# 14. Número de ranuras observado en TURBO

Evidencia recopilada:

- 30 — diseño 250 MW;
- 36 — turbo 1000 MW;
- 42 — QFSN-600-2YHG 600 MW;
- 60 — 247 MVA;
- 60 — diseño 250 MW;
- 72 — diseño 250 MW.

Muestra:

\[
\boxed{30\leq Q_s\leq72}
\]

No es un rango normativo.

---

# 15. Evidencia de reglas de diseño

Una referencia de diseño de máquinas síncronas señala:

- `q` normalmente entre 2 y 4;
- en turbogeneradores puede alcanzar aproximadamente 8 o 9;
- la densidad de flujo en dientes a vacío no debe exceder aproximadamente `1.8 T`.

Fuente:
https://www.uni-kassel.de/upress/online/frei/978-3-86219-018-8.volltext.frei.pdf

Esto explica físicamente por qué el ancho de diente no puede reducirse arbitrariamente:

\[
B_t\uparrow \quad\text{cuando}\quad b_t\downarrow
\]

y, en términos simplificados:

\[
b_s\approx\tau_s-b_t
\]

Por lo tanto existe un compromiso entre:

- área de cobre disponible;
- densidad de corriente;
- saturación de dientes;
- pérdidas;
- refrigeración;
- aislamiento;
- resistencia mecánica;
- reactancias;
- armónicos.

El informe debe utilizar estas reglas como **justificación física**, no como prueba suficiente de un rango absoluto.

---

# 16. Evidencia de que la geometría NO está universalmente normalizada

## 16.1 IEC 60034-33

IEC 60034-33:2022 cubre específicamente:

- generadores síncronos de polos salientes;
- aplicaciones hidráulicas;
- 50/60 Hz;
- 10 MVA o más;
- 6 kV o más.

Página oficial:
https://webstore.iec.ch/en/publication/30487

## 16.2 IEC 60034-3

IEC 60034-3:2020 cubre:

- grandes generadores síncronos;
- accionados por turbinas de vapor o gas;
- 10 MVA o más.

Página oficial:
https://webstore.iec.ch/en/publication/27156

## 16.3 IEC 60034-1

Norma general de rating y performance de máquinas rotativas:

https://webstore.iec.ch/en/publication/89961

Hasta ahora NO se encontró en estas normas una exigencia pública del tipo:

```text
0.XX < slot width / slot pitch < 0.YY
```

Por lo tanto no afirmar que IEC garantiza un porcentaje mínimo/máximo.

---

# 17. Evidencia del U.S. Bureau of Reclamation

**Hydrogenerator Design Manual**, U.S. Bureau of Reclamation.

URL oficial:
https://www.usbr.gov/tsc/techreferences/mands/mands-pdfs/HydroGen.pdf

El manual explica que parámetros como:

- longitud del núcleo;
- densidad de corriente;
- tensión terminal;
- **slot size**;

son determinados por el fabricante y pueden no estar disponibles para el propietario antes de la licitación.

Esto es evidencia muy importante de que la geometría de ranura es una variable propia del diseño OEM y no un valor universal normalizado.

Extracto localizable en el capítulo 8:
> core length, current density, terminal voltage, and slot size are used to determine if single-turn configuration is practical. These factors are determined by the manufacturer...

No reproducir citas extensas; parafrasear y citar página/capítulo.

---

# 18. Resumen numérico que debe aparecer en el informe final

## 18.1 Relación ancho de ranura / paso

### Hydro — evidencia directa

\[
\boxed{19.5\%-41.9\%}
\]

### Hydro — envolvente preliminar recomendada

\[
\boxed{15\%-50\%}
\]

### Turbo — evidencia publicada recopilada

\[
\boxed{15\%-71.1\%}
\]

### Turbo — envolvente preliminar recomendada

\[
\boxed{12\%-75\%}
\]

Debe usarse terminología exacta:

- “rango observado/publicado”;
- “envolvente de ingeniería”;
- NO “rango garantizado por IEC”.

---

## 18.2 Ancho absoluto

### Hydro

Máximo explícitamente encontrado hasta ahora:

\[
\boxed{30\text{ mm}}
\]

Muestra observada:

\[
\boxed{23-30\text{ mm}}
\]

Envolvente mecánica preliminar derivada para robot:

\[
\boxed{\text{hasta aproximadamente }75\text{ mm}}
\]

Este último valor es una **envolvente conservadora derivada**, no un caso observado.

### Turbo

Máximo explícitamente encontrado:

\[
\boxed{70\text{ mm}}
\]

Muestra publicada:

\[
\boxed{24-70\text{ mm}}
\]

Si se construye una envolvente cartesiana muy conservadora combinando:

\[
\tau_s\leq160\text{ mm}
\]

y

\[
k_s\leq0.75
\]

se obtiene:

\[
b_s\leq120\text{ mm}
\]

Por tanto, para el diseño del robot puede estudiarse:

\[
\boxed{b_s\leq120\text{ mm}}
\]

como límite mecánico provisional para turbo.

**Advertencia:** no existe todavía una máquina de 120 mm de ranura en la evidencia reunida. Es una extrapolación deliberadamente conservadora.

---

## 18.3 Número de ranuras

### Hydro — muestra real/publicada

\[
\boxed{264-810}
\]

### Turbo — muestra consultada

\[
\boxed{30-72}
\]

No presentarlos como límites globales.

---

## 18.4 Paso de ranura

### Hydro

Valores directamente calculados en la muestra principal:

\[
\boxed{\approx63-143\text{ mm}}
\]

### Turbo

Valores encontrados/calculados:

\[
\boxed{\approx57-160\text{ mm}}
\]

---

# 19. Recomendación preliminar para el diseño del robot

Si el robot debe ser compatible con máquinas >20 MW sin conocer previamente el modelo exacto, utilizar dos niveles:

## Nivel A — rango respaldado por máquinas encontradas

### Hydro
- `b_s`: 23–30 mm observado;
- `τ_s`: 63–143 mm observado;
- `b_s/τ_s`: 19.5–41.9 %;
- `Q_s`: 264–810 observado.

### Turbo
- `b_s`: 24–70 mm publicado;
- `τ_s`: 57–160 mm publicado/calculado;
- `b_s/τ_s`: 15–71.1 %;
- `Q_s`: 30–72 en la muestra.

## Nivel B — envolvente conservadora para hardware

Provisionalmente:

### Hydro
- `b_s/τ_s`: 0.15–0.50;
- `τ_s`: aproximadamente 50–150 mm;
- ancho de ranura de diseño: hasta ~75 mm.

### Turbo
- `b_s/τ_s`: 0.12–0.75;
- `τ_s`: aproximadamente 50–160 mm;
- ancho de ranura de diseño: hasta ~120 mm.

Estos valores NO deben congelarse como especificación definitiva sin una segunda campaña de validación con más datos OEM.

---

# 20. Cómo obtener una garantía real para el producto

La investigación actual permite construir una envolvente estadística/de ingeniería, pero no una garantía universal.

Para poder declarar compatibilidad comercial con una máquina concreta, recomendar uno o más de estos mecanismos:

1. Solicitar antes del servicio:
   - fabricante;
   - modelo;
   - potencia;
   - diámetro interior;
   - número de ranuras;
   - plano de stator slot;
   - ancho de wedge / slot opening.

2. Calcular:

\[
\tau_s=\frac{\pi D_i}{Q_s}
\]

y verificar que la máquina cae dentro de la envolvente del robot.

3. Incorporar un escaneo/perfilado previo del estator para reconocer:
   - paso;
   - ancho de diente;
   - ancho visible de wedge/slot;
   - bordes.

4. En una especificación contractual, exigir explícitamente un rango geométrico soportado.

5. No afirmar “compatible con todos los generadores >20 MW” basándose solamente en potencia.

---

# 21. Trabajo adicional que debe hacer el modelo que genere el informe

Antes de cerrar el informe definitivo, realizar una búsqueda adicional focalizada en:

## Hydro

Buscar datos OEM o papers de:

- Itaipú 700 MW;
- Three Gorges 700 MW;
- Baihetan 1000 MW;
- Wudongde 850 MW;
- Xiluodu 770 MW;
- Grand Coulee;
- Guri;
- Salto Grande;
- Yacyretá;
- fabricantes Voith, ANDRITZ, GE Vernova, Hitachi Mitsubishi, Harbin, Dongfang.

Objetivo:
- encontrar `b_s` explícito;
- encontrar `D_i`;
- encontrar `Q_s`;
- calcular `b_s/τ_s`;
- buscar especialmente casos `b_s > 30 mm` o `b_s/τ_s < 0.195` / `> 0.419`.

## Turbo

Buscar datos de:

- 300 MW;
- 500 MW;
- 600/660 MW;
- 800 MW;
- 1000 MW;
- 1100/1200 MW;
- Siemens/Siemens Energy;
- GE;
- Mitsubishi Power;
- BHEL;
- Harbin;
- Dongfang;
- Shanghai Electric.

Objetivo:
- confirmar si existen ranuras estatóricas >70 mm;
- verificar el QFSN-600-2YHG `160×70 mm`;
- encontrar ancho de ranura del turbo de 1000 MW con 36 slots;
- verificar si `b_s/τ_s > 0.71` aparece en otra máquina.

---

# 22. Requisitos de calidad del informe

El informe generado debe:

- citar cada máquina con fuente;
- diferenciar claramente datos medidos/publicados de valores calculados;
- mostrar la fórmula usada para cada cálculo;
- no mezclar slot opening con slot body width;
- no mezclar rotor slots con stator slots;
- indicar si la fuente es:
  - OEM;
  - operador de central;
  - IEEE/IET/MDPI/journal;
  - tesis;
  - material docente;
  - fuente secundaria;
- priorizar fuentes primarias;
- evitar usar ResearchGate como autoridad cuando exista DOI/editorial original;
- marcar explícitamente cualquier interpretación;
- no afirmar límites universales sin norma que los imponga;
- incluir una tabla maestra con todos los casos;
- dar una conclusión para el diseño del robot y otra conclusión puramente electromagnética.

---

# 23. Jerarquía recomendada de evidencia

1. Plano/datasheet OEM o documentación del operador.
2. Paper que describa máquina real e incluya geometría.
3. Paper de diseño industrial basado en práctica OEM.
4. Manual gubernamental / estándar.
5. Libro de diseño reconocido.
6. Tesis.
7. Material docente.
8. Agregadores / Scribd / presentaciones: sólo como pista; buscar fuente original.

---

# 24. Tabla maestra actual

| Tipo | Máquina | Potencia | Qs | Di [mm] | bs [mm] | τs [mm] | bs/τs | Evidencia |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Hydro | Tubular | 34 MW | 264 | 5620 | 28.0 | 66.88 | 41.9 % | paper específico |
| Hydro | Manic-2 | 122.6/150.7 MVA | 504 | 10617.2 | 23.24 | 66.18 | 35.1 % | máquina real |
| Hydro | Pumped-storage | 145 MW | 360 | 7240 | 24.5 | 63.18 | 38.8 % | máquina real/modelo validado |
| Hydro | CB 870/300-28 | 250 MW | 348 | 15819.8 | 27.9 | 142.81 | 19.5 % | máquina existente |
| Hydro | Gezhouba SF150-96/15600 | 150 MW | — | — | 30 | — | — | máquina real, ancho |
| Hydro | caso A | 95.5 MVA | 432 | — | 24.76 | — | — | paper técnico |
| Hydro | caso B | 95.5 MVA | 576 | — | 23.19 | — | — | paper técnico |
| Hydro | Itaipú | 700 MW | 504 | ~16000 | — | 99.73 | — | central real |
| Hydro | 1000 MW A | 1000 MW | 810 | ~17500 | — | ~67.87 | — | paper |
| Hydro | 1000 MW B | 1000 MW | 696 | 16580 | — | 74.84 | — | paper |
| Turbo | diseño 30 MVA | 30 MVA | — | — | 24 | 160 | 15.0 % | diseño publicado |
| Turbo | 250 MW aire | 250 MW | 72 | ~1300 | 27 | 56.72 | 47.6 % | diseño industrial |
| Turbo | 250 MW H₂ | 250 MW | 60 | ~1275 | 38.6 | 66.76 | 57.8 % | diseño industrial |
| Turbo | 250 MW H₂/agua/H₂ | 250 MW | 30 | ~1275 | 50.8 | 133.52 | 38.0 % | diseño industrial |
| Turbo | QFSN-600-2YHG | 600 MW | 42 | 1316 | 70 | 98.44 | 71.1 % | máquina/modelo específico |
| Turbo | 247 MVA | 247 MVA | 60 | — | — | — | — | paper |
| Turbo | 1000 MW | 1000 MW | 36 | 1471 | — | 128.37 | — | paper |

---

# 25. Conclusión técnica que NO debe perderse

El resultado principal no es un único número.

La evidencia indica que:

\[
\boxed{\text{Hydro y Turbo deben tratarse como poblaciones geométricas distintas}}
\]

Para la muestra recopilada:

\[
\boxed{\text{Hydro: }b_s/\tau_s=19.5\%-41.9\%}
\]

\[
\boxed{\text{Turbo: }b_s/\tau_s=15\%-71.1\%}
\]

La diferencia es coherente con:

- cantidad de polos;
- cantidad de ranuras;
- velocidad;
- profundidad de ranura;
- densidad de corriente;
- refrigeración;
- diseño de barras;
- saturación de dientes.

Para el robot debe distinguirse además entre:

\[
\boxed{\text{ancho del cuerpo de ranura}}
\]

y

\[
\boxed{\text{ancho visible de boca/wedge}}
\]

porque el sensor puede interactuar con una geometría diferente de la utilizada en el cálculo electromagnético.

Finalmente:

> **No existe evidencia de una norma IEC que garantice un límite universal de `b_s/τ_s`.**
>
> Los rangos de este documento deben describirse como **rango observado** y **envolvente de ingeniería**, no como “rango obligatorio de todos los generadores”.

