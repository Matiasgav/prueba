# Brief de investigación — Robots de inspección industrial

Conversión del brief original en Markdown a dos formatos de entrega.

## Archivos

| Archivo | Descripción |
|---|---|
| `robot_opportunities_research_brief.html` | Informe HTML autocontenido (un solo archivo, sin dependencias externas): índice lateral fijo con resaltado de sección activa, callouts, tablas con encabezado sticky y scroll horizontal, estilos de impresión. |
| `robot_opportunities_research_brief.tex` | Fuente LaTeX (pdfLaTeX + babel español). Portada, índice con hipervínculos, tablas `longtable` y callouts. |
| `robot_opportunities_research_brief.pdf` | PDF compilado a partir del `.tex` (45 páginas, sin *overfull boxes*). |
| `source/claude_code_robot_opportunities_research_brief.md` | Markdown original, sin modificar. |
| `tools/md2report.py` | Conversor usado para generar ambas salidas desde el Markdown. |

## Regenerar

```bash
python3 tools/md2report.py \
  source/claude_code_robot_opportunities_research_brief.md \
  robot_opportunities_research_brief.html \
  robot_opportunities_research_brief.tex
```

## Compilar el PDF

```bash
pdflatex robot_opportunities_research_brief.tex   # dos veces, para el índice
pdflatex robot_opportunities_research_brief.tex
```

Paquetes requeridos (TeX Live): `texlive-latex-recommended`, `texlive-latex-extra`,
`texlive-lang-spanish`, `texlive-fonts-recommended`.
