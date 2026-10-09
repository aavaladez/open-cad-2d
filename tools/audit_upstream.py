"""Record pinned source evidence. Presence does not establish functionality."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def audit(path, repo):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()
    sha = git("rev-parse", "HEAD")
    actions = {}
    if repo == "qcad/qcad":
        files = list((path / "scripts").rglob("*Init.js"))
        pattern = r"setDefaultCommands\(\[([^]]*)\]"
    else:
        files = list((path / "lcUILua").rglob("*.lua"))
        pattern = r"command_line\s*=\s*(\{[^}]*\}|\"[^\"]*\")"
    for p in sorted(files):
        text = p.read_text(encoding="utf-8", errors="replace")
        for group in re.findall(pattern, text):
            for command in re.findall(r'["\']([^"\']+)["\']', group):
                actions.setdefault(command.upper(), []).append({"path": p.relative_to(path).as_posix(),
                    "url": f"https://github.com/{repo}/blob/{sha}/{p.relative_to(path).as_posix()}",
                    "pro_marker": bool(re.search(r"requiresPro|setRequiresPro|QCAD Pro", text, re.I))})
    paths = ["README.md", "CMakeLists.txt", "LICENSE.txt", "LICENSE", "CMakeInclude.txt", "lckernel/LICENSE", "persistence/LICENSE"]
    evidence = []
    for relative in paths:
        p = path / relative
        if p.is_file():
            evidence.append({"path": relative, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "url": f"https://github.com/{repo}/blob/{sha}/{relative}"})
    return {"repository": repo, "sha": sha, "commit": git("log", "-1", "--format=%cs %s"),
            "evidence": evidence, "commands": actions, "build_executed": False}


if __name__ == "__main__":
    results = [audit(ROOT / ".cache/upstream/qcad", "qcad/qcad"), audit(ROOT / ".cache/upstream/librecad3", "LibreCAD/LibreCAD_3")]
    (ROOT / "requirements/upstream-evidence.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for r in results:
        print(r["repository"], r["sha"], len(r["commands"]), "registered names; not runtime coverage")
