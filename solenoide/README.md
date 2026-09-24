# Selección del solenoide para el actuador de impacto WTT

Memoria técnica de selección del solenoide que acciona el impactador del
Wedge Tap Test (robot de inspección de cuñas de estator).

## Entregables

| Archivo | Descripción |
|---|---|
| `informe_seleccion_solenoide.pdf` | Informe completo (A4), con las capturas de las hojas de datos en el anexo A. |
| `informe_seleccion_solenoide.html` | La misma fuente en HTML (abrir desde esta carpeta para ver las imágenes). |
| `hojas_de_datos/` | Capturas de página completa de las hojas de datos oficiales; los recuadros rojos marcan los datos citados. |
| `figuras/` | Gráficos del informe (curvas, energía útil, planitud). |
| `data_curvas.json` | Curvas fuerza–carrera extraídas de los PDF de los fabricantes. |
| `data_resultados.json` | Energía útil, sensibilidad y velocidad por candidato. |

## Regenerar

Descargar los PDF listados en el anexo B del informe a una carpeta y ejecutar:

```bash
pip install pymupdf numpy matplotlib
python3 tools/digitalizar_curvas.py <carpeta_pdfs> data_curvas.json
python3 tools/analisis.py
```

El PDF se imprime desde el HTML con Chromium (A4, fondos activados).
