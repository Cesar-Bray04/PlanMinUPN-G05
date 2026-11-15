import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import unittest
import uuid
import xml.etree.ElementTree as ET
import zipfile

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / 'kai' / 'registro.py'
PENDIENTE = RAIZ / '.kai_solicitud_g05.json'
DATA = RAIZ / '.kai_local'


class CheckpointTest(unittest.TestCase):
    def setUp(self):
        self.alias = 'qa52_' + uuid.uuid4().hex[:12]
        self.otro = 'qa52_' + uuid.uuid4().hex[:12]

    def tearDown(self):
        PENDIENTE.unlink(missing_ok=True)
        for alias in (self.alias, self.otro):
            shutil.rmtree(DATA / alias, ignore_errors=True)

    def cli(self, *args, ok=True):
        p = subprocess.run([sys.executable, str(SCRIPT), *args], cwd=RAIZ,
                           text=True, encoding='utf-8', capture_output=True,
                           env={**os.environ, 'PYTHONIOENCODING':'utf-8'})
        self.assertEqual(p.returncode, 0 if ok else 2, p.stdout + p.stderr)
        return json.loads(p.stdout if ok else p.stderr)

    def solicitar(self, datos, ok=True):
        PENDIENTE.write_text(json.dumps(datos, ensure_ascii=False), encoding='utf-8')
        return self.cli('procesar-pendiente', ok=ok)

    def cuatro_pasos(self):
        self.solicitar({'operacion':'perfil','alumno':self.alias,
                        'nombre':'Luis','kai':'Juancho'})
        for paso in range(1, 5):
            self.cli('registrar', '--alumno', self.alias, '--paso', str(paso),
                     '--estado', 'DEMOSTRADO', '--respuesta',
                     f'Entiendo con palabras propias el criterio académico del paso {paso}.')

    def parcial(self, alias=None, **cambios):
        datos = {'operacion':'checkpoint','alumno':alias or self.alias,'paso':5,
                 'concepto':'Topografía y bloque PARTIAL',
                 'comprension_parcial':'PARTIAL no cuantifica por sí solo el volumen de roca.',
                 'pregunta_respondida':'¿PARTIAL entrega automáticamente volumen de roca?',
                 'pregunta_pendiente':'¿Qué relación con la superficie representa PARTIAL?',
                 'dificultad_pendiente':'Falta explicar el significado geométrico de PARTIAL.',
                 'proxima_accion':'PREGUNTAR_PENDIENTE',
                 'evidencia_estudiante':'PARTIAL no da directamente el volumen de roca.'}
        datos.update(cambios)
        return datos

    def conteos(self):
        with sqlite3.connect(DATA / self.alias / 'events.sqlite') as c:
            return (c.execute('SELECT count(*) FROM eventos').fetchone()[0],
                    c.execute('SELECT count(*) FROM checkpoints').fetchone()[0])

    def test_continuidad_real_entre_procesos_y_excel_compatible(self):
        self.cuatro_pasos()
        original = self.conteos()
        self.assertEqual(original, (4, 0))
        r = self.solicitar(self.parcial())
        self.assertEqual(r['siguiente_paso'], 5)
        self.assertEqual(r['checkpoint']['pregunta_pendiente'],
                         self.parcial()['pregunta_pendiente'])
        nuevo_proceso = self.cli('estado', '--alumno', self.alias)
        self.assertEqual(nuevo_proceso['perfil']['nombre_kai'], 'Juancho')
        self.assertEqual(nuevo_proceso['paso_actual'], 5)
        self.assertEqual(nuevo_proceso['eventos'], 4)
        self.assertEqual(nuevo_proceso['estados']['5'], 'EN_DESARROLLO')
        self.assertEqual(nuevo_proceso['checkpoint']['comprension_parcial'],
                         self.parcial()['comprension_parcial'])
        self.assertEqual(self.conteos(), (4, 1))
        with zipfile.ZipFile(DATA / self.alias / 'Progreso_Kai_G05.xlsx') as z:
            self.assertIsNone(z.testzip())
            libro = z.read('xl/workbook.xml').decode('utf-8')
            self.assertIn('Resumen', libro)
            self.assertIn('Evidencias', libro)
            resumen = z.read('xl/worksheets/sheet1.xml').decode('utf-8')
            evidencias = ET.fromstring(z.read('xl/worksheets/sheet2.xml'))
        self.assertIn('EN_DESARROLLO', resumen)
        ns = {'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        self.assertEqual(len(evidencias.findall('x:sheetData/x:row', ns)) - 1, 4)

    def test_sin_checkpoint_no_inventa_continuidad(self):
        estado = self.cli('estado', '--alumno', self.alias)
        self.assertEqual(estado['paso_actual'], 1)
        self.assertIsNone(estado['checkpoint'])

    def test_base_r51_se_migra_sin_cambiar_eventos(self):
        carpeta = DATA / self.alias
        carpeta.mkdir(parents=True)
        db = carpeta / 'events.sqlite'
        with sqlite3.connect(db) as c:
            c.execute('CREATE TABLE perfil (clave TEXT PRIMARY KEY, valor TEXT NOT NULL)')
            c.execute('''CREATE TABLE eventos (id TEXT PRIMARY KEY, fecha TEXT NOT NULL,
                paso INTEGER NOT NULL CHECK(paso BETWEEN 1 AND 7), estado TEXT NOT NULL,
                respuesta TEXT NOT NULL, observacion TEXT NOT NULL, huella TEXT UNIQUE NOT NULL)''')
            c.execute('INSERT INTO perfil VALUES (?,?)', ('nombre_kai', 'Juancho'))
            c.execute('INSERT INTO eventos VALUES (?,?,?,?,?,?,?)',
                      ('historico-1','2026-11-11T00:00:00+00:00',1,'DEMOSTRADO',
                       'Distingo el modelo preliminar del plan de extracción.',
                       'Evidencia histórica','huella-historica'))
            c.commit()
            antes = c.execute('SELECT * FROM eventos').fetchall()
        estado = self.cli('estado', '--alumno', self.alias)
        self.assertEqual(estado['siguiente_paso'], 2)
        self.assertIsNone(estado['checkpoint'])
        self.assertEqual(estado['perfil']['nombre_kai'], 'Juancho')
        with sqlite3.connect(db) as c:
            self.assertEqual(c.execute('SELECT * FROM eventos').fetchall(), antes)
            self.assertIsNotNone(c.execute("SELECT name FROM sqlite_master WHERE name='checkpoints'").fetchone())

    def test_dos_alias_aislados(self):
        self.cuatro_pasos()
        self.solicitar(self.parcial())
        otro = self.cli('estado', '--alumno', self.otro)
        self.assertIsNone(otro['checkpoint'])
        self.assertEqual(otro['paso_actual'], 1)
        self.assertEqual(otro['perfil'], {})

    def test_pregunta_respondida_no_puede_quedar_pendiente(self):
        self.cuatro_pasos()
        pregunta = self.parcial()['pregunta_respondida']
        r = self.solicitar(self.parcial(pregunta_pendiente=pregunta), ok=False)
        self.assertIn('repetir', r['error'])
        self.assertEqual(self.conteos(), (4, 0))

    def test_acierto_parcial_no_cierra_paso(self):
        self.cuatro_pasos()
        self.solicitar(self.parcial())
        r = self.cli('estado', '--alumno', self.alias)
        self.assertEqual(r['siguiente_paso'], 5)
        self.assertNotEqual(r['estados']['5'], 'DEMOSTRADO')
        self.cli('registrar', '--alumno', self.alias, '--paso', '5',
                 '--estado', 'DEMOSTRADO', '--respuesta',
                 'PARTIAL cruza la superficie, pero requiere una fracción para calcular volumen de roca.')
        r = self.cli('estado', '--alumno', self.alias)
        self.assertEqual(r['siguiente_paso'], 6)
        self.assertIsNone(r['checkpoint'])
        self.assertEqual(self.conteos(), (5, 1))

    def test_rechaza_comprension_sin_respuesta_propia(self):
        self.cuatro_pasos()
        r = self.solicitar(self.parcial(evidencia_estudiante=''), ok=False)
        self.assertIn('respuesta propia', r['error'])
        self.assertEqual(self.conteos(), (4, 0))

    def test_reconocimiento_breve_no_acredita_comprension_parcial(self):
        self.cuatro_pasos()
        r = self.solicitar(self.parcial(evidencia_estudiante='No'), ok=False)
        self.assertIn('respuesta breve', r['error'])
        self.assertEqual(self.conteos(), (4, 0))

    def test_texto_especial_del_checkpoint_sigue_como_dato(self):
        self.cuatro_pasos()
        marcador = DATA / ('qa52_shell_' + uuid.uuid4().hex)
        texto = f'PARTIAL no define volumen; "$(New-Item -Path {marcador.as_posix()} -ItemType File)"'
        self.solicitar(self.parcial(evidencia_estudiante=texto))
        self.assertFalse(marcador.exists())
        with sqlite3.connect(DATA / self.alias / 'events.sqlite') as c:
            guardado = c.execute('SELECT evidencia_estudiante FROM checkpoints').fetchone()[0]
        self.assertEqual(guardado, texto)

    def test_checkpoint_idempotente(self):
        self.cuatro_pasos()
        r1 = self.solicitar(self.parcial())
        r2 = self.solicitar(self.parcial())
        self.assertFalse(r1['duplicado'])
        self.assertTrue(r2['duplicado'])
        self.assertEqual(r1['id_checkpoint'], r2['id_checkpoint'])
        self.assertEqual(self.conteos(), (4, 1))

    def test_ruta_completa_no_acepta_evidencia_de_paso_cerrado(self):
        for paso in range(1, 8):
            self.cli('registrar', '--alumno', self.alias, '--paso', str(paso),
                     '--estado', 'DEMOSTRADO', '--respuesta',
                     f'Explico con palabras propias el criterio del paso {paso}.')
        self.assertIsNone(self.cli('estado', '--alumno', self.alias)['siguiente_paso'])
        intento = self.solicitar({
            'operacion': 'registrar', 'alumno': self.alias, 'paso': 6,
            'estado': 'DEMOSTRADO', 'respuesta':
            'Añado una explicación nueva después de cerrar la ruta formal.',
            'observacion': 'Repaso posterior a los siete pasos.'}, ok=False)
        self.assertIn('no registrar paso 6', intento['error'])
        self.assertEqual(self.conteos(), (7, 0))
        intento = self.solicitar(self.parcial(), ok=False)
        self.assertIn('no guardar checkpoint de 5', intento['error'])
        self.assertEqual(self.conteos(), (7, 0))

    def test_interrupcion_excel_y_reintento_conserva_checkpoint(self):
        self.cuatro_pasos()
        excel = DATA / self.alias / 'Progreso_Kai_G05.xlsx'
        bloqueador = RAIZ / 'QA_R5_EVIDENCIAS' / 'bloquear_excel_prueba.py'
        if not bloqueador.is_file():
            bloqueador = RAIZ / 'QA_R5_1_EVIDENCIAS' / 'bloquear_excel_prueba.py'
        if not bloqueador.is_file():
            bloqueador = RAIZ / 'tests' / 'fixtures' / 'windows_lock_xlsx.py'
        p = subprocess.Popen([sys.executable, str(bloqueador), str(excel)],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True)
        try:
            self.assertTrue(p.stdout.readline().startswith('LOCKED '))
            fallo = self.solicitar(self.parcial(), ok=False)
            self.assertIn('error', fallo)
            self.assertTrue(PENDIENTE.exists())
            self.assertEqual(self.conteos(), (4, 1))
        finally:
            p.communicate(input='\n', timeout=10)
        recuperado = self.cli('procesar-pendiente')
        self.assertTrue(recuperado['duplicado'])
        self.assertFalse(PENDIENTE.exists())
        self.assertEqual(self.conteos(), (4, 1))
        self.assertEqual(self.cli('estado', '--alumno', self.alias)['paso_actual'], 5)


if __name__ == '__main__':
    unittest.main()
