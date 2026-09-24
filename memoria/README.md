# Memoria del proyecto 00503

Notas rápidas del proyecto *Generator inspection robotic system* (Mecanalisis),
con la plantilla **GRIS-NOT-001** (identidad GRIS-IDENTIDAD-001 v1.4).

```
memoria/
├── plantilla/
│   ├── 02489-00-MC000.tex   ← plantilla (no editar; copiar)
│   ├── 02489-00-MC000.pdf   ← cómo se ve
│   └── logo-gris.pdf        ← agregar aquí el logo vectorial
└── notas/                   ← una nota por archivo: 02489-00-MC###.tex
```

## Escribir una nota nueva

1. **Copiá la plantilla** a `notas/` con el siguiente número libre:
   `notas/02489-00-MC007.tex`. El `###` es correlativo: mirá la última nota y sumá uno.
2. **Completá los 4 datos** del principio del archivo: código, título, autor y fecha.
3. **Escribí los resultados primero**, dentro del recuadro `resultados`.
4. **El resto es libre.** Contexto, Desarrollo y Pendientes son sugerencias:
   borralos, renombralos o agregá los tuyos. Media página es una nota válida.
5. **Compilá** dos veces: `pdflatex 02489-00-MC007.tex` (o en Overleaf).

## Cómo escribir los resultados

Es lo único que se pide. Quien abra la nota tiene que entender qué se sabe ahora
leyendo solo ese recuadro.

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
| `\pendiente{texto}` | Marca en naranja algo por verificar. |
| `\figura{archivo}{0.8}{pie}` | Inserta una imagen al 80 % del ancho, con pie. |
| tabla con `\toprule` / `\midrule` / `\bottomrule` | Hay un ejemplo en la plantilla. |

## Identidad visual

- Encabezado: logo reducido **GRIS** (pequeño, sin marco ni banda) a la izquierda
  y el código `02489-00-MC###` a la derecha. El resto de la hoja queda libre.
- Naranja institucional `#FF7A00`; para texto naranja se usa un tono más oscuro
  (`#C45E00`) para que se lea bien impreso.
- Logo: guardá el logo vectorial como `plantilla/logo-gris.pdf`. Mientras no esté,
  la plantilla escribe «GRIS» en naranja como marcador.
