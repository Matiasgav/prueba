# Memoria del proyecto 00503

Notas rápidas del proyecto *Generator inspection robotic system* (Mecanalisis),
con la plantilla **GRIS-NOT-001** (identidad GRIS-IDENTIDAD-001 v1.4).

```
memoria/
├── plantilla/
│   ├── 02489-00-MC000.tex   ← plantilla (no editar; copiar)
│   ├── 02489-00-MC000.pdf   ← cómo se ve
│   ├── logo-gris.pdf        ← logo reducido GRIS (GRIS-LOGO-003)
│   └── logo-gris.svg        ← el mismo logo, fuente vectorial
└── notas/                   ← una nota por archivo: 02489-00-MC###.tex
    └── 02489-00-MC###/      ← script de cálculo y figuras de esa nota
```

## Índice de notas

| Código | Título | Fecha |
|---|---|---|
| [02489-00-MC001](notas/02489-00-MC001.pdf) | Torque admisible de los engranajes cónicos de la rueda | 24/09/2026 |
| [02489-00-MC002](notas/02489-00-MC002.pdf) | Caracterización de los imanes D20×4 | 24/09/2026 |
| [02489-00-MC003](notas/02489-00-MC003.pdf) | Resorte de torsión de cuerda de piano Ø0,50 para eje Ø3 (con plano) | 24/09/2026 |

## Escribir una nota nueva

1. **Copiá la plantilla** a `notas/` con el siguiente número libre:
   `notas/02489-00-MC007.tex`. El `###` es correlativo: mirá la última nota y sumá uno.
2. **Completá los 4 datos** del principio del archivo: código, título, autor y fecha.
3. **Escribí los resultados primero**, en la sección `Resultados`.
4. **El resto es libre.** Contexto y Desarrollo son sugerencias:
   borralos, renombralos o agregá los tuyos. Media página es una nota válida.
5. **Compilá** dos veces desde `notas/`: `pdflatex 02489-00-MC007.tex` (o en Overleaf).

## Cómo escribir los resultados

Es lo único que se pide. Quien abra la nota tiene que entender qué se sabe ahora
leyendo solo esa sección.

- Una idea por punto, en una frase.
- Con números cuando los hay: «error de posición < 2 mm», no «error bajo».
- Lo que no funcionó también es un resultado.
- Si la nota termina en una decisión o un siguiente paso, va aquí.

| En vez de… | Mejor… |
|---|---|
| Se hicieron pruebas del sensor. | El sensor detecta fisuras de 0,5 mm a 10 cm; a 20 cm ya no. |
| Se revisó la opción de orugas magnéticas. | Descartamos orugas magnéticas: el entrehierro no admite más de 40 mm de alto. |

## Ayudas disponibles

| Comando | Para qué |
|---|---|
| `\figura{archivo}{0.8}{pie}` | Inserta una imagen al 80 % del ancho, con pie. |
| tabla con `\toprule` / `\midrule` / `\bottomrule` | Hay un ejemplo en la plantilla. |

## Identidad visual

- Encabezado: logo reducido **GRIS** (pequeño, sin marco ni banda) a la izquierda
  y el código `02489-00-MC###` a la derecha. El resto de la hoja queda libre.
- Bajo el encabezado, una línea fina gris de ancho completo.
- Naranja institucional `#FF7A00`, solo en el logo. El texto va en negro y gris.
- Títulos numerados (1, 1.1…). Resultados siempre es la sección 1.
- Tipografía del texto: Latin Modern, la tipografía clásica de LaTeX.
- Tipografía del código `02489-00-MC###`: Roboto Condensed Bold, que se parece a
  Geogrotesque Bold, la letra del logo. Geogrotesque no es libre y el SVG del logo
  no trae sus números. Roboto viene con TeX Live y Overleaf.
- Logo: `plantilla/logo-gris.pdf`, recortado a su contorno para que no quede margen
  vacío en el encabezado. Si compilás desde `notas/`, se toma de `../plantilla/`.
  En Overleaf, subilo junto al `.tex`.
