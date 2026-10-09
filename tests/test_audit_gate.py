import copy
import hashlib
import json
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_gate import CASES, FREEZE, POLICY, artifact, evaluate, freeze
import audit_gate


class AuditGate(unittest.TestCase):
    """Synthetic controller tests; never evidence that the CAD meets A1."""
    def setUp(self):
        base = ROOT / "build/test-temp"
        base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.revision = "a" * 40
        self.candidate = self.save("application.exe", b"synthetic test binary") | {"revision": self.revision}
        self.assets = {role: self.save(role + ".txt", (role + " synthetic observation").encode()) for role in ("input", "observed", "log")}
        self.manifest = {"policy": POLICY, "candidate": self.candidate,
                         "criteria": {}, "findings": [], "audit_areas": {}}
        for criterion, cases in CASES.items():
            entry = {"status": "verified", "cases": {}}
            for case_id in cases:
                report = {"case": case_id, "kind": "application_functional", "application": "open-cad-2d",
                          "engine": "qcad", "method": "installed_ui", "revision": self.revision,
                          "build_sha256": self.candidate["sha256"], "platform": "Windows",
                          "command": "synthetic fixture for controller test only", "versions": {"test": "1"},
                          "exit_code": 0, "outcome": "passed", "checks": {"synthetic": True},
                          "artifacts": self.assets,
                          "independent_reference": {"engine": "ezdxf", "version": "1.4.3", "artifact": self.assets["observed"]}}
                entry["cases"][case_id] = self.save_json(criterion + "/" + case_id + ".json", report)
            self.manifest["criteria"][criterion] = entry

    def save(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return {"path": name, "sha256": hashlib.sha256(content).hexdigest()}

    def save_json(self, name, data):
        return self.save(name, json.dumps(data).encode())

    def change_case(self, criterion, case_id, **changes):
        reference = self.manifest["criteria"][criterion]["cases"][case_id]
        data = json.loads((self.root / reference["path"]).read_text())
        data.update(changes)
        self.manifest["criteria"][criterion]["cases"][case_id] = self.save_json(reference["path"], data)

    def result(self):
        return evaluate(self.manifest, self.root, self.revision)

    def test_six_cases_require_freeze_but_never_grant_approval(self):
        self.manifest["approval"] = True
        result = self.result()
        self.assertEqual(result["verified_count"], 6)
        self.assertEqual(result["state"], "audit_required")
        self.assertFalse(result["new_features_allowed"])
        self.assertFalse(result["next_phase_authorized"])
        self.assertEqual(result["audit_areas"]["security"], "not_reviewed")

    def test_internal_tests_or_flags_cannot_satisfy_entry(self):
        self.change_case("qcad_documents", "open_real_document", kind="unit_test")
        self.assertFalse(self.result()["entry_verified"])
        self.manifest["criteria"]["qcad_documents"]["cases"] = {}
        self.assertFalse(self.result()["entry_verified"])

    def test_stale_revision_and_changed_binary_invalidate_all(self):
        self.manifest["candidate"]["revision"] = "b" * 40
        self.assertEqual(self.result()["verified_count"], 0)
        self.manifest["candidate"]["revision"] = self.revision
        (self.root / "application.exe").write_bytes(b"different binary")
        self.assertEqual(self.result()["verified_count"], 0)

    def test_tampered_observation_or_failed_checks_rejected(self):
        (self.root / "observed.txt").write_text("altered")
        self.assertFalse(self.result()["entry_verified"])
        self.assets["observed"] = self.save("observed.txt", b"observed synthetic observation")
        self.change_case("functional_ui", "ribbon_console", checks={"failed": False})
        self.assertFalse(self.result()["entry_verified"])

    def test_portable_is_not_installation_and_same_engine_is_not_independent(self):
        self.change_case("windows_installation", "install", method="application_cli")
        self.assertFalse(self.result()["criteria"]["windows_installation"]["verified"])
        self.change_case("dxf_cycle", "independent_reader", independent_reference={"engine": "qcad", "version": "1"})
        self.assertFalse(self.result()["criteria"]["dxf_cycle"]["verified"])

    def test_blocking_findings_not_hidden_by_nonblocking_flag(self):
        self.manifest["findings"] = [{"id": "A1-001", "severity": "P1", "blocking": False,
            "problem": "loss", "action": "fix and repeat", "evidence": "log", "status": "open"}]
        result = self.result()
        self.assertEqual(result["blocking_findings"], ["A1-001"])
        self.assertFalse(result["next_phase_authorized"])

    def test_freeze_is_exclusive_and_regression_never_restarts_features(self):
        freeze(self.result(), self.root)
        before = (self.root / FREEZE).read_bytes()
        with self.assertRaises(FileExistsError):
            freeze(self.result(), self.root)
        self.change_case("functional_ui", "ribbon_console", exit_code=1)
        result = self.result()
        self.assertEqual(result["state"], "audit_corrections")
        self.assertFalse(result["new_features_allowed"])
        with self.assertRaises(ValueError):
            freeze(result, self.root)
        self.assertEqual((self.root / FREEZE).read_bytes(), before)

    def test_missing_criterion_or_outside_evidence_rejected(self):
        invalid = copy.deepcopy(self.manifest)
        del invalid["criteria"]["autolisp"]
        with self.assertRaises(ValueError):
            evaluate(invalid, self.root, self.revision)
        with self.assertRaises(ValueError):
            artifact(self.root, {"path": "../outside.txt", "sha256": "x"})

    def test_resolved_blocker_requires_current_resolution_evidence(self):
        finding = {"id": "A1-002", "severity": "P0", "problem": "loss",
                   "action": "fix", "evidence": "original log", "status": "resolved"}
        self.manifest["findings"] = [finding]
        self.assertEqual(self.result()["blocking_findings"], ["A1-002"])
        finding.update(verified_revision=self.revision, resolution_evidence=self.assets["log"])
        result = self.result()
        self.assertEqual(result["blocking_findings"], [])
        self.assertFalse(result["next_phase_authorized"])

    def test_cli_freeze_report_and_no_overwrite(self):
        manifest_path = self.root / "manifest.json"
        manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")
        report_path = self.root / "result.json"
        argv = ["--manifest", str(manifest_path), "--report", str(report_path), "--freeze"]
        with patch.object(audit_gate, "ROOT", self.root), patch("audit_gate.subprocess.check_output", return_value=self.revision):
            self.assertEqual(audit_gate.main(argv), 0)
            result = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertTrue(result["freeze_record_exists"])
            before = report_path.read_bytes()
            self.assertEqual(audit_gate.main(argv), 2)
            self.assertEqual(report_path.read_bytes(), before)
