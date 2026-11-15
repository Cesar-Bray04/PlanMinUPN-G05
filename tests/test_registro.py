import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import uuid
import zipfile
import shutil

HERE=Path(__file__).resolve().parent.parent
SCRIPT=HERE/'kai'/'registro.py'
ROOT=HERE/'.kai_local'
PENDIENTE=HERE/'.kai_solicitud_g05.json'

class RegistroTest(unittest.TestCase):
    def setUp(self):
        self.alias='qa_'+uuid.uuid4().hex[:10]
        self.other='qa_'+uuid.uuid4().hex[:10]
        self.created=[self.alias,self.other]

    def tearDown(self):
        for a in self.created:
            shutil.rmtree(ROOT/a,ignore_errors=True)
        PENDIENTE.unlink(missing_ok=True)

    def cli(self,cmd,alias=None,expect=0,**kwargs):
        parts=[sys.executable,str(SCRIPT),cmd]
        if cmd!='procesar-pendiente':
            parts+=['--alumno',alias or self.alias]
        for k,v in kwargs.items():
            parts+=['--'+k.replace('_','-'),str(v)]
        r=subprocess.run(parts,capture_output=True,text=True,cwd=HERE)
        self.assertEqual(r.returncode,expect,msg=r.stdout+r.stderr)
        return json.loads(r.stdout if expect==0 else r.stderr)

    def registro(self,paso,estado='DEMOSTRADO',respuesta=None,alias=None):
        return self.cli('registrar',alias=alias,paso=paso,estado=estado,respuesta=respuesta or f'La respuesta del estudiante demuestra comprensión de la etapa {paso} en Santa Elena')

    def test_estado_inicial_y_excel(self):
        r=self.cli('estado')
        self.assertEqual(r['siguiente_paso'],1)
        self.assertEqual(r['eventos'],0)
        self.assertTrue(Path(r['xlsx']).exists())
        with zipfile.ZipFile(r['xlsx']) as z:
            self.assertIsNone(z.testzip())
            self.assertIn('xl/worksheets/sheet2.xml',z.namelist())

    def test_perfil_optional(self):
        r=self.cli('perfil',nombre='Luis',kai='Mi Kai')
        self.assertEqual(r['perfil']['nombre_elegido'],'Luis')
        self.assertEqual(self.cli('estado')['perfil']['nombre_kai'],'Mi Kai')

    def test_avance_y_persistencia(self):
        r=self.registro(1)
        self.assertEqual(r['siguiente_paso'],2)
        self.assertEqual(self.cli('estado')['siguiente_paso'],2)
        self.assertTrue(self.cli('verificar')['ok'])

    def test_error_no_avanza(self):
        self.registro(1,'REQUIERE_REFUERZO','Confundí el modelo preliminar con un pit final')
        self.assertEqual(self.cli('estado')['siguiente_paso'],1)
        self.registro(1)
        self.assertEqual(self.cli('estado')['siguiente_paso'],2)

    def test_no_saltar_pasos(self):
        r=self.cli('registrar',expect=2,paso=4,estado='DEMOSTRADO',respuesta='Quiero saltarme las etapas del ejercicio')
        self.assertIn('siguiente paso',r['error'])

    def test_rechaza_aceptacion_no_demostrada(self):
        r=self.cli('registrar',expect=2,paso=1,estado='DEMOSTRADO',respuesta='sí')
        self.assertIn('no demuestra',r['error'])

    def test_reintento_idempotente_tras_avance(self):
        respuesta='Tenemos un modelo preliminar de Santa Elena, no un plan de extracción.'
        self.registro(1,respuesta=respuesta)
        r=self.registro(1,respuesta=respuesta)
        self.assertTrue(r['duplicado'])
        self.assertEqual(r['siguiente_paso'],2)
        self.assertEqual(self.cli('estado')['eventos'],1)

    def test_no_mezcla_aliados(self):
        self.registro(1,alias=self.alias)
        self.assertEqual(self.cli('estado',alias=self.other)['siguiente_paso'],1)
        self.assertEqual(self.cli('estado')['siguiente_paso'],2)

    def test_completa_siete_etapas(self):
        for i in range(1,8):
            self.registro(i)
        self.assertIsNone(self.cli('estado')['siguiente_paso'])
        self.assertEqual(self.cli('estado')['eventos'],7)

    def test_inyeccion_excel_es_texto(self):
        self.registro(1,respuesta='=SUM(9,9) aunque yo entiendo que esto es un modelo preliminar')
        path=ROOT/self.alias/'Progreso_Kai_G05.xlsx'
        with zipfile.ZipFile(path) as z:
            doc=z.read('xl/worksheets/sheet2.xml').decode()
        self.assertIn('=SUM(9,9)',doc)
        self.assertNotIn('<f>',doc)

    def test_alias_invalido(self):
        r=self.cli('estado',alias='../hack',expect=2)
        self.assertIn('Alias inválido',r['error'])

    def test_solicitud_fija_con_texto_hostil_es_dato(self):
        marcador=HERE/'.kai_local'/('qa_shell_marker_'+uuid.uuid4().hex)
        respuesta=(f'El modelo es preliminar; no hay pit. "; $(New-Item -ItemType File '
                   f'-Path {marcador.as_posix()}) ; `echo` =SUM(9,9) ñ <&>')
        PENDIENTE.write_text(json.dumps({
            'operacion':'registrar','alumno':self.alias,'paso':1,'estado':'DEMOSTRADO',
            'respuesta':respuesta,'observacion':'Refuerzo: comillas " y $() son texto'
        },ensure_ascii=False),encoding='utf-8')
        r=self.cli('procesar-pendiente')
        self.assertEqual(r['siguiente_paso'],2)
        self.assertFalse(PENDIENTE.exists())
        self.assertFalse(marcador.exists())
        with sqlite3.connect(ROOT/self.alias/'events.sqlite') as conn:
            self.assertEqual(conn.execute('SELECT respuesta FROM eventos').fetchone()[0],respuesta)
        with zipfile.ZipFile(ROOT/self.alias/'Progreso_Kai_G05.xlsx') as z:
            doc=z.read('xl/worksheets/sheet2.xml').decode('utf-8')
        self.assertIn('$(New-Item',doc)
        self.assertNotIn('<f>',doc)

    def test_solicitud_fija_recupera_y_separa_alias(self):
        for alias in (self.alias,self.other):
            PENDIENTE.write_text(json.dumps({'operacion':'estado','alumno':alias}),encoding='utf-8')
            self.assertEqual(self.cli('procesar-pendiente')['siguiente_paso'],1)
        self.registro(1,alias=self.alias)
        PENDIENTE.write_text(json.dumps({'operacion':'estado','alumno':self.alias}),encoding='utf-8')
        self.assertEqual(self.cli('procesar-pendiente')['siguiente_paso'],2)
        PENDIENTE.write_text(json.dumps({'operacion':'estado','alumno':self.other}),encoding='utf-8')
        self.assertEqual(self.cli('procesar-pendiente')['siguiente_paso'],1)

    def test_solicitud_fija_perfil_consentido_y_verificacion(self):
        nombre='Lu"$()is'
        PENDIENTE.write_text(json.dumps({'operacion':'perfil','alumno':self.alias,
                                         'nombre':nombre,'kai':'Kai de prueba'},
                                        ensure_ascii=False),encoding='utf-8')
        self.assertEqual(self.cli('procesar-pendiente')['perfil']['nombre_elegido'],nombre)
        PENDIENTE.write_text(json.dumps({'operacion':'verificar','alumno':self.alias}),encoding='utf-8')
        self.assertTrue(self.cli('procesar-pendiente')['ok'])

    def test_solicitud_malformada_no_se_ejecuta(self):
        PENDIENTE.write_text('{"operacion":"estado","alumno":"'+self.alias+'","alumno":"otro"}',encoding='utf-8')
        self.assertIn('duplicado',self.cli('procesar-pendiente',expect=2)['error'])
        self.assertTrue(PENDIENTE.exists())
        self.assertFalse((ROOT/self.alias).exists())

if __name__=='__main__': unittest.main()
