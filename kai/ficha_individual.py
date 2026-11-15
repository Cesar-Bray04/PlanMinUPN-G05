"""Ficha individual G05: respuestas del alumno contrastadas con el resumen del visor.

El Excel es una vista de respuestas aprobadas. SQLite conserva la evidencia local
por alias y el catálogo fija la versión de los datos que muestra index.html.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import unicodedata
import uuid
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / ".kai_local"
CATALOG = ROOT / "kai" / "ficha_individual_g05.json"
SUMMARY = ROOT / "datos" / "resumen_verificado.json"
TEMPLATE = ROOT / "kai" / "PLANTILLA_Ficha_Individual_G05.xlsx"
REQUEST = ROOT / ".kai_solicitud_ficha_g05.json"
S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
ET.register_namespace("", S[1:-1])
ALIAS = re.compile(r"^[A-Za-z0-9_-]{3,40}$")


def _fuentes():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    raw = SUMMARY.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != catalog["resumen_sha256"]:
        raise ValueError("El resumen del visor cambió: revisar y versionar la ficha antes de continuar.")
    summary = json.loads(raw)
    if summary["source"]["commit"] != catalog["source_commit"]:
        raise ValueError("La versión fuente del proyecto no coincide con la ficha.")
    for field in catalog["campos"]:
        expected = summary
        for key in field["fuente"]:
            expected = expected[key]
        if field["tipo"] == "entero" and (type(expected) not in (int, float) or expected < 0 or not float(expected).is_integer()):
            raise ValueError("Un valor de la fuente ya no tiene el tipo esperado.")
    return catalog, summary


def _source_value(summary, field):
    value = summary
    for key in field["fuente"]:
        value = value[key]
    return value


def _fold(value):
    value = " ".join(str(value).strip().split())
    return "".join(c for c in unicodedata.normalize("NFKD", value.casefold())
                   if not unicodedata.combining(c))


def _normalizar(field, proposed):
    kind = field["tipo"]
    if kind == "entero":
        if type(proposed) is int and proposed >= 0:
            return proposed
        if type(proposed) is float and proposed >= 0 and proposed.is_integer():
            return int(proposed)
        value = str(proposed).strip().replace("\u00a0", " ").replace("\u202f", " ")
        if re.fullmatch(r"\d+", value):
            return int(value)
        if re.fullmatch(r"\d{1,3}(?:[ .,]\d{3})+", value):
            return int(re.sub(r"[ .,]", "", value))
        return None
    if kind == "dimensiones":
        value = str(proposed).lower().replace("×", "x").strip()
        value = re.sub(r"\s*m\s*$", "", value)
        match = re.fullmatch(r"(\d+)\s*x\s*(\d+)\s*x\s*(\d+)", value)
        return [int(x) for x in match.groups()] if match else None
    if kind == "booleano_no":
        if proposed is False:
            return False
        return False if _fold(proposed) in {"no", "aun no", "todavia no", "no hay", "falso", "false"} else None
    if kind in {"nombre", "codigo"}:
        return _fold(proposed)
    raise ValueError("Tipo de campo de ficha desconocido.")


def _comparar(field, proposed, expected):
    normalized = _normalizar(field, proposed)
    if field["tipo"] == "dimensiones":
        return normalized == expected
    if field["tipo"] == "booleano_no":
        return normalized is False and expected is False
    if field["tipo"] in {"nombre", "codigo"}:
        return normalized == _fold(expected)
    return normalized == expected


def _display(field, expected):
    if field["tipo"] == "entero":
        return int(expected)
    if field["tipo"] == "dimensiones":
        return " × ".join(map(str, expected))
    if field["tipo"] == "booleano_no":
        return "No" if not expected else "Sí"
    return expected


def _connect(alias, catalog):
    folder = DATA / alias
    folder.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(folder / "ficha_individual.sqlite")
    db.execute("CREATE TABLE IF NOT EXISTS metadata (clave TEXT PRIMARY KEY, valor TEXT NOT NULL)")
    db.execute("""CREATE TABLE IF NOT EXISTS respuestas (
        campo_id TEXT PRIMARY KEY, valor_json TEXT NOT NULL, respuesta_literal TEXT NOT NULL,
        fecha_utc TEXT NOT NULL)""")
    db.execute("""CREATE TABLE IF NOT EXISTS intentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, campo_id TEXT NOT NULL, respuesta_literal TEXT NOT NULL,
        valor_propuesto TEXT NOT NULL, aceptado INTEGER NOT NULL, fecha_utc TEXT NOT NULL)""")
    expected = {"ficha_id": catalog["ficha_id"], "version": str(catalog["version"]),
                "resumen_sha256": catalog["resumen_sha256"]}
    for key, value in expected.items():
        found = db.execute("SELECT valor FROM metadata WHERE clave=?", (key,)).fetchone()
        if found and found[0] != value:
            db.close()
            raise ValueError("La ficha guardada corresponde a otra versión; necesita revisión docente.")
        db.execute("INSERT OR IGNORE INTO metadata (clave, valor) VALUES (?,?)", (key, value))
    db.commit()
    return db, folder


def _records(db):
    return {row[0]: json.loads(row[1]) for row in db.execute("SELECT campo_id, valor_json FROM respuestas")}


def _excel_cell(root, address, value):
    row_num = int(re.search(r"\d+$", address).group())
    row = root.find(f".//{S}sheetData/{S}row[@r='{row_num}']")
    if row is None:
        raise ValueError("La plantilla Excel no contiene la fila prevista.")
    cell = row.find(f"{S}c[@r='{address}']")
    if cell is None:
        cell = ET.Element(f"{S}c", {"r": address})
        col = re.match(r"[A-Z]+", address).group()
        index = 0
        for index, other in enumerate(row.findall(f"{S}c")):
            other_col = re.match(r"[A-Z]+", other.attrib["r"]).group()
            if other_col > col:
                row.insert(index, cell)
                break
        else:
            row.append(cell)
    for child in list(cell):
        cell.remove(child)
    if type(value) is int:
        cell.attrib.pop("t", None)
        ET.SubElement(cell, f"{S}v").text = str(value)
    else:
        cell.set("t", "inlineStr")
        text = ET.SubElement(ET.SubElement(cell, f"{S}is"), f"{S}t")
        text.text = str(value)


def _export(alias, catalog, db, folder):
    if not TEMPLATE.is_file():
        raise FileNotFoundError("Falta la plantilla Excel de la ficha individual.")
    records = _records(db)
    xml_name = "xl/worksheets/sheet1.xml"
    with zipfile.ZipFile(TEMPLATE) as source:
        root = ET.fromstring(source.read(xml_name))
        _excel_cell(root, "C3", alias)
        _excel_cell(root, "C4", len(records))
        _excel_cell(root, "F4", "Listo para entregar" if len(records) == len(catalog["campos"]) else "En curso")
        for n, field in enumerate(catalog["campos"], start=7):
            if field["id"] in records:
                _excel_cell(root, f"C{n}", records[field["id"]])
                _excel_cell(root, f"F{n}", "VALIDADO")
        target = folder / "Ficha_Individual_G05.xlsx"
        temp = folder / (".ficha_" + uuid.uuid4().hex + ".xlsx")
        try:
            with zipfile.ZipFile(temp, "w") as dest:
                for info in source.infolist():
                    data = ET.tostring(root, encoding="utf-8", xml_declaration=True) if info.filename == xml_name else source.read(info)
                    dest.writestr(info, data)
            os.replace(temp, target)
        finally:
            temp.unlink(missing_ok=True)
    return str(target)


def procesar(request):
    alias = str(request.get("alumno", ""))
    if not ALIAS.fullmatch(alias):
        raise ValueError("Alias inválido (3–40 caracteres: letras, números, _ o -).")
    catalog, summary = _fuentes()
    if request.get("ficha_id") != catalog["ficha_id"] or request.get("version") != catalog["version"]:
        raise ValueError("Identidad o versión de ficha incorrecta.")
    op = request.get("operacion")
    if op not in {"estado", "responder"}:
        raise ValueError("Operación de ficha desconocida.")
    db, folder = _connect(alias, catalog)
    try:
        records = _records(db)
        fields = catalog["campos"]
        pending = next((f for f in fields if f["id"] not in records), None)
        outcome = {"ok": True, "ficha_id": catalog["ficha_id"], "version": catalog["version"],
                   "alumno": alias, "campos_validados": len(records), "campos_total": len(fields)}
        if op == "responder":
            if pending is None:
                outcome["mensaje"] = "La ficha individual está completa."
            elif request.get("campo") != pending["id"]:
                raise ValueError("Responde primero el campo pendiente; consulta estado para retomarlo.")
            else:
                literal = str(request.get("respuesta_literal", "")).strip()
                proposed = request.get("valor_propuesto")
                if not literal or len(literal) > 1200 or proposed is None or len(str(proposed)) > 120:
                    raise ValueError("Se necesita la respuesta literal y el valor propuesto por el alumno.")
                expected = _source_value(summary, pending)
                valid = _comparar(pending, proposed, expected)
                now = datetime.now(timezone.utc).isoformat(timespec="seconds")
                db.execute("INSERT INTO intentos (campo_id,respuesta_literal,valor_propuesto,aceptado,fecha_utc) VALUES (?,?,?,?,?)",
                           (pending["id"], literal, json.dumps(proposed, ensure_ascii=False), int(valid), now))
                if valid:
                    value = _display(pending, expected)
                    db.execute("INSERT INTO respuestas (campo_id,valor_json,respuesta_literal,fecha_utc) VALUES (?,?,?,?)",
                               (pending["id"], json.dumps(value, ensure_ascii=False), literal, now))
                    outcome.update({"validado": True, "campo_validado": pending["id"], "valor_aprobado": value})
                else:
                    outcome.update({"validado": False, "campo_revisar": pending["id"], "pista": pending["pista"]})
                db.commit()
                records = _records(db)
                pending = next((f for f in fields if f["id"] not in records), None)
        outcome.update({"campos_validados": len(records), "lista_para_entregar": pending is None,
                        "pendiente": ({"id": pending["id"], "etiqueta": pending["etiqueta"],
                                       "pantalla": pending["pantalla"], "pregunta": pending["pregunta"],
                                       "pista": pending["pista"]} if pending else None)})
        try:
            outcome["xlsx"] = _export(alias, catalog, db, folder)
            outcome["excel_actualizado"] = True
        except PermissionError:
            outcome["excel_actualizado"] = False
            outcome["mensaje_excel"] = "El archivo Excel está abierto; cierra Excel y vuelve a consultar estado. La respuesta quedó guardada."
        return outcome
    finally:
        db.close()


def main():
    if sys.argv[1:] != ["procesar-pendiente"]:
        print("Uso: python kai/ficha_individual.py procesar-pendiente", file=sys.stderr)
        return 2
    try:
        request = json.loads(REQUEST.read_text(encoding="utf-8"))
        result = procesar(request)
        REQUEST.unlink()
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error, zipfile.BadZipFile) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
