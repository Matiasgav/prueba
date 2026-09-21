"""Los numeros de la pagina tienen que ser los del repositorio.

Complementa a `verify.js`, que comprueba el RENDER. Este comprueba el
CONTENIDO: que el bloque de datos embebido en la pagina sea el que emite
`studies/figuras_modelo.py`, que el palpador sea el de `design()`, que las
tablas publicadas reproduzcan, y que no hayan quedado rastros de los numeros
que revisiones anteriores corrigieron.
"""
import json, pathlib, re, sys, unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import pathlib
RAIZ = pathlib.Path(__file__).resolve().parent.parent
html = (RAIZ / 'docs' / 'modelo-cunas.html').read_text(encoding='utf-8')
res = json.loads((RAIZ / 'results' / 'figuras_modelo.json').read_text(encoding='utf-8'))
from wtd.modelo import MODELO, verificar_cadena
from wtd.softprobe import ZETA_SWEEP, F0_SWEEP_FLEXURA, design

fails = []
def ck(ok, msg):
    print(('  ok  ' if ok else 'FALLA ') + msg)
    if not ok:
        fails.append(msg)

def plano(s):                     # sin acentos, para comparar codigo con prosa
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn').lower()

print("== el bloque de datos embebido contra el estudio ==")
DAT = json.loads(re.search(r'const DAT = (\{.*?\});\n', html, re.S).group(1))
esc = res['escalera_5mJ']
ck(all(abs(DAT['st'][i][1] - round(e['x_um'], 2)) < 0.011
       and abs(DAT['st'][i][2] - round(e['a_cuña_g'])) < 1
       and abs(DAT['st'][i][3] - round(e['lectura_g'], 1)) < 0.11
       for i, e in enumerate(esc)),
   'la escalera (7 estados x 3 magnitudes)')
ck(all(abs(DAT['ener'][i][1] - round(r['sep'], 1)) < 0.11
       and abs(DAT['ener'][i][3] - round(r['salto_S3_S4'], 1)) < 0.11
       for i, r in enumerate(res['energia_golpe'])),
   'el barrido de energia (6 energias)')
d = res['despegue_12mJ']
ck(DAT['lift']['tip'] == d['tip_mg']
   and abs(DAT['lift']['frac'] - round(d['frac_pct'], 2)) < 0.011
   and abs(DAT['lift']['riel'] - 150.0) < 0.05, 'el caso de despegue')
ck(DAT['kf']['F'] == [round(f, 3) for f in res['kf_lah04']['F_N_A']], 'la curva K_F')
ck(abs(min(DAT['lift']['a']) + 150.0) < 0.02 and min(DAT['lift']['ref']) > -150.0,
   'la traza que despega toca el riel -F/m y la de referencia no')

print("\n== el palpador de la pagina contra design() ==")
p = design()
for val, txt, tol, lab in [(p.f0(), '1273 Hz', 1.0, 'f0'),
                           (p.k_series()/1e3, '43,5 N/mm', 0.05, 'k'),
                           (p.mass*1e3, '0,680 g', 0.005, 'm'),
                           (p.a_liftoff()/9.80665, '150 g', 0.01, 'a_despegue = F/m')]:
    ref = float(re.match(r'[\d,]+', txt).group().replace(',', '.'))
    ck(abs(val - ref) < tol and txt in html, f'{lab} = {txt}')

print("\n== las tablas publicadas contra el barrido recalculado ==")
#  Tolerancia: 1 % o un digito de la precision con que la tabla imprime, lo
#  que sea mayor. Las tablas llevan un decimal, asi que 154.82 contra 154.9
#  es el mismo numero; 0.747 contra 0.700 tambien, porque los dos imprimen
#  x0,7. Un error real (el default roto de design()) daba 40 % de diferencia.
def igual(a, b):
    return abs(a - b) <= max(0.1, 0.01 * abs(b))

zz = {round(z['zeta'], 3): z['sep_min'] for z in res['barrido_zeta']}
malas = [(z, s, round(zz[round(z, 3)], 2)) for z, _a, s in ZETA_SWEEP
         if not igual(zz[round(z, 3)], s)]
ck(not malas, f'ZETA_SWEEP reproduce (8 puntos){": " + str(malas) if malas else ""}')
ff = {f['f0_Hz']: f['sep_min'] for f in res['barrido_f0']}
malas = [(f, s, round(ff[f], 2)) for f, _a, s in F0_SWEEP_FLEXURA if not igual(ff[f], s)]
ck(not malas, f'F0_SWEEP_FLEXURA reproduce (9 puntos){": " + str(malas) if malas else ""}')
ck(abs(min(r['sep'] for r in res['energia_golpe']) - 112.2)/112.2 < 0.01 and '×112' in html,
   'la separacion publicada x112 es el minimo sobre las energias')
ck([z for z in res['barrido_zeta'] if z['zeta'] == 0.3][0]['despega'],
   'a zeta = 0,3 el palpador ademas despega, como dice la tabla')

print("\n== la cadena de bloques contra wtd.modelo ==")
inf = verificar_cadena()
ck(inf['cierra'], 'la cadena cierra: ningun simbolo sin productor')
hp = plano(html)
for b in MODELO:
    ck(plano(b.nombre.split(':')[0]) in hp, f'{b.id} "{b.nombre.split(":")[0]}"')
ck(inf['n_salidas'] == 32 and '32 magnitudes' in html, '32 magnitudes')
ck(inf['abiertos'] == ['B6'] and 'PENDIENTE' in html, 'el unico bloque abierto es B6')

print("\n== numeros que el texto cita ==")
for needle, lab in [('×670', 'el hueco'), ('0,0 %', 'S0 bajo el corte'),
                    ('100,0 %', 'S6 bajo el corte'), ('0,145 %', 'error del cociente'),
                    ('0,291 %', 'el inductivo'), ('33 350 Hz', 'pico asentada'),
                    ('×1230', 'ganancia del rasgo'), ('1545 g', 'el valor que se repite'),
                    ('0,43 %', 'fraccion en el riel'), ('−150,00 g', 'el riel'),
                    ('13 muestras', 'el tramo clavado')]:
    ck(needle in html, f'{lab}: "{needle}"')

ck(abs(DAT['ener'][3][0] - 5.0) < 1e-9 and abs(DAT['ener'][3][1] - 578.8) < 0.11,
   'el optimo del dato embebido es x578,8 a 5 mJ (la etiqueta "x579" la dibuja el JS: ver verify.js)')

print("\n== rastros de numeros ya corregidos ==")
for stale, why in [('6094', 'el 6,1 kHz del apoyo en extremos'),
                   ('4855', 'a_pico de S3, rev. C'),
                   ('848 g', 'a_pico de S0, rev. C'),
                   ('1820', 'el f0 del default roto de design()'),
                   ('88,9', 'la k del default roto'),
                   ('3,67 %', 'la fraccion de despegue vieja'),
                   ('sismometro', 'el mecanismo viejo')]:
    ck(stale not in html, f'no quedo "{stale}" ({why})')

print()
print(f'FALLAS: {len(fails)}' if fails else 'TODO OK')
sys.exit(1 if fails else 0)
