"""Controlador E1 → teoría S11 → aplicación S11 → S12 → entrega.

Reutiliza SQLite/Excel V1/V2 y ficha E1 sin reescribir sus aprobaciones.
Las extensiones V3 conservan los datos observados por corrida.
"""
from __future__ import annotations
from contextlib import closing
import copy
import json
from pathlib import Path
import sqlite3
import sys
import zipfile

ROOT=Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
import registro_v2 as theory
import ficha_individual as e1
import aplicacion_g05 as application
from src.missions.products import product_status, verified_product

REQUEST=ROOT/'.kai_solicitud_recorrido_g05.json'
DATA=ROOT/'.kai_local'


def e1_status(alias):
    path=DATA/alias/'ficha_individual.sqlite'
    count=0
    if path.exists():
        with closing(sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)) as db:
            count=db.execute('SELECT count(*) FROM respuestas').fetchone()[0]
    return dict(answered=count,total=21,complete=count==21,
                xlsx=str(DATA/alias/'Ficha_Individual_G05.xlsx'))


def decorate(info):
    info=copy.deepcopy(info)
    products=product_status(ROOT)
    app=application.progress(info['alumno'],ROOT,DATA)
    ficha=e1_status(info['alumno'])
    info['controller_version']=1
    info['productos_grupales']={k:{i:v for i,v in p.items() if i!='summary'} for k,p in products.items()}
    info['aplicacion_individual_v3']=app;info['ficha_e1']=ficha
    info['entregables_individuales']=dict(comprension=info['comprension_registrada'],ficha_e1=ficha['complete'],aplicacion_s11_s12=app['complete'])
    info['entrega_final_lista']=(info['comprension_registrada'] and ficha['complete'] and app['complete'] and
                               all(p['status']=='VALIDATED' for p in products.values()))
    actual=info['actividad_actual']
    if actual and actual.startswith('S11.0'):
        info['indicacion_visor']='Abre Métodos y teoría S11 en index.html#teoria. Los ejemplos de la guía no son resultados G05.'
    if actual and actual in {'S11.1','S11.2','S11.3','S11.4','S11.5','S11.6'}:
        if products['S11']['status']!='VALIDATED':
            info['objetivo_siguiente']='EJECUTAR_Y_VERIFICAR_S11_G05';info['actividad']=None
        else:
            info['actividad']['visor']=dict(url='index.html#s11',pantalla='S11 · Recursos académico',
                accion='Carga el visor S11. Cambia la propiedad, consulta un bloque y mira su valor, unidad, soporte y causa de faltante.',
                pregunta_desde_visor=info['actividad']['pregunta'])
    if info['etapas']['S11']=='S11_COMPRENSION_REGISTRADA' and not app['S11_complete']:
        info['objetivo_siguiente']='COMPLETAR_APLICACION_S11';info['actividad']=None
    if actual and actual.startswith('S12.'):
        if products['S12']['status']!='VALIDATED':
            if app['S11_complete']:info['objetivo_siguiente']='EJECUTAR_Y_VERIFICAR_S12_G05'
            info['actividad']=None
        elif info['actividad']:
            info['actividad']['visor']=dict(url='index.html#s12',pantalla='S12 · Reservas académico',
                accion='Carga S12. Consulta la clase candidata y el movimiento/OPEX asignados a un bloque; compara A y B en la tabla.',
                pregunta_desde_visor=info['actividad']['pregunta'])
    if info['comprension_registrada']:
        info['objetivo_siguiente']='ENTREGABLES_ACADEMICOS_LISTOS' if info['entrega_final_lista'] else (
            'COMPLETAR_APLICACION_S11' if not app['S11_complete'] else
            'COMPLETAR_APLICACION_S12' if not app['S12_complete'] else 'COMPLETAR_FICHA_E1' if not ficha['complete'] else 'VERIFICAR_PRODUCTOS_GRUPALES')
    if info['objetivo_siguiente'] in {'COMPLETAR_APLICACION_S11','COMPLETAR_APLICACION_S12'}:
        info['siguiente_observacion']=app.get('pending')
    return info


def deliver(alias,info):
    if not info['entrega_final_lista']:
        raise ValueError('Faltan comprensión, ficha E1, aplicación V3 o productos grupales verificados')
    folder=DATA/alias
    files=[Path(info['ficha_e1']['xlsx']),folder/'Progreso_Kai_G05_Teoria_V2.xlsx',Path(info['aplicacion_individual_v3']['xlsx'])]
    if not all(p.is_file() for p in files):raise ValueError('Falta un Excel individual; consulta su estado para regenerarlo')
    with closing(sqlite3.connect((folder/'teoria_v2.sqlite').as_uri()+'?mode=ro',uri=True)) as db:
        rows=db.execute("SELECT actividad,respuesta,criterio_observado FROM eventos_v2 WHERE estado='DEMOSTRADO' ORDER BY rowid").fetchall()
    report=f'# Evidencia individual G05 · {alias}\n\nComprensión registrada y 21 observaciones E1 + 26 de aplicación verificadas.\n\n'
    report+='Los archivos grupales se entregan separados. Generaciones: '+json.dumps({k:p.get('run_id') for k,p in info['productos_grupales'].items()})+'\n\n'
    report+='## Palabras registradas del alumno\n\n'
    for activity,response,criterion in rows:
        report+=f'### {activity}\n\n{response}\n\nCriterio observado por el tutor: {criterion}\n\n'
    report+='La valoración semántica corresponde al tutor. Este registro no acredita ensayo conversacional humano ni calificación oficial.\n'
    destination=Path(info['aplicacion_individual_v3']['xlsx']).parent
    md=destination/'Informe_Individual_G05.md';md.write_text(report,encoding='utf-8')
    target=destination/'Entregable_Individual_G05.zip'
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for p in [*files,md]:z.write(p,p.name)
    return str(target)


def process(request):
    if not isinstance(request,dict):raise ValueError('Se requiere una solicitud JSON')
    alias=request.get('alumno');theory.carpeta(alias)
    op=request.get('operacion')
    base=dict(route_id=theory.ROUTE_ID,route_version=theory.VERSION,alumno=alias)
    theory.DATA=DATA
    if op in {'estado_aplicacion','responder_aplicacion'}:
        current=theory.procesar(dict(base,operacion='estado'))
        return application.process(request,root=ROOT,data=DATA,comprehension=current)
    if op in {'estado_ficha_e1','responder_ficha_e1'}:
        e1.DATA=DATA
        translated=dict(request,operacion='estado' if op=='estado_ficha_e1' else 'responder',
                        ficha_id='G05-FICHA-INDIVIDUAL',version=1)
        return e1.procesar(translated)
    if op=='entregar_individual':
        current=decorate(theory.procesar(dict(base,operacion='estado')))
        return dict(ok=True,zip=deliver(alias,current),entrega_final_lista=True)
    if op not in theory.CAMPOS:raise ValueError('Operación del recorrido desconocida')
    payload={k:v for k,v in request.items() if k not in {'controller_version'}}|base
    if op=='iniciar_etapa' and request.get('etapa')=='S12':
        state=decorate(theory.procesar(dict(base,operacion='estado')))
        if not state['aplicacion_individual_v3']['S11_complete']:
            raise ValueError('Primero verifica las 13 observaciones de aplicación S11')
        if state['productos_grupales']['S11']['status']!='VALIDATED' or state['productos_grupales']['S12']['status']!='VALIDATED':
            raise ValueError('S12 requiere S11 validado y una corrida S12 verificada')
        # Un inicio histórico sigue identificado con su base; la aplicación V3
        # acredita separadamente el vínculo actual con G05.
        payload['base']=state['base_s12'] or 'G05_S11_VALIDADO'
    return decorate(theory.procesar(payload))


def main():
    if sys.argv[1:]!=['procesar-pendiente']:
        print('Uso: python kai/recorrido_g05.py procesar-pendiente',file=sys.stderr);return 2
    try:
        request=json.loads(REQUEST.read_text(encoding='utf-8'));result=process(request)
        REQUEST.unlink();print(json.dumps(result,ensure_ascii=True,allow_nan=False));return 0
    except (ValueError,OSError,KeyError,TypeError,sqlite3.Error,zipfile.BadZipFile) as exc:
        print(json.dumps(dict(ok=False,error=str(exc)),ensure_ascii=True));return 1


if __name__=='__main__':raise SystemExit(main())
