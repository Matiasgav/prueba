# Informe — Oportunidades de robótica de inspección industrial

Informe profesional en dos formatos, generados desde una única fuente.

## Entregables

| Archivo | Descripción |
|---|---|
| `informe_robotica_inspeccion.html` | Informe HTML autocontenido: índice lateral con seguimiento de sección, resumen ejecutivo con indicadores, tarjetas comparativas, llamados tipificados, distintivos de nivel de evidencia y madurez, 16 figuras SVG embebidas, tablas con encabezado fijo y hoja de estilos de impresión. |
| `informe_robotica_inspeccion.tex` | Fuente LaTeX equivalente (pdfLaTeX + babel español, tcolorbox). |
| `informe_robotica_inspeccion.pdf` | PDF compilado: 47 páginas, sin errores ni *overfull boxes*. |

## Estructura del informe

- **Resumen ejecutivo** — pregunta central, estado de la evidencia, lectura rápida de los siete candidatos, qué no desarrollar e incógnitas que bloquean la decisión.
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
