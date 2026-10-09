"""Reusable, fail-closed automation for the six project skills."""
import argparse
import hashlib
import json
import math
import os
import platform
import re
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPS = os.environ.get("OPENCAD_DEPS_DIR",str(ROOT/".cache/python"))
sys.path[:0] = [str(ROOT/"src"), DEPS]


def write(path, data, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x" if exclusive else "w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
        f.write("\n")


def make_spec(identifier):
    catalog = json.loads((ROOT/"requirements/catalog.json").read_text(encoding="utf-8"))
    rows = [r for r in catalog["requirements"] if r["id"] == identifier]
    if len(rows) != 1:
        raise ValueError("ID de requisito desconocido")
    row = rows[0]
    if row["scope"] == "excluded_3d":
        raise ValueError("Requisito excluido por alcance 2D: " + row["command"])
    return {"requirement": row, "source_sha256": catalog["sha256"], "status": "spec_pending",
            "variants": [], "evidence": [], "cases": [], "implementation": None,
            "acceptance": {"normal": False, "degenerate": False, "cancel_rollback": False,
                           "undo_redo": False, "z_preserved": False, "external_comparison": False}}


def compare(baseline, actual, atol):
    if not math.isfinite(atol) or atol < 0:
        raise ValueError("Tolerancia inválida")
    for item in (baseline,actual):
        if not isinstance(item,dict) or not all(k in item for k in ("origin","version","result")):
            raise ValueError("Resultado sin procedencia/versión")
    if baseline["origin"] not in ("analytic","public_documentation","external_engine") or not baseline.get("evidence"):
        raise ValueError("Baseline independiente y evidence requeridos")
    differences = []
    def walk(a,b,path):
        if isinstance(a,bool) or isinstance(b,bool):
            if type(a) is not type(b) or a != b:
                differences.append(path)
        elif isinstance(a,(float,int)) and isinstance(b,(float,int)):
            if not math.isfinite(a) or not math.isfinite(b) or abs(a-b)>atol:
                differences.append(path)
        elif isinstance(a,dict) and isinstance(b,dict):
            if a.keys() != b.keys():
                differences.append(path+":keys")
            for k in a.keys() & b.keys():
                walk(a[k],b[k],path+"."+k)
        elif isinstance(a,list) and isinstance(b,list):
            if len(a)!=len(b):
                differences.append(path+":length")
            for i,(x,y) in enumerate(zip(a,b)):
                walk(x,y,path+f"[{i}]")
        elif type(a) is not type(b) or a != b:
            differences.append(path)
    walk(baseline["result"],actual["result"],"result")
    return {"passed":not differences,"differences":sorted(differences),"atol":atol,
            "baseline_origin":baseline["origin"],"baseline_version":baseline["version"],"actual_version":actual["version"]}


def semantic(doc):
    return {"entities":[asdict(e) | {"type":type(e).__name__} for e in doc.entities.values()],
            "layers": {k:asdict(v) for k,v in doc.layers.items() if k != "Defpoints"},
            "current_layer":doc.current_layer,"units":doc.units}


def environment():
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(ROOT/"src"),DEPS,str(ROOT/"tools")])
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["PYTHONIOENCODING"] = "utf-8"
    env["XDG_CACHE_HOME"] = str(ROOT/".cache")
    return env


def main(argv=None):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode",required=True)
    spec = sub.add_parser("spec")
    spec.add_argument("--id",required=True)
    spec.add_argument("--output",type=Path,required=True)
    comp = sub.add_parser("compare")
    comp.add_argument("baseline",type=Path)
    comp.add_argument("actual",type=Path)
    comp.add_argument("--atol",type=float,default=1e-9)
    comp.add_argument("--report",type=Path,required=True)
    regression = sub.add_parser("regress")
    regression.add_argument("--report",type=Path,required=True)
    regression.add_argument("--pattern",default="test_*.py")
    ui = sub.add_parser("ui")
    ui.add_argument("--output",type=Path,required=True)
    lsp = sub.add_parser("lsp")
    lsp.add_argument("source",type=Path)
    lsp.add_argument("--report",type=Path,required=True)
    rt = sub.add_parser("roundtrip")
    rt.add_argument("source",type=Path)
    rt.add_argument("output",type=Path)
    rt.add_argument("--report",type=Path,required=True)
    args = parser.parse_args(argv)
    try:
        if args.mode == "spec":
            write(args.output,make_spec(args.id),exclusive=True)
        elif args.mode == "compare":
            result = compare(json.loads(args.baseline.read_text(encoding="utf-8")),json.loads(args.actual.read_text(encoding="utf-8")),args.atol)
            write(args.report,result)
            return 0 if result["passed"] else 1
        elif args.mode == "regress":
            command = [sys.executable,"-m","unittest","discover","-s","tests","-p",args.pattern,"-v"]
            run = subprocess.run(command,cwd=ROOT,env=environment(),capture_output=True,text=True,encoding="utf-8",errors="replace")
            counts = re.findall(r"^Ran (\d+) tests? in ",run.stderr,re.MULTILINE)
            tests_run = int(counts[-1]) if counts else 0
            exit_code = run.returncode or (0 if tests_run else 1)
            write(args.report,{"command":command,"platform":platform.platform(),"python":platform.python_version(),"exit_code":exit_code,"process_exit_code":run.returncode,"tests_run":tests_run,"passed":exit_code==0,"stdout":run.stdout,"stderr":run.stderr})
            print(run.stderr)
            if not tests_run:
                print("No se ejecutaron pruebas; regresión no acreditada.",file=sys.stderr)
            return exit_code
        elif args.mode == "ui":
            return subprocess.run([sys.executable,str(ROOT/"launch.py"),"--smoke-test",str(args.output.resolve())],cwd=ROOT,env=environment()).returncode
        else:
            from opencad.model import Document
            from opencad.commands import CommandBus
            from opencad.lisp import LispRuntime
            from opencad.interop import load_dxf,save_dxf
            if args.mode == "lsp":
                doc = Document()
                runtime = LispRuntime(CommandBus(doc))
                runtime.load(args.source)
                write(args.report,{"origin":"opencad","version":"0.1.0.dev0","source_sha256":hashlib.sha256(args.source.read_bytes()).hexdigest(),"result":semantic(doc),"output":runtime.output,"external_comparison":False})
            else:
                if args.source.resolve() == args.output.resolve():
                    raise ValueError("No sobrescribir el fixture original")
                if args.output.exists():
                    raise ValueError("La salida ya existe")
                doc = load_dxf(args.source)
                args.output.parent.mkdir(parents=True,exist_ok=True)
                save_dxf(doc,args.output)
                reopened = load_dxf(args.output)
                import ezdxf
                same = semantic(doc)==semantic(reopened)
                write(args.report,{"passed":same,"backend":"ezdxf","version":ezdxf.__version__,"external_comparison":False,"source_sha256":hashlib.sha256(args.source.read_bytes()).hexdigest(),"result":semantic(reopened)})
                return 0 if same else 1
    except (ValueError,OSError,KeyError,TypeError) as e:
        print(str(e),file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
