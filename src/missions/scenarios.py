"""Candidatos y vínculo contable por bloque con escenarios PT-01 A/B."""
from __future__ import annotations
import math


def classify(block,cutoff):
    reasons=[]
    if block['lith_status']!='ASSIGNED' or not block['lith_code']:
        reasons.append('NO_PRELIMINARY_DOMAIN')
    if block['lith_code'] in {'AIR','OVB'}:
        reasons.append('EXCLUDED_DOMAIN')
    if block['topo_status']=='AIR' or block.get('rock_volume_m3') in (None,0):
        reasons.append('NO_ELIGIBLE_ROCK_VOLUME')
    if block.get('cu_pct_est') is None:
        reasons.append('NO_CU_SUPPORT')
    if block.get('density_t_m3_est') is None:
        reasons.append('NO_DENSITY_SUPPORT')
    if block.get('tonnage_t') is None or block.get('tonnage_t',0)<=0:
        reasons.append('NO_QUANTIFIABLE_TONNAGE')
    if reasons:
        return 'UNCLASSIFIED',';'.join(reasons)
    return ('ORE_CANDIDATE' if block['cu_pct_est']>=cutoff else 'WASTE_CANDIDATE'),'ELIGIBLE_ACADEMIC_RULES'


def scenarios(blocks,params,cycles):
    classified=[]
    for b in blocks:
        kind,reason=classify(b,params['ore_cutoff_cu_pct'])
        classified.append(dict(b,candidate_class=kind,candidate_reason=reason,
                               reserve_classification='NOT_ASSIGNED',allocation_rule='G05-ALLOC-01'))
    ore=math.fsum(b['tonnage_t'] for b in classified if b['candidate_class']=='ORE_CANDIDATE')
    waste=math.fsum(b['tonnage_t'] for b in classified if b['candidate_class']=='WASTE_CANDIDATE')
    days=params['operating_days']
    mine_target=params['mine_t_per_day']*days
    plant_target=params['plant_t_per_day']*days
    # La fracción presupuestaria no se presenta como proporción observada del yacimiento.
    ore_target=min(plant_target,mine_target*params['theoretical_budget_ore_fraction'])
    waste_target=mine_target-ore_target
    ore_alloc=min(ore,ore_target);waste_alloc=min(waste,waste_target)
    moved=ore_alloc+waste_alloc
    scenario_rows=[];links=[]
    for name,cycle in cycles.items():
        daily_truck=params['truck_payload_t']*(60/cycle)*params['shifts']*params['hours_per_shift']*params['availability']*params['utilization']
        trucks=math.ceil(params['mine_t_per_day']/daily_truck)
        capex=trucks*params['truck_capex_usd']
        mining=moved*params['mining_opex_usd_per_t_moved']
        processing=ore_alloc*params['processing_opex_usd_per_t_ore_processed']
        general=moved*params['general_opex_usd_per_t_moved']
        scenario_rows.append(dict(scenario=name,cycle_min=cycle,operating_days=days,
            productivity_t_truck_day=daily_truck,trucks_for_target=trucks,
            fleet_capacity_t_day=trucks*daily_truck,mine_target_t_period=mine_target,
            plant_target_t_period=plant_target,ore_inventory_t=ore,waste_inventory_t=waste,
            ore_target_t_period=ore_target,waste_target_t_period=waste_target,
            ore_allocated_t_period=ore_alloc,waste_allocated_t_period=waste_alloc,
            moved_t_period=moved,ore_gap_t_period=ore_target-ore_alloc,waste_gap_t_period=waste_target-waste_alloc,
            actual_ore_fraction=ore_alloc/moved if moved else None,
            trucks_for_allocated_daily_movement=math.ceil(moved/days/daily_truck),
            truck_capex_usd=capex,mining_opex_usd_period=mining,
            processing_opex_usd_period=processing,general_opex_usd_period=general,
            opex_usd_period=mining+processing+general,opex_usd_day=(mining+processing+general)/days,
            theoretical_opex_usd_day=params['mine_t_per_day']*(params['mining_opex_usd_per_t_moved']+
                params['general_opex_usd_per_t_moved'])+params['mine_t_per_day']*params['theoretical_budget_ore_fraction']*params['processing_opex_usd_per_t_ore_processed'],
            allocation_rule='G05-ALLOC-01',parameter_basis='ACADEMIC_ASSUMPTION',physical_schedule='NOT_MODELLED'))
        for b in classified:
            if b['candidate_class']=='UNCLASSIFIED':
                allocated=None;fraction=None;remaining=None
            else:
                total,allocation=(ore,ore_alloc) if b['candidate_class']=='ORE_CANDIDATE' else (waste,waste_alloc)
                fraction=allocation/total if total>0 else 0.
                allocated=b['tonnage_t']*fraction;remaining=b['tonnage_t']-allocated
            is_ore=b['candidate_class']=='ORE_CANDIDATE'
            mining_cost=allocated*params['mining_opex_usd_per_t_moved'] if allocated is not None else None
            processing_cost=allocated*params['processing_opex_usd_per_t_ore_processed'] if is_ore else (0. if allocated is not None else None)
            general_cost=allocated*params['general_opex_usd_per_t_moved'] if allocated is not None else None
            link=dict(block_id=b['block_id'],scenario=name,candidate_class=b['candidate_class'],
                      inventory_t=b['tonnage_t'],allocation_fraction=fraction,
                      allocated_moved_t=allocated,allocated_processed_t=allocated if is_ore else (0. if allocated is not None else None),
                      remaining_inventory_t=remaining,mining_opex_usd=mining_cost,processing_opex_usd=processing_cost,
                      general_opex_usd=general_cost,
                      total_opex_usd=mining_cost+processing_cost+general_cost if allocated is not None else None,
                      truck_capex_accounting_share_usd=capex*allocated/moved if allocated is not None and moved>0 else None,
                      allocation_rule='G05-ALLOC-01')
            links.append(link)
            b['scenario_'+name+'_allocated_t']=allocated
            b['scenario_'+name+'_fraction']=fraction
            b['scenario_'+name+'_opex_usd']=link['total_opex_usd']
            b['scenario_'+name+'_remaining_t']=remaining
            b['scenario_'+name+'_processed_t']=link['allocated_processed_t']
            b['scenario_'+name+'_mining_opex_usd']=mining_cost
            b['scenario_'+name+'_processing_opex_usd']=processing_cost
            b['scenario_'+name+'_general_opex_usd']=general_cost
            b['scenario_'+name+'_truck_capex_share_usd']=link['truck_capex_accounting_share_usd']
    checks=[]
    for s in scenario_rows:
        rows=[r for r in links if r['scenario']==s['scenario']]
        summed=lambda key:math.fsum(r[key] for r in rows if r[key] is not None)
        checks.extend([
          (s['scenario']+'_moved_balance',math.isclose(summed('allocated_moved_t'),s['moved_t_period'],abs_tol=1e-6)),
          (s['scenario']+'_plant_balance',math.isclose(summed('allocated_processed_t'),s['ore_allocated_t_period'],abs_tol=1e-6)),
          (s['scenario']+'_opex_balance',math.isclose(summed('total_opex_usd'),s['opex_usd_period'],abs_tol=1e-5)),
          (s['scenario']+'_capex_balance',math.isclose(summed('truck_capex_accounting_share_usd'),s['truck_capex_usd'],abs_tol=1e-5) if moved else all(r['truck_capex_accounting_share_usd'] is None for r in rows)),
          (s['scenario']+'_capacities',s['moved_t_period']<=mine_target and s['ore_allocated_t_period']<=plant_target and s['moved_t_period']/days<=s['fleet_capacity_t_day']),
          (s['scenario']+'_fractions',all(r['allocation_fraction'] is None or 0<=r['allocation_fraction']<=1 for r in rows))])
    checks.append(('unknown_not_allocated',all(r['allocated_moved_t'] is None for r in links if r['candidate_class']=='UNCLASSIFIED')))
    validation=dict(passed=all(v for _,v in checks),checks=dict(checks))
    return classified,scenario_rows,links,validation
