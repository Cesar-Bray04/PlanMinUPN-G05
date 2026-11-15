import hashlib
from contextlib import closing
from html.parser import HTMLParser
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'kai'))
spec = importlib.util.spec_from_file_location('teoria_v2', ROOT / 'kai/registro_v2.py')
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)


class TeoriaV2Test(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_data = v2.DATA
        v2.DATA = Path(self.tmp.name)

    def tearDown(self):
        v2.DATA = self.old_data
        self.tmp.cleanup()

    def call(self, op='estado', alias='qa_teoria', **kwargs):
        return v2.procesar({'operacion': op, 'alumno': alias, 'route_id': v2.ROUTE_ID,
                            'route_version': v2.VERSION, **kwargs})

    def evidence(self, activity):
        return self.call('registrar', actividad=activity, estado='DEMOSTRADO',
                         respuesta='Respuesta sintética de prueba para ' + activity,
                         criterio_observado='Valoración sintética; no demuestra aprendizaje humano',
                         tipo_evidencia='RAZONAMIENTO_PROPIO')

    def complete_stage(self, stage):
        for a in v2.ACTIVIDADES:
            if a['etapa'] == stage:
                self.evidence(a['id'])

    def test_inicio_y_excel_versionado(self):
        r = self.call()
        self.assertEqual(r['actividad_actual'], 'E1.01')
        self.assertFalse(r['evaluacion_formal'])
        self.assertIn('NO_VERIFICADO', r['productos_grupales']['S11'])
        self.assertFalse((v2.DATA / 'qa_teoria/Progreso_Kai_G05.xlsx').exists())
        with zipfile.ZipFile(r['xlsx']) as z:
            self.assertIsNone(z.testzip())
            for path in z.namelist():
                if path.endswith('.xml'):
                    ET.fromstring(z.read(path))
            text = z.read('xl/worksheets/sheet1.xml').decode()
            self.assertIn('KAI-G05-TEORIA', text)
            self.assertIn('E1.08', text)

    def test_visor_guiado_en_estado_y_enlaces_reales(self):
        class Pantallas(HTMLParser):
            def __init__(self):
                super().__init__()
                self.ids = set()

            def handle_starttag(self, tag, attrs):
                if tag == 'section':
                    self.ids.update(value for key, value in attrs if key == 'id')

        pantallas = Pantallas()
        pantallas.feed((ROOT / 'index.html').read_text(encoding='utf-8'))
        guiadas = {a['id']: a['visor'] for a in v2.ACTIVIDADES if 'visor' in a}
        self.assertTrue({f'E1.{i:02d}' for i in range(1, 9)} <= guiadas.keys())
        self.assertIn('S11.0.DECISION', guiadas)
        self.assertIn('S12.1', guiadas)
        for actividad, visita in guiadas.items():
            self.assertEqual(set(visita), {'url', 'pantalla', 'accion', 'pregunta_desde_visor'})
            ruta, ancla = visita['url'].split('#', 1)
            self.assertEqual(ruta, 'index.html', actividad)
            self.assertIn(ancla, pantallas.ids, actividad)
            self.assertTrue(visita['accion'].strip(), actividad)
            self.assertEqual(visita['pregunta_desde_visor'].count('?'), 1, actividad)
        actual = self.call()['actividad']
        self.assertEqual(actual['visor'], guiadas['E1.01'])

    def test_plantilla_individual_se_llena_sin_inventar_observacion(self):
        template = ROOT / 'kai/PLANTILLA_Individual_Kai_G05_V2.xlsx'
        with zipfile.ZipFile(template) as z:
            self.assertIsNone(z.testzip())
            sheet = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
            ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
            self.assertEqual(len(sheet.findall(f'.//{ns}row')), 31)
        previo = self.call()
        with zipfile.ZipFile(previo['xlsx']) as z:
            xml = z.read('xl/worksheets/sheet5.xml').decode('utf-8')
        self.assertEqual(xml.count('<row '), 31)
        self.assertIn('index.html#proyecto', xml)
        self.assertNotIn('Veo varias trayectorias', xml)
        respuesta = 'Veo trayectorias en diferentes lugares y revisaría más sondajes antes de extender la zona.'
        r = self.call('registrar', actividad='E1.01', estado='DEMOSTRADO', respuesta=respuesta,
                      criterio_observado='Relaciona observación localizada y cobertura',
                      tipo_evidencia='RAZONAMIENTO_PROPIO',
                      observacion_visor='Veo trayectorias en diferentes lugares')
        with zipfile.ZipFile(r['xlsx']) as z:
            xml = z.read('xl/worksheets/sheet5.xml').decode('utf-8')
        self.assertIn('Veo trayectorias en diferentes lugares', xml)
        self.assertIn(respuesta, xml)
        self.assertIn('DEMOSTRADO', xml)
        self.assertIn('qa_teoria', xml)
        with zipfile.ZipFile(self.call(alias='otra_persona')['xlsx']) as z:
            otro = z.read('xl/worksheets/sheet5.xml').decode('utf-8')
        self.assertNotIn('Veo trayectorias en diferentes lugares', otro)
        self.assertIn('otra_persona', otro)
        for i in range(2, 9):
            self.evidence(f'E1.{i:02d}')
        self.call('iniciar_etapa', etapa='S11')
        with self.assertRaisesRegex(ValueError, 'no tiene una visita'):
            self.call('registrar', actividad='S11.0.NN', estado='EN_DESARROLLO',
                      respuesta='Vi algo', criterio_observado='Duda',
                      tipo_evidencia='ERROR_O_DUDA', observacion_visor='Vi algo')

    def test_migracion_registro_v2_anterior_preserva_eventos(self):
        folder = v2.DATA / 'qa_teoria'
        folder.mkdir()
        with closing(sqlite3.connect(folder / 'teoria_v2.sqlite')) as conn:
            conn.execute('''CREATE TABLE eventos_v2 (
                id TEXT PRIMARY KEY, fecha TEXT NOT NULL, route_id TEXT NOT NULL,
                route_version INTEGER NOT NULL, etapa TEXT NOT NULL, actividad TEXT NOT NULL,
                estado TEXT NOT NULL, respuesta TEXT NOT NULL, criterio_observado TEXT NOT NULL,
                tipo_evidencia TEXT NOT NULL, huella TEXT UNIQUE NOT NULL)''')
            conn.execute('INSERT INTO eventos_v2 VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                         ('antes', '2026-11-13T00:00:00+00:00', v2.ROUTE_ID, v2.VERSION,
                          'E1', 'E1.01', 'DEMOSTRADO', 'Respuesta anterior',
                          'Valoración anterior', 'RAZONAMIENTO_PROPIO', 'huella-anterior'))
            conn.commit()
        r = self.call()
        self.assertEqual(r['actividad_actual'], 'E1.02')
        with closing(sqlite3.connect(folder / 'teoria_v2.sqlite')) as conn:
            fila = conn.execute('SELECT id,respuesta,observacion_visor FROM eventos_v2').fetchone()
        self.assertEqual(fila, ('antes', 'Respuesta anterior', ''))
        with zipfile.ZipFile(r['xlsx']) as z:
            self.assertIn('Respuesta anterior', z.read('xl/worksheets/sheet5.xml').decode('utf-8'))

    def test_ocho_competencias_cierran_e1_sin_arrancar_s11(self):
        self.complete_stage('E1')
        r = self.call()
        self.assertEqual(r['etapas']['S11'], 'S11_NO_INICIADA')
        self.assertEqual(r['objetivo_siguiente'], 'INICIAR_S11')
        self.assertIsNone(r['actividad'])
        with self.assertRaisesRegex(ValueError, 'iniciar la nueva etapa'):
            self.evidence('S11.0.NN')
        self.assertEqual(self.call('iniciar_etapa', etapa='S11')['actividad']['id'], 'S11.0.NN')

    def test_no_saltar_etapas_o_actividades(self):
        with self.assertRaisesRegex(ValueError, 'etapa anterior'):
            self.call('iniciar_etapa', etapa='S11')
        with self.assertRaisesRegex(ValueError, 'no se saltan'):
            self.evidence('E1.08')

    def test_reintento_no_duplica_despues_de_avanzar(self):
        self.evidence('E1.01')
        r = self.evidence('E1.01')
        self.assertTrue(r['duplicado'])
        self.assertEqual(r['eventos'], 1)
        self.assertEqual(r['actividad_actual'], 'E1.02')

    def test_error_y_reconocimiento_no_avanzan(self):
        self.call('registrar', actividad='E1.01', estado='REQUIERE_REFUERZO', respuesta='No sé',
                  criterio_observado='Falta relacionar observación y representación', tipo_evidencia='ERROR_O_DUDA')
        self.assertEqual(self.call()['actividad_actual'], 'E1.01')
        for answer, kind in [('sí', 'RAZONAMIENTO_PROPIO'), ('Repetición identificada', 'RECONOCIMIENTO')]:
            with self.assertRaisesRegex(ValueError, 'no acredita'):
                self.call('registrar', actividad='E1.01', estado='DEMOSTRADO', respuesta=answer,
                          criterio_observado='Reconocimiento', tipo_evidencia=kind)

    def checkpoint(self, pending='¿Qué falta para representar la zona?'):
        return self.call('checkpoint', actividad='E1.01', comprension_parcial='Reconoce un dato localizado',
                         pregunta_respondida='¿Qué representa la muestra?', pregunta_pendiente=pending,
                         dificultad_pendiente='Generaliza una muestra', proxima_accion='REFORZAR',
                         evidencia_estudiante='La muestra corresponde al lugar donde la tomamos')

    def test_checkpoint_recupera_brecha_sin_cerrar(self):
        self.checkpoint()
        r = self.call()
        self.assertEqual(r['eventos'], 0)
        self.assertEqual(r['actividad_actual'], 'E1.01')
        self.assertEqual(r['checkpoint']['pregunta_pendiente'], '¿Qué falta para representar la zona?')
        self.assertEqual(r['estados']['E1.01'], 'EN_DESARROLLO')

    def test_checkpoint_no_repite_pregunta_respondida(self):
        with self.assertRaisesRegex(ValueError, 'No repetir'):
            self.checkpoint('¿Qué representa la muestra?')

    def test_recorrido_total_teorico_no_acredita_producto(self):
        self.complete_stage('E1')
        self.call('iniciar_etapa', etapa='S11')
        self.complete_stage('S11')
        self.assertEqual(self.call()['objetivo_siguiente'], 'INICIAR_S12')
        with self.assertRaisesRegex(ValueError, 'no acredita un producto'):
            self.call('iniciar_etapa', etapa='S12', base='RESULTADO_GRUPAL')
        self.call('iniciar_etapa', etapa='S12', base='EJEMPLO_CONCEPTUAL_PT01')
        self.complete_stage('S12')
        r = self.call()
        self.assertTrue(r['comprension_registrada'])
        self.assertEqual(r['objetivo_siguiente'], 'RECORRIDO_TEORICO_REGISTRADO')
        self.assertEqual(r['eventos'], 30)
        self.assertFalse(r['recursos_reservas_profesionales'])
        self.assertIn('NO_VERIFICADO', r['productos_grupales']['S12'])

    def test_v1_no_cambia_sqlite_ni_excel(self):
        folder = v2.DATA / 'qa_teoria'
        folder.mkdir()
        old = folder / 'events.sqlite'
        with closing(sqlite3.connect(old)) as conn:
            conn.executescript("CREATE TABLE perfil(clave TEXT,valor TEXT);"
                               "INSERT INTO perfil VALUES('nombre_kai','Juancho');"
                               "CREATE TABLE eventos(paso INTEGER,estado TEXT);"
                               "INSERT INTO eventos VALUES(7,'DEMOSTRADO');")
        old_excel = folder / 'Progreso_Kai_G05.xlsx'
        old_excel.write_bytes(b'Excel anterior ficticio')
        before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in (old, old_excel)]
        r = self.call()
        self.evidence('E1.01')
        self.assertEqual(before, [hashlib.sha256(p.read_bytes()).hexdigest() for p in (old, old_excel)])
        self.assertEqual(r['perfil']['nombre_kai'], 'Juancho')
        self.assertEqual(r['actividad_actual'], 'E1.01')
        self.assertFalse(r['historial_v1']['equivalencias_automaticas'])

    def test_alias_y_version_aislados(self):
        self.evidence('E1.01')
        self.assertEqual(self.call(alias='otra_persona')['actividad_actual'], 'E1.01')
        with self.assertRaisesRegex(ValueError, 'Alias inválido'):
            self.call(alias='../afuera')
        with self.assertRaisesRegex(ValueError, 'identidad de ruta'):
            v2.procesar({'operacion': 'estado', 'alumno': 'qa_teoria', 'route_id': v2.ROUTE_ID, 'route_version': 1})

    def test_memoria_social_con_consentimiento(self):
        with self.assertRaisesRegex(ValueError, 'consentimiento'):
            self.call('perfil', nombre='Alumno')
        self.assertEqual(self.call('perfil', consentimiento=True, nombre='Alumno', kai='Juancho')['perfil']['nombre_kai'], 'Juancho')

    def test_texto_hostil_no_es_formula_o_codigo(self):
        answer = '=SUM(9,9) $() `echo` "ñ" <&> es un dato sintético'
        r = self.call('registrar', actividad='E1.01', estado='DEMOSTRADO', respuesta=answer,
                      criterio_observado='Transporte de texto', tipo_evidencia='RAZONAMIENTO_PROPIO')
        with closing(sqlite3.connect(v2.DATA / 'qa_teoria/teoria_v2.sqlite')) as conn:
            self.assertEqual(conn.execute('SELECT respuesta FROM eventos_v2').fetchone()[0], answer)
        with zipfile.ZipFile(r['xlsx']) as z:
            xml = z.read('xl/worksheets/sheet2.xml').decode()
        self.assertIn('=SUM(9,9)', xml)
        self.assertNotIn('<f>', xml)
        self.assertIn('&lt;&amp;&gt;', xml)

    def test_recuperacion_tras_excel_bloqueado(self):
        with patch.object(v2.legado, 'escribir_xlsx', side_effect=PermissionError('Excel bloqueado')):
            with self.assertRaises(PermissionError):
                self.evidence('E1.01')
        r = self.evidence('E1.01')
        self.assertTrue(r['duplicado'])
        self.assertEqual(r['eventos'], 1)
        self.assertTrue(Path(r['xlsx']).is_file())

    def test_integridad_y_campos_desconocidos(self):
        self.assertEqual(self.call('verificar')['integridad_sqlite'], 'ok')
        with self.assertRaisesRegex(ValueError, 'Campo no permitido'):
            self.call(ruta='otra_version.json')
        with self.assertRaisesRegex(ValueError, 'duplicado'):
            json.loads('{"alumno":"uno","alumno":"dos"}', object_pairs_hook=v2.objeto_sin_duplicados)
        with self.assertRaisesRegex(ValueError, 'Operación'):
            self.call(op=[])
        with self.assertRaisesRegex(ValueError, 'Actividad inexistente'):
            self.call('registrar', actividad=[])

    def test_contenidos_y_parametros(self):
        self.assertEqual(len(v2.ACTIVIDADES), 30)
        self.assertEqual(len(v2.RUTA['actividades']), 8)
        for item in v2.ACTIVIDADES:
            self.assertEqual(item['pregunta'].count('¿'), 1, item['id'])
            self.assertTrue(item['criterio'], item['id'])
        p = json.loads((ROOT / 'kai/parametros_pt01_v2.json').read_text(encoding='utf-8'))
        self.assertEqual(p['geometria_g05_m'], [50, 50, 10])
        self.assertEqual(p['S12']['parameters']['ore_cutoff_cu_pct'], 0.5)
        self.assertEqual(p['aplicacion_g05'], 'CONSULTAR_MANIFIESTO_DINAMICO')

    def test_cli_nuevo_proceso_y_fallo_conserva_solicitud(self):
        isolated = Path(self.tmp.name) / 'entorno_cli'
        shutil.copytree(ROOT / 'kai', isolated / 'kai', ignore=shutil.ignore_patterns('__pycache__'))
        pending = isolated / '.kai_solicitud_g05_v2.json'
        env = {**os.environ, 'PYTHONIOENCODING': 'utf-8'}

        def run(payload, expected=0):
            pending.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
            result = subprocess.run([sys.executable, 'kai/registro_v2.py', 'procesar-pendiente'],
                                    cwd=isolated, capture_output=True, text=True, encoding='utf-8', env=env)
            self.assertEqual(result.returncode, expected, result.stderr)
            return json.loads(result.stdout if expected == 0 else result.stderr)

        common = {'alumno': 'qa_cli', 'route_id': v2.ROUTE_ID, 'route_version': 2}
        run({**common, 'operacion': 'registrar', 'actividad': 'E1.01', 'estado': 'DEMOSTRADO',
             'respuesta': 'Una muestra observa un lugar y no representa toda la zona.',
             'criterio_observado': 'Evidencia sintética para integración CLI', 'tipo_evidencia': 'RAZONAMIENTO_PROPIO'})
        r = run({**common, 'operacion': 'estado'})
        self.assertEqual(r['actividad_actual'], 'E1.02')
        self.assertFalse(pending.exists())
        r = run({**common, 'operacion': 'registrar', 'actividad': 'S12.6', 'estado': 'DEMOSTRADO',
                 'respuesta': 'Intento sintético de saltar el recorrido', 'criterio_observado': 'No válido',
                 'tipo_evidencia': 'RAZONAMIENTO_PROPIO'}, expected=2)
        self.assertTrue(r['solicitud_conservada'])
        self.assertTrue(pending.exists())
        self.assertEqual(run({**common, 'operacion': 'estado'})['eventos'], 1)


if __name__ == '__main__':
    unittest.main()
