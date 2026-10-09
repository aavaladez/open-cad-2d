import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE = {
    "LINE": ("dos puntos/cadena XYZ; faltan opciones Close/Undo interactivas y coordenadas relativas", "test_commands.Commands.test_line_alias_chain_z_undo"),
    "CIRCLE": ("centro/radio; faltan 2P, 3P, TTR y TTT", "test_commands.Commands.test_circle_invalid_and_valid"),
    "MOVE": ("IDs/vector XYZ; falta selección CAD y punto base", "test_commands.Commands.test_move_erase_layer_lock"),
    "ERASE": ("IDs; falta selección completa CAD", "test_commands.Commands.test_move_erase_layer_lock"),
    "LAYER": ("NEW/SET/LOCK/UNLOCK/ON/OFF; faltan estilos/filtros/estados", "test_commands.Commands.test_layer_visibility_undo"),
    "UNDO": ("una transacción; faltan Mark/Back/grupos y opciones", "test_commands.Commands.test_line_alias_chain_z_undo"),
    "REDO": ("una transacción", "test_commands.Commands.test_line_alias_chain_z_undo"),
    "DIST": ("XY/XYZ dos puntos; faltan opciones adicionales", "test_commands.Commands.test_dist_analytic"),
    "APPLOAD": ("diálogo carga LSP UTF-8; faltan startup suites y otros módulos", "test_lisp.Lisp.test_original_rectangle_and_c_command"),
    "LOAD": ("API LispRuntime.load y diálogo; función LISP load aún ausente", "test_lisp.Lisp.test_original_rectangle_and_c_command"),
    "OPEN": ("diálogo DXF LINE/CIRCLE; DWG y demás entidades ausentes", "test_interop.Interop.test_geometry_layers_z"),
    "SAVEAS": ("diálogo DXF LINE/CIRCLE R2010; otros formatos ausentes", "test_interop.Interop.test_geometry_layers_z"),
}


def main():
    catalog = json.loads((ROOT/"requirements/catalog.json").read_text(encoding="utf-8"))
    upstream = json.loads((ROOT/"requirements/upstream-evidence.json").read_text(encoding="utf-8"))
    rows = []
    issues = json.loads((ROOT/"requirements/issues.json").read_text(encoding="utf-8"))["issues"]
    def evidence(command,index):
        names = [c.strip().upper() for c in re.split(r"\s*/\s*",command)]
        found = [e for name in names for e in upstream[index]["commands"].get(name,[])]
        return found
    for r in catalog["requirements"]:
        q,l = evidence(r["command"],0),evidence(r["command"],1)
        variant,test = PROTOTYPE.get(r["command"],("",""))
        work = ("bootstrap" if r["scope"]=="excluded_3d" else
                "geospatial" if r["sheet"]!="AutoCAD" or "geoespaciales" in r["category"] else
                "lisp" if r["category"]=="Programación y automatización" else
                "packaging_plot" if any(t in r["command"] for t in ("PLOT","PRINT","PDF","PUBLISH")) else
                "interop" if r["category"]=="Archivo, impresión y publicación" else "commands_ui")
        row = dict(r)
        row.update(qcad_evidence=q,librecad3_evidence=l,
                   status="excluded" if r["scope"]=="excluded_3d" else ("prototype_partial" if variant else "pending"),
                   implemented_variant=variant,implementation="src/opencad" if variant else "",
                   tests=test,version="0.1.0.dev0" if variant else "",issue=issues[work])
        rows.append(row)
    (ROOT/"requirements/coverage.json").write_text(json.dumps({"source_sha256":catalog["sha256"],"rows":rows},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with (ROOT/"requirements/coverage.csv").open("w",encoding="utf-8-sig",newline="") as f:
        fields = ["id","sheet","row","category","command","alias","ui_path","description","scope","scope_reason","status","implemented_variant","implementation","tests","version","issue","qcad_evidence","librecad3_evidence"]
        writer = csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow(r | {"qcad_evidence":"; ".join(e["url"] for e in r["qcad_evidence"]),"librecad3_evidence":"; ".join(e["url"] for e in r["librecad3_evidence"])})
    counts = Counter(r["status"] for r in rows)
    text = "# Matriz de comandos\n\nGenerada desde el Excel original; cada fila conserva ID, hoja y fila.\n\n"
    text += f"SHA-256: `{catalog['sha256']}`. Total: {len(rows)} entradas.\n\n"
    text += f"Estados: {dict(counts)}. Ningún comando del Excel terminado; variantes del prototipo comprobadas por pruebas locales.\n\n"
    text += "Fuente encontrada = registro textual exacto del comando, sin ejecución ni equivalencia de opciones. Ausencia de coincidencia no prueba ausencia funcional. QCAD usa nombres/alias diferentes (p. ej. circlecr). Comparación completa pendiente de adaptar contratos por fila.\n\n"
    text += "Detalle íntegro de descripciones, aliases, rutas, alcance, implementación, test y enlaces de fuente: [coverage.csv](../requirements/coverage.csv) y [coverage.json](../requirements/coverage.json). Datos originales: [catalog.json](../requirements/catalog.json).\n\n"
    text += "| ID | Hoja: fila | Categoría | Comando | Alcance | QCAD fuente | LC3 fuente | Estado | Test |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
    def escape(value):
        return str(value).replace("|","\\|").replace("\n"," ")
    for r in rows:
        q = f"[registro]({r['qcad_evidence'][0]['url']})" if r['qcad_evidence'] else "sin coincidencia"
        l = f"[registro]({r['librecad3_evidence'][0]['url']})" if r['librecad3_evidence'] else "sin coincidencia"
        values = [r['id'],f"{r['sheet']}: {r['row']}",r['category'],r['command'],r['scope'],q,l,r['status'],r['tests'] or "pendiente"]
        text += "| " + " | ".join(escape(v) for v in values) + " |\n"
    (ROOT/"docs/COMMAND_MATRIX.md").write_text(text,encoding="utf-8")
    print(json.dumps(dict(counts)))


if __name__ == "__main__":
    main()
