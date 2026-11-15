(() => {
  'use strict';
  const products=window.G05_PRODUCTS||{},nf=new Intl.NumberFormat('es-PE',{maximumFractionDigits:3});
  for(const stage of ['S11','S12']){
    const id=stage.toLowerCase(),p=products[stage],status=document.getElementById(id+'-status');
    const button=document.querySelector('[data-mission-load="'+stage+'"]');
    if(!p||p.status!=='VALIDATED'){status.textContent='No hay una generación verificada disponible. Kai debe ejecutar y verificar la misión antes de trabajar sus resultados.';button.disabled=true;continue;}
    status.textContent='Generación '+p.run_id+' · controles aprobados al publicar. Kai comprueba de nuevo las fuentes al registrar respuestas.';
    const s=p.summary,metrics=stage==='S11'?
      [['Con Cu estimado',s.grade_estimated_blocks],['Con densidad',s.density_estimated_blocks],['Con tonelaje',s.quantified_blocks],['Tonelaje con densidad (t)',s.quantified_tonnage_t],['Tonelaje con Cu y densidad (t)',s.grade_supported_tonnage_t],['Cu a 50 m',s.grade_estimated_blocks_r50]]:
      [['Mineral candidato',s.candidate_counts.ORE_CANDIDATE||0],['Desmonte candidato',s.candidate_counts.WASTE_CANDIDATE||0],['Sin clasificar',s.candidate_counts.UNCLASSIFIED||0],['Camiones A',s.scenario_A.trucks_for_target],['Camiones B',s.scenario_B.trucks_for_target]];
    for(const [name,value] of metrics){const d=document.createElement('div'),b=document.createElement('strong'),label=document.createElement('span');b.textContent=nf.format(value);label.textContent=name;d.append(b,label);document.getElementById(id+'-metrics').append(d);}
    for(const [name,file] of [['Abrir visor completo',id+'_model_3d.html'],['Modelo CSV','block_model_'+id+'.csv'],['Controles',id+'_validation.json'],['Reporte', 'reporte_'+id+'.md']]){
      const a=document.createElement('a');a.className='button secondary';a.href=p.folder+'/'+file;a.textContent=name;a.target='_blank';a.rel='noopener';document.getElementById(id+'-files').append(a);}
    if(stage==='S12'){const a=document.createElement('a');a.className='button secondary';a.href='outputs/Entregable_Grupal_G05_S11_S12.zip';a.textContent='Entregable grupal';a.download='Entregable_Grupal_G05_S11_S12.zip';document.getElementById(id+'-files').append(a);}
    button.addEventListener('click',()=>{document.querySelector('[data-mission-frame="'+stage+'"]').src=p.folder+'/'+id+'_model_3d.html';button.disabled=true;button.textContent='Visor '+stage+' cargado';});
  }
})();
