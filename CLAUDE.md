# Instrucciones del repositorio

## Informes de la memoria del proyecto

Todo informe que se pida («haceme un informe de…», «analizá…») se entrega como
nota de la memoria, con la plantilla GRIS-NOT-001:

1. Copiar `memoria/plantilla/02489-00-MC000.tex` a
   `memoria/notas/02489-00-MC###.tex`, con `###` = siguiente correlativo libre
   en `memoria/notas/` (la primera es `MC001`).
2. Completar código, título, autor y fecha en el bloque «DATOS DE LA NOTA».
3. La sección 1 es siempre **Resultados**: conclusiones cortas, con números.
   El resto de las secciones es libre.
4. Cálculos reproducibles: el script que los genera va junto a la nota
   (`memoria/notas/02489-00-MC###/`) y las figuras se guardan ahí mismo.
5. Compilar con `pdflatex` (dos veces) desde `memoria/notas/`, revisar el PDF
   renderizado y subir `.tex` + `.pdf` + script. No subir `.aux`, `.log`, `.out`.
6. No modificar la plantilla salvo que se pida explícitamente.

Estilo: texto en Latin Modern, código documental en Roboto Condensed Bold,
títulos numerados, naranja `#FF7A00` solo en el logo. Ver `memoria/README.md`.

Referencia de diseño mecánico disponible (no versionada, la sube el usuario):
Shigley, *Diseño en ingeniería mecánica*, 8.ª ed. Citar ecuación/tabla/figura.
