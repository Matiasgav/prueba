#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convierte el brief markdown a HTML autocontenido y a LaTeX.

Parser dirigido al subconjunto de Markdown realmente usado en el documento:
encabezados, listas (con anidacion y checklists), tablas, blockquotes,
reglas horizontales, negrita/cursiva/codigo, links markdown y URLs sueltas.
"""
import re
import sys
import unicodedata

SRC = sys.argv[1]
OUT_HTML = sys.argv[2]
OUT_TEX = sys.argv[3]

# --------------------------------------------------------------------------
# 1. Parseo de bloques
# --------------------------------------------------------------------------

BULLET = re.compile(r'^(\s*)[-*]\s+(.*)$')
ORDERED = re.compile(r'^(\s*)(\d+)[.)]\s+(.*)$')
HEADING = re.compile(r'^(#{1,6})\s+(.*?)\s*#*$')
TABLE_SEP = re.compile(r'^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?\s*$')
HR = re.compile(r'^\s*(-{3,}|\*{3,}|_{3,})\s*$')


def split_row(line):
    line = line.strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]
    return [c.strip() for c in line.split('|')]


def parse(text):
    lines = text.split('\n')
    blocks = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
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

        # Tabla: fila de encabezado + separador
        if '|' in line and i + 1 < n and TABLE_SEP.match(lines[i + 1]):
            header = split_row(line)
            aligns = []
            for spec in split_row(lines[i + 1]):
                left = spec.startswith(':')
                right = spec.endswith(':')
                aligns.append('center' if left and right else
                              'right' if right else 'left')
            rows = []
            i += 2
            while i < n and '|' in lines[i] and lines[i].strip():
                rows.append(split_row(lines[i]))
                i += 1
            blocks.append(('table', {'header': header, 'aligns': aligns},
                           rows))
            continue

        # Blockquote
        if stripped.startswith('>'):
            buf = []
            while i < n and lines[i].strip().startswith('>'):
                buf.append(re.sub(r'^\s*>\s?', '', lines[i]))
                i += 1
            blocks.append(('quote', None, [b for b in buf if b.strip()]))
            continue

        # Listas
        if BULLET.match(line) or ORDERED.match(line):
            items, i = parse_list(lines, i)
            blocks.append(('list', items[0], items[1]))
            continue

        # Parrafo
        buf = []
        while i < n and lines[i].strip() and not HEADING.match(lines[i]) \
                and not HR.match(lines[i]) and not lines[i].strip().startswith('>') \
                and not BULLET.match(lines[i]) and not ORDERED.match(lines[i]):
            buf.append(lines[i])
            i += 1
        blocks.append(('para', None, buf))
    return blocks


def parse_list(lines, i):
    """Devuelve ((kind, start), items) donde cada item es
    {'text': [lineas], 'children': (kind, start, items) | None}."""
    n = len(lines)
    first = lines[i]
    mb, mo = BULLET.match(first), ORDERED.match(first)
    base_indent = len((mb or mo).group(1))
    kind = 'ul' if mb else 'ol'
    start = int(mo.group(2)) if mo else 1
    items = []
    while i < n:
        line = lines[i]
        if not line.strip():
            # una linea en blanco cierra la lista salvo que siga item al mismo
            # nivel, o un parrafo indentado que continua el item anterior
            j = i + 1
            while j < n and not lines[j].strip():
                j += 1
            if j < n:
                mb2, mo2 = BULLET.match(lines[j]), ORDERED.match(lines[j])
                if (mb2 or mo2) and len((mb2 or mo2).group(1)) == base_indent \
                        and (('ul' if mb2 else 'ol') == kind):
                    i = j
                    continue
                if not (mb2 or mo2) and items and lines[j].startswith(' ' * (base_indent + 1)):
                    para = []
                    while j < n and lines[j].strip() and not BULLET.match(lines[j]) \
                            and not ORDERED.match(lines[j]):
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
            this_kind = 'ul' if mb else 'ol'
            if indent > base_indent:
                child, i = parse_list(lines, i)
                if items:
                    items[-1]['children'] = child
                continue
            if indent < base_indent or this_kind != kind:
                break
            text = mb.group(2) if mb else mo.group(3)
            items.append({'text': [text], 'children': None})
            i += 1
            continue
        # continuacion indentada del item anterior
        if line.startswith(' ') and items:
            items[-1]['text'].append(line.strip())
            i += 1
            continue
        break
    return ((kind, start), items), i


# --------------------------------------------------------------------------
# 2. Inline: HTML
# --------------------------------------------------------------------------

URL_RE = re.compile(r'https?://[^\s<>()\[\]]+[^\s<>()\[\].,;:]')
MDLINK_RE = re.compile(r'\[([^\]\n]+)\]\((https?://[^)\s]+)\)')


def html_escape(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def inline_html(text):
    slots = []

    def stash(html):
        slots.append(html)
        return '\x00%d\x00' % (len(slots) - 1)

    # 1) codigo
    def code_sub(m):
        return stash('<code>%s</code>' % html_escape(m.group(1)))
    text = re.sub(r'`([^`]+)`', code_sub, text)

    # 2) links markdown
    def mdlink_sub(m):
        return stash('<a href="%s">%s</a>'
                     % (html_escape(m.group(2)), html_escape(m.group(1))))
    text = MDLINK_RE.sub(mdlink_sub, text)

    # 3) URLs sueltas
    def url_sub(m):
        u = m.group(0)
        return stash('<a class="url" href="%s">%s</a>'
                     % (html_escape(u), html_escape(u)))
    text = URL_RE.sub(url_sub, text)

    text = html_escape(text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', text)

    def restore(m):
        return slots[int(m.group(1))]
    return re.sub(r'\x00(\d+)\x00', restore, text)


def join_lines_html(lines):
    """Respeta el salto de linea forzado de markdown (dos espacios finales)."""
    out = []
    for k, ln in enumerate(lines):
        piece = inline_html(ln.strip())
        if k < len(lines) - 1:
            piece += '<br>' if ln.rstrip('\n').endswith('  ') else ' '
        out.append(piece)
    return ''.join(out)


SLUGS = {}


def slugify(text):
    t = re.sub(r'<[^>]+>', '', inline_html(text))
    t = t.replace('&amp;', '&')
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode()
    t = re.sub(r'[^a-zA-Z0-9]+', '-', t).strip('-').lower() or 'sec'
    SLUGS[t] = SLUGS.get(t, 0) + 1
    return t if SLUGS[t] == 1 else '%s-%d' % (t, SLUGS[t])


CHECK_RE = re.compile(r'^\[( |x|X)\]\s*')


def render_list_html(spec, items, out):
    (kind, start) = spec
    is_check = all(CHECK_RE.match(it['text'][0]) for it in items) if items else False
    cls = ' class="checklist"' if is_check else ''
    out.append('<%s%s%s>' % (kind, ' start="%d"' % start if kind == 'ol' and start != 1 else '', cls))
    for it in items:
        lines = list(it['text'])
        marker = ''
        if is_check:
            m = CHECK_RE.match(lines[0])
            done = m.group(1).lower() == 'x'
            lines[0] = lines[0][m.end():]
            marker = '<span class="box">%s</span>' % ('&#10003;' if done else '&#9633;')
        out.append('<li>%s%s' % (marker, join_lines_html(lines)))
        if it['children']:
            render_list_html(it['children'][0], it['children'][1], out)
        for para in it.get('paras', []):
            out.append('<p>%s</p>' % join_lines_html(para))
        out.append('</li>')
    out.append('</%s>' % kind)


CALLOUT_HINTS = (
    ('inferencia', 'infer'),
    ('epri', 'data'),
    ('¿en qué tareas', 'key'),
    ('cuál debería ser', 'key'),
)


def render_html(blocks, title, subtitle, meta_lines):
    body = []
    toc = []
    i = 0
    open_section = False
    while i < len(blocks):
        kind, a, b = blocks[i]
        if kind == 'hr':
            # la regla que antecede a un encabezado es decorativa
            if i + 1 < len(blocks) and blocks[i + 1][0] == 'heading':
                i += 1
                continue
            body.append('<hr>')
            i += 1
            continue
        if kind == 'heading':
            level, text = a, b
            slug = slugify(text)
            if level == 1:
                if open_section:
                    body.append('</section>')
                body.append('<section class="sec" id="%s">' % slug)
                open_section = True
                toc.append((1, slug, text))
                body.append('<h2>%s</h2>' % inline_html(text))
            else:
                if level == 2:
                    toc.append((2, slug, text))
                tag = {2: 'h3', 3: 'h4', 4: 'h5', 5: 'h6', 6: 'h6'}[level]
                body.append('<%s id="%s">%s</%s>' % (tag, slug, inline_html(text), tag))
            i += 1
            continue
        if kind == 'para':
            body.append('<p>%s</p>' % join_lines_html(b))
        elif kind == 'quote':
            joined = ' '.join(b).lower()
            cls = 'callout'
            for hint, c in CALLOUT_HINTS:
                if hint in joined:
                    cls = 'callout ' + c
                    break
            body.append('<blockquote class="%s">%s</blockquote>'
                        % (cls, join_lines_html(b)))
        elif kind == 'list':
            render_list_html(a, b, body)
        elif kind == 'table':
            header, aligns, rows = a['header'], a['aligns'], b
            t = ['<div class="tw"><table>', '<thead><tr>']
            for k, h in enumerate(header):
                al = aligns[k] if k < len(aligns) else 'left'
                t.append('<th class="%s">%s</th>' % (al, inline_html(h)))
            t.append('</tr></thead>')
            if rows:
                t.append('<tbody>')
                for r in rows:
                    t.append('<tr>')
                    for k, c in enumerate(r):
                        al = aligns[k] if k < len(aligns) else 'left'
                        t.append('<td class="%s">%s</td>' % (al, inline_html(c)))
                    t.append('</tr>')
                t.append('</tbody>')
            else:
                t.append('<tbody><tr><td class="empty" colspan="%d">'
                         'Tabla a completar durante la investigación</td></tr></tbody>'
                         % len(header))
            t.append('</table></div>')
            body.append(''.join(t))
        i += 1
    if open_section:
        body.append('</section>')

    toc_html = ['<nav id="toc"><div class="toc-title">Contenido</div><ul>']
    for level, slug, text in toc:
        toc_html.append('<li class="l%d"><a href="#%s">%s</a></li>'
                        % (level, slug, inline_html(text)))
    toc_html.append('</ul></nav>')

    meta_html = ''.join('<div class="meta-line">%s</div>' % inline_html(m)
                        for m in meta_lines)

    page = HTML_TEMPLATE.format(
        title=html_escape(re.sub(r'<[^>]+>', '', inline_html(title))),
        title_html=inline_html(title),
        subtitle=inline_html(subtitle),
        meta=meta_html,
        toc=''.join(toc_html),
        body='\n'.join(body),
    )
    return page.replace('<<SCRIPT>>', SCROLLSPY)


SCROLLSPY = """<script>
// Resalta en el indice la seccion visible.
(function () {
  var links = {};
  document.querySelectorAll('#toc a').forEach(function (a) {
    links[a.getAttribute('href').slice(1)] = a;
  });
  var targets = Object.keys(links)
    .map(function (id) { return document.getElementById(id); })
    .filter(Boolean);
  if (!('IntersectionObserver' in window) || !targets.length) return;
  var visible = new Set();
  var obs = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) visible.add(e.target.id);
      else visible.delete(e.target.id);
    });
    var current = targets.filter(function (t) { return visible.has(t.id); })[0];
    if (!current) return;
    document.querySelectorAll('#toc a.active').forEach(function (a) {
      a.classList.remove('active');
    });
    var a = links[current.id];
    if (a) a.classList.add('active');
  }, { rootMargin: '0px 0px -75% 0px' });
  targets.forEach(function (t) { obs.observe(t); });
})();
</script>"""


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root {{
    --bg: #ffffff;
    --paper: #ffffff;
    --ink: #1a1f26;
    --ink-soft: #4a5568;
    --ink-faint: #6b7684;
    --rule: #e2e6ec;
    --rule-strong: #c9d0d9;
    --accent: #14496b;
    --accent-soft: #eef3f8;
    --code-bg: #f4f6f8;
    --sidebar: #f7f9fb;
    --maxw: 46rem;
  }}
  * {{ box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, system-ui, sans-serif;
    font-size: 16px;
    line-height: 1.62;
    -webkit-font-smoothing: antialiased;
  }}
  .layout {{ display: flex; align-items: flex-start; }}

  /* ---------- TOC lateral ---------- */
  #toc {{
    position: sticky;
    top: 0;
    flex: 0 0 19rem;
    max-height: 100vh;
    overflow-y: auto;
    padding: 2rem 1.1rem 3rem 1.6rem;
    background: var(--sidebar);
    border-right: 1px solid var(--rule);
    font-size: .84rem;
  }}
  .toc-title {{
    font-size: .7rem; letter-spacing: .12em; text-transform: uppercase;
    color: var(--ink-faint); font-weight: 700; margin-bottom: .9rem;
  }}
  #toc ul {{ list-style: none; margin: 0; padding: 0; }}
  #toc li {{ margin: 0; }}
  #toc a {{
    display: block; padding: .2rem .4rem; color: var(--ink-soft);
    text-decoration: none; border-left: 2px solid transparent;
    border-radius: 0 3px 3px 0;
  }}
  #toc a:hover {{ background: #fff; color: var(--accent); border-left-color: var(--accent); }}
  #toc a.active {{
    background: #fff; color: var(--accent); font-weight: 600;
    border-left-color: var(--accent);
  }}
  #toc .l1 > a {{ font-weight: 600; color: var(--ink); margin-top: .35rem; }}
  #toc .l2 > a {{ padding-left: 1.1rem; font-size: .8rem; }}

  /* ---------- Contenido ---------- */
  main {{ flex: 1 1 auto; min-width: 0; padding: 0 2.2rem 6rem; }}
  .wrap {{ max-width: var(--maxw); margin: 0 auto; }}

  header.cover {{
    padding: 4.5rem 0 2.2rem;
    border-bottom: 3px solid var(--accent);
    margin-bottom: 2.5rem;
  }}
  .eyebrow {{
    font-size: .72rem; letter-spacing: .16em; text-transform: uppercase;
    color: var(--accent); font-weight: 700; margin-bottom: 1rem;
  }}
  header.cover h1 {{
    font-size: 2.1rem; line-height: 1.2; margin: 0 0 .6rem;
    letter-spacing: -.01em; font-weight: 700;
  }}
  .subtitle {{ font-size: 1.12rem; color: var(--ink-soft); margin: 0 0 1.6rem; }}
  .meta-line {{ font-size: .9rem; color: var(--ink-soft); padding: .18rem 0; }}
  .meta-line strong {{ color: var(--ink); }}

  section.sec {{ padding-top: .2rem; }}
  section.sec > h2:first-child {{ margin-top: 1.6rem; }}
  h2 {{
    font-size: 1.5rem; margin: 2.6rem 0 1rem; padding-bottom: .45rem;
    border-bottom: 1px solid var(--rule-strong); letter-spacing: -.01em;
  }}
  h3 {{ font-size: 1.16rem; margin: 2rem 0 .7rem; color: var(--accent); }}
  h4 {{ font-size: 1rem; margin: 1.5rem 0 .5rem; }}
  h5, h6 {{
    font-size: .82rem; margin: 1.2rem 0 .45rem; text-transform: uppercase;
    letter-spacing: .07em; color: var(--ink-faint);
  }}
  p {{ margin: 0 0 .9rem; }}
  ul, ol {{ margin: 0 0 1rem; padding-left: 1.35rem; }}
  li {{ margin: .22rem 0; }}
  li > ul, li > ol {{ margin: .25rem 0 .4rem; }}
  ul.checklist {{ list-style: none; padding-left: .1rem; }}
  ul.checklist .box {{
    display: inline-block; width: 1.2rem; color: var(--accent); font-weight: 700;
  }}
  a {{ color: var(--accent); }}
  a.url {{ word-break: break-all; font-size: .88em; font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace; }}
  code {{
    background: var(--code-bg); border: 1px solid var(--rule);
    border-radius: 3px; padding: .06em .34em; font-size: .87em;
    font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  }}
  hr {{ border: 0; border-top: 1px solid var(--rule); margin: 2rem 0; }}

  blockquote.callout {{
    margin: 1.1rem 0; padding: .85rem 1.1rem;
    background: var(--accent-soft); border-left: 3px solid var(--accent);
    border-radius: 0 4px 4px 0; color: var(--ink);
  }}
  blockquote.callout.key {{ background: #fff8e8; border-left-color: #b7791f; font-weight: 500; }}
  blockquote.callout.infer {{ background: #f2f7f2; border-left-color: #38734a; }}
  blockquote.callout.data {{ background: #f4f6fb; border-left-color: #3c5b9a; }}

  .tw {{ overflow-x: auto; margin: 1.1rem 0 1.4rem; border: 1px solid var(--rule); border-radius: 5px; }}
  table {{ border-collapse: collapse; width: 100%; font-size: .87rem; }}
  th, td {{ padding: .5rem .7rem; border-bottom: 1px solid var(--rule); vertical-align: top; }}
  thead th {{
    position: sticky; top: 0; background: var(--accent); color: #fff;
    font-weight: 600; text-align: left; white-space: nowrap;
  }}
  td.right, th.right {{ text-align: right; }}
  td.center, th.center {{ text-align: center; }}
  tbody tr:nth-child(even) {{ background: #fafbfc; }}
  td.empty {{ color: var(--ink-faint); font-style: italic; text-align: center; }}

  footer.docfoot {{
    margin-top: 3.5rem; padding-top: 1.2rem; border-top: 1px solid var(--rule);
    font-size: .82rem; color: var(--ink-faint);
  }}

  @media (max-width: 900px) {{
    .layout {{ display: block; }}
    #toc {{ position: static; max-height: none; width: auto; flex: none;
           border-right: 0; border-bottom: 1px solid var(--rule); }}
    main {{ padding: 0 1.2rem 4rem; }}
    header.cover {{ padding-top: 2.5rem; }}
  }}
  @media print {{
    #toc {{ display: none; }}
    main {{ padding: 0; }}
    body {{ font-size: 10.5pt; }}
    section.sec {{ break-inside: auto; }}
    h2, h3, h4 {{ break-after: avoid; }}
    table, blockquote, .tw {{ break-inside: avoid; }}
    thead th {{ position: static; }}
    a {{ color: inherit; text-decoration: none; }}
  }}
</style>
</head>
<body>
<div class="layout">
{toc}
<main>
  <div class="wrap">
    <header class="cover">
      <div class="eyebrow">Brief de investigación</div>
      <h1>{title_html}</h1>
      <p class="subtitle">{subtitle}</p>
      {meta}
    </header>
{body}
    <footer class="docfoot">
      Documento de trabajo — brief metodológico. Las hipótesis y fuentes seed
      aquí listadas no constituyen conclusiones de investigación.
    </footer>
  </div>
</main>
</div>
<<SCRIPT>>
</body>
</html>
"""


# --------------------------------------------------------------------------
# 3. Inline: LaTeX
# --------------------------------------------------------------------------

TEX_CHARS = {
    '\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
    '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}',
    '~': r'\textasciitilde{}', '^': r'\textasciicircum{}',
    '<': r'\textless{}', '>': r'\textgreater{}',
    '×': r'$\times$', '→': r'$\rightarrow$', '±': r'$\pm$',
    '“': r'``', '”': r"''", '"': r"''",
}


def tex_escape(s):
    return ''.join(TEX_CHARS.get(ch, ch) for ch in s)


def inline_tex(text):
    slots = []

    def stash(tex):
        slots.append(tex)
        return '\x00%d\x00' % (len(slots) - 1)

    text = re.sub(r'`([^`]+)`',
                  lambda m: stash(r'\texttt{%s}' % tex_escape(m.group(1))), text)
    text = MDLINK_RE.sub(
        lambda m: stash(r'\href{%s}{%s}' % (m.group(2).replace('%', r'\%'),
                                            tex_escape(m.group(1)))), text)
    text = URL_RE.sub(lambda m: stash(r'\url{%s}' % m.group(0)), text)

    text = tex_escape(text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\\textbf{\1}', text)
    text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'\\emph{\1}', text)

    return re.sub(r'\x00(\d+)\x00', lambda m: slots[int(m.group(1))], text)


def join_lines_tex(lines):
    out = []
    for k, ln in enumerate(lines):
        piece = inline_tex(ln.strip())
        if k < len(lines) - 1:
            piece += r' \\' + '\n' if ln.rstrip('\n').endswith('  ') else '\n'
        out.append(piece)
    return ''.join(out)


def render_list_tex(spec, items, out, depth=0):
    kind, start = spec
    is_check = all(CHECK_RE.match(it['text'][0]) for it in items) if items else False
    if is_check:
        out.append(r'\begin{itemize}[label=$\square$,leftmargin=1.6em]')
        env = 'itemize'
    elif kind == 'ol':
        opt = '[start=%d]' % start if start != 1 else ''
        out.append(r'\begin{enumerate}%s' % opt)
        env = 'enumerate'
    else:
        out.append(r'\begin{itemize}')
        env = 'itemize'
    for it in items:
        lines = list(it['text'])
        if is_check:
            lines[0] = lines[0][CHECK_RE.match(lines[0]).end():]
        content = join_lines_tex(lines)
        if content.startswith('['):
            content = '{}' + content
        out.append(r'\item ' + content)
        if it['children']:
            render_list_tex(it['children'][0], it['children'][1], out, depth + 1)
        for para in it.get('paras', []):
            out.append('')
            out.append(join_lines_tex(para))
    out.append(r'\end{%s}' % env)


TEX_SEC = {1: 'section', 2: 'subsection', 3: 'subsubsection', 4: 'paragraph',
           5: 'subparagraph', 6: 'subparagraph'}


def render_tex(blocks, title, subtitle, meta_lines):
    out = []
    i = 0
    while i < len(blocks):
        kind, a, b = blocks[i]
        if kind == 'hr':
            if not (i + 1 < len(blocks) and blocks[i + 1][0] == 'heading'):
                out.append(r'\medskip\noindent\rule{\linewidth}{0.4pt}\medskip')
            i += 1
            continue
        if kind == 'heading':
            level, text = a, b
            name = TEX_SEC[level]
            t = inline_tex(text)
            plain = re.sub(r'\\(textbf|emph|texttt)\{([^{}]*)\}', r'\2', t)
            out.append('\n' + r'\%s*{%s}' % (name, t))
            if level <= 3:
                out.append(r'\addcontentsline{toc}{%s}{%s}' % (name, plain))
            i += 1
            continue
        if kind == 'para':
            out.append(join_lines_tex(b))
        elif kind == 'quote':
            out.append(r'\begin{callout}' + '\n' + join_lines_tex(b)
                       + '\n' + r'\end{callout}')
        elif kind == 'list':
            render_list_tex(a, b, out)
        elif kind == 'table':
            out.append(tex_table(a['header'], a['aligns'], b))
        out.append('')
        i += 1

    meta = '\\\\[2pt]\n'.join(inline_tex(m.strip()) for m in meta_lines)
    return TEX_TEMPLATE.replace('<<TITLE>>', inline_tex(title)) \
                       .replace('<<SUBTITLE>>', inline_tex(subtitle)) \
                       .replace('<<META>>', meta) \
                       .replace('<<BODY>>', '\n'.join(out))


def tex_table(header, aligns, rows):
    ncol = len(header)
    colspec = ' '.join(['L'] * ncol)
    wide = ncol >= 8
    lines = ([r'\begin{landscape}'] if wide else []) + \
            [r'\begingroup' + (r'\footnotesize' if wide else r'\footnotesize'),
             r'\setlength{\tabcolsep}{%dpt}' % (2 if wide else 4),
             r'\setlength{\emergencystretch}{3em}',
             r'\hyphenpenalty=50 \exhyphenpenalty=50',
             r'\setlength{\colw}{\dimexpr(\linewidth-%d\tabcolsep)/%d\relax}'
             % (2 * ncol, ncol),
             r'\begin{longtable}{@{}%s@{}}' % colspec,
             r'\toprule']
    head = ' & '.join(r'\textbf{%s}' % inline_tex(h).replace('/', r'\slash ')
                      for h in header) + r' \\'
    lines += [head, r'\midrule', r'\endfirsthead',
              r'\toprule', head, r'\midrule', r'\endhead',
              r'\bottomrule', r'\endfoot']
    if rows:
        for r in rows:
            cells = [inline_tex(c) for c in r] + [''] * (ncol - len(r))
            lines.append(' & '.join(cells[:ncol]) + r' \\')
    else:
        lines.append(r'\multicolumn{%d}{@{}l@{}}{\itshape Tabla a completar '
                     r'durante la investigación.} \\' % ncol)
    lines += [r'\end{longtable}', r'\endgroup']
    if wide:
        lines.append(r'\end{landscape}')
    return '\n'.join(lines)


TEX_TEMPLATE = r"""% !TeX program = pdflatex
%=======================================================================
%  Brief de investigacion - robots de inspeccion industrial
%  Compilar:  pdflatex archivo.tex   (dos veces, para el indice)
%=======================================================================
\documentclass[11pt,a4paper]{article}

\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[spanish,es-noshorthands,es-tabla]{babel}
\usepackage{lmodern}
\usepackage[a4paper,top=2.6cm,bottom=2.6cm,left=3cm,right=2.6cm]{geometry}

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
\usepackage{microtype}
\usepackage{parskip}
\usepackage[hidelinks,breaklinks=true]{hyperref}
\usepackage{url}

% --- colores ----------------------------------------------------------
\definecolor{accent}{HTML}{14496B}
\definecolor{rulegray}{HTML}{C9D0D9}
\definecolor{calloutbg}{HTML}{EEF3F8}
\definecolor{inksoft}{HTML}{4A5568}

\hypersetup{colorlinks=true, linkcolor=accent, urlcolor=accent,
            citecolor=accent, pdftitle={<<TITLE>>}}

% --- URLs largas ------------------------------------------------------
\renewcommand{\UrlFont}{\small\ttfamily}
\Urlmuskip=0mu plus 1mu
\def\UrlBreaks{\do\/\do\-\do\_\do\.\do\=\do\&\do\?\do\#}
\sloppy

% --- tablas: columnas justificadas, ancho calculado por tabla ----------
\newlength{\colw}
\newcolumntype{L}{>{\RaggedRight\arraybackslash}p{\colw}}
\setlength{\LTcapwidth}{\linewidth}
\renewcommand{\arraystretch}{1.25}

% --- listas -----------------------------------------------------------
\setlist{topsep=3pt, itemsep=1.5pt, parsep=0pt, leftmargin=1.4em}

% --- titulos ----------------------------------------------------------
\titleformat{\section}
  {\sffamily\Large\bfseries\color{accent}}{}{0pt}{}
  [\vspace{2pt}{\color{rulegray}\titlerule[0.8pt]}]
\titleformat{\subsection}{\sffamily\large\bfseries}{}{0pt}{}
\titleformat{\subsubsection}{\sffamily\normalsize\bfseries\color{inksoft}}{}{0pt}{}
\titleformat{\paragraph}[runin]{\sffamily\bfseries\small}{}{0pt}{}[.\quad]
\titlespacing*{\section}{0pt}{22pt}{9pt}
\titlespacing*{\subsection}{0pt}{16pt}{6pt}
\titlespacing*{\subsubsection}{0pt}{12pt}{4pt}

% --- encabezado / pie -------------------------------------------------
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0.4pt}
\fancyhead[L]{\sffamily\footnotesize\color{inksoft}Brief de investigación --- Robots de inspección industrial}
\fancyfoot[C]{\sffamily\footnotesize\thepage}

% --- callout ----------------------------------------------------------
\newenvironment{callout}
  {\par\medskip\noindent
   \begin{lrbox}{\calloutbox}%
   \begin{minipage}{\dimexpr\linewidth-2.2em\relax}\itshape}
  {\end{minipage}\end{lrbox}%
   \noindent{\color{accent}\vrule width 2.5pt}\hspace{0.6em}%
   \colorbox{calloutbg}{\usebox{\calloutbox}}\par\medskip}
\newsavebox{\calloutbox}

\begin{document}
\pagenumbering{roman}

%=======================================================================
% Portada
%=======================================================================
\begin{titlepage}
\thispagestyle{empty}
\setlength{\parindent}{0pt}
\raggedright
\vspace*{3.2cm}
{\sffamily\footnotesize\bfseries\color{accent}%
 \MakeUppercase{Brief de investigación}\par}
\vspace{8pt}
{\color{accent}\rule{\linewidth}{2.5pt}}
\vspace{20pt}

{\sffamily\huge\bfseries <<TITLE>>\par}
\vspace{12pt}
{\sffamily\large\color{inksoft} <<SUBTITLE>>\par}
\vspace{30pt}
{\color{rulegray}\rule{0.35\linewidth}{0.6pt}\par}
\vspace{14pt}
{\normalsize <<META>>\par}
\vfill
{\sffamily\footnotesize\color{inksoft}Documento de trabajo --- brief metodológico.
Las hipótesis y fuentes seed aquí listadas no constituyen conclusiones de
investigación.\par}
\end{titlepage}
\setcounter{page}{2}

\tableofcontents
\clearpage
\pagenumbering{arabic}

%=======================================================================
% Cuerpo
%=======================================================================
<<BODY>>

\end{document}
"""


# --------------------------------------------------------------------------
# 4. Main
# --------------------------------------------------------------------------

def main():
    raw = open(SRC, encoding='utf-8').read()
    lines = raw.split('\n')

    # Encabezado del documento: H1 titulo, H2 subtitulo, luego metadatos
    title = re.sub(r'^#\s+', '', lines[0]).strip()
    subtitle = re.sub(r'^##\s+', '', lines[1]).strip()
    meta_lines = []
    idx = 2
    while idx < len(lines) and lines[idx].strip() and not lines[idx].startswith('#'):
        meta_lines.append(lines[idx])
        idx += 1

    blocks = parse('\n'.join(lines[idx:]))
    open(OUT_HTML, 'w', encoding='utf-8').write(
        render_html(blocks, title, subtitle, meta_lines))
    open(OUT_TEX, 'w', encoding='utf-8').write(
        render_tex(blocks, title, subtitle, meta_lines))
    print('bloques: %d' % len(blocks))
    print('HTML  -> %s' % OUT_HTML)
    print('LaTeX -> %s' % OUT_TEX)


main()
