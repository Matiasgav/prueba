# Mitras KG m0,5 × 20 a 90° — torque admisible según Shigley

Análisis del par de engranajes cónicos rectos KG (serie M, 1:1) que transmite el giro a la rueda de un carro,
en todos los materiales en que KG ofrece la pieza (S45C, SUS304L MIM, latón C3604B y POM inyectado).
Confiabilidad del 95 %, torque en ambos sentidos, servicio normal con torque bajo más picos ocasionales de 10 s.
Incluye alternativas de mayor capacidad con diámetro exterior ≤ 14 mm y el análisis de lubricación.

## Entregables

| Archivo | Contenido |
|---|---|
| `informe_conicos_m05_z20.pdf` | Informe técnico en LaTeX (17 páginas). |
| `informe_conicos_m05_z20.tex` | Fuente LaTeX generada. |
| `resultados/resultados.json` | Todos los valores intermedios y finales. |
| `figuras/` | Gráficos (PDF vectorial y PNG). |
| `capturas/` | Recortes de los PDF oficiales de KG (filas del producto resaltadas) y láminas de KHK para POM. |

## Resultado (N·m por engranaje, R = 0,95, carga alternada, 10 años)

| Material | Normal 0,5 rpm | Normal 50 rpm | Normal 100 rpm | Pico 0 rpm | Pico 0,5 rpm | Pico 50 rpm | Pico 100 rpm |
|---|---|---|---|---|---|---|---|
| S45C | 0,129 | 0,083 | 0,076 | 0,195 | 0,194 | 0,147 | 0,133 |
| SUS304L MIM | 0,052 | 0,033 | 0,032 | 0,078 | 0,078 | 0,059 | 0,053 |
| Latón C3604B | 0,063 | 0,040 | 0,039 | 0,094 | 0,094 | 0,071 | 0,065 |
| POM inyectado | 0,025 | 0,020 | 0,020 | 0,021 | 0,029 | 0,027 | 0,026 |

## Alternativas con d_a ≤ 14 mm (100 rpm)

| | Producto | Material | d_a [mm] | Normal [N·m] | Pico 10 s [N·m] |
|---|---|---|---|---|---|
| A | Referencia: KG M50S20 | S45C | 10,71 | 0,076 | 0,133 |
| B | KG M50S25 (stock) | S45C | 13,21 | 0,135 | 0,224 |
| C | KG M50B25 (stock) | Latón C3604B | 13,21 | 0,065 | 0,108 |
| D | RS PRO 521-5780 (stock) | S45C | 13,93 | 0,148 | 0,302 |
| E | A medida, S45C | S45C | 13,45 | 0,151 | 0,253 |
| F | A medida, m0,5 carburizado | SCM415 carburizado | 10,71 | 0,254 | 0,421 |
| G | A medida, m0,6 carburizado | SCM415 carburizado | 13,45 | 0,481 | 0,798 |

## Regenerar

```bash
tools/descargar_fuentes.sh      # PDF oficiales de KG (no versionados)
python3 tools/capturas.py       # recortes del catálogo
python3 tools/calculo.py        # cálculo, resultados.json y figuras
python3 tools/informe_tex.py    # .tex y compilación con pdflatex
```

Requiere `pip install matplotlib numpy pymupdf` y TeX Live (`texlive-latex-recommended`,
`texlive-latex-extra`, `texlive-lang-spanish`, `texlive-science`).
