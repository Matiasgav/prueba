#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compone el informe en HTML autocontenido y en LaTeX desde una unica fuente.

Uso:
    python3 tools/md2report.py source/informe.md salida.html salida.tex

Sintaxis propia sobre Markdown
------------------------------
    ::: nota <clase> | <titulo>      llamado (clave, dato, riesgo, inferencia)
    ::: kpi                          fila de indicadores: valor || etiqueta || nota
    ::: fig <id> | <epigrafe> | <fuente>
    ::: tarjetas <n>                 grilla de tarjetas
    ::: tarjeta <titulo> | <meta>
    ::: detalle <titulo>             bloque desplegable
    :::                              cierre

    {{ev:A}} {{mad:M4}} {{tipo:Declaracion}} {{conf:Media}}   distintivos en linea
"""
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')

# =========================================================================
# 1. Parseo
# =========================================================================
BULLET = re.compile(r'^(\s*)[-*]\s+(.*)$')
ORDERED = re.compile(r'^(\s*)(\d+)[.)]\s+(.*)$')
HEADING = re.compile(r'^(#{1,6})\s+(.*?)\s*#*$')
TABLE_SEP = re.compile(r'^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?\s*$')
HR = re.compile(r'^\s*(-{3,}|\*{3,}|_{3,})\s*$')
OPEN = re.compile(r'^:::\s+(\S+)\s*(.*)$')
CLOSE = re.compile(r'^:::\s*$')
CHECK = re.compile(r'^\[( |x|X)\]\s*')


def split_pipes(s):
    """Divide por | ignorando los que están dentro de {{...}}.

    El marcador de término usa | como separador interno, y | también separa
    celdas de tabla y argumentos de bloque: sin esto, {{t:clave|texto}} se
    partiría en dos.
    """
    out, buf, depth, i = [], [], 0, 0
    while i < len(s):
        if s.startswith('{{', i):
            depth += 1
            buf.append('{{')
            i += 2
            continue
        if s.startswith('}}', i) and depth:
            depth -= 1
            buf.append('}}')
            i += 2
            continue
        if s[i] == '|' and depth == 0:
            out.append(''.join(buf))
            buf = []
        else:
            buf.append(s[i])
        i += 1
    out.append(''.join(buf))
    return out


def split_row(line):
    line = line.strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]
    return [c.strip() for c in split_pipes(line)]


def parse(lines, i=0, inside=False):
    """Devuelve (bloques, indice_siguiente)."""
    blocks = []
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if inside and CLOSE.match(stripped):
            return blocks, i + 1

        if not stripped:
            i += 1
            continue

        m = OPEN.match(stripped)
        if m:
            kind, arg = m.group(1), m.group(2).strip()
            body, i = parse(lines, i + 1, inside=True)
            blocks.append(('dir', {'kind': kind, 'arg': arg}, body))
            continue

        m = HEADING.match(line)
        if m:
            blocks.append(('heading', len(m.group(1)), m.group(2)))
            i += 1
            continue

        if HR.match(line):
            blocks.append(('hr', None, None))
            i += 1
            continue

        if '|' in line and i + 1 < n and TABLE_SEP.match(lines[i + 1]):
            header = split_row(line)
            aligns = []
            for spec in split_row(lines[i + 1]):
                l, r = spec.startswith(':'), spec.endswith(':')
                aligns.append('center' if l and r else 'right' if r else 'left')
            rows = []
            i += 2
            while i < n and '|' in lines[i] and lines[i].strip():
                rows.append(split_row(lines[i]))
                i += 1
            blocks.append(('table', {'header': header, 'aligns': aligns}, rows))
            continue

        if stripped.startswith('>'):
            buf = []
            while i < n and lines[i].strip().startswith('>'):
                buf.append(re.sub(r'^\s*>\s?', '', lines[i]))
                i += 1
            blocks.append(('quote', None, [b for b in buf if b.strip()]))
            continue

        if BULLET.match(line) or ORDERED.match(line):
            (spec, items), i = parse_list(lines, i)
            blocks.append(('list', spec, items))
            continue

        buf = []
        while (i < n and lines[i].strip() and not HEADING.match(lines[i])
               and not HR.match(lines[i]) and not lines[i].strip().startswith('>')
               and not BULLET.match(lines[i]) and not ORDERED.match(lines[i])
               and not OPEN.match(lines[i].strip())
               and not CLOSE.match(lines[i].strip())):
            buf.append(lines[i])
            i += 1
        blocks.append(('para', None, buf))
    return blocks, i


def parse_list(lines, i):
    n = len(lines)
    mb, mo = BULLET.match(lines[i]), ORDERED.match(lines[i])
    base = len((mb or mo).group(1))
    kind = 'ul' if mb else 'ol'
    start = int(mo.group(2)) if mo else 1
    items = []
    while i < n:
        line = lines[i]
        if not line.strip():
            j = i + 1
            while j < n and not lines[j].strip():
                j += 1
            if j < n:
                mb2, mo2 = BULLET.match(lines[j]), ORDERED.match(lines[j])
                if ((mb2 or mo2) and len((mb2 or mo2).group(1)) == base
                        and ('ul' if mb2 else 'ol') == kind):
                    i = j
                    continue
                if (not (mb2 or mo2) and items
                        and lines[j].startswith(' ' * (base + 1))):
                    para = []
                    while (j < n and lines[j].strip()
                           and not BULLET.match(lines[j])
                           and not ORDERED.match(lines[j])):
                        para.append(lines[j].strip())
                        j += 1
                    items[-1].setdefault('paras', []).append(para)
                    i = j
                    continue
            break
        mb, mo = BULLET.match(line), ORDERED.match(line)
        m = mb or mo
        if m:
            indent = len(m.group(1))
            this = 'ul' if mb else 'ol'
            if indent > base:
                child, i = parse_list(lines, i)
                if items:
                    items[-1]['children'] = child
                continue
            if indent < base or this != kind:
                break
            items.append({'text': [mb.group(2) if mb else mo.group(3)],
                          'children': None})
            i += 1
            continue
        if line.startswith(' ') and items:
            items[-1]['text'].append(line.strip())
            i += 1
            continue
        break
    return ((kind, start), items), i


# =========================================================================
# 2. Texto en linea
# =========================================================================
URL_RE = re.compile(r'https?://[^\s<>()\[\]]+[^\s<>()\[\].,;:]')
MDLINK = re.compile(r'\[([^\]\n]+)\]\((https?://[^)\s]+)\)')
BADGE = re.compile(r'\{\{(ev|mad|tipo|conf):([^}]+)\}\}')
TERM = re.compile(r'\{\{t:([a-z0-9-]+)\|([^}]+)\}\}')
GLOSARIO = {}

BADGE_CLS = {'ev': 'ev', 'mad': 'mad', 'tipo': 'tipo', 'conf': 'conf'}


def esc_html(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _emph_html(text):
    t = esc_html(text)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    return re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', t)


def _emph_tex(text):
    t = esc_tex(text)
    t = re.sub(r'\*\*([^*]+)\*\*', r'\\textbf{\1}', t)
    return re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'\\emph{\1}', t)


def badge_html(kind, value):
    if kind == 'ev':
        cls = 'b-ev b-ev-%s' % value.strip().lower()
        return '<span class="badge %s" title="Nivel de evidencia %s">%s</span>' \
               % (cls, esc_html(value), esc_html(value))
    if kind == 'mad':
        return '<span class="badge b-mad" title="Madurez comercial">%s</span>' \
               % esc_html(value)
    if kind == 'conf':
        return '<span class="badge b-conf">Confianza %s</span>' % esc_html(value)
    return '<span class="badge b-tipo">%s</span>' % esc_html(value)


def inline_html(text):
    slots = []

    def stash(h):
        slots.append(h)
        return '\x00%d\x00' % (len(slots) - 1)

    text = re.sub(r'`([^`]+)`',
                  lambda m: stash('<code>%s</code>' % esc_html(m.group(1))), text)
    text = TERM.sub(lambda m: stash(
        '<a class="term" href="#g-%s" title="%s">%s</a>'
        % (m.group(1), esc_html(GLOSARIO.get(m.group(1), '')[:180]),
           _emph_html(m.group(2)))), text)
    text = BADGE.sub(lambda m: stash(badge_html(m.group(1), m.group(2))), text)
    text = MDLINK.sub(lambda m: stash('<a href="%s">%s</a>'
                                      % (esc_html(m.group(2)),
                                         esc_html(m.group(1)))), text)
    text = URL_RE.sub(lambda m: stash('<a class="url" href="%s">%s</a>'
                                      % (esc_html(m.group(0)),
                                         esc_html(m.group(0)))), text)
    text = esc_html(text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', text)
    return re.sub(r'\x00(\d+)\x00', lambda m: slots[int(m.group(1))], text)


def join_html(lines):
    out = []
    for k, ln in enumerate(lines):
        piece = inline_html(ln.strip())
        if k < len(lines) - 1:
            piece += '<br>' if ln.rstrip('\n').endswith('  ') else ' '
        out.append(piece)
    return ''.join(out)


def plain(text):
    t = re.sub(r'<[^>]+>', '', inline_html(text))
    return t.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')


SLUGS = {}


def slug(text):
    t = unicodedata.normalize('NFKD', plain(text)).encode('ascii', 'ignore').decode()
    t = re.sub(r'[^a-zA-Z0-9]+', '-', t).strip('-').lower() or 'sec'
    SLUGS[t] = SLUGS.get(t, 0) + 1
    return t if SLUGS[t] == 1 else '%s-%d' % (t, SLUGS[t])


# =========================================================================
# 3. Render HTML
# =========================================================================
def svg_inline(fig_id):
    path = os.path.join(ASSETS, fig_id + '.svg')
    with open(path, encoding='utf-8') as fh:
        s = fh.read()
    s = re.sub(r'<\?xml[^>]*\?>', '', s)
    s = s.replace('id="ti"', 'id="ti-%s"' % fig_id)
    s = s.replace('id="de"', 'id="de-%s"' % fig_id)
    s = s.replace('aria-labelledby="ti de"',
                  'aria-labelledby="ti-%s de-%s"' % (fig_id, fig_id))
    s = re.sub(r'(<svg[^>]*?)\swidth="\d+"\sheight="\d+"', r'\1', s, count=1)
    return s.strip()


def render_list_html(spec, items, out):
    kind, start = spec
    check = all(CHECK.match(it['text'][0]) for it in items) if items else False
    cls = ' class="checklist"' if check else ''
    st = ' start="%d"' % start if kind == 'ol' and start != 1 else ''
    out.append('<%s%s%s>' % (kind, st, cls))
    for it in items:
        lines = list(it['text'])
        mark = ''
        if check:
            m = CHECK.match(lines[0])
            lines[0] = lines[0][m.end():]
            mark = '<span class="box">%s</span>' % (
                '&#10003;' if m.group(1).lower() == 'x' else '&#9633;')
        out.append('<li>%s%s' % (mark, join_html(lines)))
        if it['children']:
            render_list_html(it['children'][0], it['children'][1], out)
        for p in it.get('paras', []):
            out.append('<p>%s</p>' % join_html(p))
        out.append('</li>')
    out.append('</%s>' % kind)


NOTA_LABEL = {'clave': 'Punto clave', 'dato': 'Dato verificado',
              'riesgo': 'Riesgo', 'inferencia': 'Inferencia de ingeniería'}

FIGN = {'n': 0}


def render_dir_html(meta, body, out, ctx):
    kind, arg = meta['kind'], meta['arg']
    if kind == 'nota':
        parts = [p.strip() for p in split_pipes(arg)]
        clase = parts[0] if parts and parts[0] else 'clave'
        titulo = parts[1] if len(parts) > 1 else NOTA_LABEL.get(clase, '')
        out.append('<aside class="callout c-%s">' % clase)
        if titulo:
            out.append('<div class="callout-h">%s</div>' % inline_html(titulo))
        render_html_blocks(body, out, ctx)
        out.append('</aside>')
    elif kind == 'kpi':
        rows = []
        for b in body:
            if b[0] == 'para':
                rows.extend(b[2])
        out.append('<div class="kpis">')
        for r in rows:
            cells = [c.strip() for c in r.split('||')]
            val = cells[0] if cells else ''
            lab = cells[1] if len(cells) > 1 else ''
            note = cells[2] if len(cells) > 2 else ''
            out.append('<div class="kpi"><div class="kpi-v">%s</div>'
                       '<div class="kpi-l">%s</div>'
                       '<div class="kpi-n">%s</div></div>'
                       % (inline_html(val), inline_html(lab), inline_html(note)))
        out.append('</div>')
    elif kind == 'fig':
        parts = [p.strip() for p in split_pipes(arg)]
        fid = parts[0]
        cap = parts[1] if len(parts) > 1 else ''
        src = parts[2] if len(parts) > 2 else ''
        FIGN['n'] += 1
        out.append('<figure class="fig" id="%s">' % fid)
        out.append(svg_inline(fid))
        out.append('<figcaption>%s%s</figcaption>'
                   % (inline_html(cap),
                      ' <span class="src">%s</span>' % inline_html(src)
                      if src else ''))
        out.append('</figure>')
    elif kind == 'tarjetas':
        n = arg.strip() or '2'
        out.append('<div class="cards cards-%s">' % n)
        render_html_blocks(body, out, ctx)
        out.append('</div>')
    elif kind == 'tarjeta':
        parts = [p.strip() for p in split_pipes(arg)]
        tit = parts[0] if parts else ''
        meta_txt = parts[1] if len(parts) > 1 else ''
        out.append('<div class="card">')
        if tit:
            out.append('<div class="card-h">%s</div>' % inline_html(tit))
        if meta_txt:
            out.append('<div class="card-m">%s</div>' % inline_html(meta_txt))
        render_html_blocks(body, out, ctx)
        out.append('</div>')
    elif kind == 'glosario':
        rows = []
        for blk in body:
            if blk[0] == 'para':
                rows.extend(blk[2])
        out.append('<dl class="gloss">')
        for r in rows:
            c = [x.strip() for x in r.split('||')]
            if len(c) < 3:
                continue
            key, term, definicion = c[0], c[1], c[2]
            fuente = c[3] if len(c) > 3 else ''
            out.append('<dt id="g-%s">%s</dt>' % (key, inline_html(term)))
            out.append('<dd>%s%s</dd>'
                       % (inline_html(definicion),
                          '<span class="gsrc">%s</span>' % inline_html(fuente)
                          if fuente else ''))
        out.append('</dl>')
    elif kind == 'detalle':
        out.append('<details class="det"><summary>%s</summary><div class="det-b">'
                   % inline_html(arg))
        render_html_blocks(body, out, ctx)
        out.append('</div></details>')
    else:
        render_html_blocks(body, out, ctx)


def render_html_blocks(blocks, out, ctx):
    for kind, a, b in blocks:
        if kind == 'dir':
            render_dir_html(a, b, out, ctx)
        elif kind == 'para':
            out.append('<p>%s</p>' % join_html(b))
        elif kind == 'quote':
            out.append('<blockquote>%s</blockquote>' % join_html(b))
        elif kind == 'list':
            render_list_html(a, b, out)
        elif kind == 'hr':
            pass
        elif kind == 'table':
            render_table_html(a['header'], a['aligns'], b, out)
        elif kind == 'heading':
            level, text = a, b
            sl = slug(text)
            if level == 1:
                ctx['toc'].append((1, sl, text))
                out.append('<h2 class="part" id="%s">%s</h2>'
                           % (sl, inline_html(text)))
            elif level == 2:
                ctx['toc'].append((2, sl, text))
                out.append('<h3 id="%s">%s</h3>' % (sl, inline_html(text)))
            elif level == 3:
                out.append('<h4 id="%s">%s</h4>' % (sl, inline_html(text)))
            else:
                out.append('<h5 id="%s">%s</h5>' % (sl, inline_html(text)))


def render_table_html(header, aligns, rows, out):
    out.append('<div class="tw"><table><thead><tr>')
    for k, h in enumerate(header):
        al = aligns[k] if k < len(aligns) else 'left'
        out.append('<th class="%s">%s</th>' % (al, inline_html(h)))
    out.append('</tr></thead>')
    if rows:
        out.append('<tbody>')
        for r in rows:
            out.append('<tr>')
            for k, c in enumerate(r):
                al = aligns[k] if k < len(aligns) else 'left'
                out.append('<td class="%s">%s</td>' % (al, inline_html(c)))
            out.append('</tr>')
        out.append('</tbody>')
    else:
        out.append('<tbody><tr><td class="empty" colspan="%d">Plantilla de '
                   'registro: se completa durante la investigación.</td></tr>'
                   '</tbody>' % len(header))
    out.append('</table></div>')


def render_html(meta, blocks):
    ctx = {'toc': []}
    body = []
    render_html_blocks(blocks, body, ctx)

    toc = ['<nav id="toc"><div class="toc-t">Contenido</div><ul>']
    for level, sl, text in ctx['toc']:
        toc.append('<li class="l%d"><a href="#%s">%s</a></li>'
                   % (level, sl, inline_html(text)))
    toc.append('</ul></nav>')

    return HTML.format(
        title=esc_html(meta.get('titulo', 'Informe')),
        titulo=inline_html(meta.get('titulo', '')),
        subtitulo=inline_html(meta.get('subtitulo', '')),
        edicion=inline_html(meta.get('edicion', '')),
        fecha=inline_html(meta.get('fecha', '')),
        toc=''.join(toc),
        body='\n'.join(body),
    ).replace('<<SCRIPT>>', SCRIPT)


SCRIPT = """<script>
(function () {
  var links = {};
  document.querySelectorAll('#toc a').forEach(function (a) {
    links[a.getAttribute('href').slice(1)] = a;
  });
  var targets = Object.keys(links).map(function (id) {
    return document.getElementById(id);
  }).filter(Boolean);
  if (!('IntersectionObserver' in window) || !targets.length) return;
  var seen = new Set();
  var obs = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) seen.add(e.target.id); else seen.delete(e.target.id);
    });
    var cur = targets.filter(function (t) { return seen.has(t.id); })[0];
    if (!cur) return;
    document.querySelectorAll('#toc a.on').forEach(function (a) {
      a.classList.remove('on');
    });
    if (links[cur.id]) {
      links[cur.id].classList.add('on');
      var box = document.getElementById('toc');
      var el = links[cur.id];
      if (box && el.offsetTop < box.scrollTop ||
          el.offsetTop > box.scrollTop + box.clientHeight - 60) {
        box.scrollTop = el.offsetTop - box.clientHeight / 2;
      }
    }
  }, { rootMargin: '0px 0px -72% 0px' });
  targets.forEach(function (t) { obs.observe(t); });
})();
</script>"""


HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root {{
    --ink:#18222e; --ink-2:#43505f; --ink-3:#6d7885;
    --line:#e3e6ea; --line-2:#cfd5dc;
    --nav:#14496b; --nav-2:#1d6096; --paper:#ffffff; --plane:#f3f5f7;
    --amber:#a6690c; --amber-bg:#fdf7ec;
    --red:#b23b32; --red-bg:#fdf4f3;
    --green:#2c6a49; --green-bg:#f1f7f3;
    --blue-bg:#eff4f9;
  }}
  * {{ box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  body {{
    margin:0; background:var(--plane); color:var(--ink);
    font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,
      "Helvetica Neue",Arial,sans-serif;
    font-size:16px; line-height:1.65; -webkit-font-smoothing:antialiased;
  }}
  .layout {{ display:flex; align-items:flex-start; }}

  /* ---------------- indice lateral ---------------- */
  #toc {{
    position:sticky; top:0; flex:0 0 19.5rem; max-height:100vh;
    overflow-y:auto; padding:2rem 1rem 3rem 1.6rem;
    border-right:1px solid var(--line); background:var(--paper);
  }}
  .toc-t {{ font-size:.68rem; letter-spacing:.14em; text-transform:uppercase;
           color:var(--ink-3); font-weight:700; margin-bottom:.9rem; }}
  #toc ul {{ list-style:none; margin:0; padding:0; font-size:.82rem; }}
  #toc a {{ display:block; padding:.22rem .5rem; color:var(--ink-2);
            text-decoration:none; border-left:2px solid transparent; }}
  #toc a:hover {{ color:var(--nav); background:var(--plane); }}
  #toc a.on {{ color:var(--nav); background:var(--blue-bg);
               border-left-color:var(--nav); font-weight:600; }}
  #toc .l1 > a {{ margin-top:.7rem; font-weight:700; color:var(--ink);
                  font-size:.8rem; letter-spacing:.02em;
                  text-transform:uppercase; }}
  #toc .l2 > a {{ padding-left:.9rem; }}

  /* ---------------- hoja ---------------- */
  main {{ flex:1 1 auto; min-width:0; padding:2.2rem 2rem 5rem; }}
  .sheet {{
    max-width:64rem; margin:0 auto; background:var(--paper);
    border:1px solid var(--line); border-radius:4px;
    box-shadow:0 1px 3px rgba(20,35,60,.05);
    padding:3.4rem 3.4rem 4rem;
  }}
  /* medida de lectura para el texto; medios a ancho completo */
  .sheet > p, .sheet > ul, .sheet > ol, .sheet > blockquote,
  .sheet > h3, .sheet > h4, .sheet > h5, .sheet > .callout,
  .sheet > details.det, .sheet > dl.gloss {{ max-width:46rem; }}

  /* ---------------- portada ---------------- */
  .cover {{ border-bottom:3px solid var(--nav); padding-bottom:2rem;
            margin-bottom:2.4rem; }}
  .eyebrow {{ font-size:.7rem; letter-spacing:.16em; text-transform:uppercase;
              color:var(--nav); font-weight:700; }}
  .cover h1 {{ font-size:2.3rem; line-height:1.18; margin:1.1rem 0 .7rem;
               letter-spacing:-.015em; }}
  .cover + h2.part {{ border-top:0; padding-top:0; margin-top:2rem; }}
  .cover .sub {{ font-size:1.14rem; color:var(--ink-2); margin:0 0 1.6rem;
                 max-width:38rem; }}
  .cover .meta {{ display:flex; flex-wrap:wrap; gap:.5rem 2.4rem;
                  font-size:.85rem; color:var(--ink-3); }}

  /* ---------------- jerarquia ---------------- */
  h2.part {{
    font-size:1.62rem; margin:3.4rem 0 1.4rem; padding-top:1.6rem;
    border-top:2px solid var(--nav); color:var(--nav);
    letter-spacing:-.01em;
  }}
  h3 {{ font-size:1.22rem; margin:2.4rem 0 .8rem; padding-bottom:.4rem;
        border-bottom:1px solid var(--line); letter-spacing:-.005em; }}
  h4 {{ font-size:1.02rem; margin:1.7rem 0 .5rem; color:var(--nav); }}
  h5 {{ font-size:.78rem; margin:1.3rem 0 .4rem; text-transform:uppercase;
        letter-spacing:.08em; color:var(--ink-3); }}
  p {{ margin:0 0 .95rem; }}
  ul,ol {{ margin:0 0 1rem; padding-left:1.3rem; }}
  li {{ margin:.24rem 0; }}
  li > ul, li > ol {{ margin:.3rem 0 .5rem; }}
  a {{ color:var(--nav-2); }}
  a.url {{ word-break:break-all; font-size:.85em;
           font-family:ui-monospace,Menlo,Consolas,monospace; }}
  code {{ background:var(--plane); border:1px solid var(--line);
          border-radius:3px; padding:.06em .34em; font-size:.86em;
          font-family:ui-monospace,Menlo,Consolas,monospace; }}
  blockquote {{ margin:1.1rem 0; padding:.2rem 0 .2rem 1.1rem;
                border-left:3px solid var(--line-2); color:var(--ink-2);
                font-style:italic; }}

  /* ---------------- distintivos ---------------- */
  .badge {{ display:inline-block; font-size:.68rem; font-weight:700;
            letter-spacing:.04em; padding:.1rem .42rem; border-radius:3px;
            vertical-align:.08em; white-space:nowrap; }}
  .b-ev-a {{ background:var(--nav); color:#fff; }}
  .b-ev-b {{ background:#2a78d6; color:#fff; }}
  .b-ev-c {{ background:#cfe0f3; color:#123f66; }}
  .b-ev-d {{ background:#e6e8ea; color:#4a5560; }}
  .b-mad {{ background:#eff4f9; color:#14496b; border:1px solid #c5d8ea; }}
  .b-tipo {{ background:var(--amber-bg); color:var(--amber);
             border:1px solid #ecd9b4; }}
  .b-conf {{ background:#f1f2f4; color:var(--ink-2); border:1px solid var(--line); }}

  /* ---------------- llamados ---------------- */
  .callout {{ margin:1.4rem 0; padding:.95rem 1.15rem; border-radius:0 4px 4px 0;
              border-left:3px solid var(--nav); background:var(--blue-bg); }}
  .callout p:last-child, .callout ul:last-child, .callout ol:last-child
    {{ margin-bottom:0; }}
  .callout-h {{ font-size:.72rem; font-weight:700; letter-spacing:.09em;
                text-transform:uppercase; margin-bottom:.45rem;
                color:var(--nav); }}
  .c-clave {{ border-left-color:var(--amber); background:var(--amber-bg); }}
  .c-clave .callout-h {{ color:var(--amber); }}
  .c-riesgo {{ border-left-color:var(--red); background:var(--red-bg); }}
  .c-riesgo .callout-h {{ color:var(--red); }}
  .c-inferencia {{ border-left-color:var(--green); background:var(--green-bg); }}
  .c-inferencia .callout-h {{ color:var(--green); }}

  /* ---------------- indicadores ---------------- */
  .kpis {{ display:grid; grid-template-columns:repeat(4,1fr); gap:1rem;
           margin:1.5rem 0 1.8rem; }}
  .kpi {{ border:1px solid var(--line); border-top:3px solid var(--nav);
          border-radius:4px; padding:.85rem .9rem; background:var(--paper); }}
  .kpi-v {{ font-size:1.6rem; font-weight:700; color:var(--nav);
            line-height:1.15; font-variant-numeric:tabular-nums; }}
  .kpi-l {{ font-size:.82rem; margin-top:.25rem; }}
  .kpi-n {{ font-size:.74rem; color:var(--ink-3); margin-top:.2rem; }}

  /* ---------------- tarjetas ---------------- */
  .cards {{ display:grid; gap:.9rem; margin:1.4rem 0 1.8rem; }}
  .cards-2 {{ grid-template-columns:repeat(2,1fr); }}
  .cards-3 {{ grid-template-columns:repeat(3,1fr); }}
  .card {{ border:1px solid var(--line); border-radius:5px; padding:.9rem 1rem;
           background:var(--paper); }}
  .card-h {{ font-weight:700; font-size:.95rem; color:var(--nav);
             margin-bottom:.15rem; }}
  .card-m {{ font-size:.75rem; color:var(--ink-3); margin-bottom:.5rem;
             text-transform:uppercase; letter-spacing:.06em; }}
  .card p:last-child, .card ul:last-child {{ margin-bottom:0; }}
  .card p, .card li {{ font-size:.92rem; }}

  /* ---------------- figuras ---------------- */
  figure.fig {{ margin:1.8rem 0; padding:1rem 1rem .6rem;
                border:1px solid var(--line); border-radius:5px;
                background:var(--paper); }}
  figure.fig svg {{ display:block; width:100%; height:auto; }}
  figcaption {{ font-size:.8rem; color:var(--ink-2); margin-top:.7rem;
                padding-top:.6rem; border-top:1px solid var(--line);
                line-height:1.5; }}
  figcaption .src {{ color:var(--ink-3); }}

  /* ---------------- desplegables ---------------- */
  details.det {{ border:1px solid var(--line); border-radius:5px;
                 margin:1.3rem 0; background:var(--paper); }}
  details.det > summary {{ cursor:pointer; padding:.7rem 1rem;
                           font-weight:600; font-size:.9rem; color:var(--nav);
                           list-style:none; }}
  details.det > summary::-webkit-details-marker {{ display:none; }}
  details.det > summary::before {{ content:"▸"; margin-right:.5rem;
                                   color:var(--ink-3); }}
  details.det[open] > summary::before {{ content:"▾"; }}
  .det-b {{ padding:0 1rem .6rem; border-top:1px solid var(--line);
            padding-top:.8rem; }}
  .det-b p:last-child, .det-b ul:last-child {{ margin-bottom:0; }}

  /* ---------------- glosario ---------------- */
  a.term {{ color:inherit; text-decoration:none;
            border-bottom:1px dotted var(--nav-2); cursor:help; }}
  a.term:hover {{ color:var(--nav-2); border-bottom-style:solid; }}
  dl.gloss {{ margin:1.2rem 0; }}
  dl.gloss dt {{ font-weight:700; color:var(--nav); margin-top:.9rem;
                 scroll-margin-top:1rem; }}
  dl.gloss dt:target {{ background:var(--blue-bg); box-shadow:0 0 0 .3rem var(--blue-bg); }}
  dl.gloss dd {{ margin:.15rem 0 0; font-size:.94rem; }}
  dl.gloss .gsrc {{ display:block; font-size:.78rem; color:var(--ink-3);
                    margin-top:.15rem; }}

  /* ---------------- tablas ---------------- */
  .tw {{ overflow-x:auto; margin:1.3rem 0 1.6rem; border:1px solid var(--line);
         border-radius:5px; }}
  table {{ border-collapse:collapse; width:100%; font-size:.82rem; }}
  td {{ hyphens:auto; }}
  th,td {{ padding:.5rem .7rem; border-bottom:1px solid var(--line);
           vertical-align:top; text-align:left; }}
  thead th {{ position:sticky; top:0; background:var(--nav); color:#fff;
              font-weight:600; white-space:nowrap; }}
  td.right,th.right {{ text-align:right; }}
  td.center,th.center {{ text-align:center; }}
  tbody tr:nth-child(even) {{ background:#fafbfc; }}
  td.empty {{ color:var(--ink-3); font-style:italic; text-align:center; }}

  /* ---------------- listas de verificacion ---------------- */
  ul.checklist {{ list-style:none; padding-left:0; }}
  ul.checklist li {{ padding-left:1.6rem; text-indent:-1.6rem; }}
  ul.checklist .box {{ display:inline-block; width:1.6rem; text-indent:0;
                       color:var(--nav); font-weight:700; }}

  @media (max-width:1080px) {{
    .layout {{ display:block; }}
    #toc {{ position:static; max-height:none; width:auto; flex:none;
            border-right:0; border-bottom:1px solid var(--line); }}
    main {{ padding:1.2rem .8rem 3rem; }}
    .sheet {{ padding:2rem 1.3rem 2.5rem; }}
    .cards-2,.cards-3 {{ grid-template-columns:1fr; }}
    .kpis {{ grid-template-columns:repeat(2,1fr); }}
    .cover h1 {{ font-size:1.7rem; }}
  }}
  @media print {{
    body {{ background:#fff; font-size:10.5pt; }}
    #toc {{ display:none; }}
    main {{ padding:0; }}
    .sheet {{ max-width:none; border:0; box-shadow:none; padding:0; }}
    h2.part {{ break-before:page; }}
    figure.fig, .card, .callout, .kpi, table {{ break-inside:avoid; }}
    details.det {{ break-inside:avoid; }}
    details.det > summary {{ list-style:none; }}
    details.det:not([open]) .det-b {{ display:block; }}
    thead th {{ position:static; }}
    a {{ color:inherit; text-decoration:none; }}
  }}
</style>
</head>
<body>
<div class="layout">
{toc}
<main>
  <article class="sheet">
    <header class="cover">
      <div class="eyebrow">{edicion}</div>
      <h1>{titulo}</h1>
      <p class="sub">{subtitulo}</p>
      <div class="meta"><span>{fecha}</span></div>
    </header>
{body}
  </article>
</main>
</div>
<<SCRIPT>>
</body>
</html>
"""


# =========================================================================
# 4. Render LaTeX
# =========================================================================
TEXCH = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
         '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}',
         '~': r'\textasciitilde{}', '^': r'\textasciicircum{}',
         '<': r'\textless{}', '>': r'\textgreater{}',
         '×': r'$\times$', '→': r'$\rightarrow$', '±': r'$\pm$',
         '“': r'``', '”': r"''", '"': r"''", '│': r'|',
         '·': r'\textperiodcentered{}', '≈': r'$\approx$', '≥': r'$\geq$',
         '≤': r'$\leq$', '−': r'$-$', '°': r'\textdegree{}',
         '•': r'\textbullet{}', '…': r'\dots{}', '™': r'\texttrademark{}',
         '®': r'\textregistered{}', '½': r'$\frac{1}{2}$'}


def esc_tex(s):
    return ''.join(TEXCH.get(c, c) for c in s)


def badge_tex(kind, value):
    v = esc_tex(value.strip())
    if kind == 'ev':
        color = {'a': 'navy', 'b': 'sblue', 'c': 'lblue', 'd': 'lgray'}.get(
            value.strip().lower(), 'lgray')
        fg = 'white' if color in ('navy', 'sblue') else 'ink'
        return r'\badge{%s}{%s}{%s}' % (color, fg, v)
    if kind == 'mad':
        return r'\badge{lblue}{ink}{%s}' % v
    if kind == 'conf':
        return r'\badge{lgray}{ink}{Confianza %s}' % v
    return r'\badge{lamber}{amber}{%s}' % v


def inline_tex(text):
    slots = []

    def stash(t):
        slots.append(t)
        return '\x00%d\x00' % (len(slots) - 1)

    text = re.sub(r'`([^`]+)`',
                  lambda m: stash(r'\texttt{%s}' % esc_tex(m.group(1))), text)
    text = TERM.sub(lambda m: stash(
        r'\hyperlink{g-%s}{%s}\textsuperscript{\textsc{g}}'
        % (m.group(1), _emph_tex(m.group(2)))), text)
    text = BADGE.sub(lambda m: stash(badge_tex(m.group(1), m.group(2))), text)
    text = MDLINK.sub(lambda m: stash(r'\href{%s}{%s}'
                                      % (m.group(2).replace('%', r'\%'),
                                         esc_tex(m.group(1)))), text)
    text = URL_RE.sub(lambda m: stash(r'\url{%s}' % m.group(0)), text)
    text = esc_tex(text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\\textbf{\1}', text)
    text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'\\emph{\1}', text)
    return re.sub(r'\x00(\d+)\x00', lambda m: slots[int(m.group(1))], text)


def join_tex(lines):
    out = []
    for k, ln in enumerate(lines):
        piece = inline_tex(ln.strip())
        if k < len(lines) - 1:
            piece += (r' \\' + '\n') if ln.rstrip('\n').endswith('  ') else '\n'
        out.append(piece)
    return ''.join(out)


def render_list_tex(spec, items, out):
    kind, start = spec
    check = all(CHECK.match(it['text'][0]) for it in items) if items else False
    if check:
        out.append(r'\begin{itemize}[label=$\square$,leftmargin=1.6em]')
        env = 'itemize'
    elif kind == 'ol':
        out.append(r'\begin{enumerate}%s'
                   % ('[start=%d]' % start if start != 1 else ''))
        env = 'enumerate'
    else:
        out.append(r'\begin{itemize}')
        env = 'itemize'
    for it in items:
        lines = list(it['text'])
        if check:
            lines[0] = lines[0][CHECK.match(lines[0]).end():]
        content = join_tex(lines)
        if content.startswith('['):
            content = '{}' + content
        out.append(r'\item ' + content)
        if it['children']:
            render_list_tex(it['children'][0], it['children'][1], out)
        for p in it.get('paras', []):
            out.append('')
            out.append(join_tex(p))
    out.append(r'\end{%s}' % env)


def render_dir_tex(meta, body, out):
    kind, arg = meta['kind'], meta['arg']
    if kind == 'nota':
        parts = [p.strip() for p in split_pipes(arg)]
        clase = parts[0] if parts and parts[0] else 'clave'
        titulo = parts[1] if len(parts) > 1 else NOTA_LABEL.get(clase, '')
        env = 'nota' + (clase if clase in ('clave', 'dato', 'riesgo',
                                           'inferencia') else 'dato')
        out.append(r'\begin{%s}{%s}' % (env, inline_tex(titulo)))
        render_tex_blocks(body, out)
        out.append(r'\end{%s}' % env)
    elif kind == 'kpi':
        rows = []
        for b in body:
            if b[0] == 'para':
                rows.extend(b[2])
        n = max(1, len(rows))
        out.append(r'\begin{center}\setlength{\tabcolsep}{4pt}')
        colspec = ('>{\\raggedright\\arraybackslash}p{%.3f\\linewidth}'
                   % (0.94 / n)) * n
        out.append(r'\begin{tabular}{%s}' % colspec)
        cells = []
        for r in rows:
            c = [x.strip() for x in r.split('||')]
            val = inline_tex(c[0]) if c else ''
            lab = inline_tex(c[1]) if len(c) > 1 else ''
            note = inline_tex(c[2]) if len(c) > 2 else ''
            cells.append(r'{\color{navy}\Large\bfseries %s}\\[2pt]'
                         r'{\small %s}\\[1pt]{\footnotesize\color{gray2} %s}'
                         % (val, lab, note))
        out.append(' & '.join(cells) + r' \\')
        out.append(r'\end{tabular}\end{center}')
    elif kind == 'fig':
        parts = [p.strip() for p in split_pipes(arg)]
        fid = parts[0]
        cap = parts[1] if len(parts) > 1 else ''
        src = parts[2] if len(parts) > 2 else ''
        out.append(r'\begin{figure}[htbp]\centering')
        out.append(r'\fbox{\includegraphics[width=0.98\linewidth]{assets/%s.pdf}}'
                   % fid)
        out.append(r'\caption*{\footnotesize\raggedright %s%s}'
                   % (inline_tex(cap),
                      r' {\color{gray2}%s}' % inline_tex(src) if src else ''))
        out.append(r'\end{figure}')
    elif kind == 'tarjetas':
        render_tex_blocks(body, out)
    elif kind == 'tarjeta':
        parts = [p.strip() for p in split_pipes(arg)]
        tit = parts[0] if parts else ''
        met = parts[1] if len(parts) > 1 else ''
        out.append(r'\begin{tarjeta}{%s}{%s}' % (inline_tex(tit), inline_tex(met)))
        render_tex_blocks(body, out)
        out.append(r'\end{tarjeta}')
    elif kind == 'glosario':
        rows = []
        for blk in body:
            if blk[0] == 'para':
                rows.extend(blk[2])
        out.append(r'\begin{description}[leftmargin=0pt,style=unboxed,'
                   r'font=\normalfont\bfseries\sffamily,itemsep=3pt]')
        for r in rows:
            c = [x.strip() for x in r.split('||')]
            if len(c) < 3:
                continue
            key, term, definicion = c[0], c[1], c[2]
            fuente = c[3] if len(c) > 3 else ''
            out.append(r'\item[\hypertarget{g-%s}{%s}] %s%s'
                       % (key, inline_tex(term), inline_tex(definicion),
                          r' {\footnotesize\color{gray2}%s}' % inline_tex(fuente)
                          if fuente else ''))
        out.append(r'\end{description}')
    elif kind == 'detalle':
        out.append(r'\begin{detalle}{%s}' % inline_tex(arg))
        render_tex_blocks(body, out)
        out.append(r'\end{detalle}')
    else:
        render_tex_blocks(body, out)


TEXSEC = {1: 'section', 2: 'subsection', 3: 'subsubsection', 4: 'paragraph',
          5: 'paragraph', 6: 'paragraph'}


def render_tex_blocks(blocks, out):
    for kind, a, b in blocks:
        if kind == 'dir':
            render_dir_tex(a, b, out)
        elif kind == 'para':
            out.append(join_tex(b))
            out.append('')
        elif kind == 'quote':
            out.append(r'\begin{quote}\itshape %s\end{quote}' % join_tex(b))
        elif kind == 'list':
            render_list_tex(a, b, out)
            out.append('')
        elif kind == 'hr':
            pass
        elif kind == 'table':
            out.append(tex_table(a['header'], a['aligns'], b))
            out.append('')
        elif kind == 'heading':
            level, text = a, b
            name = TEXSEC[level]
            t = inline_tex(text)
            toc = re.sub(r'\\badge\{[^}]*\}\{[^}]*\}\{([^}]*)\}', r'\1', t)
            toc = re.sub(r'\\(textbf|emph|texttt)\{([^{}]*)\}', r'\2', toc)
            if level == 1:
                out.append(r'\clearpage')
            out.append('\n' + r'\%s*{%s}' % (name, t))
            if level <= 3:
                out.append(r'\addcontentsline{toc}{%s}{%s}' % (name, toc))
            out.append('')


def _visible(cell):
    """Texto tal como se ve, para estimar el ancho de columna.

    Los marcadores ocupan mucho más en la fuente que en el papel: medir el
    original inflaba unas columnas y estrujaba otras.
    """
    t = re.sub(r'\{\{t:[a-z0-9-]+\|([^}]+)\}\}', r'\1 ', cell)
    t = re.sub(r'\{\{(?:ev|mad|tipo|conf):([^}]+)\}\}', r'\1 ', t)
    return re.sub(r'\*\*|\*|`', '', t)


def tex_table(header, aligns, rows):
    ncol = len(header)
    wide = ncol >= 8
    # ancho de columna proporcional al contenido, acotado
    widths = []
    for k in range(ncol):
        cells = [_visible(header[k])] + [_visible(r[k]) for r in rows
                                         if k < len(r)]
        lens = [len(cells[0]) * 1.35] + [len(c) for c in cells[1:]]
        # piso: la palabra mas larga debe entrar sin desbordar
        palabras = [len(w) for c in cells for w in c.split()] or [4]
        widths.append(min(max(max(lens), max(palabras) * 2.6, 10), 60))
    total = float(sum(widths))
    colspec = ''.join(
        '>{\\RaggedRight\\arraybackslash}p{\\dimexpr %.4f\\linewidth-'
        '2\\tabcolsep\\relax}' % (0.995 * w / total) for w in widths)
    lines = ([r'\begin{landscape}'] if wide else []) + [
        r'\begingroup\footnotesize',
        r'\setlength{\tabcolsep}{%dpt}' % (2 if wide else 3 if ncol >= 5 else 4),
        r'\setlength{\emergencystretch}{4em}',
        r'\hyphenpenalty=50 \exhyphenpenalty=50',
        r'\begin{longtable}{@{}%s@{}}' % colspec,
        r'\toprule']
    head = ' & '.join(r'\scriptsize\textbf{%s}'
                      % inline_tex(h).replace('/', r'\slash ')
                      for h in header) + r' \\'
    lines += [head, r'\midrule', r'\endfirsthead', r'\toprule', head,
              r'\midrule', r'\endhead', r'\bottomrule', r'\endfoot']
    if rows:
        for r in rows:
            cells = [inline_tex(c) for c in r] + [''] * (ncol - len(r))
            lines.append(' & '.join(cells[:ncol]) + r' \\')
    else:
        lines.append(r'\multicolumn{%d}{@{}l@{}}{\itshape Plantilla de registro: '
                     r'se completa durante la investigación.} \\' % ncol)
    lines += [r'\end{longtable}', r'\endgroup']
    if wide:
        lines.append(r'\end{landscape}')
    return '\n'.join(lines)


def render_tex(meta, blocks):
    out = []
    render_tex_blocks(blocks, out)
    return (TEX.replace('<<TITULO>>', inline_tex(meta.get('titulo', '')))
               .replace('<<SUBTITULO>>', inline_tex(meta.get('subtitulo', '')))
               .replace('<<EDICION>>', inline_tex(meta.get('edicion', '')))
               .replace('<<FECHA>>', inline_tex(meta.get('fecha', '')))
               .replace('<<BODY>>', '\n'.join(out)))


TEX = r"""% !TeX program = pdflatex
%=======================================================================
%  Informe generado desde source/informe.md por tools/md2report.py
%  Compilar:  pdflatex informe.tex  (tres veces, por el indice)
%=======================================================================
\documentclass[11pt,a4paper]{article}

\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[spanish,es-noshorthands,es-tabla]{babel}
\usepackage{lmodern}
\usepackage[a4paper,top=2.5cm,bottom=2.4cm,left=2.8cm,right=2.5cm]{geometry}

\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{pdflscape}
\usepackage{array}
\usepackage{ragged2e}
\usepackage{enumitem}
\usepackage{amssymb}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{parskip}
\usepackage{microtype}
\usepackage{caption}
\usepackage{etoolbox}
\usepackage[most]{tcolorbox}
\usepackage[hidelinks,breaklinks=true]{hyperref}
\usepackage{url}

\definecolor{navy}{HTML}{14496B}
\definecolor{sblue}{HTML}{2A78D6}
\definecolor{lblue}{HTML}{DCE8F4}
\definecolor{lgray}{HTML}{E6E8EA}
\definecolor{lamber}{HTML}{FBF1DE}
\definecolor{amber}{HTML}{A6690C}
\definecolor{red}{HTML}{B23B32}
\definecolor{green}{HTML}{2C6A49}
\definecolor{ink}{HTML}{18222E}
\definecolor{gray2}{HTML}{6D7885}
\definecolor{rule2}{HTML}{CFD5DC}
\definecolor{navybg}{HTML}{EFF4F9}
\definecolor{amberbg}{HTML}{FDF7EC}
\definecolor{redbg}{HTML}{FDF4F3}
\definecolor{greenbg}{HTML}{F1F7F3}

\hypersetup{colorlinks=true, linkcolor=navy, urlcolor=navy,
            citecolor=navy, pdftitle={<<TITULO>>}}
\renewcommand{\UrlFont}{\small\ttfamily}
\Urlmuskip=0mu plus 1mu
\def\UrlBreaks{\do\/\do\-\do\_\do\.\do\=\do\&\do\?\do\#\do\:\do\0\do\1\do\2\do\3\do\4\do\5\do\6\do\7\do\8\do\9}
\sloppy

\newlength{\colw}
\newcolumntype{L}{>{\RaggedRight\arraybackslash}p{\colw}}
\renewcommand{\arraystretch}{1.3}
\setlist{topsep=3pt, itemsep=1.5pt, parsep=0pt, leftmargin=1.4em}
\captionsetup{skip=4pt}

% --- titulos ----------------------------------------------------------
\titleformat{\section}
  {\sffamily\LARGE\bfseries\color{navy}}{}{0pt}{}
  [\vspace{2pt}{\color{navy}\titlerule[1.4pt]}]
\titleformat{\subsection}{\sffamily\large\bfseries}{}{0pt}{}
  [\vspace{1pt}{\color{rule2}\titlerule[0.5pt]}]
\titleformat{\subsubsection}{\sffamily\normalsize\bfseries\color{navy}}{}{0pt}{}
\titleformat{\paragraph}[runin]{\sffamily\small\bfseries\color{gray2}}{}{0pt}{}[\quad]
\titlespacing*{\section}{0pt}{0pt}{14pt}
\titlespacing*{\subsection}{0pt}{18pt}{7pt}
\titlespacing*{\subsubsection}{0pt}{13pt}{4pt}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0.4pt}
\fancyhead[L]{\sffamily\footnotesize\color{gray2}Oportunidades de robótica de
  inspección industrial para generación y utilities}
\fancyfoot[C]{\sffamily\footnotesize\thepage}

% --- distintivos ------------------------------------------------------
\newcommand{\badge}[3]{%
  \tcbox[on line, boxsep=1pt, left=2pt, right=2pt, top=0.5pt, bottom=0.5pt,
         colback=#1, colframe=#1, arc=1pt, boxrule=0pt]%
    {\color{#2}\sffamily\scriptsize\bfseries #3}}

% --- llamados ---------------------------------------------------------
\newtcolorbox{notaclavebase}{enhanced, breakable, sharp corners, boxrule=0pt,
  leftrule=2.5pt, colframe=amber, colback=amberbg,
  left=8pt, right=8pt, top=7pt, bottom=7pt, before skip=10pt, after skip=10pt}
\newenvironment{notaclave}[1]
  {\begin{notaclavebase}{\sffamily\scriptsize\bfseries\color{amber}#1}\par\vspace{2pt}}
  {\end{notaclavebase}}
\newtcolorbox{notadatobase}{enhanced, breakable, sharp corners, boxrule=0pt,
  leftrule=2.5pt, colframe=navy, colback=navybg,
  left=8pt, right=8pt, top=7pt, bottom=7pt, before skip=10pt, after skip=10pt}
\newenvironment{notadato}[1]
  {\begin{notadatobase}{\sffamily\scriptsize\bfseries\color{navy}#1}\par\vspace{2pt}}
  {\end{notadatobase}}
\newtcolorbox{notariesgobase}{enhanced, breakable, sharp corners, boxrule=0pt,
  leftrule=2.5pt, colframe=red, colback=redbg,
  left=8pt, right=8pt, top=7pt, bottom=7pt, before skip=10pt, after skip=10pt}
\newenvironment{notariesgo}[1]
  {\begin{notariesgobase}{\sffamily\scriptsize\bfseries\color{red}#1}\par\vspace{2pt}}
  {\end{notariesgobase}}
\newtcolorbox{notainferenciabase}{enhanced, breakable, sharp corners, boxrule=0pt,
  leftrule=2.5pt, colframe=green, colback=greenbg,
  left=8pt, right=8pt, top=7pt, bottom=7pt, before skip=10pt, after skip=10pt}
\newenvironment{notainferencia}[1]
  {\begin{notainferenciabase}{\sffamily\scriptsize\bfseries\color{green}#1}\par\vspace{2pt}}
  {\end{notainferenciabase}}

% --- tarjetas ---------------------------------------------------------
\newtcolorbox{tarjetabase}{enhanced, breakable, colframe=rule2, colback=white,
  boxrule=0.6pt, arc=2pt, left=8pt, right=8pt, top=6pt, bottom=6pt,
  before skip=8pt, after skip=8pt}
\newenvironment{tarjeta}[2]
  {\begin{tarjetabase}%
   {\sffamily\bfseries\color{navy}#1}%
   \ifstrempty{#2}{}{\\[1pt]{\sffamily\scriptsize\color{gray2}#2}}%
   \par\vspace{3pt}}
  {\end{tarjetabase}}

% --- desplegables (siempre visibles en papel) -------------------------
\newtcolorbox{detallebase}[1]{enhanced, breakable, colframe=rule2,
  colback=white, boxrule=0.6pt, arc=2pt, left=8pt, right=8pt, top=6pt,
  bottom=6pt, before skip=10pt, after skip=10pt,
  title={\sffamily\small\bfseries #1}, colbacktitle=navybg, coltitle=navy,
  titlerule=0pt}
\newenvironment{detalle}[1]{\begin{detallebase}{#1}}{\end{detallebase}}

\begin{document}
\pagenumbering{roman}

\begin{titlepage}
\thispagestyle{empty}
\setlength{\parindent}{0pt}\raggedright
\vspace*{3cm}
{\sffamily\footnotesize\bfseries\color{navy}\MakeUppercase{<<EDICION>>}\par}
\vspace{8pt}
{\color{navy}\rule{\linewidth}{2.5pt}}
\vspace{22pt}

{\sffamily\huge\bfseries <<TITULO>>\par}
\vspace{14pt}
{\sffamily\large\color{gray2} <<SUBTITULO>>\par}
\vspace{30pt}
{\color{rule2}\rule{0.35\linewidth}{0.6pt}\par}
\vspace{12pt}
{\normalsize <<FECHA>>\par}
\vfill
{\sffamily\footnotesize\color{gray2}Documento de trabajo para decisión de
inversión. Las hipótesis y las fuentes recopiladas no constituyen conclusiones
de investigación mientras no estén verificadas.\par}
\end{titlepage}
\setcounter{page}{2}

\tableofcontents
\clearpage
\pagenumbering{arabic}

<<BODY>>

\end{document}
"""


# =========================================================================
# 5. Main
# =========================================================================
def read_meta(text):
    meta = {}
    if text.startswith('---'):
        end = text.index('\n---', 3)
        for line in text[3:end].strip().split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip()] = v.strip()
        text = text[end + 4:]
    return meta, text


def cargar_glosario(blocks):
    """Indexa las entradas del glosario para los tooltips del HTML."""
    for kind, a, b in blocks:
        if kind == 'dir':
            if a['kind'] == 'glosario':
                for blk in b:
                    if blk[0] != 'para':
                        continue
                    for r in blk[2]:
                        c = [x.strip() for x in r.split('||')]
                        if len(c) >= 3:
                            limpio = re.sub(r'\{\{[^}]+\}\}', '',
                                            '%s: %s' % (c[1], c[2]))
                            GLOSARIO[c[0]] = limpio.replace('*', '').strip()
            else:
                cargar_glosario(b)


def main():
    src, out_html, out_tex = sys.argv[1], sys.argv[2], sys.argv[3]
    raw = open(src, encoding='utf-8').read()
    meta, body = read_meta(raw)
    blocks, _ = parse(body.split('\n'))
    cargar_glosario(blocks)
    with open(out_html, 'w', encoding='utf-8') as fh:
        fh.write(render_html(meta, blocks))
    with open(out_tex, 'w', encoding='utf-8') as fh:
        fh.write(render_tex(meta, blocks))
    print('bloques de primer nivel: %d' % len(blocks))
    print('figuras insertadas:      %d' % FIGN['n'])
    print('HTML  -> %s' % out_html)
    print('LaTeX -> %s' % out_tex)


if __name__ == '__main__':
    main()
