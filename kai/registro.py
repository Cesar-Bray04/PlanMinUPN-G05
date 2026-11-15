#!/usr/bin/env python3
"""Registro académico individual G05 (piloto).

Almacenamiento canónico SQLite en .kai_local/<alias>/events.sqlite.
Exportación XLSX automática: vista derivada, nunca fuente de verdad.
Sin servicios externos ni dependencia Python adicional.

Advertencia: el alias no es autenticación. Los permisos OS del perfil determinan
la confidencialidad; no emplear en evaluación oficial sin autorización.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import tempfile
import uuid
import zipfile
from xml.sax.saxutils import escape

RAIZ = Path(__file__).resolve().parent.parent
DATA = RAIZ / '.kai_local'
SOLICITUD = RAIZ / '.kai_solicitud_g05.json'
RUTA = json.loads((RAIZ / 'kai' / 'ruta_g05.json').read_text(encoding='utf-8'))
PASOS = RUTA['pasos']
ALIAS_RE = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_-]{2,39}$')
ESTADOS = {'DEMOSTRADO', 'EN_DESARROLLO', 'REQUIERE_REFUERZO'}
HEADERS = ['Fecha UTC', 'Paso', 'Concepto', 'Estado', 'Respuesta del estudiante', 'Observación formativa', 'ID del evento']
ACCIONES_CHECKPOINT = {'PREGUNTAR_PENDIENTE', 'REFORZAR', 'COMPROBAR_TRANSFERENCIA'}
FUENTES_CHECKPOINT = {'ESTUDIANTE', 'RECONSTRUCCION_DOCENTE', 'AJUSTE_DOCENTE'}
CHECKPOINT_CAMPOS = ('concepto', 'comprension_parcial', 'pregunta_respondida',
                     'pregunta_pendiente', 'dificultad_pendiente',
                     'proxima_accion', 'evidencia_estudiante')
RESULTADOS_VERIFICACION = {'PENDIENTE', 'PARCIAL', 'VERIFICADO'}
PROCEDENCIAS_VERIFICACION = {'ESTUDIANTE', 'REVISION_DOCENTE'}
VERIFICACION_CAMPOS = ('resultado', 'evidencia_estudiante', 'criterio_observado',
                      'componente_pendiente', 'pregunta_pendiente')


def perfil_path(alias: str) -> Path:
    if not ALIAS_RE.fullmatch(alias):
        raise ValueError('Alias inválido: use 3–40 caracteres, letras, números, _ o -')
    return DATA / alias


def abrir_bd(alias: str):
    carpeta = perfil_path(alias)
    carpeta.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(carpeta / 'events.sqlite'), timeout=10)
    conn.execute('PRAGMA busy_timeout=10000')
    conn.execute('''CREATE TABLE IF NOT EXISTS perfil (
        clave TEXT PRIMARY KEY, valor TEXT NOT NULL)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS eventos (
        id TEXT PRIMARY KEY, fecha TEXT NOT NULL,
        paso INTEGER NOT NULL CHECK(paso BETWEEN 1 AND 7),
        estado TEXT NOT NULL, respuesta TEXT NOT NULL,
        observacion TEXT NOT NULL, huella TEXT UNIQUE NOT NULL)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS checkpoints (
        id TEXT PRIMARY KEY, fecha TEXT NOT NULL,
        paso INTEGER NOT NULL CHECK(paso BETWEEN 1 AND 7),
        concepto TEXT NOT NULL, comprension_parcial TEXT NOT NULL,
        pregunta_respondida TEXT NOT NULL, pregunta_pendiente TEXT NOT NULL,
        dificultad_pendiente TEXT NOT NULL, proxima_accion TEXT NOT NULL,
        evidencia_estudiante TEXT NOT NULL, fuente TEXT NOT NULL,
        huella TEXT UNIQUE NOT NULL)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS verificaciones (
        id TEXT PRIMARY KEY, fecha TEXT NOT NULL,
        paso INTEGER NOT NULL CHECK(paso BETWEEN 1 AND 7),
        resultado TEXT NOT NULL CHECK(resultado IN ('PENDIENTE','PARCIAL','VERIFICADO')),
        evidencia_estudiante TEXT NOT NULL, criterio_observado TEXT NOT NULL,
        componente_pendiente TEXT NOT NULL, pregunta_pendiente TEXT NOT NULL,
        procedencia TEXT NOT NULL CHECK(procedencia IN ('ESTUDIANTE','REVISION_DOCENTE')),
        referencia TEXT NOT NULL, huella TEXT UNIQUE NOT NULL)''')
    conn.commit()
    return conn


def perfil(conn):
    return dict(conn.execute('SELECT clave, valor FROM perfil').fetchall())


def eventos(conn):
    return [dict(zip(['id', 'fecha', 'paso', 'estado', 'respuesta', 'observacion'], r))
            for r in conn.execute('SELECT id, fecha, paso, estado, respuesta, observacion FROM eventos ORDER BY fecha, rowid').fetchall()]


def resumen(rows):
    estados = {p['id']: 'NO_INICIADO' for p in PASOS}
    for r in rows:
        # Un concepto DEMOSTRADO conserva su logro tras intervenciones posteriores.
        if estados[r['paso']] == 'DEMOSTRADO':
            continue
        estados[r['paso']] = r['estado']
    siguiente = next((p['id'] for p in PASOS if estados[p['id']] != 'DEMOSTRADO'), None)
    return estados, siguiente


def ultimo_checkpoint(conn, paso):
    if paso is None:
        return None
    cols = ['id', 'fecha', 'paso', *CHECKPOINT_CAMPOS, 'fuente']
    row = conn.execute('''SELECT id, fecha, paso, concepto, comprension_parcial,
        pregunta_respondida, pregunta_pendiente, dificultad_pendiente,
        proxima_accion, evidencia_estudiante, fuente
        FROM checkpoints WHERE paso=? ORDER BY rowid DESC LIMIT 1''', (paso,)).fetchone()
    return dict(zip(cols, row)) if row else None


def estado_y_checkpoint(conn, rows=None):
    estados, siguiente = resumen(eventos(conn) if rows is None else rows)
    checkpoint = ultimo_checkpoint(conn, siguiente)
    if checkpoint and estados[siguiente] == 'NO_INICIADO':
        estados[siguiente] = 'EN_DESARROLLO'
    return estados, siguiente, checkpoint


def estado_verificaciones(conn, estados, siguiente):
    """El recorrido registrado no equivale a revisión pedagógica de su evidencia."""
    cols = ('id', 'fecha', 'paso', *VERIFICACION_CAMPOS, 'procedencia', 'referencia')
    ultimas = {}
    for row in conn.execute('''SELECT id, fecha, paso, resultado,
            evidencia_estudiante, criterio_observado, componente_pendiente,
            pregunta_pendiente, procedencia, referencia
            FROM verificaciones ORDER BY rowid'''):
        item = dict(zip(cols, row))
        ultimas[item['paso']] = item
    verificaciones = {}
    sin_revision = []
    por_comprobar = []
    for paso in PASOS:
        numero = paso['id']
        if estados[numero] != 'DEMOSTRADO':
            verificaciones[numero] = {'paso': numero, 'resultado': 'NO_APLICA'}
        elif numero in ultimas:
            verificaciones[numero] = ultimas[numero]
            if ultimas[numero]['resultado'] in {'PENDIENTE', 'PARCIAL'}:
                por_comprobar.append(numero)
        else:
            verificaciones[numero] = {'paso': numero, 'resultado': 'SIN_REVISION'}
            sin_revision.append(numero)
    recorrido = siguiente is None
    ruta_verificada = recorrido and not sin_revision and not por_comprobar
    if not recorrido:
        objetivo = 'CONTINUAR_RUTA'
    elif por_comprobar:
        objetivo = 'VERIFICAR_COMPETENCIAS'
    elif sin_revision:
        objetivo = 'REVISION_DOCENTE'
    else:
        objetivo = 'PREPARAR_T3'
    return {'recorrido_registrado': recorrido,
            'verificaciones': verificaciones,
            'pendientes_revision_docente': sin_revision,
            'pendientes_comprobacion': por_comprobar,
            'proxima_verificacion': verificaciones[por_comprobar[0]] if por_comprobar else None,
            'ruta_pedagogica_verificada': ruta_verificada,
            'objetivo_siguiente': objetivo,
            't3_requisitos_oficiales': 'NO_VERIFICADOS'}


def valor_xml(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return f'<v>{v}</v>', 'n'
    s = escape(str(v).replace('\x00', ''))
    return f'<is><t xml:space="preserve">{s}</t></is>', 'inlineStr'


def nombre_col(n):
    s = ''
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def hoja_xml(data, widths, freeze=True):
    from xml.sax.saxutils import quoteattr
    cols = ''.join(f'<col min="{i}" max="{i}" width="{w}" customWidth="1"/>' for i, w in enumerate(widths, 1))
    rows_xml = []
    for rid, row in enumerate(data, 1):
        cells = []
        for j, val in enumerate(row, 1):
            if val is None:continue
            content, typ = valor_xml(val)
            style = ' s="1"' if rid == 1 else ''
            cells.append(f'<c r="{nombre_col(j)}{rid}" t="{typ}"{style}>{content}</c>')
        rows_xml.append(f'<row r="{rid}">{"".join(cells)}</row>')
    frozen = '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>' if freeze else '<sheetViews><sheetView workbookViewId="0"/></sheetViews>'
    ref=f'A1:{nombre_col(max(len(x) for x in data))}{max(1,len(data))}'
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><dimension ref="{ref}"/>{frozen}<sheetFormatPr defaultRowHeight="17"/><cols>{cols}</cols><sheetData>{''.join(rows_xml)}</sheetData><autoFilter ref="{ref}"/></worksheet>'''


def escribir_xlsx(path: Path, sheets):
    # Escritura derivada y atómica. No modificar manualmente el XLSX: sus cambios
    # no se fusionan al registro canónico. Celdas textuales nunca son fórmulas.
    estilos='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF143C5B"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/></cellXfs></styleSheet>'''
    types='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'''+''.join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in range(1,len(sheets)+1))+'</Types>'
    rels='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'''
    workbook='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'''+''.join(f'<sheet name="{escape(name)}" sheetId="{i}" r:id="rId{i}"/>' for i,(name,_,_) in enumerate(sheets,1))+'</sheets></workbook>'
    wrels='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'''+''.join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1,len(sheets)+1))+f'<Relationship Id="rId{len(sheets)+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.kai_xlsx_',suffix='.tmp',dir=path.parent)
    os.close(fd)
    try:
        with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr('[Content_Types].xml',types)
            z.writestr('_rels/.rels',rels)
            z.writestr('xl/workbook.xml',workbook)
            z.writestr('xl/_rels/workbook.xml.rels',wrels)
            z.writestr('xl/styles.xml',estilos)
            for i,(_,data,widths) in enumerate(sheets,1):
                z.writestr(f'xl/worksheets/sheet{i}.xml',hoja_xml(data,widths))
        with zipfile.ZipFile(tmp) as z:
            if z.testzip() is not None: raise RuntimeError('Exportación Excel corrupta')
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


def exportar_excel(alias, conn):
    rows=eventos(conn)
    states, siguiente, _ = estado_y_checkpoint(conn, rows)
    revision=estado_verificaciones(conn, states, siguiente)
    resumen_rows=[['Paso','Concepto','Estado','Visualizador','Proyecto']]+[[p['id'],p['titulo'],states[p['id']],p['url'],'Santa Elena · DS05/EXP03'] for p in PASOS]
    evid_rows=[HEADERS]+[[r['fecha'],r['paso'],PASOS[r['paso']-1]['titulo'],r['estado'],r['respuesta'],r['observacion'],r['id']] for r in rows]
    revision_rows=[['Paso','Verificación pedagógica','Procedencia','Criterio observado',
                    'Evidencia del estudiante','Componente pendiente','Pregunta pendiente',
                    'Fecha UTC','Referencia']]
    for p in PASOS:
        item=revision['verificaciones'][p['id']]
        revision_rows.append([p['id'], item['resultado'], item.get('procedencia',''),
                              item.get('criterio_observado',''),
                              item.get('evidencia_estudiante',''),
                              item.get('componente_pendiente',''),
                              item.get('pregunta_pendiente',''),
                              item.get('fecha',''), item.get('referencia','')])
    sheets=[('Resumen',resumen_rows,[9,33,24,30,31]),
            ('Evidencias',evid_rows,[24,9,33,22,65,45,38]),
            ('Verificaciones',revision_rows,[9,25,22,65,65,65,65,24,56])]
    path=perfil_path(alias)/'Progreso_Kai_G05.xlsx'
    escribir_xlsx(path,sheets)
    return str(path)


def comando_perfil(a):
    with abrir_bd(a.alumno) as conn:
        conn.execute('BEGIN IMMEDIATE')
        if a.nombre:
            conn.execute('INSERT INTO perfil VALUES (?, ?) ON CONFLICT(clave) DO UPDATE SET valor=excluded.valor',('nombre_elegido',a.nombre[:80]))
        if a.kai:
            conn.execute('INSERT INTO perfil VALUES (?, ?) ON CONFLICT(clave) DO UPDATE SET valor=excluded.valor',('nombre_kai',a.kai[:80]))
        conn.commit()
        xlsx=exportar_excel(a.alumno,conn)
        return {'ok':True,'alumno':a.alumno,'perfil':perfil(conn),'xlsx':xlsx}


def comando_estado(a):
    with abrir_bd(a.alumno) as conn:
        rows=eventos(conn)
        estados,siguiente,checkpoint=estado_y_checkpoint(conn, rows)
        revision=estado_verificaciones(conn, estados, siguiente)
        # Auto-reparación de vista Excel si escritura anterior se interrumpió.
        xlsx=exportar_excel(a.alumno,conn)
        return {'ok':True,'alumno':a.alumno,'perfil':perfil(conn),'estados':estados,
                'paso_actual':siguiente,'siguiente_paso':siguiente,'checkpoint':checkpoint,
                'eventos':len(rows),'xlsx':xlsx, **revision}


def comando_registrar(a):
    if a.estado not in ESTADOS:raise ValueError('Estado no permitido')
    respuesta=a.respuesta.strip()
    if not respuesta:raise ValueError('Se necesita evidencia textual del estudiante')
    if len(respuesta)>3500:raise ValueError('Respuesta demasiado larga; resume evidencia')
    if a.estado=='DEMOSTRADO' and (len(respuesta)<12 or respuesta.casefold() in {'si','sí','ok','listo','entendí','ya','correcto','claro'}):
        raise ValueError('Una aceptación breve no demuestra comprensión')
    if a.paso not in {p['id'] for p in PASOS}:raise ValueError('Paso inexistente')
    huella=hashlib.sha256(json.dumps([a.paso,a.estado,respuesta.strip().casefold()],ensure_ascii=False).encode('utf-8')).hexdigest()
    with abrir_bd(a.alumno) as conn:
        conn.execute('BEGIN IMMEDIATE')
        rows=eventos(conn)
        estados,siguiente=resumen(rows)
        existe=conn.execute('SELECT id FROM eventos WHERE huella=?',(huella,)).fetchone()
        duplicado=bool(existe)
        if a.paso!=siguiente and not duplicado:
            # Repetir una misma llamada tras fallo de exportación es idempotente,
            # pero registrar evidencia nueva de un paso ya cerrado no está permitido.
            raise ValueError(f'El siguiente paso no demostrado es {siguiente}; no registrar paso {a.paso}')
        if not duplicado:
            uid=str(uuid.uuid4())
            ahora=dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
            conn.execute('INSERT INTO eventos VALUES (?,?,?,?,?,?,?)',(uid,ahora,a.paso,a.estado,respuesta,a.observacion[:1200],huella))
        else:uid=existe[0]
        conn.commit()
        xlsx=exportar_excel(a.alumno,conn)
        estados,siguiente=resumen(eventos(conn))
        return {'ok':True,'duplicado':duplicado,'id_evento':uid,'paso_registrado':a.paso,'estado_registrado':a.estado,'siguiente_paso':siguiente,'estados':estados,'xlsx':xlsx}


def comando_checkpoint(a):
    if type(a.paso) is not int or a.paso not in {p['id'] for p in PASOS}:
        raise ValueError('Paso de checkpoint inválido')
    if a.proxima_accion not in ACCIONES_CHECKPOINT:
        raise ValueError('Próxima acción inválida')
    if a.fuente not in FUENTES_CHECKPOINT:
        raise ValueError('Fuente de checkpoint inválida')
    limites = {'concepto': 160, 'comprension_parcial': 500,
               'pregunta_respondida': 500, 'pregunta_pendiente': 500,
               'dificultad_pendiente': 500, 'proxima_accion': 40,
               'evidencia_estudiante': 1500}
    for campo, limite in limites.items():
        valor = getattr(a, campo)
        if not isinstance(valor, str) or len(valor) > limite:
            raise ValueError('Campo de checkpoint inválido: ' + campo)
    if not a.concepto.strip() or not a.pregunta_pendiente.strip():
        raise ValueError('Checkpoint requiere concepto y pregunta pendiente')
    if (a.pregunta_respondida.strip() and
            a.pregunta_respondida.strip().casefold() == a.pregunta_pendiente.strip().casefold()):
        raise ValueError('No se puede repetir como pendiente una pregunta ya respondida')
    if (a.fuente == 'ESTUDIANTE' and a.comprension_parcial.strip()
            and not a.evidencia_estudiante.strip()):
        raise ValueError('La comprensión parcial requiere respuesta propia del estudiante')
    if (a.fuente == 'ESTUDIANTE' and a.comprension_parcial.strip()
            and (len(a.evidencia_estudiante.strip()) < 12 or
                 a.evidencia_estudiante.strip().casefold() in
                 {'si', 'sí', 'no', 'ok', 'listo', 'entendí', 'claro'})):
        raise ValueError('Una respuesta breve no demuestra comprensión parcial razonada')
    contenido = [a.paso, *[getattr(a, campo) for campo in CHECKPOINT_CAMPOS], a.fuente]
    huella = hashlib.sha256(json.dumps(contenido, ensure_ascii=False).encode('utf-8')).hexdigest()
    with abrir_bd(a.alumno) as conn:
        conn.execute('BEGIN IMMEDIATE')
        existe = conn.execute('SELECT id FROM checkpoints WHERE huella=?', (huella,)).fetchone()
        _, siguiente = resumen(eventos(conn))
        if a.paso != siguiente and not existe:
            raise ValueError(f'El siguiente paso no demostrado es {siguiente}; no guardar checkpoint de {a.paso}')
        duplicado = bool(existe)
        if duplicado:
            uid = existe[0]
        else:
            uid = str(uuid.uuid4())
            ahora = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
            conn.execute('''INSERT INTO checkpoints
                (id, fecha, paso, concepto, comprension_parcial, pregunta_respondida,
                 pregunta_pendiente, dificultad_pendiente, proxima_accion,
                 evidencia_estudiante, fuente, huella)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                (uid, ahora, a.paso, *[getattr(a, campo) for campo in CHECKPOINT_CAMPOS],
                 a.fuente, huella))
        conn.commit()
        xlsx = exportar_excel(a.alumno, conn)
        estados, siguiente, checkpoint = estado_y_checkpoint(conn)
        return {'ok': True, 'duplicado': duplicado, 'id_checkpoint': uid,
                'paso_actual': siguiente, 'siguiente_paso': siguiente,
                'checkpoint': checkpoint, 'estados': estados, 'xlsx': xlsx}


def comando_verificacion(a):
    """Anexa una revisión de un paso registrado, sin editar su evento original."""
    if type(a.paso) is not int or a.paso not in {p['id'] for p in PASOS}:
        raise ValueError('Paso de verificación inválido')
    if a.resultado not in RESULTADOS_VERIFICACION:
        raise ValueError('Resultado de verificación inválido')
    if a.procedencia not in PROCEDENCIAS_VERIFICACION:
        raise ValueError('Procedencia de verificación inválida')
    limites = {'evidencia_estudiante': 1500, 'criterio_observado': 500,
               'componente_pendiente': 500, 'pregunta_pendiente': 500,
               'referencia': 300}
    for campo, limite in limites.items():
        valor = getattr(a, campo)
        if not isinstance(valor, str) or len(valor) > limite:
            raise ValueError('Campo de verificación inválido: ' + campo)
    if a.procedencia == 'ESTUDIANTE':
        if a.resultado == 'PENDIENTE':
            raise ValueError('Solo la revisión docente puede abrir una comprobación pendiente')
        respuesta = a.evidencia_estudiante.strip()
        # Un avance parcial puede expresarse con pocas palabras (p. ej.
        # «falta economía»); el cierre completo conserva su umbral anterior.
        minimo = 4 if a.resultado == 'PARCIAL' else 15
        if len(respuesta) < minimo or respuesta.casefold() in {
                'sí', 'si', 'no', 'no hay soporte', 'faltan bases técnicas'}:
            raise ValueError('La verificación requiere respuesta propia suficiente del estudiante')
        if not a.criterio_observado.strip() or a.referencia.strip():
            raise ValueError('La verificación estudiantil requiere criterio observado y no referencia docente')
    else:
        if not a.referencia.strip():
            raise ValueError('La revisión docente requiere referencia de procedencia')
        if a.evidencia_estudiante.strip():
            raise ValueError('La revisión docente no debe atribuir una respuesta nueva al estudiante')
    if a.resultado == 'VERIFICADO':
        if not a.criterio_observado.strip() or a.componente_pendiente.strip() or a.pregunta_pendiente.strip():
            raise ValueError('El cierre requiere criterio observado y ningún componente pendiente')
    else:
        if not a.componente_pendiente.strip() or not a.pregunta_pendiente.strip():
            raise ValueError('La revisión pendiente requiere componente y pregunta siguiente')
    contenido = [a.paso, *[getattr(a, campo) for campo in VERIFICACION_CAMPOS],
                 a.procedencia, a.referencia]
    huella = hashlib.sha256(json.dumps(contenido, ensure_ascii=False).encode('utf-8')).hexdigest()
    with abrir_bd(a.alumno) as conn:
        conn.execute('BEGIN IMMEDIATE')
        existe = conn.execute('SELECT id FROM verificaciones WHERE huella=?', (huella,)).fetchone()
        estados, siguiente = resumen(eventos(conn))
        if estados[a.paso] != 'DEMOSTRADO' and not existe:
            raise ValueError('Solo se verifica un paso ya registrado como DEMOSTRADO')
        previa = conn.execute('''SELECT resultado FROM verificaciones
            WHERE paso=? ORDER BY rowid DESC LIMIT 1''', (a.paso,)).fetchone()
        if a.procedencia == 'ESTUDIANTE' and not existe and (
                not previa or previa[0] not in {'PENDIENTE', 'PARCIAL'}):
            raise ValueError('No existe comprobación pendiente autorizada para este paso')
        if existe:
            uid = existe[0]
        else:
            uid = str(uuid.uuid4())
            ahora = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
            conn.execute('''INSERT INTO verificaciones
                (id, fecha, paso, resultado, evidencia_estudiante, criterio_observado,
                 componente_pendiente, pregunta_pendiente, procedencia, referencia, huella)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                (uid, ahora, a.paso, *[getattr(a, campo) for campo in VERIFICACION_CAMPOS],
                 a.procedencia, a.referencia, huella))
        conn.commit()
        xlsx = exportar_excel(a.alumno, conn)
        estados, siguiente, _ = estado_y_checkpoint(conn)
        revision = estado_verificaciones(conn, estados, siguiente)
        return {'ok': True, 'duplicado': bool(existe), 'id_verificacion': uid,
                'paso_revisado': a.paso, 'xlsx': xlsx, **revision}


def comando_verificar(a):
    with abrir_bd(a.alumno) as conn:
        ok=conn.execute('PRAGMA integrity_check').fetchone()[0]
        path=perfil_path(a.alumno)/'Progreso_Kai_G05.xlsx'
        if not path.is_file(): raise RuntimeError('No existe la vista XLSX')
        with zipfile.ZipFile(path) as z:
            bad=z.testzip()
            if bad:raise RuntimeError('XLSX corrupto: '+bad)
            workbook=z.read('xl/workbook.xml').decode('utf-8')
            if any(nombre not in workbook for nombre in ('Resumen', 'Evidencias', 'Verificaciones')):
                raise RuntimeError('Faltan hojas Excel')
        return {'ok':ok=='ok','sqlite':ok,'eventos':len(eventos(conn)),
                'verificaciones':conn.execute('SELECT count(*) FROM verificaciones').fetchone()[0],
                'excel':str(path),'xlsx_crc':'OK'}


def comando_procesar_pendiente(_):
    """Lee datos estructurados sin interpolar texto del estudiante en la shell.

    El comando de terminal es constante. El archivo se elimina solo si la
    operación completa, incluida la exportación Excel, termina correctamente.
    """
    if not SOLICITUD.is_file():
        raise ValueError('No hay solicitud académica pendiente')
    if SOLICITUD.stat().st_size > 12000:
        raise ValueError('Solicitud demasiado grande')

    def objeto_sin_duplicados(pares):
        objeto = {}
        for clave, valor in pares:
            if clave in objeto:
                raise ValueError('Campo JSON duplicado: ' + clave)
            objeto[clave] = valor
        return objeto

    try:
        solicitud = json.loads(SOLICITUD.read_text(encoding='utf-8'),
                               object_pairs_hook=objeto_sin_duplicados)
    except (UnicodeError, json.JSONDecodeError) as ex:
        raise ValueError('Solicitud JSON inválida') from ex
    if not isinstance(solicitud, dict):
        raise ValueError('La solicitud debe ser un objeto JSON')
    operacion = solicitud.get('operacion')
    campos = {
        'estado': {'operacion', 'alumno'},
        'verificar': {'operacion', 'alumno'},
        'perfil': {'operacion', 'alumno', 'nombre', 'kai'},
        'registrar': {'operacion', 'alumno', 'paso', 'estado', 'respuesta', 'observacion'},
        'checkpoint': {'operacion', 'alumno', 'paso', *CHECKPOINT_CAMPOS},
        'verificacion': {'operacion', 'alumno', 'paso', *VERIFICACION_CAMPOS},
    }
    if not isinstance(operacion, str) or operacion not in campos or set(solicitud) != campos[operacion]:
        raise ValueError('Operación o campos de solicitud inválidos')
    if not isinstance(solicitud['alumno'], str):
        raise ValueError('Alias inválido')
    if operacion == 'perfil':
        if not all(isinstance(solicitud[k], str) for k in ('nombre', 'kai')):
            raise ValueError('Perfil inválido')
    if operacion == 'registrar':
        if type(solicitud['paso']) is not int or not all(
                isinstance(solicitud[k], str) for k in ('estado', 'respuesta', 'observacion')):
            raise ValueError('Registro inválido')
    if operacion == 'checkpoint':
        if type(solicitud['paso']) is not int or not all(
                isinstance(solicitud[k], str) for k in CHECKPOINT_CAMPOS):
            raise ValueError('Checkpoint inválido')
        solicitud['fuente'] = 'ESTUDIANTE'
    if operacion == 'verificacion':
        if type(solicitud['paso']) is not int or not all(
                isinstance(solicitud[k], str) for k in VERIFICACION_CAMPOS):
            raise ValueError('Verificación inválida')
        solicitud['procedencia'] = 'ESTUDIANTE'
        solicitud['referencia'] = ''
    accion = argparse.Namespace(**solicitud)
    resultado = {
        'estado': comando_estado,
        'verificar': comando_verificar,
        'perfil': comando_perfil,
        'registrar': comando_registrar,
        'checkpoint': comando_checkpoint,
        'verificacion': comando_verificacion,
    }[operacion](accion)
    SOLICITUD.unlink()
    return resultado


def main():
    ap=argparse.ArgumentParser(description='Kai G05: registro individual y exportación Excel automática')
    sub=ap.add_subparsers(dest='comando',required=True)
    for nombre in ['perfil','estado','registrar','verificar','procesar-pendiente']:
        s=sub.add_parser(nombre)
        if nombre != 'procesar-pendiente':
            s.add_argument('--alumno',required=True,help='ID pseudónimo estable, sin espacios')
        if nombre=='perfil':
            s.add_argument('--nombre',default='',help='Nombre preferido, opcional')
            s.add_argument('--kai',default='',help='Nombre elegido para el compañero, opcional')
        if nombre=='registrar':
            s.add_argument('--paso',type=int,required=True)
            s.add_argument('--estado',required=True,choices=sorted(ESTADOS))
            s.add_argument('--respuesta',required=True,help='Respuesta redactada por estudiante')
            s.add_argument('--observacion',default='',help='Breve retroalimentación docente/formativa')
    a=ap.parse_args()
    try:
        output={'perfil':comando_perfil,'estado':comando_estado,'registrar':comando_registrar,
                'verificar':comando_verificar,'procesar-pendiente':comando_procesar_pendiente}[a.comando](a)
        print(json.dumps(output,ensure_ascii=False,indent=2))
        return 0
    except (ValueError,RuntimeError,sqlite3.DatabaseError,OSError) as ex:
        print(json.dumps({'ok':False,'error':str(ex)},ensure_ascii=False),file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
