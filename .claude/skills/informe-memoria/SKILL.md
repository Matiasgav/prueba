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

Todo informe del proyecto se entrega como **nota de la memoria**:

- **Fuentes:** una carpeta por nota, `memoria/notas/02489-00-MC###/`, con el `.tex`
  (`02489-00-MC###.tex`), el script de cálculo, `resultados.json`, `figuras/` y lo
  que haga falta (fuentes, datos, planos).
- **PDF final:** `memoria/pdf/02489-00-MC###.pdf`. Todos los PDF van juntos ahí.
- **Todas las notas terminan en `main`** (paso 8).
Las reglas base están en `CLAUDE.md` y `memoria/README.md` del repo; esta habilidad
agrega el procedimiento completo y los errores ya cometidos.

**`$SKILL`** es la carpeta de esta habilidad: la que figura como directorio base al
cargarla (en el repo, `.claude/skills/informe-memoria`). Los scripts trabajan sobre el
repo de la carpeta actual, no sobre el de la habilidad; correrlos desde la raíz del
repo del proyecto.

## 1. Preparar el entorno

```bash
bash $SKILL/scripts/preparar_entorno.sh
```

Instala `pdflatex`, Roboto (encabezado; sin ella el código sale en otra letra),
`pymupdf` para leer PDFs y extraer imágenes, y `numpy`/`scipy`/`matplotlib`.

**Ubicar la memoria antes de escribir:**

1. Si la rama actual tiene `memoria/`, seguir.
2. Si no la tiene pero `origin/main` sí (`git ls-tree -d origin/main memoria`), traerla
   con `git merge origin/main`, no copiando archivos a mano.
3. Si el repo no tiene memoria en ninguna rama, **preguntar al usuario** antes de crearla:
   puede ser otro repo. Si confirma, `nueva_nota.py ... --crear-memoria` la arma con la
   plantilla que trae la habilidad (`$SKILL/assets/`).

## 2. Elegir el código, crear la nota y reservarla

**El código se elige mirando TODAS las ramas, no la carpeta local.** Varias sesiones
escriben notas en paralelo, cada una en su rama: mirar solo `memoria/notas/` de la
rama actual hizo que dos notas distintas salieran como `MC003` (resorte de torsión en
`claude/jolly-maxwell-wagfg8` y selección del actuador en otra rama).

```bash
python3 $SKILL/scripts/codigos.py      # códigos usados en todas las ramas
python3 $SKILL/scripts/nueva_nota.py "Título corto" [--autor "Matías Gaviño"] [--fecha 24/09/2026]
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
  python3 $SKILL/scripts/extraer_pdf.py <archivo.pdf> <carpeta_salida>
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
- Citas de Shigley (*Diseño en ingeniería mecánica*, 8.ª ed.) con ecuación, tabla o figura.
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
bash $SKILL/scripts/compilar.sh 02489-00-MC###
```

Compila dos veces desde la carpeta de la nota, deja el PDF en `memoria/pdf/`, muestra errores, *overfull boxes* y avisos
de fuente, borra `.aux/.log/.out` y renderiza cada página a PNG en el scratchpad.
**Mirar todas las páginas**: título en una línea, figuras legibles, sin huecos grandes
(achicar figuras si un `[H]` deja media página vacía), encabezado con logo y código
en Roboto.

## 8. Cerrar

1. **Verificar el código otra vez** justo antes del push (otra sesión pudo haberlo
   tomado mientras se escribía):
   ```bash
   python3 $SKILL/scripts/codigos.py --verificar MC###
   ```
   Si hay colisión: renumerar la nota propia al siguiente libre (`git mv` de la
   carpeta, del `.tex` dentro de ella y del `.pdf` en `memoria/pdf/`; reemplazar el código dentro del `.tex` y del script; recompilar),
   traer con `git merge` la rama que tiene la otra nota y resolver el índice dejando
   las dos filas en orden. Nunca renumerar la nota de otra sesión.
2. Actualizar la fila en «Índice de notas» de `memoria/README.md`.
3. `git add` de la carpeta de la nota, su PDF en `memoria/pdf/` y el README; commit y
   push a la rama de trabajo.
4. **Llevar la nota a `main`.** Todas las notas tienen que quedar juntas en `main`.
   Traer solo los archivos de la nota, no el resto de la rama de trabajo:
   ```bash
   git fetch origin main
   git worktree add /tmp/wt-main origin/main -B main
   cd /tmp/wt-main
   git checkout <rama-de-trabajo> -- memoria/notas/02489-00-MC###/ memoria/pdf/02489-00-MC###.pdf
   # agregar la fila de la nota al índice de memoria/README.md (en orden de código)
   git add memoria && git commit -m "02489-00-MC###: <título>" && git push origin main
   cd - && git worktree remove /tmp/wt-main
   ```
   Si la nota depende de archivos de fuera de `memoria/` (datos de otra carpeta del
   repo), copiarlos antes a la carpeta de la nota, para que en `main` compile sola.
5. Enviar el PDF al usuario y resumir: estructura, de dónde sale cada número y
   cualquier discrepancia encontrada.
