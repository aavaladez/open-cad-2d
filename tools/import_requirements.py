"""Read XLSX as data, without executing formulas/macros or adding dependencies."""
import argparse
import csv
import hashlib
import json
import posixpath
import re
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def read_xlsx(path):
    with zipfile.ZipFile(path) as z:
        if sum(i.file_size for i in z.infolist()) > 50_000_000:
            raise ValueError("Workbook exceeds the 50 MB uncompressed limit")
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            shared = ["".join(e.itertext()) for e in ET.fromstring(z.read("xl/sharedStrings.xml"))]
        rels = {r.attrib["Id"]: r.attrib["Target"] for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        sheets = []
        for s in ET.fromstring(z.read("xl/workbook.xml")).find("m:sheets", NS):
            target = rels[s.attrib[REL]]
            target = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
            rows = []
            for row in ET.fromstring(z.read(target)).findall("m:sheetData/m:row", NS):
                cells = {}
                formulas = []
                for c in row:
                    ref = c.attrib["r"]
                    col = re.match(r"[A-Z]+", ref).group()
                    value = c.findtext("m:v", default="", namespaces=NS)
                    if c.attrib.get("t") == "s":
                        value = shared[int(value)]
                    elif c.attrib.get("t") == "inlineStr":
                        value = "".join(t.text or "" for t in c.findall("m:is//m:t", NS))
                    if c.find("m:f", NS) is not None:
                        formulas.append(ref)
                    cells[col] = value
                rows.append({"row": int(row.attrib["r"]), "cells": cells, "formulas": formulas})
            sheets.append({"name": s.attrib["name"], "rows": rows})
    return sheets


def build_catalog(path):
    sheets = read_xlsx(path)
    items, notes, formulas = [], [], []
    for sheet in sheets:
        for row in sheet["rows"]:
            formulas.extend(f"{sheet['name']}!{c}" for c in row["formulas"])
            cells = row["cells"]
            if row["row"] == 1 or not any(cells.values()):
                continue
            if sheet["name"] == "Notas":
                notes.append({"sheet": sheet["name"], "row": row["row"], "text": cells.get("A", "")})
                continue
            if sheet["name"] not in ("AutoCAD", "Civil 3D geoespacial"):
                raise ValueError(f"Unexpected requirement sheet: {sheet['name']}")
            civil = sheet["name"] != "AutoCAD"
            category, command = cells.get("A", ""), cells.get("B", "")
            scope = "2d"
            reason = ""
            if category == "Sólidos 3D" and command != "SKETCH":
                scope, reason = "excluded_3d", "Exclusión explícita de sólidos, superficies y herramientas 3D; no se elimina la fila."
            elif command in ("HELIX", "3DORBIT", "3DFORBIT", "3DCORBIT", "WALK / FLY", "3DPRINT"):
                scope, reason = "excluded_3d", "Herramienta de geometría/navegación 3D fuera del producto 2D."
            elif command == "3DPOLY":
                scope, reason = "2d_with_z", "Conservar vértices XYZ sin modelado de sólidos."
            elif civil:
                scope, reason = "geospatial_2d_z", "GIS, topografía o terreno: implementación por etapas, sin sólidos."
            items.append({"id": f"{'CIV' if civil else 'ACAD'}-{row['row']:04d}",
                          "sheet": sheet["name"], "row": row["row"], "category": category,
                          "command": command, "alias": "" if civil else cells.get("C", ""),
                          "ui_path": cells.get("C", "") if civil else "",
                          "description": cells.get("D", ""), "scope": scope, "scope_reason": reason,
                          "source_cells": cells, "status": "pending"})
    return {"source": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "sheets": [{"name": s["name"], "rows": len(s["rows"])} for s in sheets],
            "formula_cells": formulas, "notes": notes, "requirements": items}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", nargs="?", type=Path, default=ROOT / "requirements/Comandos_AutoCAD_Civil3D (1).xlsx")
    args = parser.parse_args()
    catalog = build_catalog(args.source)
    out = ROOT / "requirements/catalog.json"
    out.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with out.with_suffix(".csv").open("w", encoding="utf-8-sig", newline="") as f:
        fields = [k for k in catalog["requirements"][0] if k != "source_cells"]
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(catalog["requirements"])
    print(json.dumps({"requirements": len(catalog["requirements"]), "scope": Counter(r["scope"] for r in catalog["requirements"]), "sha256": catalog["sha256"]}, ensure_ascii=True))


if __name__ == "__main__":
    main()

