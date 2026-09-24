#!/usr/bin/env bash
# Compila una nota de la memoria y renderiza sus páginas para revisarlas.
# Uso (desde la raíz del repo): bash compilar.sh 02489-00-MC###
set -u
NOTA=$1
RAIZ=$(git rev-parse --show-toplevel)
OUT=${CLAUDE_SCRATCH:-${TMPDIR:-/tmp}}/revision-$NOTA
cd "$RAIZ/memoria/notas"
for i in 1 2; do pdflatex -interaction=nonstopmode "$NOTA.tex" >/dev/null; done
echo "--- problemas (vacío = ninguno)"
grep -E -A2 "^!|Overfull|Font Warning|undefined" "$NOTA.log" | head -30
rm -f "$NOTA".aux "$NOTA".log "$NOTA".out "$NOTA".synctex.gz
mkdir -p "$OUT"
python3 - "$NOTA.pdf" "$OUT" <<'PY'
import sys, pymupdf
d = pymupdf.open(sys.argv[1])
for i, p in enumerate(d, 1):
    p.get_pixmap(dpi=80).save(f'{sys.argv[2]}/pagina{i}.png')
print(f'{d.page_count} páginas renderizadas en {sys.argv[2]}/pagina*.png')
PY
