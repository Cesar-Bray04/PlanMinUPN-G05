/* Prueba de contrato JS/HTML con DOM y Plotly simulados; no es inspección visual. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),pointer=JSON.parse(fs.readFileSync(path.join(root,'outputs/g05_products.json')));
class Element{
 constructor(tag='div'){this.tag=tag;this.children=[];this.events={};this.textContent='';this.value='';this.checked=false;this.hidden=false;this.className='';}
 append(...items){this.children.push(...items);if(this.tag==='select' && !this.value && items.length)this.value=items[0].value||'';}
 replaceChildren(...items){this.children=items;this.textContent='';}
 addEventListener(name,fn){this.events[name]=fn;}
 removeAllListeners(){}
 on(name,fn){this.events[name]=fn;}
}
(async()=>{
 const checks=[];
 for(const stage of ['S11','S12']){
  const folder=path.dirname(path.join(root,pointer[stage].manifest));
  const html=fs.readFileSync(path.join(folder,stage.toLowerCase()+'_model_3d.html'),'utf8');
  const match=html.match(/window\.G05_MODEL=(.*?);<\/script>/s);assert.ok(match);
  const data=JSON.parse(match[1].replaceAll('<\\/','</'));assert.equal(data.blocks.length,11550);
  assert.equal(new Set(data.blocks.map(b=>b.block_id)).size,11550);
  const elements={};
  for(const id of ['plot-error','metrics','run-id','block-id','block-detail','inspect','plot','drawing-count','legend','scenario-table','scenario-section'])elements[id]=new Element();
  for(const id of ['color-mode','class-filter'])elements[id]=new Element('select');
  elements['class-filter'].value='ALL';elements['show-missing']=new Element('input');elements['show-missing'].checked=true;
  elements['show-holes']=new Element('input');elements['show-holes'].checked=true;
  let latest=[];
  const ctx={window:{G05_MODEL:data,Plotly:null},document:{getElementById:id=>elements[id],createElement:tag=>new Element(tag)},Intl,console,
    Plotly:{react:async(id,traces)=>{latest=traces;for(const t of traces){assert.ok(t.x.length===t.y.length&&t.y.length===t.z.length);assert.ok([...t.x,...t.y,...t.z].every(Number.isFinite));}return true;}}};
  ctx.window.Plotly=ctx.Plotly;vm.createContext(ctx);vm.runInContext(fs.readFileSync(path.join(root,'assets/quantitative.js'),'utf8'),ctx);await new Promise(resolve=>setImmediate(resolve));
  assert.equal(ctx.window.G05_VIEW_READY,true);assert.ok(latest.some(t=>t.type==='mesh3d'));assert.ok(elements['drawing-count'].textContent.includes('11,550'));
  const inspect=data.blocks.find(b=>b.cu_pct_est!==null);elements['block-id'].value=inspect.block_id;elements.inspect.events.click();
  assert.ok(elements['block-detail'].children.length>0);assert.ok(elements['block-detail'].children[0].children.some(row=>row.children[0].textContent==='cu_pct_est'));
  for(const mode of ['cu_pct_est','density_t_m3_est','tonnage_t','rock_fraction','cu_pct_est_r50',...(stage==='S12'?['candidate_class','scenario_A_allocated_t','scenario_B_opex_usd']:[])]){
    elements['color-mode'].value=mode;elements['color-mode'].events.change();await new Promise(resolve=>setImmediate(resolve));assert.ok(latest.length>0);
  }
  elements['show-missing'].checked=false;elements['show-missing'].events.change();await new Promise(resolve=>setImmediate(resolve));
  const ids=latest.filter(t=>t.type==='mesh3d').flatMap(t=>t.customdata);
  assert.ok(ids.every(id=>data.blocks.find(b=>b.block_id===id).cu_pct_est!==null));
  if(stage==='S12'){
   assert.equal(data.scenarios.length,2);assert.equal(data.scenarios[0].trucks_for_target,6);assert.equal(data.scenarios[1].trucks_for_target,8);
   elements['class-filter'].value='ORE_CANDIDATE';elements['class-filter'].events.change();await new Promise(resolve=>setImmediate(resolve));
   assert.ok(latest.filter(t=>t.type==='mesh3d').flatMap(t=>t.customdata).every(id=>data.blocks.find(b=>b.block_id===id).candidate_class==='ORE_CANDIDATE'));
  }
  checks.push({stage,passed:true,contract:'HTML payload, field selection, finite meshes, per-block lookup, missing filter, scenario filter',visual_browser:false});
 }
 console.log(JSON.stringify({passed:true,checks},null,2));
})().catch(e=>{console.error(e);process.exit(1);});
