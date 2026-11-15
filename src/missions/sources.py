"""Valida G05 y reconstruye propiedades de compósitos y posición de densidades."""
from __future__ import annotations

import csv
import hashlib
import math
from collections import defaultdict
from src.mod1.loader import load_raw_data
from src.mod1.validator import validate_data
from src.mod1.desurvey import desurvey
from src.mod1.positioning import position_intervals
from src.missions.estimation import Sample

ANALYTES = ('cu_pct', 'mo_pct', 'au_gt')


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def number(value, *, nullable=False, minimum=None):
    if value is None or str(value).strip() == '':
        if nullable:
            return None
        raise ValueError('Número obligatorio ausente')
    result = float(value)
    if not math.isfinite(result) or (minimum is not None and result < minimum):
        raise ValueError(f'Número no válido: {value!r}')
    return result


def interval_code(row, lithology):
    start, end = float(row['from_m']), float(row['to_m'])
    found = [r['lith_code'] for r in lithology.get(row['hole_id'], [])
             if float(r['from_m']) <= start+1e-8 and float(r['to_m']) >= end-1e-8]
    return found[0] if len(found) == 1 else None


def prepare(root, parameters):
    raw = load_raw_data(root / 'data/raw')
    findings = validate_data(raw)['findings']
    errors = [f for f in findings if f['severity'] == 'ERROR']
    if errors:
        raise ValueError(f'M01: {len(errors)} errores: {errors[:2]}')
    manifest = raw['release_manifest']
    if (manifest.get('dataset_id'),manifest.get('release_id'),manifest.get('synthetic_data')) != ('DS05','EXP03',True):
        raise ValueError('La misión requiere el release sintético G05 DS05/EXP03')
    for name, digest in manifest['file_sha256'].items():
        actual = hashlib.sha256((root/'data/raw'/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
        if actual != digest:
            raise ValueError(f'Fuente raw distinta del manifiesto: {name}')
    counts = {k:len(raw[k]) for k in ['collar','survey','assay','lithology','density']}
    expected = dict(collar=44,survey=313,assay=5803,lithology=120,density=459)
    if counts != expected:
        raise ValueError(f'Conteos G05 distintos del corte esperado: {counts}')
    trajectory = desurvey(raw['collar'], raw['survey'])
    lith = defaultdict(list)
    for row in raw['lithology']:
        lith[row['hole_id']].append(row)
    assays = {r['sample_id']:r for r in raw['assay']}
    if len(assays) != len(raw['assay']):
        raise ValueError('sample_id de ensayo duplicado')
    composites = read_csv(root/'data/processed/m01b/composites.csv')
    positioned = position_intervals(trajectory,dict(assay=composites,lithology=[],alteration=[],density=[]))['assay']
    grades, composite_rows = [], []
    ids = set()
    for row, pos in zip(composites, positioned):
        start,end = number(row['from_m'],minimum=0),number(row['to_m'],minimum=0)
        length = end-start
        if length <= 0 or not math.isclose(length,number(row['length_m']),abs_tol=1e-7):
            raise ValueError('Longitud de compósito inconsistente')
        sid = f"{row['hole_id']}:{start:.9f}:{end:.9f}"
        if sid in ids:
            raise ValueError('Compósito duplicado')
        ids.add(sid)
        xyz = tuple(number(row[a+'_mid']) for a in 'xyz')
        if max(abs(a-number(pos[k+'_mid'])) for a,k in zip(xyz,'xyz')) > 1e-5:
            raise ValueError(f'XYZ de compósito no reproduce desurvey: {sid}')
        code = interval_code(row,lith)
        if not code or code != row['lith_code']:
            raise ValueError('Compósito cruza contacto o no reproduce su dominio')
        origins = row['source_sample_ids'].split(';')
        # El exportador M01 separa identidades con | en algunas versiones.
        if len(origins)==1 and '|' in origins[0]:
            origins=origins[0].split('|')
        origins=[s.strip() for s in origins if s.strip()]
        if not origins or len(set(origins)) != len(origins):
            raise ValueError('Procedencia de compósito vacía o duplicada')
        segments=[]
        for origin in origins:
            a=assays.get(origin)
            if a is None or a['hole_id'] != row['hole_id']:
                raise ValueError(f'Ensayo fuente no corresponde: {origin}')
            lo,hi=max(start,float(a['from_m'])),min(end,float(a['to_m']))
            if hi <= lo:
                raise ValueError('Ensayo fuente no intersecta el compósito')
            segments.append((lo,hi,a))
        segments.sort(key=lambda s:s[0])
        cursor=start
        for lo,hi,_ in segments:
            if abs(lo-cursor)>1e-7:
                raise ValueError('Hueco/solape en procedencia de compósito')
            cursor=hi
        if abs(cursor-end)>1e-7:
            raise ValueError('Cobertura de ensayo incompleta')
        values={}
        for key in ANALYTES:
            vals=[number(a.get(key),nullable=True,minimum=0) for _,_,a in segments]
            values[key]=None if any(v is None for v in vals) else math.fsum(
                (hi-lo)*v for (lo,hi,_),v in zip(segments,vals))/length
        original=number(row.get('cu_pct'),nullable=True,minimum=0)
        if original is None or not math.isclose(values['cu_pct'],original,rel_tol=1e-8,abs_tol=1e-9):
            raise ValueError('Cu reconstruido no concilia con M01')
        full=math.isclose(length,parameters['grade']['reference_length_m'],abs_tol=1e-7)
        eligible=full and code not in parameters['excluded_lithologies']
        sample=Sample(sid,row['hole_id'],code,xyz,values,frozenset(origins))
        if eligible:
            grades.append(sample)
        composite_rows.append(dict(row, **values) | dict(composite_id=sid,eligible_idw2=eligible,
                                   eligibility_reason='ELIGIBLE_2M' if eligible else
                                   'EXCLUDED_LITHOLOGY' if full else 'RESIDUAL_SUPPORT'))
    densities=position_intervals(trajectory,dict(assay=[],lithology=[],alteration=[],density=raw['density']))['density']
    density_samples,density_rows=[],[]
    density_ids=set()
    for row in densities:
        sid=row['density_sample_id']
        if not sid or sid in density_ids:
            raise ValueError('Identidad de densidad duplicada o vacía')
        density_ids.add(sid)
        code=interval_code(row,lith)
        rho=number(row.get('density_t_m3'),nullable=True,minimum=0)
        eligible=bool(code and code not in parameters['excluded_lithologies'] and rho and rho>0)
        reason='ELIGIBLE' if eligible else 'CONTACT_CROSSING_OR_UNCOVERED' if not code else 'INVALID_DENSITY_OR_EXCLUDED_DOMAIN'
        density_rows.append({k:v for k,v in row.items() if k!='trajectory_segments'} |
                            dict(lith_code=code,eligible_idw2=eligible,eligibility_reason=reason))
        if eligible:
            density_samples.append(Sample(sid,row['hole_id'],code,tuple(row[k+'_mid'] for k in 'xyz'),
                                          {'density_t_m3':rho},frozenset([sid])))
    blocks=read_csv(root/'data/processed/m01b/block_model_preliminary_geology_topography.csv')
    block_ids=set()
    for b in blocks:
        for key in ['i','j','k']:
            b[key]=int(b[key])
        bid=f"G05-{b['i']:02d}-{b['j']:02d}-{b['k']:02d}"
        if bid in block_ids:
            raise ValueError('Identidad de bloque duplicada')
        block_ids.add(bid);b['block_id']=bid
        for axis,expected_size in zip('xyz',(50,50,10)):
            for suffix in ['_min','_max','_center']:
                b[axis+suffix]=number(b[axis+suffix])
            if not math.isclose(b[axis+'_max']-b[axis+'_min'],expected_size,abs_tol=1e-7):
                raise ValueError('Dimensiones de malla G05 alteradas')
            if not math.isclose(b[axis+'_center'],(b[axis+'_min']+b[axis+'_max'])/2,abs_tol=1e-7):
                raise ValueError('Centro fuera de geometría')
        for axis,index,origin,size in [('x',b['i'],242225,50),('y',b['j'],8196250,50),('z',b['k'],2990,10)]:
            if not math.isclose(b[axis+'_min'],origin+index*size,abs_tol=1e-7):
                raise ValueError('Índice del bloque no corresponde a su posición en la malla G05')
        if b['topo_status'] not in {'AIR','ROCK','PARTIAL'}:
            raise ValueError('Estado topográfico desconocido')
    if len(blocks)!=11550 or len(composites)!=5830:
        raise ValueError('Modelo o compósitos no corresponden al corte G05')
    if {(b['i'],b['j'],b['k']) for b in blocks}!={(i,j,k) for i in range(15) for j in range(14) for k in range(55)}:
        raise ValueError('El conjunto de índices no corresponde a la malla 15 × 14 × 55')
    return blocks,grades,density_samples,composite_rows,density_rows,dict(
        raw_counts=counts,composites=len(composites),eligible_composites=len(grades),
        density_samples=len(density_rows),eligible_density_samples=len(density_samples),
        m01_findings=findings,composite_xyz_reproduced=True,cu_reconciled=True,
        analytes_augmented_from_raw=['mo_pct','au_gt'])
