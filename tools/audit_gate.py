"""Collect A1 readiness evidence. Never grants next-phase approval or runs evidence code."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = "A1-2026-10-09"
CASES = {
    "qcad_documents": ("open_real_document", "edit_transaction_undo_redo", "persist_restart"),
    "functional_ui": ("ribbon_console", "layers_properties", "selection_cancel"),
    "essential_commands": ("draw", "modify", "select", "dimension", "undo_cancel"),
    "autolisp": ("load_lsp", "custom_command", "error_rollback"),
    "dxf_cycle": ("open_edit_save_reopen", "attributes_z_units", "independent_reader", "reject_loss"),
    "windows_installation": ("install", "installed_functional_workflow", "uninstall"),
}
AREAS = ("architecture", "code", "ui", "performance", "stability", "autolisp", "dxf",
         "technical_debt", "licenses", "dependencies", "security")
FREEZE = Path("docs/audits/first/freeze.json")


def artifact(root, reference):
    if not isinstance(reference, dict) or not isinstance(reference.get("path"), str):
        raise ValueError("Referencia de evidencia inválida")
    path = (root / reference["path"]).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("Evidencia ausente o fuera del repositorio")
    if not path.stat().st_size:
        raise ValueError("Evidencia vacía")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if reference.get("sha256") != digest:
        raise ValueError("Hash de evidencia no coincide")
    return path


def functional_case(root, case, candidate, case_id):
    report_path = artifact(root, case)
    data = json.loads(report_path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("Reporte funcional no es un objeto")
    if data.get("case") != case_id or data.get("kind") != "application_functional":
        raise ValueError("Se exige prueba funcional de aplicación, no test interno")
    if data.get("application") != "open-cad-2d" or data.get("engine") != "qcad":
        raise ValueError("Aplicación/backend de candidata no acreditados")
    if data.get("method") not in ("ui_e2e", "installed_ui", "application_cli"):
        raise ValueError("Método funcional no acreditado")
    if data.get("revision") != candidate["revision"] or data.get("build_sha256") != candidate["sha256"]:
        raise ValueError("Evidencia de otra candidata")
    if data.get("platform") != "Windows" or not data.get("command") or not data.get("versions"):
        raise ValueError("Falta plataforma, reproducción o versiones")
    if type(data.get("exit_code")) is not int or data["exit_code"] != 0 or data.get("outcome") != "passed":
        raise ValueError("Ejecución funcional fallida o incompleta")
    checks = data.get("checks")
    if not isinstance(checks, dict) or not checks or any(v is not True for v in checks.values()):
        raise ValueError("Faltan comprobaciones observadas o existen fallos")
    artifacts = data.get("artifacts", {})
    if not isinstance(artifacts, dict):
        raise ValueError("Inventario de artefactos inválido")
    for role in ("input", "observed", "log"):
        artifact(root, artifacts.get(role))
    if case_id == "independent_reader":
        reference = data.get("independent_reference", {})
        if reference.get("engine") in (None, "", "qcad", "open-cad-2d") or not reference.get("version"):
            raise ValueError("Se exige otro motor identificado para DXF")
        artifact(root, reference.get("artifact"))
    if case_id in ("install", "installed_functional_workflow", "uninstall") and data["method"] != "installed_ui":
        raise ValueError("Un portable o smoke CLI no acredita instalación Windows")
    return str(report_path.relative_to(root.resolve()))


def evaluate(manifest, root, revision):
    root = Path(root).resolve()
    if manifest.get("policy") != POLICY or set(manifest.get("criteria", {})) != set(CASES):
        raise ValueError("Política o seis criterios obligatorios inválidos")
    candidate = manifest.get("candidate")
    candidate_errors = []
    if candidate:
        try:
            if not isinstance(candidate, dict) or not isinstance(candidate.get("revision"), str):
                raise ValueError("Identidad de candidata inválida")
            if not re.fullmatch(r"[0-9a-f]{40}", candidate["revision"]) or candidate["revision"] != revision:
                raise ValueError("Commit de candidata ausente u obsoleto")
            artifact(root, candidate)
        except (ValueError, OSError) as error:
            candidate_errors.append(str(error))
    else:
        candidate_errors.append("Sin candidata instalada identificada")
    criteria = {}
    for key, required in CASES.items():
        entry = manifest["criteria"][key]
        if not isinstance(entry, dict) or not isinstance(entry.get("cases", {}), dict):
            raise ValueError("Criterio o casos inválidos: " + key)
        errors = list(candidate_errors)
        evidence = []
        if entry.get("status") != "verified":
            errors.append("Criterio pendiente o parcial")
        for case_id in required:
            case = entry.get("cases", {}).get(case_id)
            if case is None:
                errors.append("Sin prueba funcional: " + case_id)
            elif not candidate_errors:
                try:
                    evidence.append(functional_case(root, case, candidate, case_id))
                except (ValueError, OSError, KeyError, TypeError) as error:
                    errors.append(case_id + ": " + str(error))
        criteria[key] = {"verified": not errors, "errors": errors, "evidence": evidence,
                         "gap": entry.get("gap", "")}
    findings = manifest.get("findings", [])
    for finding in findings:
        if not isinstance(finding, dict) or finding.get("severity") not in ("P0", "P1", "P2", "P3") or not all(finding.get(k) for k in ("id", "problem", "action", "evidence")):
            raise ValueError("Defecto sin severidad, evidencia o acción correctiva")
    blockers, resolution_errors = [], {}
    for finding in findings:
        if finding["severity"] not in ("P0", "P1") and finding.get("blocking") is not True:
            continue
        resolved = False
        if finding.get("status") == "resolved":
            try:
                if finding.get("verified_revision") != revision:
                    raise ValueError("Resolución no verificada en candidata actual")
                artifact(root, finding.get("resolution_evidence"))
                resolved = True
            except (ValueError, OSError) as error:
                resolution_errors[finding["id"]] = str(error)
        if not resolved:
            blockers.append(finding["id"])
    ready = all(c["verified"] for c in criteria.values())
    frozen = (root / FREEZE).exists()
    areas = {area: manifest.get("audit_areas", {}).get(area, "not_reviewed") for area in AREAS}
    return {"policy": POLICY, "revision": revision, "candidate": candidate,
            "verified_count": sum(c["verified"] for c in criteria.values()),
            "entry_verified": ready, "freeze_record_exists": frozen,
            "state": "audit_required" if ready else "audit_corrections" if frozen else "development",
            "new_features_allowed": not ready and not frozen,
            "next_phase_authorized": False, "approval_required": True,
            "criteria": criteria, "audit_areas": areas, "findings": findings,
            "blocking_findings": blockers,
            "resolution_errors": resolution_errors,
            "limitation": "Hashes y metadatos no autentican una observación; revisar artefactos y reproducir flujos. No es una aprobación humana."}


def freeze(result, root):
    if not result["entry_verified"]:
        raise ValueError("No congelar candidata sin seis verificaciones funcionales")
    path = Path(root) / FREEZE
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"policy": POLICY, "candidate": result["candidate"], "next_phase_authorized": False}
    with path.open("x", encoding="utf-8") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)


def markdown(result):
    lines = ["# A1 — control de entrada a primera auditoría", "",
             "Este control no sustituye el informe integral ni autoriza la siguiente fase.", "",
             f"Estado: **{result['state']}**. Criterios funcionales: **{result['verified_count']}/6**.",
             f"Commit observado: `{result['revision']}`.", "",
             "| Criterio | Verificado | Pendientes / fallos |", "| --- | --- | --- |"]
    for key, item in result["criteria"].items():
        detail = "; ".join(item["errors"]) or "Evidencias hash verificadas; reproducir y revisar"
        lines.append(f"| {key} | {'Sí' if item['verified'] else 'No'} | {detail.replace('|', '/')} |")
    lines += ["", "## Auditoría integral", ""]
    lines += [f"- {key}: {value}" for key, value in result["audit_areas"].items()]
    lines += ["", "## Defectos y acciones", ""]
    for finding in result["findings"]:
        lines.append(f"- {finding['id']} ({finding['severity']}): {finding['problem']}; acción: {finding['action']}; evidencia: {finding['evidence']}")
    if not result["findings"]:
        lines.append("Sin hallazgos registrados; esto no acredita ausencia de defectos.")
    lines += ["", "Al verificar 6/6: detener funciones, congelar, auditar, corregir bloqueantes y PAUSAR.",
              "Siguiente fase: bloqueada hasta aprobación explícita del director y resolución de bloqueantes.",
              "", result["limitation"], ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT / "requirements/audit-gate.json")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args(argv)
    try:
        outputs = [p for p in (args.report, args.markdown) if p is not None]
        if len({p.resolve() for p in outputs}) != len(outputs) or any(p.exists() for p in outputs):
            raise ValueError("No sobrescribir reportes existentes; elegir una nueva salida")
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        result = evaluate(json.loads(args.manifest.read_text(encoding="utf-8-sig")), ROOT, revision)
        if args.freeze:
            freeze(result, ROOT)
            result["freeze_record_exists"] = True
        for path in outputs:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("x", encoding="utf-8") as stream:
                stream.write(markdown(result) if path == args.markdown else json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        print(f"A1: {result['verified_count']}/6, {result['state']}; siguiente fase sin autorización")
        return 0 if result["entry_verified"] else 1
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print(str(error))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
