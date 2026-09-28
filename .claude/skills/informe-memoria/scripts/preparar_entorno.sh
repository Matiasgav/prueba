#!/usr/bin/env bash
# Prepara el entorno para compilar notas de la memoria GRIS.
set -e
if ! command -v pdflatex >/dev/null || ! kpsewhich roboto.sty >/dev/null 2>&1; then
  apt-get update -qq >/dev/null 2>&1 || true
  apt-get install -y -qq texlive-latex-recommended texlive-latex-extra \
    texlive-lang-spanish texlive-fonts-recommended texlive-fonts-extra lmodern \
    >/dev/null 2>&1
fi
python3 -c "import pymupdf, numpy, scipy, matplotlib" 2>/dev/null || \
  pip install -q pymupdf numpy scipy matplotlib 2>&1 | grep -v WARNING || true
command -v pdflatex && kpsewhich roboto.sty && python3 -c "import pymupdf; print('pymupdf ok')"
