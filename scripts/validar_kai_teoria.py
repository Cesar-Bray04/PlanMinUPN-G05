"""Ejecuta la regresión de Kai en copia temporal, sin historiales reales."""
from pathlib import Path
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ['test_registro.py', 'test_checkpoint.py', 'test_verificaciones_r53.py',
            'test_verificaciones_r531.py', 'test_teoria_v2.py']
parser = argparse.ArgumentParser()
parser.add_argument('--log', type=Path)
args = parser.parse_args()

with tempfile.TemporaryDirectory(prefix='kai_r6_') as temp:
    isolated = Path(temp)
    shutil.copytree(ROOT / 'kai', isolated / 'kai', ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy2(ROOT / 'index.html', isolated / 'index.html')
    (isolated / 'tests').mkdir()
    for name in PATTERNS:
        shutil.copy2(ROOT / 'tests' / name, isolated / 'tests' / name)
    # Las pruebas históricas buscan este helper; solo se reubica en el temporal.
    helper = isolated / 'QA_R5_1_EVIDENCIAS'
    helper.mkdir()
    shutil.copy2(ROOT / 'tests/fixtures/windows_lock_xlsx.py', helper / 'bloquear_excel_prueba.py')
    result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                            cwd=isolated, capture_output=True, text=True, encoding='utf-8',
                            env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'})
    output = result.stdout + result.stderr
    if args.log:
        args.log.write_text(output, encoding='utf-8')
    print(output, end='')
    sys.exit(result.returncode)
