// Verifica el RENDER de docs/modelo-cunas.html: errores de consola, que los
// trece graficos dibujen, NaN en atributos, texto que se salga de su SVG,
// scroll horizontal y los dos temas. Corre con:
//     NODE_PATH=/opt/node22/lib/node_modules node docs/verificar_modelo.js
// El companero es docs/verificar_numeros.py, que comprueba el CONTENIDO.

const {chromium} = require('playwright');
const path = require('path');
const FILE = 'file://' + path.resolve(__dirname, 'modelo-cunas.html');

(async () => {
  const browser = await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
  let fail = 0;
  const say = (ok, msg) => { if(!ok) fail++; console.log((ok?'  ok  ':'FALLA ') + msg); };

  for (const [w, scheme, label] of [[1100,'light','ancho claro'],[900,'dark','900 oscuro'],[390,'light','teléfono']]) {
    const ctx = await browser.newContext({viewport:{width:w,height:1000}, colorScheme:scheme});
    const page = await ctx.newPage();
    const errs = [];
    const CDN = /ERR_CERT_AUTHORITY_INVALID|fonts\.googleapis|fonts\.gstatic|ERR_NAME_NOT_RESOLVED|ERR_PROXY/;
    page.on('console', m => { if (m.type()==='error' && !CDN.test(m.text())) errs.push(m.text()); });
    page.on('pageerror', e => errs.push('pageerror: ' + e.message));
    await page.goto(FILE);
    await page.waitForTimeout(1500);
    console.log('\n--- ' + label + ' (' + w + 'px, ' + scheme + ') ---');
    say(errs.length===0, 'sin errores de consola' + (errs.length?': '+errs.slice(0,3).join(' | '):''));

    const r = await page.evaluate(() => {
      const svgs = [...document.querySelectorAll('svg.plot')];
      const drawn = svgs.map(s => ({id:s.id, n:s.childElementCount}));
      // NaN / Infinity en cualquier atributo geometrico de cualquier svg
      const bad = [];
      document.querySelectorAll('svg *').forEach(el => {
        for (const a of el.attributes) {
          if (/NaN|Infinity|undefined|null/.test(a.value)) bad.push(el.tagName+'@'+a.name+'='+a.value.slice(0,40));
        }
      });
      // texto fuera de la caja de su svg
      const out = [];
      document.querySelectorAll('svg').forEach(s => {
        const vb = s.viewBox.baseVal; if (!vb || !vb.width) return;
        s.querySelectorAll('text').forEach(t => {
          let b; try { b = t.getBBox(); } catch(e) { return; }
          if (b.x < -2 || b.y < -2 || b.x + b.width > vb.width + 2 || b.y + b.height > vb.height + 2)
            out.push(s.id + ': "' + t.textContent.slice(0,32) + '"');
        });
      });
      // colores sin resolver
      // var() en atributo de presentacion resuelve; lo que importa es el color CALCULADO
      const unresolved = [];
      document.querySelectorAll('svg [fill^="var"],svg [stroke^="var"]').forEach(el=>{
        const cs = getComputedStyle(el);
        for (const a of ['fill','stroke']) {
          const v = cs[a];
          if (/var\(|^$|invalid/.test(v)) unresolved.push(el.tagName+' '+a+' -> '+v);
        }
      });
      const cs = getComputedStyle(document.body);
      return {
        drawn,
        figuras: document.querySelectorAll('figure').length,
        secciones: document.querySelectorAll('section').length,
        bloques: document.querySelectorAll('section .bid').length,
        objeto: document.body.innerHTML.includes('[object Object]'),
        undef: /\bundefined\b/.test(document.body.innerText),
        bad, out, unresolved: unresolved.slice(0,5),
        scrollX: document.documentElement.scrollWidth > window.innerWidth + 1,
        bg: cs.backgroundColor, fg: cs.color,
        tablas: document.querySelectorAll('table').length,
        // etiquetas que dibuja el JS: no estan en el fuente, solo en el DOM
        faltan: ['×579 a 5 mJ','1545 g las dos','rechazo 1/472','ζ = 0,02','1273 Hz · ×150 · 78 g',
                 'dK/dx = 0','2 GDL','1 GDL','contacto perdido','×112','pico 44.46 g']
                .filter(t => ![...document.querySelectorAll('svg text')]
                               .some(e => e.textContent.includes(t))),
        anclas: [...document.querySelectorAll('.bar a')].map(a=>a.getAttribute('href'))
                 .filter(h=>h.startsWith('#') && !document.getElementById(h.slice(1))),
      };
    });

    const vacias = r.drawn.filter(d => d.n < 5);
    say(vacias.length===0, 'los ' + r.drawn.length + ' gráficos dibujaron' + (vacias.length?': vacíos '+vacias.map(v=>v.id):''));
    say(r.figuras===13, '13 figuras numeradas (hay ' + r.figuras + ')');
    say(r.bloques===6, '6 bloques (hay ' + r.bloques + ')');
    say(r.bad.length===0, 'sin NaN/undefined en atributos SVG' + (r.bad.length?': '+r.bad.slice(0,3).join(', '):''));
    say(r.out.length===0, 'ningún texto sale de su SVG' + (r.out.length?': '+r.out.slice(0,4).join(' · '):''));
    say(r.unresolved.length===0, 'los colores var() resuelven a un color real' + (r.unresolved.length?': '+r.unresolved.join(', '):''));
    say(!r.objeto, 'sin [object Object]');
    say(!r.undef, 'sin "undefined" en el texto');
    say(!r.scrollX, 'sin scroll horizontal');
    say(r.faltan.length===0, 'las etiquetas clave se dibujaron' + (r.faltan.length?': faltan '+r.faltan.join(' · '):''));
    say(r.anclas.length===0, 'todos los enlaces de la barra apuntan a algo' + (r.anclas.length?': '+r.anclas:''));
    say(r.bg!=='rgba(0, 0, 0, 0)', 'el body pinta su fondo (' + r.bg + ' sobre texto ' + r.fg + ')');
    console.log('       tablas: ' + r.tablas + ' · secciones: ' + r.secciones);
    await page.screenshot({path:require('os').tmpdir()+'/ver_'+w+'_'+scheme+'.png', fullPage:false});
    await ctx.close();
  }
  await browser.close();
  console.log('\n' + (fail ? 'FALLAS: ' + fail : 'TODO OK'));
  process.exit(fail ? 1 : 0);
})();
