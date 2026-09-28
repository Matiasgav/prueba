#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Crea una nota nueva de la memoria GRIS a partir de la plantilla.

Uso (desde cualquier carpeta del repo del proyecto):
    python3 <habilidad>/scripts/nueva_nota.py "Título" \
        [--autor "Matías Gaviño"] [--fecha 24/09/2026] [--codigo 02489-00-MC007] \
        [--crear-memoria]

El repo es el de la carpeta actual (git rev-parse --show-toplevel), no el de la
habilidad: así funciona igual instalada en el repo o como habilidad de la cuenta.
Si el repo no tiene memoria/, sale con error; --crear-memoria la crea con la
plantilla que trae la habilidad (solo si el usuario lo confirmó).
"""
import argparse
import datetime
import pathlib
import re
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import codigos  # noqa: E402

HABILIDAD = pathlib.Path(__file__).resolve().parents[1]
RAIZ = pathlib.Path(subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True,
                                   text=True, check=True).stdout.strip())
MEMORIA = RAIZ / 'memoria'
PLANTILLA = MEMORIA / 'plantilla/02489-00-MC000.tex'
NOTAS = MEMORIA / 'notas'


def crear_memoria():
    """memoria/ con la plantilla y el README que trae la habilidad."""
    shutil.copytree(HABILIDAD / 'assets/plantilla', MEMORIA / 'plantilla')
    shutil.copy(HABILIDAD / 'assets/README_memoria.md', MEMORIA / 'README.md')
    for d in ('notas', 'pdf'):
        (MEMORIA / d).mkdir(parents=True, exist_ok=True)
    (NOTAS / '.gitkeep').touch()
    (MEMORIA / '.gitignore').write_text('*.aux\n*.log\n*.out\n*.synctex.gz\n__pycache__/\n')
    print(f'Creada {MEMORIA.relative_to(RAIZ)}/ con la plantilla de la habilidad.')


def siguiente_codigo():
    """Siguiente correlativo libre en TODAS las ramas (git fetch --all) y en
    la carpeta local. Mirar solo la carpeta local provocó la colisión de
    MC003 (dos sesiones usaron el mismo código en ramas distintas)."""
    codigos.fetch()
    usados = codigos.codigos_en_ramas()
    locales = [p.name for p in NOTAS.glob('02489-00-MC*')
               if re.fullmatch(r'02489-00-MC\d{3}', p.name)]
    return codigos.siguiente(usados, locales)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('titulo')
    ap.add_argument('--autor', default='Matías Gaviño')
    ap.add_argument('--fecha', default=datetime.date.today().strftime('%d/%m/%Y'))
    ap.add_argument('--codigo')
    ap.add_argument('--crear-memoria', action='store_true')
    a = ap.parse_args()

    if not PLANTILLA.exists():
        if not a.crear_memoria:
            sys.exit(f'{RAIZ.name} no tiene memoria/plantilla/. Traela de main '
                     '(git merge origin/main) o, si el usuario confirma que este repo lleva '
                     'memoria, repetí con --crear-memoria.')
        crear_memoria()

    codigo = a.codigo or siguiente_codigo()
    carpeta = NOTAS / codigo
    destino = carpeta / f'{codigo}.tex'
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
    for clave in (codigo, a.titulo, 'amssymb', '{figuras/}'):
        if clave not in s:
            sys.exit(f'No se pudo completar «{clave}»: ¿cambió la plantilla?')

    (carpeta / 'figuras').mkdir(parents=True, exist_ok=True)
    destino.write_text(s, encoding='utf-8')
    print(destino.relative_to(RAIZ))
    print('Reservá el código ya: commit + push del esqueleto (ver SKILL.md, paso 2).')


if __name__ == '__main__':
    main()
