"""Ejecuta S11/S12 G05 sin modificar datos raw ni progreso individual.

Uso: python -m src.missions.g05 s11|s12|todo|verificar
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import sys

from src.missions.estimation import Estimator
from src.missions.sources import ANALYTES, prepare, read_csv, number
from src.missions.volume import tin_volumes
from src.missions.scenarios import scenarios
from src.missions.products import (ROOT, begin, digest, dump, publish, activate, scientific_inputs,
                                   product_status, verified_product, write_csv)
from src.missions.viewer import render_view


def excluded_reason(block,volume,params):
    if block['topo_status']=='AIR' or volume['rock_volume_m3']==0:
        return 'AIR_EXCLUDED'
    if block['lith_status']!='ASSIGNED' or not block['lith_code']:
        return 'NO_PRELIMINARY_DOMAIN'
    if block['lith_code'] in params['excluded_lithologies']:
        return 'EXCLUDED_LITHOLOGY'
    return None


def estimate_blocks(blocks,volumes,grades,densities,params):
    ge, de = Estimator(grades), Estimator(densities)
    rows=[]
    for b,vol in zip(blocks,volumes):
        row=dict(b,**vol,estimation_method='IDW2',estimation_support='CELL_CENTER_PROXY',
                 geological_domain_basis='PRELIMINARY_LITERAL_CODE',parameter_basis='PT01_ACADEMIC')
        reason=excluded_reason(b,vol,params)
        xyz=tuple(b[a+'_center'] for a in 'xyz')
        for prop in (*ANALYTES,'density_t_m3'):
            cfg=params['density'] if prop=='density_t_m3' else params['grade']
            estimator=de if prop=='density_t_m3' else ge
            settings={k:cfg[k] for k in ['radius_m','max_samples','min_samples','power']}
            settings['min_holes']=cfg.get('min_holes',1)
            r=estimator.estimate(xyz,b['lith_code'],prop,**settings) if reason is None else dict(
                value=None,reason=reason,n=0,holes=0,independent_origins=0,sample_ids=[],distances_m=[],weights=[])
            row[prop+'_est']=r.pop('value')
            row.update({prop+'_'+k:v for k,v in r.items()})
            if prop in ANALYTES:
                settings['radius_m']=50
                r50=estimator.estimate(xyz,b['lith_code'],prop,**settings) if reason is None else dict(value=None,reason=reason,n=0,holes=0)
                row[prop+'_est_r50']=r50['value'];row[prop+'_reason_r50']=r50['reason']
                row[prop+'_n_r50']=r50['n'];row[prop+'_holes_r50']=r50['holes']
        rho=row['density_t_m3_est']
        row['tonnage_t']=rho*vol['rock_volume_m3'] if rho is not None and vol['rock_volume_m3'] is not None and vol['rock_volume_m3']>0 else None
        row['tonnage_reason']='QUANTIFIED' if row['tonnage_t'] is not None else 'NO_DENSITY_SUPPORT' if rho is None else 'NO_ROCK_VOLUME'
        row['supported_grade_tonnage_t']=row['tonnage_t'] if row['cu_pct_est'] is not None else None
        rows.append(row)
    return rows


def validate_s11(rows,params):
    checks={
      'all_11550_block_ids_preserved':len(rows)==11550 and len({b['block_id'] for b in rows})==11550,
      'finite_volume_bounds':all(b['rock_volume_m3'] is None or 0<=b['rock_volume_m3']<=b['cell_volume_m3'] for b in rows),
      'air_not_estimated':all(b['cu_pct_est'] is None and b['density_t_m3_est'] is None for b in rows if b['topo_status']=='AIR'),
      'unassigned_not_estimated':all(b['cu_pct_est'] is None for b in rows if b['lith_status']!='ASSIGNED'),
      'missing_density_preserves_null_tonnage':all(b['tonnage_t'] is None for b in rows if b['density_t_m3_est'] is None),
      'tonnage_mass_balance':all(b['tonnage_t'] is None or math.isclose(b['tonnage_t'],b['rock_volume_m3']*b['density_t_m3_est'],rel_tol=1e-12) for b in rows),
      'partial_volumes_integrated_or_explicitly_missing':all(b['rock_volume_m3'] is not None or b['volume_status']=='NO_TIN_COVERAGE' for b in rows if b['topo_status']=='PARTIAL')}
    for prop in (*ANALYTES,'density_t_m3'):
        cfg=params['density'] if prop=='density_t_m3' else params['grade']
        estimated=[b for b in rows if b[prop+'_est'] is not None]
        checks[prop+'_minima']=all(b[prop+'_n']>=cfg['min_samples'] and b[prop+'_holes']>=cfg.get('min_holes',1) for b in estimated)
        checks[prop+'_maximum_and_radius']=all(b[prop+'_n']<=cfg['max_samples'] and max(b[prop+'_distances_m'])<=cfg['radius_m']+1e-9 for b in estimated)
        checks[prop+'_weights_sum_one']=all(math.isclose(math.fsum(b[prop+'_weights']),1,abs_tol=1e-12) for b in estimated)
        checks[prop+'_zero_or_positive']=all(b[prop+'_est']>=0 for b in estimated)
    return dict(passed=all(checks.values()),checks=checks,
                validation_scope='COMPUTATIONAL_AND_ACADEMIC_RULES; no continuidad geológica ni CRS formal acreditados')


def run_s11(root=ROOT):
    inputs=scientific_inputs(root)
    temp,final,run_id,existing=begin(root,'S11',inputs)
    if existing:
        activate(root,'S11',final,run_id)
        return {'stage':'S11','run_id':run_id,'reused_verified_generation':True}
    p=json.loads((root/'kai/parametros_pt01_v2.json').read_text())['S11']
    blocks,grades,densities,comps,density_rows,source_qa=prepare(root,p)
    volumes,volume_qa=tin_volumes(blocks,root/'data/raw/topography/Topopl.csv')
    rows=estimate_blocks(blocks,volumes,grades,densities,p)
    validation=validate_s11(rows,p)
    if not validation['passed']:
        raise ValueError('S11 no aprobó: '+str(validation))
    quantified=[b for b in rows if b['tonnage_t'] is not None]
    supported=[b for b in quantified if b['cu_pct_est'] is not None]
    tonnage=math.fsum(b['tonnage_t'] for b in supported)
    summary=dict(product='Modelo de bloques de recursos ACADÉMICO',stage='S11',run_id=run_id,
        total_blocks=len(rows),grade_estimated_blocks=sum(b['cu_pct_est'] is not None for b in rows),
        density_estimated_blocks=sum(b['density_t_m3_est'] is not None for b in rows),
        quantified_blocks=len(quantified),quantified_tonnage_t=math.fsum(b['tonnage_t'] for b in quantified),
        grade_and_tonnage_blocks=len(supported),grade_supported_tonnage_t=tonnage,
        tonnage_weighted_cu_pct=math.fsum(b['cu_pct_est']*b['tonnage_t'] for b in supported)/tonnage if tonnage else None,
        missing_cu_blocks=sum(b['cu_pct_est'] is None for b in rows),
        grade_estimated_blocks_r50=sum(b['cu_pct_est_r50'] is not None for b in rows),
        observed_density_samples=459,positioned_density_samples=len(density_rows),eligible_density_samples=len(densities),
        composite_count=len(comps),eligible_complete_composites=len(grades),
        inherited_topo_counts=dict(Counter(b['topo_status'] for b in rows)),
        integrated_volume_counts=dict(Counter(b['volume_status'] for b in rows)),
        partial_inherited_blocks=sum(b['topo_status']=='PARTIAL' for b in rows),
        estimation_reasons=dict(Counter(b['cu_pct_reason'] for b in rows)),
        units=dict(cu_pct='%',mo_pct='%',au_gt='g/t',density='t/m3',volume='m3',tonnage='t'),
        limitations=['Litología preliminar; continuidad entre sondajes no demostrada.',
          'Estimación en centro como proxy académico; soporte volumétrico no corregido.',
          'CRS/datum topográfico no documentados; compatibilidad local heredada como supuesto.',
          'Incertidumbre de estimación no cuantificada por IDW².'],
        source_qa=source_qa,volume_qa=volume_qa)
    write_csv(temp/'block_model_s11.csv',rows)
    write_csv(temp/'composites_multianalyte_qa.csv',comps)
    write_csv(temp/'density_positioned_qa.csv',density_rows)
    write_csv(temp/'sensitivity_75_50.csv',[{k:b[k] for k in ['block_id','cu_pct_est','cu_pct_est_r50','cu_pct_n','cu_pct_n_r50','cu_pct_holes','cu_pct_holes_r50','cu_pct_reason','cu_pct_reason_r50']} for b in rows])
    dump(temp/'s11_summary.json',summary);dump(temp/'s11_validation.json',validation)
    (temp/'reporte_s11.md').write_text(f"# {summary['product']}\n\nCorrida `{run_id}`. G05 DS05/EXP03; 11 550 celdas.\n\n"
        f"Cu estimado: {summary['grade_estimated_blocks']} bloques a 75 m; {summary['grade_estimated_blocks_r50']} a 50 m. "
        f"Densidad estimada: {summary['density_estimated_blocks']}. Tonelaje cuantificable: {summary['quantified_tonnage_t']:.6f} t "
        f"en {summary['quantified_blocks']} bloques. Con Cu y tonelaje: {len(supported)} bloques, {tonnage:.6f} t.\n\n"
        "## Trazabilidad\n\nEnsayes originales → compósitos por longitud y contacto → IDW² por código preliminar. "
        "Mo y Au se reconstruyen desde ensayes; Cu se concilia con M01. Cada estimación conserva IDs, distancias, pesos y sondajes. "
        "Densidad usa desurvey M01 y mediciones íntegramente contenidas en un dominio. Residuales se preservan en QA. "
        "Volumen: recorte de TIN por huella y límites verticales; integración analítica de planos. "
        "Se conserva el estado topográfico antiguo por separado. Nulo no significa cero.\n\n"
        "## Supuestos y límites\n\n"+'\n'.join('- '+s for s in summary['limitations'])+
        "\n\n## Verificación\n\n`s11_validation.json` contiene controles ejecutados. "
        "La comparación manual .60 % / 2.64 t/m³ es un microcaso PT-01, no un bloque G05. "
        "La tabla completa respalda los totales; el 3D reduce contexto si excede 6000 cajas.\n",encoding='utf-8')
    render_view(root,temp,'S11',run_id,rows,summary)
    publish(root,'S11',temp,final,run_id,inputs,summary)
    return {'stage':'S11','run_id':run_id,'summary':{k:summary[k] for k in ['grade_estimated_blocks','density_estimated_blocks','quantified_tonnage_t','grade_estimated_blocks_r50']}}


def load_s11_rows(folder):
    rows=read_csv(folder/'block_model_s11.csv')
    for b in rows:
        for k,v in list(b.items()):
            if k in {'i','j','k'}:b[k]=int(v)
            elif k.endswith(('_sample_ids','_distances_m','_weights')):b[k]=json.loads(v)
            elif k in ['x_min','x_max','y_min','y_max','z_min','z_max','x_center','y_center','z_center',
                       'cell_volume_m3','rock_volume_m3','rock_fraction','tonnage_t','supported_grade_tonnage_t'] or (
                       k.startswith(('cu_pct_','mo_pct_','au_gt_','density_t_m3_')) and
                       (k.endswith(('_est','_n','_holes','_independent_origins','_est_r50','_n_r50','_holes_r50')))):
                b[k]=number(v,nullable=True)
    return rows


def run_s12(root=ROOT):
    s11,source,source_summary=verified_product(root,'S11')
    inputs=scientific_inputs(root)
    for name in ['manifest.json','block_model_s11.csv','s11_validation.json']:
        path=source/name;inputs[str(path.relative_to(root))]=digest(path)
    temp,final,run_id,existing=begin(root,'S12',inputs)
    if existing:
        activate(root,'S12',final,run_id)
        return {'stage':'S12','run_id':run_id,'reused_verified_generation':True}
    p=json.loads((root/'kai/parametros_pt01_v2.json').read_text())['S12']
    rows,scenario_rows,links,validation=scenarios(load_s11_rows(source),p['parameters'],p['scenario_cycles_min'])
    if not validation['passed']:raise ValueError('S12 no aprobó: '+str(validation))
    a,b=scenario_rows
    summary=dict(product='Modelo preliminar de bloques de reservas ACADÉMICO',stage='S12',run_id=run_id,
        s11_run_id=s11['run_id'],total_blocks=len(rows),candidate_counts=dict(Counter(r['candidate_class'] for r in rows)),
        ore_inventory_t=a['ore_inventory_t'],waste_inventory_t=a['waste_inventory_t'],
        ore_allocated_t_period=a['ore_allocated_t_period'],waste_allocated_t_period=a['waste_allocated_t_period'],
        allocation_rule='G05-ALLOC-01',allocation_basis='PROPORTIONAL_FRACTIONAL_INVENTORY_NO_SEQUENCE',
        block_scenario_rows=len(links),scenario_A=a,scenario_B=b,capex_difference_usd=b['truck_capex_usd']-a['truck_capex_usd'],
        physical_schedule='NOT_MODELLED',reserve_classification='NOT_ASSIGNED',
        limitations=source_summary['limitations']+['Sin pit, accesos, precedencias, secuencia, recuperación ni rentabilidad modelados.',
            'Asignación proporcional de inventario por clase; no identifica bloques físicamente extraíbles en el período.'])
    write_csv(temp/'block_model_s12.csv',rows);write_csv(temp/'scenario_s12.csv',scenario_rows)
    write_csv(temp/'block_scenario_s12.csv',links)
    dump(temp/'s12_summary.json',summary);dump(temp/'s12_validation.json',validation)
    report=f"# {summary['product']}\n\nS11 fuente `{s11['run_id']}`; S12 `{run_id}`.\n\n"
    report+=f"Mineral candidato: {a['ore_inventory_t']:.6f} t; desmonte candidato: {a['waste_inventory_t']:.6f} t. "
    report+=f"Período: {a['operating_days']} días; asignados {a['ore_allocated_t_period']:.6f} t de mineral y {a['waste_allocated_t_period']:.6f} t de desmonte.\n\n"
    report+="## Vínculo verificable por bloque\n\nG05-ALLOC-01, regla académica nueva, explícita y versionada: "
    report+="cada clase participa proporcionalmente a su tonelaje. Mineral se limita al menor entre inventario, capacidad de planta y objetivo presupuestario de mineral. "
    report+="Desmonte se limita a su inventario y al remanente presupuestario. No se suplen déficits de una clase con otra. "
    report+="Fracción asignada = toneladas objetivo alcanzables de la clase / inventario de la clase; cada bloque conserva su remanente. "
    report+="Es una asignación de inventario fraccionaria para comparar capacidades, no una secuencia de extracción ni un porcentaje de reservas recuperables. "
    report+="Las 23 100 relaciones bloque/escenario incluyen también exclusiones con asignación nula. El CSV conserva costos variables por bloque y reparto contable del CAPEX.\n\n"
    report+="## A/B\n\n|Escenario|Productividad t/camión/día|Camiones meta|CAPEX USD|OPEX USD/período|\n|---|---:|---:|---:|---:|\n"
    for s in scenario_rows:report+=f"|{s['scenario']}|{s['productivity_t_truck_day']:.3f}|{s['trucks_for_target']}|{s['truck_capex_usd']:.2f}|{s['opex_usd_period']:.2f}|\n"
    report+="\nEl cambio de ciclo modifica productividad y flota. Las tasas OPEX permanecen iguales: no se inventa un consumo de combustible diferente. "
    report+="CAPEX corresponde a camiones para la meta PT-01; no es inversión total del proyecto. Los costos se aplican a toneladas asignadas, no al inventario completo. "
    report+="La comparación favorece A en adquisición bajo esos supuestos; no demuestra rentabilidad ni acceso a esos bloques.\n\n## Límites\n\n"
    report+='\n'.join('- '+s for s in summary['limitations'])+'\n'
    (temp/'reporte_s12.md').write_text(report,encoding='utf-8');(temp/'escenarios_s12.md').write_text(report,encoding='utf-8')
    render_view(root,temp,'S12',run_id,rows,summary,scenario_rows)
    publish(root,'S12',temp,final,run_id,inputs,summary)
    return {'stage':'S12','run_id':run_id,'candidate_counts':summary['candidate_counts'],'ore_inventory_t':a['ore_inventory_t'],'waste_inventory_t':a['waste_inventory_t']}


def refresh_index(root=ROOT):
    status=product_status(root)
    # El visor muestra la generación verificada al publicar; el tutor vuelve a verificar al operar.
    target=root/'datos/resultados_g05.js'
    target.write_text('window.G05_PRODUCTS='+json.dumps(status,ensure_ascii=False,allow_nan=False)+';\n',encoding='utf-8')
    return status


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mission',choices=['s11','s12','todo','verificar'])
    args=parser.parse_args()
    try:
        if args.mission in {'s11','todo'}:print(json.dumps(run_s11(),ensure_ascii=False))
        if args.mission in {'s12','todo'}:print(json.dumps(run_s12(),ensure_ascii=False))
        status=refresh_index()
        print(json.dumps({'products':{k:{i:v for i,v in d.items() if i!='summary'} for k,d in status.items()}},ensure_ascii=False))
        requested=['S11','S12'] if args.mission in {'todo','verificar'} else [args.mission.upper()]
        return 0 if all(status[k]['status']=='VALIDATED' for k in requested) else 1
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print(json.dumps({'ok':False,'error':str(exc)},ensure_ascii=False),file=sys.stderr);return 1


if __name__=='__main__':raise SystemExit(main())
