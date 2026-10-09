"""Build onedir portable; exclude unused Qt modules; collect license notices."""
import os
import shutil
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    deps = Path(os.environ.get("OPENCAD_DEPS_DIR",str(ROOT/".cache/python"))).resolve()
    sys.path[:0] = [str(ROOT/"src"),str(deps)]
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(ROOT/"src"),str(deps)])
    env["PYINSTALLER_CONFIG_DIR"] = str(ROOT/".cache/pyinstaller")
    env["TEMP"] = env["TMP"] = str(ROOT/"build/temp")
    (ROOT/"build/temp").mkdir(parents=True,exist_ok=True)
    command = [sys.executable,"-m","PyInstaller","--noconfirm","--clean",str(ROOT/"packaging/opencad.spec")]
    subprocess.run(command,cwd=ROOT,env=env,check=True)
    destination = ROOT/"dist/OPEN-CAD-2D"
    shutil.copy2(ROOT/"LICENSE",destination/"LICENSE")
    shutil.copy2(ROOT/"docs/THIRD_PARTY_NOTICES.md",destination/"THIRD_PARTY_NOTICES.md")
    shutil.copytree(ROOT/"packaging/licenses",destination/"licenses",dirs_exist_ok=True)
    shutil.copytree(ROOT/"examples",destination/"examples",dirs_exist_ok=True)
