/* Prueba local del HTML: no opera sesiones personales del navegador. */
const {chromium} = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const assert = require('node:assert/strict');

(async () => {
  const root = path.resolve(__dirname, '..');
  const out = path.resolve(process.argv[2] || path.join(root, 'audit', 'guia_teoria'));
  fs.mkdirSync(out, {recursive:true});
  const browser = await chromium.launch({headless:true,channel:'chrome'});
  const context = await browser.newContext({viewport:{width:1440,height:1000}, reducedMotion:'reduce'});
  const page = await context.newPage();
  const errors = [], external = [], checks = [];
  page.on('pageerror', e => errors.push(String(e)));
  await context.route(/^https?:/, route => {external.push(route.request().url()); return route.abort();});
  const record = (name) => checks.push(name);
  try {
    await page.goto(pathToFileURL(path.join(root,'docs','guia_visual_estimacion.html')).href);
    await page.locator('#method-buttons button').last().waitFor();
    const ids = await page.locator('nav a').evaluateAll(items => items.map(a=>a.hash.slice(1)));
    for (const id of ids) assert.equal(await page.locator('[id="'+id+'"]').count(),1,id);
    record('Once secciones con anclas únicas');
    const images = await page.locator('header img').evaluateAll(items=>items.map(i=>i.complete&&i.naturalWidth>0));
    assert.equal(images.length,2); assert.ok(images.every(Boolean)); record('L1 y L3 cargan desde archivos locales');
    assert.equal(await page.locator('#mission-decision').getAttribute('open'),null);
    assert.equal(await page.locator('#mission-decision p').first().isVisible(),false);
    record('Decisión de misión oculta inicialmente');
    await page.screenshot({path:path.join(out,'01_portada.png')});
    for (const [size,count] of [['2',5],['5',3],['10',2]]) {
      await page.selectOption('#support',size);
      assert.equal(await page.locator('#comp-bars .bar').count(),count);
    }
    assert.match(await page.locator('#comp-bars').getAttribute('aria-label'),/0 a 6 metros|0 a 6 m/);
    const lengths=await page.locator('#length-strip span').evaluateAll(items=>items.map(i=>parseFloat(i.style.flex)));
    assert.deepEqual(lengths,[6,4]); record('Soportes 2/5/10 m conservan contacto y residuos; longitudes proporcionales');
    await page.locator('#compositacion').screenshot({path:path.join(out,'02_compositacion.png')});
    assert.equal(await page.locator('#block-diagram circle').count(),5);
    await page.selectOption('#block-size','25');
    assert.equal(await page.locator('#block-grid').getAttribute('width'),'30');
    assert.equal(await page.locator('#block-diagram circle').count(),5);
    record('Subdivisión cambia la malla y conserva observaciones');
    await page.locator('#bloques').screenshot({path:path.join(out,'03_bloques.png')});
    for (let i=0;i<8;i++) {
      await page.locator('#method-buttons button').nth(i).click();
      assert.equal(await page.locator('#method-buttons [aria-pressed="true"]').count(),1);
      for (const id of ['method-explain','method-needs','method-assumptions','method-use','method-appearance','method-limit','method-question'])
        assert.ok((await page.locator('#'+id).textContent()).trim(),id);
    }
    record('Ocho fichas con lógica, requisitos, supuestos, utilidad, apariencia y límites');
    await page.locator('#method-detail').screenshot({path:path.join(out,'04_metodos.png')});
    await page.locator('#mission-decision summary').click();
    assert.equal(await page.locator('#mission-decision p').first().isVisible(),true);
    record('Revelación manual de IDW²');
    assert.equal(await page.locator('#quiz h3').count(),1);
    assert.equal(await page.locator('#quiz .quiz-nav button').isDisabled(),true);
    await page.locator('#quiz .choices button').nth(1).click();
    assert.match(await page.locator('#quiz .feedback').textContent(),/coherente/);
    assert.doesNotMatch(await page.locator('#quiz .feedback').textContent(),/Bien razonado/);
    await page.locator('#quiz .quiz-nav button').click();
    assert.match(await page.locator('#quiz .quiz-nav span').textContent(),/2 de 4/);
    assert.equal(await page.locator('#quiz h3').count(),1);
    record('Una situación visible y respuesta sin acreditar razonamiento por un clic');
    await page.locator('#escenarios').screenshot({path:path.join(out,'05_escenarios.png')});
    await page.setViewportSize({width:390,height:844});
    await page.evaluate(()=>scrollTo(0,0));
    const dimensions=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));
    assert.ok(dimensions.scroll<=dimensions.width,'Desborde horizontal móvil: '+JSON.stringify(dimensions));
    await page.screenshot({path:path.join(out,'06_movil.png')});
    record('Pantalla de 390 px sin desborde horizontal');
    assert.equal(errors.length,0,errors.join('\n'));
    assert.equal(external.length,0,external.join('\n'));
    record('Sin errores JavaScript ni solicitudes de red');
    fs.writeFileSync(path.join(out,'resultado_guia.json'),JSON.stringify({ok:true,checks,errors,external},null,2));
    console.log(JSON.stringify({ok:true,controles:checks.length,screenshots:6,output:out}));
  } catch(error) {
    fs.writeFileSync(path.join(out,'resultado_guia.json'),JSON.stringify({ok:false,checks,errors,external,error:String(error)},null,2));
    throw error;
  } finally {
    await browser.close();
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
