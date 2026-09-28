# Informe — Oportunidades de robótica de inspección industrial

Informe profesional en dos formatos, generados desde una única fuente.

## Entregables

| Archivo | Descripción |
|---|---|
| `informe_robotica_inspeccion.html` | Informe HTML autocontenido: índice lateral con seguimiento de sección, resumen ejecutivo con indicadores, tarjetas comparativas, llamados tipificados, distintivos de nivel de evidencia y madurez, 17 figuras SVG embebidas, tablas con encabezado fijo y hoja de estilos de impresión. |
| `informe_robotica_inspeccion.tex` | Fuente LaTeX equivalente (pdfLaTeX + babel español, tcolorbox). |
| `informe_robotica_inspeccion.pdf` | PDF compilado: 47 páginas, sin errores ni *overfull boxes*. |

## Estructura del informe

- **Resumen ejecutivo** — pregunta central, estado de la evidencia, lectura rápida de los ocho candidatos, qué no desarrollar e incógnitas que bloquean la decisión.
- **Parte I — Marco de decisión** — objetivo, lógica económica del producto de referencia, disciplina de evidencia (clases A–D, jerarquía de fuentes, reglas de verificación, escala de madurez) y proceso de evaluación.
- **Parte II — Mapa de oportunidades** — ficha por candidato (A a H) con esquema del activo, evidencia, competencia, pregunta estratégica y agenda de verificación; mercados con madurez probablemente alta; barrido de oportunidades fuera de la lista.
- **Parte III — Método y economía** — ficha estándar de 23 campos, dimensionamiento bottom-up, economía del cliente, rankings y sensibilidad, patentes y competidores, Argentina y Latinoamérica, costos de desarrollo.
- **Parte IV — Entregables y cierre** — estructura y requisitos del informe final, preguntas a responder, programa de entrevistas, criterio de finalización y conclusión operativa.
- **Anexos** — paquete de fuentes verificado con direcciones, registro de hallazgos iniciales y **glosario con la fuente de cada definición**: 20 términos de negocio y 22 términos técnicos, cada uno con la obra o el organismo donde puede verificarse, o declarado explícitamente como definición operativa del informe cuando no existe definición normativa. La primera aparición de cada término en el texto enlaza a su entrada.

## Fuente y generación

| Archivo | Función |
|---|---|
| `source/informe.md` | Texto del informe, con bloques propios (`::: nota`, `::: kpi`, `::: fig`, `::: tarjetas`, `::: detalle`) y distintivos en línea (`{{ev:A}}`, `{{mad:M4}}`). |
| `source/material-de-partida.md` | Material de trabajo original del que deriva el contenido. |
| `source/registro-investigacion.md` | Bitácora del barrido ampliado de oportunidades: consultas, hallazgos con fuente y nivel, y pistas descartadas. |
| `tools/md2report.py` | Compone el HTML y el LaTeX desde `source/informe.md`. |
| `tools/make_figures.py` | Genera las 17 figuras en SVG (y en PDF para LaTeX). |
| `assets/` | Figuras generadas: 9 gráficos y esquemas de método, 8 esquemas de activos. |

Las figuras son originales. Los gráficos con datos llevan la fuente al pie; los esquemas de activo están marcados como esquema del autor y no están a escala. La paleta de los gráficos está validada para daltonismo y contraste sobre fondo claro, y las 17 figuras se revisaron una por una en render para descartar colisiones de etiquetas, texto recortado y jerga sin desarrollar.

## Regenerar

```bash
python3 tools/make_figures.py --pdf        # figuras SVG + PDF
python3 tools/md2report.py source/informe.md \
        informe_robotica_inspeccion.html \
        informe_robotica_inspeccion.tex
pdflatex informe_robotica_inspeccion.tex   # tres veces, por el índice
```

Paquetes LaTeX requeridos (TeX Live): `texlive-latex-recommended`,
`texlive-latex-extra`, `texlive-lang-spanish`, `texlive-fonts-recommended`.
Para exportar las figuras a PDF: `pip install cairosvg`.

---

# Memoria técnica — Selección del LED OSLON SSL 80

Segundo informe generado con la misma herramienta: justifica la selección del
LED **ams OSRAM OSLON SSL 80, GW CS8PM1.PM, 5000 K, bin LUMQ** para el módulo
de iluminación compacto (conducto de aluminio de Ø 5 × 7 mm) del robot de
almacenamiento de medicamentos.

| Archivo | Descripción |
|---|---|
| `informe_led_oslon_ssl80.html` | Informe HTML autocontenido, con 15 figuras embebidas. |
| `informe_led_oslon_ssl80.tex` / `.pdf` | Versión LaTeX y PDF compilado (23 páginas). |
| `source/informe_led_oslon_ssl80.md` | Fuente del informe. |
| `tools/led_montecarlo.py` | Cálculo óptico: captura directa y Monte Carlo del conducto (pared difusa y especular). |
| `tools/led_figures.py` | Tres figuras propias y doce capturas recortadas del datasheet oficial v1.10. |

El informe incluye el resumen ejecutivo, los requisitos frente al cumplimiento
del LED, las características eléctricas, ópticas, térmicas y mecánicas, la
comparación con otras alternativas, el driver recomendado, el cálculo óptico con
análisis de sensibilidad, los riesgos, el abastecimiento, el plan de prototipo y
las fuentes consultadas.

```bash
pip install numpy pymupdf cairosvg
python3 tools/led_figures.py              # descarga el datasheet a tools/.cache/
python3 tools/md2report.py source/informe_led_oslon_ssl80.md \
        informe_led_oslon_ssl80.html informe_led_oslon_ssl80.tex
pdflatex informe_led_oslon_ssl80.tex      # tres veces
python3 tools/led_montecarlo.py           # tablas de eficiencia del conducto
```

`tools/md2report.py` acepta ahora las claves `encabezado` y `aviso` en la
cabecera de la fuente, y un ancho opcional por figura
(`::: fig id | epígrafe | fuente | 0.6`).
