import importlib.util
from html.parser import HTMLParser
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('ficha_individual', ROOT / 'kai/ficha_individual.py')
ficha = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ficha)


class FichaIndividualTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.original = ficha.DATA
        ficha.DATA = Path(self.temp.name)
        self.base = {'alumno': 'alumno_prueba', 'ficha_id': 'G05-FICHA-INDIVIDUAL', 'version': 1}
        self.catalog = json.loads(ficha.CATALOG.read_text(encoding='utf-8'))
        self.source = json.loads(ficha.SUMMARY.read_text(encoding='utf-8'))

    def tearDown(self):
        ficha.DATA = self.original
        self.temp.cleanup()

    def call(self, operation, **kwargs):
        return ficha.procesar({**self.base, 'operacion': operation, **kwargs})

    @staticmethod
    def cell(xlsx, address):
        with zipfile.ZipFile(xlsx) as z:
            assert z.testzip() is None
            root = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
        cell = root.find(f".//{ns}c[@r='{address}']")
        return None if cell is None else ''.join(cell.itertext())

    def test_campo_equivocado_no_llena_excel_ni_avanza(self):
        initial = self.call('estado')
        self.assertEqual(initial['campos_validados'], 0)
        self.assertEqual(initial['pendiente']['pantalla'], 'index.html#proyecto')
        bad = self.call('responder', campo='PROYECTO.NOMBRE', valor_propuesto='Otro proyecto',
                        respuesta_literal='Se llama Otro proyecto')
        self.assertFalse(bad['validado'])
        self.assertEqual(bad['campos_validados'], 0)
        self.assertIn(self.cell(bad['xlsx'], 'C7'), (None, ''))
        self.assertEqual(self.cell(bad['xlsx'], 'F7'), 'PENDIENTE')
        with self.assertRaises(ValueError):
            self.call('responder', campo='DATOS.SONDAJES', valor_propuesto=44,
                      respuesta_literal='44 sondajes')

    def test_una_respuesta_aprobada_puebla_solo_su_celda_y_aisla_alias(self):
        good = self.call('responder', campo='PROYECTO.NOMBRE', valor_propuesto='Santa Elena',
                         respuesta_literal='En la portada leo Santa Elena')
        self.assertTrue(good['validado'])
        self.assertEqual(good['campos_validados'], 1)
        self.assertEqual(good['pendiente']['id'], 'PROYECTO.DATASET')
        self.assertEqual(self.cell(good['xlsx'], 'C7'), 'Santa Elena')
        self.assertEqual(self.cell(good['xlsx'], 'F7'), 'VALIDADO')
        self.assertIn(self.cell(good['xlsx'], 'C8'), (None, ''))
        other = self.call('estado', alumno='otro_alumno')
        self.assertEqual(other['campos_validados'], 0)
        self.assertIn(self.cell(other['xlsx'], 'C7'), (None, ''))

    def test_los_21_valores_reales_completan_una_ficha_tipificada(self):
        last = None
        for field in self.catalog['campos']:
            value = self.source
            for key in field['fuente']:
                value = value[key]
            if field['tipo'] == 'dimensiones':
                proposed = '50 × 50 × 10 m'
            elif field['tipo'] == 'booleano_no':
                proposed = 'No'
            else:
                proposed = value
            last = self.call('responder', campo=field['id'], valor_propuesto=proposed,
                             respuesta_literal=f'Leo en la pantalla: {proposed}')
            self.assertTrue(last['validado'], field['id'])
        self.assertTrue(last['lista_para_entregar'])
        self.assertEqual(last['campos_validados'], 21)
        self.assertEqual(self.cell(last['xlsx'], 'C4'), '21')
        self.assertEqual(self.cell(last['xlsx'], 'F4'), 'Listo para entregar')
        self.assertEqual(self.cell(last['xlsx'], 'C10'), '44')
        self.assertEqual(self.cell(last['xlsx'], 'C20'), '50 × 50 × 10')
        self.assertEqual(self.cell(last['xlsx'], 'C27'), 'No')

    def test_fuente_modificada_se_rechaza_sin_reinterpretar_respuestas(self):
        with tempfile.TemporaryDirectory() as d:
            mutated = Path(d) / 'resumen.json'
            mutated.write_text('{}', encoding='utf-8')
            with patch.object(ficha, 'SUMMARY', mutated):
                with self.assertRaisesRegex(ValueError, 'resumen del visor cambió'):
                    self.call('estado')

    def test_indice_muestra_teoria_y_total_compuestos_en_pantalla_indicada(self):
        class Sections(HTMLParser):
            def __init__(self):
                super().__init__()
                self.current = None
                self.sections = {}

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if tag == 'section' and attrs.get('id'):
                    self.current = attrs['id']
                    self.sections[self.current] = []
                if self.current:
                    self.sections[self.current].append((tag, attrs))

            def handle_endtag(self, tag):
                if tag == 'section':
                    self.current = None

        page = (ROOT / 'index.html').read_text(encoding='utf-8')
        sections = Sections()
        sections.feed(page)
        self.assertIn('teoria', sections.sections)
        self.assertIn('data-target="teoria"', page)
        self.assertTrue(any(tag == 'iframe' and attrs.get('src') == 'docs/guia_visual_estimacion.html#metodos'
                            for tag, attrs in sections.sections['teoria']))
        self.assertTrue(any(attrs.get('data-value') == 'compositing.total'
                            for _, attrs in sections.sections['compositado']))
        guide = (ROOT / 'docs/guia_visual_estimacion.html').read_text(encoding='utf-8')
        self.assertEqual(guide.count('{name:"'), 8)
        self.assertIn('id="continuidad"', guide)


if __name__ == '__main__':
    unittest.main()
