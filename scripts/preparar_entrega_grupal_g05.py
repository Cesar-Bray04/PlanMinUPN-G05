"""Entrega técnica del grupo; nunca incorpora progreso o solicitudes individuales."""
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.missions.products import product_status


def main():
    products=product_status(ROOT)
    if any(p['status']!='VALIDATED' for p in products.values()):
        raise ValueError('Verifica ambas misiones antes de preparar el entregable grupal')
    files=set()
    for base in ['data/raw','src','data/processed/m01b']:
        files.update(p for p in (ROOT/base).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    for p in products.values():files.update(q for q in (ROOT/p['folder']).rglob('*') if q.is_file())
    for relative in ['requirements.txt','kai/parametros_pt01_v2.json','kai/politicas_cuantificacion_g05_v1.json',
                     'outputs/g05_products.json','assets/quantitative.js','assets/quantitative.css','assets/plotly-4.1.1.min.js',
                     'datos/resultados_g05.js',
                     'scripts/preparar_entrega_grupal_g05.py','MISION_S11.cmd','MISION_S12.cmd','VERIFICAR_PRODUCTOS_G05.cmd',
                     'outputs/audit_g05/verificacion_final.json','docs/PROTOCOLO_HUMANO_KAI_G05_IMP008.md',
                     'docs/implementation/IMP-008_g05_recursos_reservas_academicos.md',
                     'docs/INTEGRACION_LOCAL_IMP008_20261114.md']:
        files.add(ROOT/relative)
    missing=[str(p) for p in files if not p.is_file()]
    if missing:raise ValueError('Faltan archivos grupales: '+str(missing))
    target=ROOT/'outputs/Entregable_Grupal_G05_S11_S12.zip'
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(files):
            relative=p.relative_to(ROOT)
            if '.kai_local' in relative.parts or relative.name.startswith('.kai_solicitud'):raise ValueError('Datos personales fuera de alcance')
            z.write(p,relative.as_posix())
        links=[]
        for stage,p in products.items():
            folder=Path(p['folder']).as_posix()
            links.append(f'<section id="{stage.lower()}"><h2>{stage}: {p["product"]}</h2><a href="{folder}/{stage.lower()}_model_3d.html">Abrir visor</a> · <a href="{folder}/block_model_{stage.lower()}.csv">Modelo CSV</a> · <a href="{folder}/reporte_{stage.lower()}.md">Reporte</a></section>')
        links=''.join(links)
        z.writestr('index.html','<!doctype html><html lang="es"><meta charset="utf-8"><title>Entrega grupal G05 S11/S12</title><body style="font:18px Arial;max-width:1000px;margin:50px auto"><h1>Entrega grupal G05</h1><p>Datos sintéticos DS05/EXP03. Productos técnicos separados de las respuestas individuales.</p>'+links+'</body></html>')
        z.writestr('LEEME_GRUPAL.md','# Entrega grupal G05\n\nAbre index.html para explorar S11 y S12. Los modelos, controles y relación por bloque están dentro de outputs.\n\nReproducción: instala requirements.txt y ejecuta `python -m src.missions.g05 todo`; verificación: `python -m src.missions.g05 verificar`.\n\nEl archivo no contiene historiales ni respuestas individuales. Los supuestos y límites constan en los reportes y en la política versionada.\n')
    print(json.dumps({'ok':True,'zip':str(target),'files':len(files)+2},ensure_ascii=False))


if __name__=='__main__':main()
