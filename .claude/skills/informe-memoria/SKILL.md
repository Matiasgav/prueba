---
name: informe-memoria
description: Redacta un informe como nota de la memoria del proyecto GRIS (plantilla GRIS-NOT-001, código 02489-00-MC###) y la compila a PDF. Usar siempre que se pida un informe, nota, memoria, análisis o «pasalo a la memoria», aunque no se nombre la plantilla, y también cuando se adjunte un informe o gráfico existente para llevarlo a la memoria.
---

# Informe de memoria (GRIS-NOT-001)

Sirve para **cualquier informe del proyecto**, sea cual sea el tema: ensayos,
cálculos de diseño, comparaciones, relevamientos, estudios de mercado o técnicos.
**Cada informe queda guardado y codificado en el repo**: un código correlativo
`02489-00-MC###` por informe, sin reutilizar números, con fuente, PDF, script y
figuras versionados, y una fila en el índice de `memoria/README.md`. Nada se entrega
solo por el chat.

Todo informe del proyecto se entrega como **nota de la memoria** en
`memoria/notas/02489-00-MC###.tex` + `.pdf`, con su carpeta
`memoria/notas/02489-00-MC###/` (script de cálculo, `resultados.json`, `figuras/`).
Las reglas base están en `CLAUDE.md` y `memoria/README.md`; esta habilidad agrega el
procedimiento completo y los errores ya cometidos.

## 1. Preparar el entorno

```bash
bash .claude/skills/informe-memoria/scripts/preparar_entorno.sh
```

Instala `pdflatex`, Roboto (encabezado; sin ella el código sale en otra letra),
`pymupdf` para leer PDFs y extraer imágenes, y `numpy`/`scipy`/`matplotlib`.

Si la carpeta `memoria/` no está en la rama actual, buscarla en las ramas remotas
(`git ls-tree -r --name-only <rama> | grep ^memoria/`) y traerla con `git merge`
de esa rama, no copiando archivos a mano.

## 2. Elegir el código, crear la nota y reservarla

**El código se elige mirando TODAS las ramas, no la carpeta local.** Varias sesiones
escriben notas en paralelo, cada una en su rama: mirar solo `memoria/notas/` de la
rama actual hizo que dos notas distintas salieran como `MC003` (resorte de torsión en
`claude/jolly-maxwell-wagfg8` y selección del actuador en otra rama).

```bash
python3 .claude/skills/informe-memoria/scripts/codigos.py      # códigos usados en todas las ramas
python3 .claude/skills/informe-memoria/scripts/nueva_nota.py "Título corto" [--autor "Matías Gaviño"] [--fecha 24/09/2026]
```

`codigos.py` hace `git fetch --all` y lista cada código con su título y las ramas donde
está. `nueva_nota.py` usa esa misma búsqueda para tomar el siguiente correlativo libre,
copia la plantilla, completa los cuatro datos, agrega `amsmath`, `amssymb` y `float` al
preámbulo y la ruta `figuras/` de la nota a `\graphicspath`, y crea la carpeta de la
nota. **No tocar la plantilla** en `memoria/plantilla/`. Si hay que rehacer una nota
existente, editar esa misma nota (mismo código), no crear otra.

**Reservar el código enseguida**, antes de investigar o escribir: agregar la fila al
índice de `memoria/README.md`, hacer commit del esqueleto
(«Reservar 02489-00-MC###: título») y push a la rama de trabajo. Así el código ya
aparece en el remoto para las otras sesiones.

Título: corto, que entre en una línea a 20 pt (≈ 40 caracteres). Si se corta con
guion, acortarlo.

## 3. Leer el material de partida

- **PDF adjunto:** leer todo el texto con pymupdf y **extraer sus imágenes**:
  ```bash
  python3 .claude/skills/informe-memoria/scripts/extraer_pdf.py <archivo.pdf> <carpeta_salida>
  ```
  Las **fotos del informe original van en la nota** (ensayo, probeta, instrumento,
  montaje). Pasar las fotos a JPG; los gráficos quedan en PNG.
- **Gráfico adjunto como imagen:** incluirlo en `figuras/` y tomar de él los valores
  rotulados; decir en el texto que salen de la figura.
- Si el material cita otro documento del proyecto (p. ej. `02489-00-ZIT200`), citarlo
  por su código.

## 4. Estructura

La sección 1 es siempre **Resultados**. El resto sigue la lógica del tema, del
fundamento a la derivada. **Lo que el usuario pide como tema es el cuerpo principal**;
los análisis derivados van después, en secciones propias.

Ejemplo de ensayo o caracterización (MC002):

1. **Resultados:** una idea por viñeta, en negrita la afirmación, con números; cerrar
   con «Pendiente» o «Siguiente paso». Puede empezar con una tabla resumen.
2. **Relevamiento:** probeta, instrumento y montaje con **fotos**; método; tabla de
   mediciones completa (datos crudos y convertidos); curva y valores característicos.
3. **Análisis / estimación** (modelo, ajuste, residuos, alcance de la inferencia).
4. **Evaluación de alternativas** (otros grados, otras variantes).

Si el tema no es de cálculo ni de ensayo (p. ej. un estudio o una comparación de
opciones): Resultados → Contexto → Desarrollo / opciones comparadas → Recomendación
y pendientes. Si no hay cálculo, la carpeta de la nota guarda igual las figuras y
las fuentes consultadas.

Ejemplo de cálculo de diseño (MC001): Resultados → Datos y supuestos (tabla
Dato / Valor / Origen, marcando **supuesto**) → método con ecuaciones → sensibilidad.

## 5. Estilo

- Español rioplatense técnico, frases cortas. Coma decimal: `1,5~mm`, en matemática
  `1{,}5`. Unidades con `~` (`25,6~N`), porcentajes `9,3\,\%`. No usar `siunitx`.
- Figuras y tablas con `[H]`. Tres fotos verticales: tres `minipage` de `0.3\linewidth`
  con rótulos (a), (b), (c) dentro de una sola figura.
- Tablas con `booktabs`; tablas largas en dos bloques de columnas lado a lado.
- Limitaciones al final de cada análisis, en viñetas con el término en negrita.
- Citas de Shigley con ecuación, tabla o figura (ver `CLAUDE.md`).
- El naranja `#FF7A00` solo en el logo.

## 6. Cálculo reproducible

`memoria/notas/02489-00-MC###/calculo.py` con un docstring que diga qué calcula, de
dónde salen los datos y qué se toma de figuras externas. Escribe `resultados.json`.
Partir de los **datos crudos** (lecturas originales), no de valores ya procesados.

**Verificar los números del material de partida contra los datos.** Si un valor
citado no cuadra (p. ej. «cae a la mitad en 0,8 mm» cuando a 0,80 mm se midió más de
la mitad), usar el valor correcto en la nota y avisarle al usuario en la respuesta.
Distinguir con «≈» lo estimado de lo tomado del modelo o de la figura.

## 7. Compilar y revisar

```bash
bash .claude/skills/informe-memoria/scripts/compilar.sh 02489-00-MC###
```

Compila dos veces desde `memoria/notas/`, muestra errores, *overfull boxes* y avisos
de fuente, borra `.aux/.log/.out` y renderiza cada página a PNG en el scratchpad.
**Mirar todas las páginas**: título en una línea, figuras legibles, sin huecos grandes
(achicar figuras si un `[H]` deja media página vacía), encabezado con logo y código
en Roboto.

## 8. Cerrar

1. **Verificar el código otra vez** justo antes del push (otra sesión pudo haberlo
   tomado mientras se escribía):
   ```bash
   python3 .claude/skills/informe-memoria/scripts/codigos.py --verificar MC###
   ```
   Si hay colisión: renumerar la nota propia al siguiente libre (`git mv` del `.tex`,
   `.pdf` y carpeta; reemplazar el código dentro del `.tex` y del script; recompilar),
   traer con `git merge` la rama que tiene la otra nota y resolver el índice dejando
   las dos filas en orden. Nunca renumerar la nota de otra sesión.
2. Actualizar la fila en «Índice de notas» de `memoria/README.md`.
3. `git add` de `.tex`, `.pdf`, carpeta de la nota y README; commit y push a la rama
   de trabajo.
4. Enviar el PDF al usuario y resumir: estructura, de dónde sale cada número y
   cualquier discrepancia encontrada.
