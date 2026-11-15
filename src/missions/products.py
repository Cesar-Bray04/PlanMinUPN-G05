"""Publicación local de generaciones inmutables y comprobación de integridad."""
from __future__ import annotations
import csv
import hashlib
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
POINTER = 'outputs/g05_products.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def write_csv(path, rows):
    if not rows:
        raise ValueError('Tabla de salida vacía: '+str(path))
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fields,lineterminator='\n');writer.writeheader()
        for row in rows:
            writer.writerow({k:json.dumps(v,ensure_ascii=False,allow_nan=False) if isinstance(v,(list,dict))
                             else '' if v is None else v for k,v in row.items()})


def scientific_inputs(root):
    paths=[*sorted((root/'data/raw').rglob('*')),
           *sorted((root/'src/mod1').glob('*.py')),*sorted((root/'src/missions').glob('*.py')),
           root/'data/processed/m01b/composites.csv',
           root/'data/processed/m01b/block_model_preliminary_geology_topography.csv',
           root/'kai/parametros_pt01_v2.json',root/'kai/politicas_cuantificacion_g05_v1.json',
           root/'assets/quantitative.js',root/'assets/quantitative.css']
    return {str(p.relative_to(root)):digest(p) for p in paths if p.is_file()}


def begin(root, stage, inputs):
    run_id=hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()[:20]
    final=root/'outputs'/('g05_'+stage.lower())/run_id
    if final.exists():
        manifest=verify_manifest(root,str((final/'manifest.json').relative_to(root)))
        return None,final,run_id,manifest
    final.parent.mkdir(parents=True,exist_ok=True)
    temp=Path(tempfile.mkdtemp(prefix='.pending_',dir=final.parent))
    return temp,final,run_id,None


def publish(root, stage, temp, final, run_id, inputs, summary):
    manifest=dict(schema='g05-product/1',stage=stage,run_id=run_id,
                  product=summary['product'],status='VALIDATED',inputs=inputs,
                  outputs={str(p.relative_to(temp)):digest(p) for p in sorted(temp.rglob('*')) if p.is_file()})
    dump(temp/'manifest.json',manifest)
    temp.rename(final)
    activate(root,stage,final,run_id)
    return manifest


def activate(root,stage,final,run_id):
    """Selecciona una generación verificada, incluso tras volver a una fuente anterior."""
    pointer_path=root/POINTER
    pointer=json.loads(pointer_path.read_text()) if pointer_path.exists() else {'schema':'g05-products/1'}
    changed=pointer.get(stage,{}).get('run_id')!=run_id
    pointer[stage]={'manifest':str((final/'manifest.json').relative_to(root)),'run_id':run_id}
    if stage=='S11' and changed:
        pointer.pop('S12',None)  # Un S12 anterior nunca acompaña silenciosamente otro S11.
    pointer_path.parent.mkdir(exist_ok=True,parents=True)
    pending=pointer_path.with_suffix('.pending')
    dump(pending,pointer);os.replace(pending,pointer_path)


def safe_path(root, relative):
    path=root/relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Ruta fuera del proyecto')
    return path


def verify_manifest(root, manifest_path):
    path=safe_path(root,manifest_path)
    manifest=json.loads(path.read_text(encoding='utf-8'))
    if manifest.get('status')!='VALIDATED':
        raise ValueError('Producto no validado')
    for rel,expected in manifest['inputs'].items():
        p=safe_path(root,rel)
        if not p.is_file() or digest(p)!=expected:
            raise ValueError('Fuente cambió; repetir misión: '+rel)
    for rel,expected in manifest['outputs'].items():
        p=safe_path(root,str((path.parent/rel).relative_to(root)))
        if not p.is_file() or digest(p)!=expected:
            raise ValueError('Producto incompleto o modificado: '+rel)
    validation=json.loads((path.parent/(manifest['stage'].lower()+'_validation.json')).read_text())
    if validation.get('passed') is not True:
        raise ValueError('Los controles del producto no aprobaron')
    return manifest


def verified_product(root,stage):
    pointer=json.loads((root/POINTER).read_text())
    item=pointer[stage]
    manifest=verify_manifest(root,item['manifest'])
    if manifest['stage']!=stage or manifest['run_id']!=item['run_id']:
        raise ValueError('Identidad de producto no coincide')
    folder=(root/item['manifest']).parent
    summary=json.loads((folder/(stage.lower()+'_summary.json')).read_text())
    return manifest,folder,summary


def product_status(root=ROOT):
    result={}
    for stage in ('S11','S12'):
        try:
            m,p,s=verified_product(root,stage)
            result[stage]=dict(status='VALIDATED',run_id=m['run_id'],product=s['product'],
                               folder=str(p.relative_to(root)),summary=s)
        except (OSError,ValueError,KeyError,TypeError) as exc:
            result[stage]=dict(status='NOT_VERIFIED',reason=str(exc))
    if result['S12']['status']=='VALIDATED' and (result['S11']['status']!='VALIDATED' or
        result['S12']['summary'].get('s11_run_id')!=result['S11'].get('run_id')):
        result['S12']=dict(status='NOT_VERIFIED',reason='S12 no corresponde al S11 activo')
    return result
