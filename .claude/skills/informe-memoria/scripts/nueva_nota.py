#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Crea una nota nueva de la memoria GRIS a partir de la plantilla.

Uso (desde la raíz del repo):
    python3 .claude/skills/informe-memoria/scripts/nueva_nota.py "Título" \
        [--autor "Matías Gaviño"] [--fecha 24/09/2026] [--codigo 02489-00-MC007]
"""
import argparse
import datetime
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import codigos  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parents[4]
PLANTILLA = RAIZ / 'memoria/plantilla/02489-00-MC000.tex'
NOTAS = RAIZ / 'memoria/notas'


def siguiente_codigo():
    """Siguiente correlativo libre en TODAS las ramas (git fetch --all) y en
    la carpeta local. Mirar solo la carpeta local provocó la colisión de
    MC003 (dos sesiones usaron el mismo código en ramas distintas)."""
    codigos.fetch()
    usados = codigos.codigos_en_ramas()
    locales = [m.group(1) for p in NOTAS.glob('02489-00-MC*.tex')
               if (m := re.match(r'(02489-00-MC\d{3})\.tex$', p.name))]
    return codigos.siguiente(usados, locales)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('titulo')
    ap.add_argument('--autor', default='Matías Gaviño')
    ap.add_argument('--fecha', default=datetime.date.today().strftime('%d/%m/%Y'))
    ap.add_argument('--codigo')
    a = ap.parse_args()

    codigo = a.codigo or siguiente_codigo()
    destino = NOTAS / f'{codigo}.tex'
    if destino.exists():
        sys.exit(f'Ya existe {destino}; editá esa nota.')

    s = PLANTILLA.read_text(encoding='utf-8')
    s = s.replace(r'\newcommand{\codigo}{02489-00-MC000}', rf'\newcommand{{\codigo}}{{{codigo}}}')
    s = s.replace(r'\newcommand{\titulo}{Título corto y concreto de la nota}',
                  rf'\newcommand{{\titulo}}{{{a.titulo}}}')
    s = s.replace(r'\newcommand{\autor}{Nombre Apellido}', rf'\newcommand{{\autor}}{{{a.autor}}}')
    s = s.replace(r'\newcommand{\fecha}{\today}', rf'\newcommand{{\fecha}}{{{a.fecha}}}')
    s = s.replace(r'\usepackage[hidelinks]{hyperref}',
                  '\\usepackage{amsmath,amssymb}\n\\usepackage{float}\n\\usepackage[hidelinks]{hyperref}')
    s = s.replace(r'\graphicspath{{./}{../plantilla/}{plantilla/}}',
                  rf'\graphicspath{{{{./}}{{../plantilla/}}{{plantilla/}}{{{codigo}/figuras/}}}}')
    for clave in (codigo, a.titulo, 'amssymb', f'{codigo}/figuras/'):
        if clave not in s:
            sys.exit(f'No se pudo completar «{clave}»: ¿cambió la plantilla?')

    destino.write_text(s, encoding='utf-8')
    (NOTAS / codigo / 'figuras').mkdir(parents=True, exist_ok=True)
    print(destino.relative_to(RAIZ))
    print('Reservá el código ya: commit + push del esqueleto (ver SKILL.md, paso 2).')


if __name__ == '__main__':
    main()
