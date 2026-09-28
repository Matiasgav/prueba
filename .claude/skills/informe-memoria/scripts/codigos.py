#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Códigos de nota 02489-00-MC### usados en TODAS las ramas del repositorio.

Las notas se escriben en sesiones y ramas distintas en paralelo: mirar solo
la carpeta local no alcanza. Este módulo hace `git fetch --all` y recorre
todas las ramas locales y remotas.

Uso (desde la raíz del repo):
    python3 codigos.py                    # lista códigos, títulos y ramas
    python3 codigos.py --verificar MC004  # falla si otra rama usa ese código
                                          # para una nota con otro título
"""
import argparse
import re
import subprocess
import sys

PATRON = re.compile(r'^memoria/notas/(02489-00-MC(\d{3}))\.tex$')


def git(*args):
    return subprocess.run(['git', *args], capture_output=True, text=True,
                          check=False).stdout


def fetch():
    subprocess.run(['git', 'fetch', '--all', '--prune', '--quiet'], check=False)


def titulo(ref, codigo):
    tex = git('show', f'{ref}:memoria/notas/{codigo}.tex')
    m = re.search(r'\\newcommand\{\\titulo\}\{(.*)\}', tex)
    return m.group(1).strip() if m else '?'


def codigos_en_ramas():
    """{codigo: {titulo: [ramas]}} para todas las ramas locales y remotas."""
    refs = git('for-each-ref', '--format=%(refname:short)',
               'refs/heads', 'refs/remotes').split()
    usados = {}
    for ref in refs:
        if ref.endswith('/HEAD') or ref in ('origin', 'HEAD'):
            continue
        for ruta in git('ls-tree', '-r', '--name-only', ref, 'memoria/notas/').split():
            m = PATRON.match(ruta)
            if m:
                cod = m.group(1)
                usados.setdefault(cod, {}).setdefault(titulo(ref, cod), []).append(ref)
    return usados


def siguiente(usados, locales=()):
    nums = [int(c[-3:]) for c in list(usados) + list(locales)]
    return f'02489-00-MC{max(nums, default=0) + 1:03d}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--verificar', metavar='CODIGO')
    ap.add_argument('--sin-fetch', action='store_true')
    a = ap.parse_args()
    if not a.sin_fetch:
        fetch()
    usados = codigos_en_ramas()

    if a.verificar:
        cod = a.verificar if a.verificar.startswith('02489') else f'02489-00-{a.verificar}'
        propio = titulo('HEAD', cod)
        ajenos = {t: r for t, r in usados.get(cod, {}).items() if t != propio}
        if ajenos:
            print(f'COLISIÓN: {cod} ya existe con otro título:')
            for t, r in ajenos.items():
                print(f'  «{t}» en {", ".join(r)}')
            print(f'Siguiente código libre: {siguiente(usados)}')
            sys.exit(1)
        print(f'{cod} libre de colisiones («{propio}»).')
        return

    for cod in sorted(usados):
        for t, r in usados[cod].items():
            print(f'{cod}  {t}  [{", ".join(sorted(set(r)))}]')
    print(f'Siguiente código libre: {siguiente(usados)}')


if __name__ == '__main__':
    main()
