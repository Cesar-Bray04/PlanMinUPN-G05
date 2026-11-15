"""Caso humano R5.3.1: una respuesta breve puede ser evidencia parcial."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
import uuid

from kai import registro

RAIZ = Path(__file__).resolve().parent.parent


class RespuestaBreveR531Test(unittest.TestCase):
    def setUp(self):
        self.alias = 'qa531_' + uuid.uuid4().hex[:12]

    def tearDown(self):
        registro.SOLICITUD.unlink(missing_ok=True)
        shutil.rmtree(RAIZ / '.kai_local' / self.alias, ignore_errors=True)

    def test_parcial_breve_se_guarda_sin_acreditar_el_paso(self):
        for paso in range(1, 8):
            registro.comando_registrar(argparse.Namespace(
                alumno=self.alias, paso=paso, estado='DEMOSTRADO',
                respuesta=f'Explicación académica propia y suficiente del paso {paso}.',
                observacion='Prueba aislada'))
        registro.comando_verificacion(argparse.Namespace(
            alumno=self.alias, paso=7, resultado='PENDIENTE',
            evidencia_estudiante='', criterio_observado='',
            componente_pendiente='Falta estudiar el alcance del modelo.',
            pregunta_pendiente='¿Qué falta antes de decidir una extracción?',
            procedencia='REVISION_DOCENTE', referencia='QA R5.3.1'))

        respuesta = 'falta economía'  # 14 caracteres; fue un parcial real de DD.
        self.assertEqual(len(respuesta), 14)
        registro.SOLICITUD.write_text(json.dumps({
            'operacion': 'verificacion', 'alumno': self.alias,
            'paso': 7, 'resultado': 'PARCIAL',
            'evidencia_estudiante': respuesta,
            'criterio_observado': 'Reconoce la necesidad de evaluar la viabilidad económica.',
            'componente_pendiente': 'Falta razonar el respaldo técnico del modelo.',
            'pregunta_pendiente': '¿Qué riesgo hay al usar solo unos pocos datos?'
        }, ensure_ascii=False), encoding='utf-8')
        p = subprocess.run([sys.executable, str(RAIZ / 'kai' / 'registro.py'),
                            'procesar-pendiente'], cwd=RAIZ, text=True,
                           encoding='utf-8', capture_output=True,
                           env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
        self.assertEqual(p.returncode, 0, p.stderr)
        resultado = json.loads(p.stdout)
        self.assertTrue(resultado['ok'])
        self.assertEqual(resultado['proxima_verificacion']['resultado'], 'PARCIAL')
        self.assertFalse(resultado['ruta_pedagogica_verificada'])
        self.assertFalse(registro.SOLICITUD.exists())

        with self.assertRaisesRegex(ValueError, 'respuesta propia'):
            registro.comando_verificacion(argparse.Namespace(
                alumno=self.alias, paso=7, resultado='VERIFICADO',
                evidencia_estudiante='faltan bases técnicas',
                criterio_observado='Frase genérica insuficiente.',
                componente_pendiente='', pregunta_pendiente='',
                procedencia='ESTUDIANTE', referencia=''))


if __name__ == '__main__':
    unittest.main()
