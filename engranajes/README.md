# Engranajes cónicos a 90° para la rueda de un carro — torque admisible según Shigley

Torque admisible de cinco pares de engranajes cónicos 1:1 con diámetro exterior ≤ 14 mm:
KG M50S20 (S45C), KG M50B20 (latón), KG M50S25 (S45C), RS PRO 521-5780 (m0,8 z16) y una mitra
a medida m0,6 z21 de SCM415 carburizado (58–62 HRC). Método AGMA para cónicos del cap. 15 de Shigley,
confiabilidad del 95 %, torque en ambos sentidos, servicio normal con torque bajo más picos de 10 s.

## Entregables

| Archivo | Contenido |
|---|---|
| `informe_conicos_m05_z20.pdf` | Informe técnico en LaTeX. |
| `informe_conicos_m05_z20.tex` | Fuente LaTeX generada. |
| `resultados/resultados.json` | Valores intermedios y finales de todos los diseños. |
| `figuras/` | Gráficos (PDF vectorial y PNG). |
| `capturas/` | Recortes de los PDF oficiales de KG con las filas del producto resaltadas. |

## Resultado (N·m por engranaje, R = 0,95, carga alternada, 10 años)

| Diseño | d_a [mm] | Normal 0,5 rpm | Normal 50 rpm | Normal 100 rpm | Pico 0 rpm | Pico 0,5 rpm | Pico 50 rpm | Pico 100 rpm |
|---|---|---|---|---|---|---|---|---|
| KG M50S20, S45C (stock, referencia) | 10,7 | 0,129 | 0,083 | 0,076 | 0,195 | 0,194 | 0,147 | 0,133 |
| KG M50B20, latón C3604B (stock) | 10,7 | 0,063 | 0,040 | 0,039 | 0,094 | 0,094 | 0,071 | 0,065 |
| KG M50S25, S45C (stock) | 13,2 | 0,218 | 0,140 | 0,135 | 0,328 | 0,327 | 0,246 | 0,224 |
| RS PRO 521-5780, m0,8 z16, S45C (stock) | 13,9 | 0,294 | 0,164 | 0,148 | 0,407 | 0,405 | 0,332 | 0,302 |
| A medida m0,6 z21, SCM415 carburizado 58-62 HRC | 13,4 | 0,778 | 0,499 | 0,481 | 1,171 | 1,167 | 0,878 | 0,798 |

## Regenerar

```bash
tools/descargar_fuentes.sh      # PDF oficiales de KG (no versionados)
python3 tools/capturas.py       # recortes del catálogo
python3 tools/calculo.py        # cálculo, resultados.json y figuras
python3 tools/informe_tex.py    # .tex (con tools/preambulo.tex) y compilación con pdflatex
```

Requiere `pip install matplotlib numpy pymupdf` y TeX Live (`texlive-latex-recommended`,
`texlive-latex-extra`, `texlive-lang-spanish`, `texlive-science`).
