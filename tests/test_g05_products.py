"""Reconciliación independiente de datos, cantidades y escenarios publicados."""
import csv
import json
import math
from pathlib import Path
import tempfile
import unittest
import numpy as np

from src.missions.products import verified_product, verify_manifest
from src.missions.g05 import load_s11_rows
from src.missions.sources import prepare, read_csv
from src.missions.scenarios import scenarios, classify
from src.missions.volume import tin_volumes
from src.mod1.topography import read_topography_points,triangulate_topography

ROOT=Path(__file__).resolve().parents[1]


class ProductTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m11,cls.p11,cls.s11=verified_product(ROOT,'S11')
        cls.m12,cls.p12,cls.s12=verified_product(ROOT,'S12')
        cls.rows=load_s11_rows(cls.p11)
        cls.params=json.loads((ROOT/'kai/parametros_pt01_v2.json').read_text())

    def test_independent_cu_estimation_all_eligible_blocks(self):
        _,samples,_,_,_,_=prepare(ROOT,self.params['S11'])
        estimated=0
        for b in self.rows:
            if b['lith_status']!='ASSIGNED' or b['lith_code'] in {'AIR','OVB'} or b['topo_status']=='AIR' or b['rock_volume_m3']==0:
                self.assertIsNone(b['cu_pct_est']);continue
            point=tuple(b[a+'_center'] for a in 'xyz')
            candidates=sorted([(math.dist(point,s.xyz),s.id,s) for s in samples if s.lith==b['lith_code'] and math.dist(point,s.xyz)<=75],key=lambda r:(r[0],r[1]))
            selected=[];source_ids=set()
            for distance,_,sample in candidates:
                if source_ids & sample.origins:continue
                selected.append((distance,sample));source_ids.update(sample.origins)
                if len(selected)==12:break
            if len(selected)<3 or len({s.hole for _,s in selected})<2:
                self.assertIsNone(b['cu_pct_est']);continue
            self.assertTrue(all(d>0 for d,_ in selected),'G05 real no tiene caso coincidente; cubierto por casos manuales')
            weights=[1/d**2 for d,_ in selected]
            value=sum(w*s.values['cu_pct'] for w,(_,s) in zip(weights,selected))/sum(weights)
            self.assertAlmostEqual(b['cu_pct_est'],value,places=12)
            self.assertEqual(b['cu_pct_sample_ids'],[s.id for _,s in selected]);estimated+=1
        self.assertEqual(estimated,self.s11['grade_estimated_blocks'])

    def test_density_position_independent_straight_first_hole(self):
        raw=read_csv(ROOT/'data/raw/collar.csv')[0]
        r=read_csv(self.p11/'density_positioned_qa.csv')[0]
        az=math.radians(float(raw['azimuth_deg']));dip=math.radians(float(raw['dip_deg']));md=float(r['mid_m'])
        for axis,direction in zip('xyz',[math.sin(az)*math.cos(dip),math.cos(az)*math.cos(dip),math.sin(dip)]):
            self.assertAlmostEqual(float(r[axis+'_mid']),float(raw[axis])+md*direction,places=6)
        self.assertEqual(len(read_csv(self.p11/'density_positioned_qa.csv')),459)

    def test_tin_coverage_and_independent_midpoint_quadrature(self):
        self.assertLess(self.s11['volume_qa']['max_footprint_area_error_m2'],1e-6)
        self.assertEqual(sum(self.s11['integrated_volume_counts'].values()),11550)
        self.assertNotIn('NO_TIN_COVERAGE',self.s11['integrated_volume_counts'])
        points=read_topography_points(ROOT/'data/raw/topography/Topopl.csv');origin=points[:,:2].min(0);points[:,:2]-=origin
        surface=triangulate_topography(points)
        partial=[b for b in self.rows if b['volume_status']=='PARTIAL_ROCK_TIN']
        for b in partial[::max(1,len(partial)//8)][:8]:
            x=b['x_min']+(np.arange(80)+.5)/80*(b['x_max']-b['x_min'])
            y=b['y_min']+(np.arange(80)+.5)/80*(b['y_max']-b['y_min'])
            xx,yy=np.meshgrid(x,y);xy=np.column_stack([xx.ravel(),yy.ravel()])-origin
            z=surface.interpolate(xy)
            expected=np.clip(z-b['z_min'],0,b['z_max']-b['z_min']).mean()*(b['x_max']-b['x_min'])*(b['y_max']-b['y_min'])
            self.assertAlmostEqual(b['rock_volume_m3'],expected,delta=50)

    def test_inventory_and_block_scenario_balances(self):
        table=read_csv(self.p12/'block_scenario_s12.csv');model=read_csv(self.p12/'block_model_s12.csv')
        self.assertEqual(len(table),23100);self.assertEqual(len(model),11550)
        self.assertEqual(len({(r['block_id'],r['scenario']) for r in table}),23100)
        for s in read_csv(self.p12/'scenario_s12.csv'):
            links=[r for r in table if r['scenario']==s['scenario']]
            moved=sum(float(r['allocated_moved_t']) for r in links if r['allocated_moved_t'])
            processed=sum(float(r['allocated_processed_t']) for r in links if r['allocated_processed_t'])
            opex=sum(float(r['total_opex_usd']) for r in links if r['total_opex_usd'])
            self.assertAlmostEqual(moved,110000,places=6);self.assertAlmostEqual(processed,66000,places=6)
            self.assertAlmostEqual(opex,1001000,places=5)
            self.assertAlmostEqual(float(s['productivity_t_truck_day']),870.4 if s['scenario']=='A' else 652.8)
            self.assertEqual(int(s['trucks_for_target']),6 if s['scenario']=='A' else 8)
            for r in links:
                if r['candidate_class']=='UNCLASSIFIED':self.assertEqual(r['allocated_moved_t'],'')
                else:
                    self.assertAlmostEqual(float(r['allocated_moved_t'])+float(r['remaining_inventory_t']),float(r['inventory_t']),places=7)
                    self.assertLessEqual(float(r['allocated_moved_t']),float(r['inventory_t']))
        self.assertTrue(all(r['reserve_classification']=='NOT_ASSIGNED' for r in model))
        by_id={r['block_id']:r for r in model}
        for link in table:
            if not link['allocated_moved_t']:continue
            row=by_id[link['block_id']];prefix='scenario_'+link['scenario']
            self.assertAlmostEqual(float(row[prefix+'_remaining_t']),float(link['remaining_inventory_t']),places=6)
            self.assertAlmostEqual(float(row[prefix+'_allocated_t'])+float(row[prefix+'_remaining_t']),float(link['inventory_t']),places=6)
            self.assertAlmostEqual(float(row[prefix+'_mining_opex_usd'])+float(row[prefix+'_processing_opex_usd'])+
                                   float(row[prefix+'_general_opex_usd']),float(row[prefix+'_opex_usd']),places=6)
        self.assertAlmostEqual(self.s11['grade_supported_tonnage_t'],self.s12['ore_inventory_t']+self.s12['waste_inventory_t'],places=6)

    def test_cutoff_alone_not_enough(self):
        b=dict(self.rows[0],cu_pct_est=2.,density_t_m3_est=None,tonnage_t=None)
        self.assertEqual(classify(b,.5)[0],'UNCLASSIFIED')
        eligible=next(dict(b) for b in self.rows if b['cu_pct_est'] is not None and b['tonnage_t'] is not None)
        eligible['cu_pct_est']=.5
        self.assertEqual(classify(eligible,.5)[0],'ORE_CANDIDATE')

    def test_deficient_inventory_no_invented_tonnage(self):
        eligible=[dict(b) for b in self.rows if b['cu_pct_est'] is not None and b['tonnage_t'] is not None][:2]
        eligible[0].update(cu_pct_est=.6,tonnage_t=100)
        eligible[1].update(cu_pct_est=.2,tonnage_t=50)
        _,sc,links,validation=scenarios(eligible,self.params['S12']['parameters'],self.params['S12']['scenario_cycles_min'])
        self.assertTrue(validation['passed'])
        for s in sc:
            self.assertEqual(s['moved_t_period'],150);self.assertEqual(s['ore_allocated_t_period'],100)
            self.assertGreater(s['ore_gap_t_period'],0)
        self.assertTrue(all(r['allocation_fraction']==1 for r in links))

    def test_modified_source_and_output_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);(r/'source').write_text('a');(r/'table.csv').write_text('a')
            from src.missions.products import digest,dump
            dump(r/'s11_validation.json',{'passed':True})
            dump(r/'manifest.json',dict(stage='S11',status='VALIDATED',inputs={'source':digest(r/'source')},outputs={'table.csv':digest(r/'table.csv')}))
            verify_manifest(r,'manifest.json')
            (r/'source').write_text('b')
            with self.assertRaisesRegex(ValueError,'Fuente cambió'):verify_manifest(r,'manifest.json')
            (r/'source').write_text('a');(r/'table.csv').write_text('b')
            with self.assertRaisesRegex(ValueError,'modificado'):verify_manifest(r,'manifest.json')


class VolumeTranslationTests(unittest.TestCase):
    def test_large_coordinates_do_not_change_volume(self):
        for origin in [(0,0),(242250,8196250)]:
            x,y=origin
            with tempfile.TemporaryDirectory() as d:
                p=Path(d)/'topo.csv'
                with p.open('w',newline='') as f:
                    w=csv.writer(f);w.writerow(['PID','X','Y','Z']);w.writerows([[1,x,y,0],[2,x+10,y,10],[3,x+10,y+10,10],[4,x,y+10,0],[5,x+5,y+5,5]])
                b=dict(i=0,j=0,k=0,x_min=x,x_max=x+10,y_min=y,y_max=y+10,z_min=0,z_max=10,
                       x_center=x+5,y_center=y+5,topo_z_m=5,topo_status='PARTIAL')
                rows,qa=tin_volumes([b],p)
                self.assertAlmostEqual(rows[0]['rock_volume_m3'],500,places=8)
                self.assertLess(qa['max_footprint_area_error_m2'],1e-8)


if __name__=='__main__':unittest.main()
