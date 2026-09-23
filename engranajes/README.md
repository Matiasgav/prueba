# Mitras KG m0,5 × 20 dientes a 90° — torque admisible según Shigley

Análisis independiente de un par de engranajes cónicos rectos KG (serie M, relación 1:1)
en todos los materiales en que KG ofrece la pieza: S45C, SUS304L MIM, latón C3604B y POM inyectado.
Se calcula a 0 (estático), 0,5, 50 y 100 rpm, con 20 h de uso por mes, grasa y 30–40 °C.

## Entregables

| Archivo | Contenido |
|---|---|
| `informe_conicos_m05_z20.pdf` | Informe completo (24 páginas): resultado, supuestos, capturas del catálogo KG, método de Shigley, factores, cálculo paso a paso, tablas, gráficos, sensibilidad, verificaciones y referencias. |
| `informe_conicos_m05_z20.html` | El mismo informe en HTML autocontenido. |
| `resultados/resultados.json` | Todos los valores intermedios y finales. |
| `figuras/` | Gráficos (PNG y SVG). |
| `capturas/` | Recortes de los PDF oficiales de KG (filas del producto resaltadas) y láminas de KHK para POM. |

## Resultado (N·m por engranaje, R = 0,99, S = 1, 10 años)

| Material | 0 rpm | 0,5 rpm | 50 rpm | 100 rpm |
|---|---|---|---|---|
| S45C | 0,186 | 0,146 | 0,082 | 0,074 |
| SUS304L MIM | 0,091 | 0,072 | 0,044 | 0,040 |
| Latón C3604B | 0,110 | 0,087 | 0,053 | 0,051 |
| POM inyectado | 0,029 | 0,037 | 0,030 | 0,029 |

## Regenerar

```bash
tools/descargar_fuentes.sh             # PDF oficiales de KG (no versionados)
python3 tools/capturas.py              # recortes del catálogo
python3 tools/calculo.py               # cálculo, resultados.json y figuras
python3 tools/informe.py               # HTML
NODE_PATH=$(npm root -g) node tools/pdf.js informe_conicos_m05_z20.html informe_conicos_m05_z20.pdf
```

Requiere `pip install matplotlib numpy pymupdf` y Playwright con Chromium para el PDF.
Las láminas de KHK se descargan de
`https://khkgears.net/new/images/design-of-plastic-gears/` a `capturas/`.
