/* Datos locales de la generación publicada. Sin CDN y sin solicitudes de red. */
(() => {
  'use strict';
  const D=window.G05_MODEL, $=id=>document.getElementById(id), nf=new Intl.NumberFormat('es-PE',{maximumFractionDigits:3});
  const fmt=v=>v===null||v===undefined||v===''?'Sin estimación / no aplica':typeof v==='number'?nf.format(v):String(v);
  const precise=(key,v)=>typeof v==='number' && /_est(?:_r50)?$/.test(key)?
    new Intl.NumberFormat('es-PE',{minimumFractionDigits:6,maximumFractionDigits:6}).format(v):fmt(v);
  if(!D || !window.Plotly){$('plot-error').textContent='Faltan datos o Plotly local. Revisa la carpeta completa.';return;}
  const fields={cu_pct_est:['Cu estimado (%)',0,1.5],mo_pct_est:['Mo estimado (%)',0,.1],au_gt_est:['Au estimado (g/t)',0,.5],
    density_t_m3_est:['Densidad estimada (t/m³)',2.4,3],tonnage_t:['Tonelaje (t)',0,75000],
    rock_fraction:['Fracción de roca TIN',0,1],rock_volume_m3:['Volumen de roca TIN (m³)',0,25000],cu_pct_n:['Compósitos Cu usados',0,12],
    cu_pct_est_r50:['Cu con radio 50 m (%)',0,1.5]};
  if(D.stage==='S12')Object.assign(fields,{candidate_class:['Clase candidata',0,2],
    scenario_A_allocated_t:['A: movimiento asignado (t)',0,1000],scenario_B_allocated_t:['B: movimiento asignado (t)',0,1000],
    scenario_A_opex_usd:['A: OPEX asignado (USD)',0,10000],scenario_B_opex_usd:['B: OPEX asignado (USD)',0,10000]});
  for(const [id,[name]] of Object.entries(fields)){const o=document.createElement('option');o.value=id;o.textContent=name;$('color-mode').append(o);}
  if(D.stage==='S12')$('color-mode').value='candidate_class';
  const metric=D.stage==='S11'?
    [['Bloques con Cu estimado',D.summary.grade_estimated_blocks],['Con densidad estimada',D.summary.density_estimated_blocks],
     ['Bloques cuantificables',D.summary.quantified_blocks],['Tonelaje con densidad (t)',D.summary.quantified_tonnage_t],
     ['Con Cu y tonelaje',D.summary.grade_and_tonnage_blocks],['Con Cu a 50 m',D.summary.grade_estimated_blocks_r50],
     ['Tonelaje con Cu y densidad (t)',D.summary.grade_supported_tonnage_t]]:
    [['Candidatos a mineral',D.summary.candidate_counts.ORE_CANDIDATE||0],['Candidatos a desmonte',D.summary.candidate_counts.WASTE_CANDIDATE||0],
     ['Mineral candidato (t)',D.summary.ore_inventory_t],['Sin clasificación',D.summary.candidate_counts.UNCLASSIFIED||0],
     ['Desmonte candidato (t)',D.summary.waste_inventory_t],['Diferencia CAPEX B−A (USD)',D.summary.capex_difference_usd]];
  for(const [label,value] of metric){const a=document.createElement('article');a.className='metric';const s=document.createElement('span');s.textContent=label;const b=document.createElement('strong');b.textContent=fmt(value);a.append(s,b);$('metrics').append(a);}
  $('run-id').textContent=D.run_id;
  const all=new Map(D.blocks.map(b=>[b.block_id,b]));
  const keys=['block_id','lith_code','lith_status','topo_status','volume_status','cell_volume_m3','rock_volume_m3','rock_fraction',
    'cu_pct_est','mo_pct_est','au_gt_est','density_t_m3_est','tonnage_t','tonnage_reason',
    'cu_pct_n','cu_pct_holes','cu_pct_reason','cu_pct_sample_ids','cu_pct_distances_m','cu_pct_weights',
    'density_t_m3_n','density_t_m3_holes','density_t_m3_reason','density_t_m3_sample_ids','density_t_m3_distances_m',
    'cu_pct_est_r50','cu_pct_reason_r50','candidate_class','candidate_reason','reserve_classification',
    'allocation_rule','scenario_A_fraction','scenario_B_fraction','scenario_A_allocated_t','scenario_B_allocated_t',
    'scenario_A_processed_t','scenario_B_processed_t','scenario_A_remaining_t','scenario_B_remaining_t',
    'scenario_A_mining_opex_usd','scenario_B_mining_opex_usd','scenario_A_processing_opex_usd','scenario_B_processing_opex_usd',
    'scenario_A_general_opex_usd','scenario_B_general_opex_usd','scenario_A_opex_usd','scenario_B_opex_usd',
    'scenario_A_truck_capex_share_usd','scenario_B_truck_capex_share_usd'];
  function inspect(id){const b=all.get(id);$('block-detail').replaceChildren();if(!b){$('block-detail').textContent='No existe ese ID en este modelo.';return;}
    $('block-id').value=id;const table=document.createElement('table');
    for(const key of keys){if(!(key in b))continue;const tr=document.createElement('tr'),h=document.createElement('th'),c=document.createElement('td');h.textContent=key;c.textContent=Array.isArray(b[key])?b[key].map(fmt).join(', '):precise(key,b[key]);tr.append(h,c);table.append(tr);} $('block-detail').append(table);}
  $('inspect').addEventListener('click',()=>inspect($('block-id').value.trim()));
  $('block-id').addEventListener('keydown',e=>{if(e.key==='Enter')inspect(e.target.value.trim());});
  const palette=['#597079','#3a9ba3','#6eb487','#e5c873','#dd9455','#d45b50'];
  const categoryColor={ORE_CANDIDATE:'#e9bb64',WASTE_CANDIDATE:'#519bac',UNCLASSIFIED:'#62747a'};
  function draw(){
    const field=$('color-mode').value,showMissing=$('show-missing').checked,filter=$('class-filter').value;
    let filtered=D.blocks.filter(b=>b.topo_status!=='AIR' && (showMissing || b.cu_pct_est!==null) &&
       (filter==='ALL'||b.candidate_class===filter));
    // Conservar todos los estimados/candidatos y reducir contexto, sin cambiar inventario.
    let important=filtered.filter(b=>b.cu_pct_est!==null),context=filtered.filter(b=>b.cu_pct_est===null);
    let slots=Math.max(0,D.max_display_blocks-important.length),step=Math.max(1,Math.ceil(context.length/Math.max(1,slots)));
    let shown=important.slice(0,D.max_display_blocks).concat(context.filter((_,i)=>i%step===0).slice(0,slots));
    const groups=new Map();
    for(const b of shown){let value=b[field],color;
      if(field==='candidate_class')color=categoryColor[value]||'#62747a';
      else if(value===null||value===undefined)color='#4b5e65';
      else{const [,low,high]=fields[field];color=palette[Math.max(0,Math.min(5,Math.floor((value-low)/(high-low)*6)))];}
      if(!groups.has(color))groups.set(color,[]);groups.get(color).push(b);}
    const traces=[];
    for(const [color,blocks] of groups){let x=[],y=[],z=[],i=[],j=[],k=[],text=[],customdata=[];
      const faces=[[0,1,2],[0,2,3],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]];
      for(const b of blocks){let n=x.length;for(const [a,c,d] of [[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,0,1],[1,0,1],[1,1,1],[0,1,1]]){
        x.push(b.x_min+a*(b.x_max-b.x_min));y.push(b.y_min+c*(b.y_max-b.y_min));z.push(b.z_min+d*(b.z_max-b.z_min));
        customdata.push(b.block_id);text.push(b.block_id+'<br>'+fields[field][0]+': '+fmt(b[field])+'<br>Cu: '+fmt(b.cu_pct_est)+' %<br>T: '+fmt(b.tonnage_t)+' t');}
        for(const [a,bf,c] of faces){i.push(n+a);j.push(n+bf);k.push(n+c);}}
      traces.push({type:'mesh3d',x,y,z,i,j,k,color,opacity:.65,flatshading:true,text,customdata,
        hoverinfo:'text',name:color==='#4b5e65'?'Sin valor':fields[field][0],showscale:false});}
    if($('show-holes').checked)for(const hole of D.trajectories){traces.push({type:'scatter3d',mode:'lines',x:hole.x,y:hole.y,z:hole.z,
      line:{color:'#d4e8f2',width:3},name:hole.hole_id,showlegend:false,hovertext:hole.hole_id,hoverinfo:'text'});}
    const [label,low,high]=fields[field];
    $('legend').textContent=field==='candidate_class'?'Dorado: mineral candidato · azul: desmonte candidato · gris: sin clasificación':
      label+': escala '+fmt(low)+' a '+fmt(high)+' · azul a rojo · gris: sin valor. Consulta el valor exacto del bloque.';
    $('drawing-count').textContent=`${nf.format(shown.length)} cajas dibujadas de ${nf.format(filtered.length)} filtradas; ${nf.format(D.blocks.length)} filas en el CSV completo.`;
    Plotly.react('plot',traces,{paper_bgcolor:'#101719',plot_bgcolor:'#101719',font:{color:'#dce8ed'},margin:{l:0,r:0,t:8,b:0},
      showlegend:false,uirevision:'g05-fixed-camera',scene:{aspectmode:'data',xaxis:{title:'X este (m)'},yaxis:{title:'Y norte (m)'},zaxis:{title:'Z arriba (m)'},
      camera:{eye:{x:1.5,y:1.5,z:1.2}}}},{responsive:true,displaylogo:false}).then(()=>{
      $('plot').removeAllListeners('plotly_click');$('plot').on('plotly_click',e=>{const id=e.points[0].customdata;if(all.has(id))inspect(id);});
      window.G05_VIEW_READY=true;}).catch(e=>{$('plot-error').textContent=String(e);});
  }
  for(const id of ['color-mode','show-missing','class-filter','show-holes'])$(id).addEventListener('change',draw);
  if(D.stage==='S12'){
    const table=document.createElement('table');let head=document.createElement('tr');
    for(const label of ['Escenario','Ciclo (min)','t/camión/día','Camiones meta','CAPEX (USD)','Movido período (t)','Procesado (t)','OPEX período (USD)']){const h=document.createElement('th');h.textContent=label;head.append(h);}table.append(head);
    for(const s of D.scenarios){const row=document.createElement('tr');for(const key of ['scenario','cycle_min','productivity_t_truck_day','trucks_for_target','truck_capex_usd','moved_t_period','ore_allocated_t_period','opex_usd_period']){const c=document.createElement('td');c.textContent=fmt(s[key]);row.append(c);}table.append(row);}$('scenario-table').append(table);
  }else $('scenario-section').hidden=true;
  inspect(D.blocks.find(b=>b.cu_pct_est!==null)?.block_id||D.blocks[0].block_id);draw();
})();
