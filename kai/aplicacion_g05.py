"""Aplicación individual V3: valores observados, comprobados y ligados a una corrida.

Se conserva E1 v1 y la teoría V2. La plantilla se genera con Artifact Tool;
el escritor OOXML de ejecución sigue el contrato sin dependencias de Kai.
"""
from __future__ import annotations
from contextlib import closing
from datetime import datetime,timezone
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import sys
import uuid
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from src.missions.products import product_status, verified_product
from src.missions.g05 import load_s11_rows
from src.missions.sources import read_csv
from ficha_individual import ALIAS,_excel_cell,S

DATA=ROOT/'.kai_local'
TEMPLATE=ROOT/'kai/PLANTILLA_Aplicacion_Individual_G05_V3.xlsx'
_CATALOG_CACHE={}


def catalog(root=ROOT):
    s11,folder,summary=verified_product(root,'S11')
    try:
        sm,fp,s=verified_product(root,'S12')
        if s['s11_run_id']!=s11['run_id']:sm=None
    except (OSError,ValueError,KeyError):sm=None
    cache_key=(str(root.resolve()),s11['run_id'],sm['run_id'] if sm else None)
    # Se verifica integridad antes de reutilizar el catálogo; nunca se cachea
    # la decisión de que un producto permanece válido.
    if cache_key in _CATALOG_CACHE:return _CATALOG_CACHE[cache_key]
    rows=load_s11_rows(folder)
    eligible=sorted([b for b in rows if b['cu_pct_est'] is not None and b['tonnage_t'] is not None],key=lambda b:b['block_id'])
    if not eligible:raise ValueError('No hay un bloque con Cu y tonelaje respaldados para la aplicación')
    example=eligible[0];fields=[]
    def add(fid,label,value,unit,stage,block='',places=3):
        fields.append(dict(id=fid,label=label,expected=value,unit=unit,stage=stage,block=block,
            places=places,pantalla='index.html#'+stage.lower(),
            pregunta=f"En {'el bloque '+block if block else 'el resumen '+stage}, ¿qué valor observas para {label.lower()} ({unit})?",
            pista='Vuelve a la pantalla indicada y lee ese dato. Conserva la unidad; no lo deduzcas por el color.'))
    for fid,label,key,unit,places in [
        ('S11.CU75','Bloques con Cu a 75 m','grade_estimated_blocks','bloques',0),
        ('S11.CU50','Bloques con Cu a 50 m','grade_estimated_blocks_r50','bloques',0),
        ('S11.DENSIDAD','Bloques con densidad','density_estimated_blocks','bloques',0),
        ('S11.CUANTIFICADOS','Bloques con tonelaje','quantified_blocks','bloques',0),
        ('S11.TONELAJE','Tonelaje cuantificable','quantified_tonnage_t','t',3),
        ('S11.CU_T','Bloques con Cu y tonelaje','grade_and_tonnage_blocks','bloques',0)]:
        add(fid,label,summary[key],unit,'S11',places=places)
    for fid,label,key,unit,places in [
        ('S11.B.CU','Cu estimado','cu_pct_est','%',6),('S11.B.RHO','Densidad estimada','density_t_m3_est','t/m3',6),
        ('S11.B.V','Volumen de roca','rock_volume_m3','m3',3),('S11.B.T','Tonelaje del bloque','tonnage_t','t',3),
        ('S11.B.H','Sondajes usados para Cu','cu_pct_holes','sondajes',0),
        ('S11.B.MO','Mo estimado','mo_pct_est','%',6),('S11.B.AU','Au estimado','au_gt_est','g/t',6)]:
        add(fid,label,example[key],unit,'S11',example['block_id'],places)
    if sm:
        a=s['scenario_A'];b=s['scenario_B']
        for fid,label,value,unit,places in [
          ('S12.ORE_N','Bloques candidatos a mineral',s['candidate_counts'].get('ORE_CANDIDATE',0),'bloques',0),
          ('S12.WASTE_N','Bloques candidatos a desmonte',s['candidate_counts'].get('WASTE_CANDIDATE',0),'bloques',0),
          ('S12.UNKNOWN','Bloques sin clasificar',s['candidate_counts'].get('UNCLASSIFIED',0),'bloques',0),
          ('S12.ORE_T','Tonelaje candidato a mineral',s['ore_inventory_t'],'t',3),
          ('S12.WASTE_T','Tonelaje candidato a desmonte',s['waste_inventory_t'],'t',3),
          ('S12.MINE','Movimiento asignado del período',a['moved_t_period'],'t',3),
          ('S12.PLANT','Tratamiento asignado del período',a['ore_allocated_t_period'],'t',3),
          ('S12.TRUCK_A','Camiones para la meta A',a['trucks_for_target'],'camiones',0),
          ('S12.TRUCK_B','Camiones para la meta B',b['trucks_for_target'],'camiones',0),
          ('S12.CAPEX','Diferencia CAPEX B menos A',s['capex_difference_usd'],'USD',2),
          ('S12.OPEX','OPEX A del período',a['opex_usd_period'],'USD',2)]:
            add(fid,label,value,unit,'S12',places=places)
        relation=next(r for r in read_csv(fp/'block_scenario_s12.csv') if r['block_id']==example['block_id'] and r['scenario']=='A')
        add('S12.B.ALLOC','A: movimiento asignado al bloque',float(relation['allocated_moved_t']),'t','S12',example['block_id'],3)
        add('S12.B.OPEX','A: OPEX asignado al bloque',float(relation['total_opex_usd']),'USD','S12',example['block_id'],3)
    result=fields,s11['run_id'],sm['run_id'] if sm else None
    if len(_CATALOG_CACHE)>16:_CATALOG_CACHE.clear()
    _CATALOG_CACHE[cache_key]=result
    return result


def folder_for(alias,run_id,data=DATA):
    if not isinstance(alias,str) or not ALIAS.fullmatch(alias):raise ValueError('Alias inválido')
    return data/alias/'aplicacion_v3'/run_id


def progress(alias,root=ROOT,data=DATA):
    try:
        fields,run_id,s12_id=catalog(root)
    except (OSError,ValueError,KeyError) as exc:
        return dict(status='WAITING_FOR_VERIFIED_S11',reason=str(exc),S11_complete=False,S12_complete=False,complete=False)
    folder=folder_for(alias,run_id,data);dbpath=folder/'aplicacion_v3.sqlite';answers={}
    if dbpath.exists():
        with closing(sqlite3.connect(dbpath.as_uri()+'?mode=ro',uri=True)) as db:
            answers={r[0]:json.loads(r[1]) for r in db.execute('SELECT field_id,value_json FROM answers')}
    s11=[f for f in fields if f['stage']=='S11'];s12=[f for f in fields if f['stage']=='S12']
    pending=next((f for f in fields if f['id'] not in answers),None)
    public={k:v for k,v in pending.items() if k!='expected'} if pending else None
    return dict(status='COMPLETE' if len(answers)==26 and s12_id else 'IN_PROGRESS',version=3,s11_run_id=run_id,s12_run_id=s12_id,
        answered=len(answers),total=26,S11_total=13,S12_total=13,
        S11_answered=sum(f['id'] in answers for f in s11),S12_answered=sum(f['id'] in answers for f in s12),
        S11_complete=all(f['id'] in answers for f in s11),
        S12_complete=bool(s12_id) and len(s12)==13 and all(f['id'] in answers for f in s12),
        complete=len(answers)==26 and bool(s12_id),pending=public,
        xlsx=str(folder/'Ficha_Aplicacion_G05_V3.xlsx'))


def parse_numeric(value):
    if type(value) in (int,float):return float(value) if math.isfinite(value) else None
    if not isinstance(value,str):return None
    s=value.strip().replace('\u00a0',' ').replace('\u202f',' ')
    if not re.fullmatch(r'[+-]?[\d .,]+',s):return None
    s=s.replace(' ','')
    if ',' in s and '.' in s:
        s=s.replace(',','') if s.rfind('.')>s.rfind(',') else s.replace('.','').replace(',','.')
    elif ',' in s:
        if s.count(',')>1:s=s.replace(',','')
        else:s=s.replace(',','.')
    elif s.count('.')>1:s=s.replace('.','')
    try:v=float(s)
    except ValueError:return None
    return v if math.isfinite(v) else None


def literal_contains(literal,value):
    # Extrae números del texto del alumno, sin reinterpretar su decisión.
    tokens=re.findall(r'[+-]?\d+(?:[ .,\u00a0\u202f]\d+)*',literal)
    return any((v:=parse_numeric(t)) is not None and math.isclose(v,value,rel_tol=1e-10,abs_tol=1e-9) for t in tokens)


def set_cell(xml,address,value):
    _excel_cell(xml,address,value)
    if type(value) in (int,float):
        cell=xml.find(f".//{S}c[@r='{address}']");cell.attrib.pop('t',None)
        for child in list(cell):cell.remove(child)
        ET.SubElement(cell,f'{S}v').text=repr(value)


def export(db,folder,alias,fields,run_id,s12_id):
    records={r[0]:r for r in db.execute('SELECT field_id,value_json,literal,date,unit,stage FROM answers')}
    with zipfile.ZipFile(TEMPLATE) as source:
        sheets={i:ET.fromstring(source.read(f'xl/worksheets/sheet{i}.xml')) for i in (1,2)}
        set_cell(sheets[1],'C3',alias);set_cell(sheets[1],'F3',run_id)
        set_cell(sheets[1],'C4',len(records));set_cell(sheets[1],'F4','Lista para entregar' if len(records)==26 else 'En curso')
        for n,f in enumerate(fields,start=7):
            set_cell(sheets[1],f'F{n}',f['block'] or 'Resumen')
            row=records.get(f['id'])
            if row:
                value=json.loads(row[1]);set_cell(sheets[1],f'C{n}',value);set_cell(sheets[1],f'E{n}','VALIDADO')
                for col,val in zip('ABCDEF',[f['id'],row[3],row[2],row[4],row[5],run_id if f['stage']=='S11' else s12_id]):
                    set_cell(sheets[2],f'{col}{n-1}',val)
        temp=folder/('.application_'+uuid.uuid4().hex+'.xlsx');target=folder/'Ficha_Aplicacion_G05_V3.xlsx'
        try:
            with zipfile.ZipFile(temp,'w') as dest:
                for info in source.infolist():
                    data=source.read(info)
                    for i,xml in sheets.items():
                        if info.filename==f'xl/worksheets/sheet{i}.xml':data=ET.tostring(xml,encoding='utf-8',xml_declaration=True)
                    dest.writestr(info,data)
            os.replace(temp,target)
        finally:temp.unlink(missing_ok=True)
    return str(target)


def process(request,*,root=ROOT,data=DATA,comprehension=None):
    alias=request.get('alumno');fields,run_id,s12_id=catalog(root)
    folder=folder_for(alias,run_id,data);folder.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(folder/'aplicacion_v3.sqlite')) as db:
        db.execute('CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY,value TEXT NOT NULL)')
        db.execute('''CREATE TABLE IF NOT EXISTS answers (field_id TEXT PRIMARY KEY,value_json TEXT NOT NULL,
            literal TEXT NOT NULL,date TEXT NOT NULL,unit TEXT NOT NULL,stage TEXT NOT NULL)''')
        db.execute('''CREATE TABLE IF NOT EXISTS attempts (id INTEGER PRIMARY KEY,date TEXT NOT NULL,
            field_id TEXT NOT NULL,literal TEXT NOT NULL,proposed TEXT NOT NULL,accepted INTEGER NOT NULL)''')
        for key,val in [('s11_run_id',run_id),('s12_run_id',s12_id)]:
            if val is None:continue
            prev=db.execute('SELECT value FROM metadata WHERE key=?',(key,)).fetchone()
            if prev and prev[0]!=val:raise ValueError('La generación cambió: conserva la ficha anterior y consulta a DD')
            db.execute('INSERT OR IGNORE INTO metadata VALUES (?,?)',(key,val))
        records={r[0] for r in db.execute('SELECT field_id FROM answers')}
        pending=next((f for f in fields if f['id'] not in records),None)
        result=dict(ok=True)
        if request.get('operacion')=='responder_aplicacion':
            if pending is None:raise ValueError('La aplicación ya está completa')
            if request.get('campo')!=pending['id']:raise ValueError('Responde primero el campo pendiente')
            required='S11.6' if pending['stage']=='S11' else 'S12.6'
            if comprehension is None or comprehension['estados'].get(required)!='DEMOSTRADO':
                raise ValueError('Primero termina y comprende '+pending['stage'])
            literal=request.get('respuesta_literal');value=parse_numeric(request.get('valor_propuesto'))
            unit=request.get('unidad')
            if not isinstance(literal,str) or not 1<=len(literal.strip())<=1200:raise ValueError('Se requiere la respuesta literal del alumno')
            unit_ok=unit==pending['unit']
            tolerance=0 if pending['places']==0 else .5001*10**(-pending['places'])
            accepted=value is not None and unit_ok and literal_contains(literal,value) and abs(value-pending['expected'])<=tolerance
            now=datetime.now(timezone.utc).isoformat(timespec='microseconds')
            db.execute('INSERT INTO attempts (date,field_id,literal,proposed,accepted) VALUES (?,?,?,?,?)',
                (now,pending['id'],literal,json.dumps(request.get('valor_propuesto'),ensure_ascii=False),int(accepted)))
            if accepted:
                approved=int(pending['expected']) if pending['places']==0 else value
                db.execute('INSERT INTO answers VALUES (?,?,?,?,?,?)',(pending['id'],json.dumps(approved),literal,now,pending['unit'],pending['stage']))
            result.update(validado=accepted,campo=pending['id'])
            if not accepted:result['pista']=pending['pista']+' Revisa también la unidad.'
        elif request.get('operacion')!='estado_aplicacion':raise ValueError('Operación de aplicación desconocida')
        db.commit()
        try:
            result['xlsx']=export(db,folder,alias,fields,run_id,s12_id);result['excel_actualizado']=True
        except PermissionError:
            result['excel_actualizado']=False;result['mensaje_excel']='Cierra Excel y consulta estado_aplicacion. SQLite conserva la respuesta.'
    result.update(progress(alias,root,data));return result
