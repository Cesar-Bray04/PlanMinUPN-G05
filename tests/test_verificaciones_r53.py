"""Regresión del cierre pedagógico R5.3, aislada por alias de prueba."""
import argparse
import importlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import unittest
import uuid
import zipfile

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / 'kai' / 'registro.py'
SOLICITUD = RAIZ / '.kai_solicitud_g05.json'
DATA = RAIZ / '.kai_local'


class VerificacionR53Test(unittest.TestCase):
    def setUp(self):
        self.alias = 'qa53_' + uuid.uuid4().hex[:12]

    def tearDown(self):
        SOLICITUD.unlink(missing_ok=True)
        shutil.rmtree(DATA / self.alias, ignore_errors=True)

    def cli(self, *args, ok=True):
        p = subprocess.run([sys.executable, str(SCRIPT), *args], cwd=RAIZ,
                           text=True, encoding='utf-8', capture_output=True,
                           env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
        self.assertEqual(p.returncode, 0 if ok else 2, p.stdout + p.stderr)
        return json.loads(p.stdout if ok else p.stderr)

    def solicitar(self, data, ok=True):
        SOLICITUD.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        return self.cli('procesar-pendiente', ok=ok)

    def siete_pasos(self):
        for paso in range(1, 8):
            self.cli('registrar', '--alumno', self.alias, '--paso', str(paso),
                     '--estado', 'DEMOSTRADO', '--respuesta',
                     f'Explicación independiente del criterio académico {paso}.')

    def revisar_docente(self, paso, resultado, pendiente='', pregunta=''):
        registro = importlib.import_module('kai.registro')
        return registro.comando_verificacion(argparse.Namespace(
            alumno=self.alias, paso=paso, resultado=resultado,
            evidencia_estudiante='',
            criterio_observado=f'Revisión docente del criterio del paso {paso}.'
            if resultado == 'VERIFICADO' else '',
            componente_pendiente=pendiente, pregunta_pendiente=pregunta,
            procedencia='REVISION_DOCENTE', referencia='QA_R5_3_EVIDENCIAS/prueba_docente'))

    def luis_pendiente(self):
        self.siete_pasos()
        for paso in range(1, 6):
            self.revisar_docente(paso, 'VERIFICADO')
        self.revisar_docente(6, 'PENDIENTE', 'Distinguir clase, ley no estimada y cero.',
                            '¿Qué concluirías de una celda UNASSIGNED con un ensayo cercano?')
        self.revisar_docente(7, 'PENDIENTE', 'Estimación, geología y planificación.',
                            '¿Qué faltaría para respaldar una evaluación minera?')

    def respuesta(self, paso, resultado, evidencia, observado, pendiente='', pregunta=''):
        return {'operacion': 'verificacion', 'alumno': self.alias, 'paso': paso,
                'resultado': resultado, 'evidencia_estudiante': evidencia,
                'criterio_observado': observado, 'componente_pendiente': pendiente,
                'pregunta_pendiente': pregunta}

    def conteos(self):
        with sqlite3.connect(DATA / self.alias / 'events.sqlite') as c:
            return (c.execute('SELECT count(*) FROM eventos').fetchone()[0],
                    c.execute('SELECT count(*) FROM verificaciones').fetchone()[0])

    def test_siete_eventos_no_equivalen_a_ruta_verificada(self):
        self.siete_pasos()
        estado = self.cli('estado', '--alumno', self.alias)
        self.assertTrue(estado['recorrido_registrado'])
        self.assertFalse(estado['ruta_pedagogica_verificada'])
        self.assertEqual(estado['pendientes_revision_docente'], list(range(1, 8)))
        self.assertEqual(estado['pendientes_comprobacion'], [])
        self.assertEqual(estado['objetivo_siguiente'], 'REVISION_DOCENTE')
        self.assertEqual(estado['t3_requisitos_oficiales'], 'NO_VERIFICADOS')

    def test_luis_pendientes_se_recuperan_sin_repetir_siete_pasos(self):
        self.luis_pendiente()
        estado = self.cli('estado', '--alumno', self.alias)
        self.assertEqual(estado['eventos'], 7)
        self.assertEqual(estado['siguiente_paso'], None)
        self.assertEqual(estado['pendientes_revision_docente'], [])
        self.assertEqual(estado['pendientes_comprobacion'], [6, 7])
        self.assertEqual(estado['proxima_verificacion']['paso'], 6)
        self.assertEqual(estado['verificaciones']['5']['resultado'], 'VERIFICADO')
        self.assertEqual(estado['objetivo_siguiente'], 'VERIFICAR_COMPETENCIAS')
        self.assertEqual(self.conteos(), (7, 7))

    def test_parcial_y_cierre_complementario_no_duplican_eventos(self):
        self.luis_pendiente()
        p = self.respuesta(6, 'PARCIAL',
                          'UNASSIGNED no equivale a ley cero; aún no explico la clase.',
                          'Distingue ausencia de soporte de cero.',
                          'Falta clase litológica frente a propiedad cuantitativa.',
                          '¿Qué diferencia habría entre asignar litología y estimar Cu?')
        guardado = self.solicitar(p)
        self.assertEqual(guardado['pendientes_comprobacion'], [6, 7])
        self.assertEqual(guardado['proxima_verificacion']['resultado'], 'PARCIAL')
        self.assertTrue(self.solicitar(p)['duplicado'])
        self.assertEqual(self.conteos(), (7, 8))
        c6 = self.respuesta(6, 'VERIFICADO',
                           'Sin asignación no conozco litología ni ley del bloque; cero sería un valor medido o estimado, no ausencia de datos. La clase no es una ley.',
                           'Diferencia ausencia, cero, categoría y propiedad cuantitativa.')
        self.solicitar(c6)
        estado = self.cli('estado', '--alumno', self.alias)
        self.assertEqual(estado['pendientes_comprobacion'], [7])
        self.assertEqual(estado['proxima_verificacion']['paso'], 7)
        self.assertFalse(estado['ruta_pedagogica_verificada'])
        c7 = self.respuesta(7, 'VERIFICADO',
                           'Antes de recursos o plan necesito estimaciones cuantitativas validadas, controles geológicos y estudios de planificación con restricciones.',
                           'Identifica estimación respaldada, geología y planificación sin atribuir recursos.')
        self.solicitar(c7)
        final = self.cli('estado', '--alumno', self.alias)
        self.assertTrue(final['ruta_pedagogica_verificada'])
        self.assertEqual(final['objetivo_siguiente'], 'PREPARAR_T3')
        self.assertEqual(final['pendientes_comprobacion'], [])
        self.assertEqual(final['t3_requisitos_oficiales'], 'NO_VERIFICADOS')
        self.assertEqual(self.conteos(), (7, 10))
        with zipfile.ZipFile(DATA / self.alias / 'Progreso_Kai_G05.xlsx') as z:
            workbook = z.read('xl/workbook.xml').decode('utf-8')
            self.assertIn('Resumen', workbook)
            self.assertIn('Evidencias', workbook)
            self.assertIn('Verificaciones', workbook)

    def test_no_acepta_verificacion_sin_revision_ni_respuesta_propia(self):
        self.siete_pasos()
        intento = self.respuesta(6, 'VERIFICADO', 'No hay soporte.',
                                'No se ha aportado el criterio completo.')
        error = self.solicitar(intento, ok=False)
        self.assertIn('pendiente', error['error'])
        self.assertEqual(self.conteos(), (7, 0))
        self.revisar_docente(6, 'PENDIENTE', 'Diferencias de soporte y ley.',
                            '¿Qué significa una celda sin asignación?')
        intento['evidencia_estudiante'] = 'sí'
        error = self.solicitar(intento, ok=False)
        self.assertIn('respuesta propia', error['error'])
        self.assertEqual(self.conteos(), (7, 1))

    def test_texto_especial_queda_como_dato_en_sqlite_y_excel(self):
        self.siete_pasos()
        self.revisar_docente(6, 'PENDIENTE', 'Falta diferenciar datos y ley.',
                            '¿Qué diferencia hay entre ausencia de ley y cero?')
        marcador = DATA / ('qa53_shell_' + uuid.uuid4().hex)
        texto = f'=SUM(1,1) y "$(New-Item -Path {marcador.as_posix()} -ItemType File)" son texto del alumno.'
        dato = self.respuesta(6, 'PARCIAL', texto,
                              'Mencionó que no se debe asumir ley cero.',
                              'Falta explicar clase litológica.',
                              '¿Cómo distingues la clase de una propiedad cuantitativa?')
        self.solicitar(dato)
        self.assertFalse(marcador.exists())
        with sqlite3.connect(DATA / self.alias / 'events.sqlite') as c:
            guardado = c.execute('''SELECT evidencia_estudiante FROM verificaciones
                WHERE procedencia='ESTUDIANTE' ''').fetchone()[0]
        self.assertEqual(guardado, texto)
        with zipfile.ZipFile(DATA / self.alias / 'Progreso_Kai_G05.xlsx') as z:
            assert z.testzip() is None
            for name in ('xl/worksheets/sheet1.xml', 'xl/worksheets/sheet2.xml',
                         'xl/worksheets/sheet3.xml'):
                self.assertNotIn('<f>', z.read(name).decode('utf-8'))

    def test_excel_bloqueado_reintenta_sin_duplicar_verificacion(self):
        self.siete_pasos()
        self.revisar_docente(6, 'PENDIENTE', 'Falta explicar clase y ley.',
                            '¿Qué concluirías de una celda UNASSIGNED?')
        dato = self.respuesta(6, 'VERIFICADO',
                              'UNASSIGNED no es ley cero; la clase litológica tampoco estima cobre del bloque.',
                              'Distingue ausencia, cero, categoría y ley estimada.')
        bloqueador = RAIZ / 'QA_R5_1_EVIDENCIAS' / 'bloquear_excel_prueba.py'
        if not bloqueador.is_file():
            bloqueador = RAIZ / 'tests' / 'fixtures' / 'windows_lock_xlsx.py'
        excel = DATA / self.alias / 'Progreso_Kai_G05.xlsx'
        p = subprocess.Popen([sys.executable, str(bloqueador), str(excel)],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True)
        try:
            self.assertTrue(p.stdout.readline().startswith('LOCKED '))
            fallo = self.solicitar(dato, ok=False)
            self.assertIn('error', fallo)
            self.assertTrue(SOLICITUD.exists())
            self.assertEqual(self.conteos(), (7, 2))
        finally:
            p.communicate(input='\n', timeout=10)
        recuperado = self.cli('procesar-pendiente')
        self.assertTrue(recuperado['duplicado'])
        self.assertFalse(SOLICITUD.exists())
        self.assertEqual(self.conteos(), (7, 2))


if __name__ == '__main__':
    unittest.main()
