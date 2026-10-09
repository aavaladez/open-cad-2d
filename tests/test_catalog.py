import hashlib
import json
import sys
import unittest
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from import_requirements import build_catalog,read_xlsx


class Catalog(unittest.TestCase):
    def test_all_rows_hash_notes_and_scope(self):
        source = ROOT/"requirements/Comandos_AutoCAD_Civil3D (1).xlsx"
        generated = build_catalog(source)
        checked = json.loads((ROOT/"requirements/catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(generated,checked)
        self.assertEqual(generated["sha256"],hashlib.sha256(source.read_bytes()).hexdigest())
        self.assertEqual(len(generated["requirements"]),472)
        self.assertEqual(Counter(r["sheet"] for r in generated["requirements"]),{"AutoCAD":422,"Civil 3D geoespacial":50})
        self.assertEqual(len(set(r["id"] for r in generated["requirements"])),472)
        self.assertEqual(len(generated["notes"]),8)
        self.assertEqual(len([r for r in generated["requirements"] if r["scope"]=="excluded_3d"]),61)
        self.assertFalse(generated["formula_cells"])
        self.assertTrue(any(r["command"]=="—" for r in generated["requirements"]))

    def test_every_source_row_preserved_exactly(self):
        source = ROOT/"requirements/Comandos_AutoCAD_Civil3D (1).xlsx"
        rows = build_catalog(source)["requirements"]
        indexed = {(r["sheet"],r["row"]):r for r in rows}
        for sheet in read_xlsx(source):
            if sheet["name"] == "Notas":
                continue
            for row in sheet["rows"][1:]:
                self.assertEqual(indexed[(sheet["name"],row["row"])]["source_cells"],row["cells"])

