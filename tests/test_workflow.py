import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from cad_workflow import compare,make_spec,main


class Workflow(unittest.TestCase):
    def setUp(self):
        self.tmp_root = ROOT/"build/test-temp"
        self.tmp_root.mkdir(parents=True,exist_ok=True)
        self.baseline = {"origin":"analytic","version":"1","evidence":"distancia euclidiana 3-4-12","result":{"distance":13,"z":12}}
        self.actual = {"origin":"opencad","version":"0.1","result":{"distance":13.0000000001,"z":12}}

    def test_comparison_tolerance_detects_real_difference(self):
        self.assertTrue(compare(self.baseline,self.actual,1e-9)["passed"])
        self.actual["result"]["z"] = 0
        self.assertFalse(compare(self.baseline,self.actual,1e-9)["passed"])

    def test_no_self_generated_baseline_or_nonfinite(self):
        self.baseline["origin"] = "opencad"
        with self.assertRaises(ValueError):
            compare(self.baseline,self.actual,1e-9)
        self.baseline["origin"] = "analytic"
        for tolerance in (-1,float("nan"),float("inf")):
            with self.assertRaises(ValueError):
                compare(self.baseline,self.actual,tolerance)
        self.actual["result"]["distance"] = float("nan")
        self.assertFalse(compare(self.baseline,self.actual,1e-9)["passed"])

    def test_missing_fields_and_bool_numeric_difference(self):
        with self.assertRaises(ValueError):
            compare(self.baseline,{"result":13},1e-9)
        self.actual["result"]["z"] = True
        self.assertFalse(compare(self.baseline,self.actual,1e-9)["passed"])

    def test_spec_real_row_unknown_and_excluded(self):
        result = make_spec("ACAD-0002")
        self.assertEqual(result["requirement"]["command"],"LINE")
        self.assertEqual(result["status"],"spec_pending")
        self.assertFalse(any(result["acceptance"].values()))
        for identifier in ("ACAD-9999","ACAD-0354"):
            with self.assertRaises(ValueError):
                make_spec(identifier)

    def test_existing_contract_not_overwritten(self):
        with tempfile.TemporaryDirectory(dir=self.tmp_root) as temp:
            p = Path(temp)/"case.json"
            self.assertEqual(main(["spec","--id","ACAD-0002","--output",str(p)]),0)
            before = p.read_bytes()
            self.assertEqual(main(["spec","--id","ACAD-0002","--output",str(p)]),2)
            self.assertEqual(p.read_bytes(),before)

    def test_six_helper_entrypoints(self):
        paths = list((ROOT/".agents/skills").glob("*/scripts/*.py"))
        self.assertEqual(len(paths),6)
        for p in paths:
            run = subprocess.run([sys.executable,str(p),"--help"],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertIn("usage:",run.stdout)
