"""Ensayo automático del protocolo; no acredita conversación humana o semántica LLM."""
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'kai'))
import recorrido_g05 as control
import aplicacion_g05 as application


class RecorridoTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.data=Path(self.tmp.name)
        self.patches=[patch.object(control,'DATA',self.data),patch.object(control.theory,'DATA',self.data),
                      patch.object(control.e1,'DATA',self.data)]
        for p in self.patches:p.start()
        self.alias='qa_alumno_ficticio'

    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.tmp.cleanup()

    def call(self,op='estado',**kw):
        return control.process(dict(alumno=self.alias,operacion=op,**kw))

    def evidence(self,activity):
        return self.call('registrar',actividad=activity,estado='DEMOSTRADO',
            respuesta='Evidencia sintética de integración sobre '+activity+'; no acredita comprensión humana.',
            criterio_observado='Fixture automática, solo control de secuencia.',tipo_evidencia='RAZONAMIENTO_PROPIO')

    def complete_stage(self,stage):
        for a in control.theory.ACTIVIDADES:
            if a['etapa']==stage:self.evidence(a['id'])

    def fill_application(self,stage):
        fields,_,_=application.catalog()
        for f in fields:
            if f['stage']!=stage:continue
            value=round(f['expected'],f['places']) if f['places'] else int(f['expected'])
            r=self.call('responder_aplicacion',campo=f['id'],respuesta_literal=f'Observo {value} {f["unit"]}',
                        valor_propuesto=value,unidad=f['unit'])
            self.assertTrue(r['validado'],f['id']);self.assertTrue(r['excel_actualizado'])
        return r

    def test_full_protocol_error_no_se_checkpoint_resume_and_delivery(self):
        s=self.call();self.assertEqual(s['actividad_actual'],'E1.01')
        r=self.call('registrar',actividad='E1.01',estado='REQUIERE_REFUERZO',
            respuesta='No sé',criterio_observado='Requiere una explicación de exploración',tipo_evidencia='ERROR_O_DUDA')
        self.assertEqual(r['actividad_actual'],'E1.01')
        self.call('checkpoint',actividad='E1.01',comprension_parcial='',pregunta_respondida='¿Qué sabes de exploración?',
            pregunta_pendiente='¿Por qué un sondaje no observa todo el terreno?',dificultad_pendiente='No diferencia punto y entorno',
            proxima_accion='REFORZAR',evidencia_estudiante='No sé')
        resumed=self.call();self.assertEqual(resumed['checkpoint']['pregunta_pendiente'],'¿Por qué un sondaje no observa todo el terreno?')
        self.complete_stage('E1');closed=self.call()
        self.assertEqual(closed['objetivo_siguiente'],'INICIAR_S11');self.assertIsNone(closed['actividad'])
        with self.assertRaises(ValueError):self.evidence('S11.0.NN')
        self.call('iniciar_etapa',etapa='S11');self.complete_stage('S11')
        self.assertEqual(self.call()['objetivo_siguiente'],'COMPLETAR_APLICACION_S11')
        with self.assertRaisesRegex(ValueError,'13 observaciones'):self.call('iniciar_etapa',etapa='S12')
        initial=self.call('estado_aplicacion');self.assertEqual(initial['answered'],0)
        f=initial['pending'];bad=self.call('responder_aplicacion',campo=f['id'],respuesta_literal='Veo 999 bloques',valor_propuesto=999,unidad=f['unit'])
        self.assertFalse(bad['validado']);self.assertEqual(bad['answered'],0)
        expected=application.catalog()[0][0]['expected']
        inconsistent=self.call('responder_aplicacion',campo=f['id'],respuesta_literal='Veo 999 bloques',valor_propuesto=expected,unidad=f['unit'])
        self.assertFalse(inconsistent['validado'])
        wrongunit=self.call('responder_aplicacion',campo=f['id'],respuesta_literal=f'Veo {expected} toneladas',valor_propuesto=expected,unidad='t')
        self.assertFalse(wrongunit['validado']);self.assertEqual(wrongunit['answered'],0)
        self.fill_application('S11')
        self.assertEqual(self.call()['objetivo_siguiente'],'INICIAR_S12')
        self.call('iniciar_etapa',etapa='S12');self.assertEqual(self.call()['base_s12'],'G05_S11_VALIDADO')
        self.complete_stage('S12');self.assertEqual(self.call()['objetivo_siguiente'],'COMPLETAR_APLICACION_S12')
        self.fill_application('S12');self.assertEqual(self.call()['objetivo_siguiente'],'COMPLETAR_FICHA_E1')
        # Reusar el flujo original de E1, con el corte preliminar preservado.
        catalog,summary=control.e1._fuentes()
        for f in catalog['campos']:
            value=control.e1._source_value(summary,f)
            proposed=' x '.join(map(str,value)) if f['tipo']=='dimensiones' else 'No' if f['tipo']=='booleano_no' else value
            response=self.call('responder_ficha_e1',campo=f['id'],respuesta_literal=f'Leo {proposed}',valor_propuesto=proposed)
            self.assertTrue(response['validado'])
        self.assertTrue(self.call()['entrega_final_lista'])
        delivery=self.call('entregar_individual');self.assertTrue(Path(delivery['zip']).is_file())
        with zipfile.ZipFile(delivery['zip']) as z:
            self.assertEqual(len(z.namelist()),4)
            self.assertTrue(all('block_model' not in n for n in z.namelist()))
        with zipfile.ZipFile(self.call()['aplicacion_individual_v3']['xlsx']) as z:
            xml=ET.fromstring(z.read('xl/worksheets/sheet1.xml'));ns='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
            cell=xml.find(f'.//{ns}c[@r="C7"]')
            self.assertIsNone(cell.get('t'));self.assertEqual(float(cell.find(f'{ns}v').text),expected)
            self.assertEqual(sum('VALIDADO' in ''.join(c.itertext()) for c in xml.findall(f'.//{ns}c')),26)
        other=control.process(dict(alumno='otro_alias',operacion='estado'))
        self.assertFalse(other['entrega_final_lista']);self.assertEqual(other['aplicacion_individual_v3']['answered'],0)
        with closing(sqlite3.connect(self.data/self.alias/'aplicacion_v3'/self.call()['aplicacion_individual_v3']['s11_run_id']/'aplicacion_v3.sqlite')) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM answers').fetchone()[0],26)
            self.assertEqual(db.execute('SELECT count(*) FROM attempts WHERE accepted=0').fetchone()[0],3)

    def test_originals_preserved_and_numeric_cells_typed(self):
        before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'kai').glob('PLANTILLA*.xlsx')}
        state=self.call('estado_aplicacion')
        with zipfile.ZipFile(state['xlsx']) as z:
            self.assertIsNone(z.testzip())
            xml=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
            ns='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
            c=xml.find(f'.//{ns}c[@r="C7"]')
            self.assertTrue(c is None or c.find(f'{ns}v') is None)
        self.assertEqual(before,{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'kai').glob('PLANTILLA*.xlsx')})

    def test_excel_lock_keeps_answer_in_sqlite(self):
        self.complete_stage('E1');self.call('iniciar_etapa',etapa='S11');self.complete_stage('S11')
        field=application.catalog()[0][0]
        with patch.object(application,'export',side_effect=PermissionError('fixture bloqueo Excel')):
            r=self.call('responder_aplicacion',campo=field['id'],respuesta_literal=f"Observo {field['expected']} bloques",valor_propuesto=field['expected'],unidad='bloques')
        self.assertTrue(r['validado']);self.assertFalse(r['excel_actualizado']);self.assertEqual(r['answered'],1)
        retry=self.call('estado_aplicacion');self.assertEqual(retry['answered'],1);self.assertTrue(retry['excel_actualizado'])

    def test_historical_pt01_basis_and_approvals_are_preserved(self):
        self.complete_stage('E1');self.call('iniciar_etapa',etapa='S11');self.complete_stage('S11')
        base=dict(route_id=control.theory.ROUTE_ID,route_version=control.theory.VERSION,alumno=self.alias)
        control.theory.procesar(dict(base,operacion='iniciar_etapa',etapa='S12',base='EJEMPLO_CONCEPTUAL_PT01'))
        for a in control.theory.ACTIVIDADES:
            if a['etapa']=='S12':
                control.theory.procesar(dict(base,operacion='registrar',actividad=a['id'],estado='DEMOSTRADO',
                    respuesta='Fixture histórica de comprensión sobre '+a['id'],criterio_observado='Prueba de preservación de historial',tipo_evidencia='RAZONAMIENTO_PROPIO'))
        path=self.data/self.alias/'teoria_v2.sqlite'
        with closing(sqlite3.connect(path)) as db:before=db.execute('SELECT id,actividad,respuesta FROM eventos_v2 ORDER BY rowid').fetchall()
        self.assertEqual(self.call()['objetivo_siguiente'],'COMPLETAR_APLICACION_S11')
        self.fill_application('S11');self.fill_application('S12')
        self.assertEqual(self.call()['base_s12'],'EJEMPLO_CONCEPTUAL_PT01')
        with closing(sqlite3.connect(path)) as db:after=db.execute('SELECT id,actividad,respuesta FROM eventos_v2 ORDER BY rowid').fetchall()
        self.assertEqual(before,after)

    @unittest.skipUnless(os.name=='nt','Bloqueo exclusivo de archivo requiere Windows')
    def test_real_windows_excel_lock_keeps_application_and_recovers(self):
        self.complete_stage('E1');self.call('iniciar_etapa',etapa='S11');self.complete_stage('S11')
        state=self.call('estado_aplicacion');field=application.catalog()[0][0]
        helper=ROOT/'tests/fixtures/windows_lock_xlsx.py'
        proc=subprocess.Popen([sys.executable,str(helper),state['xlsx']],stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8')
        try:
            self.assertTrue(proc.stdout.readline().startswith('LOCKED '))
            result=self.call('responder_aplicacion',campo=field['id'],
                respuesta_literal=f"Observo {field['expected']} bloques",valor_propuesto=field['expected'],unidad='bloques')
            self.assertTrue(result['validado']);self.assertFalse(result['excel_actualizado'])
            self.assertEqual(result['answered'],1)
        finally:
            proc.communicate(input='\n',timeout=10)
        resumed=self.call('estado_aplicacion')
        self.assertEqual(resumed['answered'],1);self.assertTrue(resumed['excel_actualizado'])
        database=Path(resumed['xlsx']).with_name('aplicacion_v3.sqlite')
        moved=database.with_suffix('.closed-check')
        database.replace(moved);moved.replace(database)  # Sin handles retenidos en Windows.


if __name__=='__main__':unittest.main()
