"""Apply only the reviewed CMake patch, or confirm it is already present."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN = '4c830eb4d80285ca64b1f2c2dc0987f729344126'


def main():
    source = Path(sys.argv[1]).resolve()
    patch = ROOT / 'native/patches/qcad-msvc-link-paths.patch'
    actual = subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    if actual != PIN:
        raise SystemExit('Re-auditar upstream antes de cambiar el pin.')
    command = ['git','-C',str(source),'apply']
    if subprocess.run(command+['--reverse','--check',str(patch)],capture_output=True).returncode == 0:
        print('Reviewed QCAD patch already applied.')
        return
    subprocess.run(command+['--check',str(patch)],check=True)
    subprocess.run(command+[str(patch)],check=True)
    print('Applied reviewed QCAD CMake path patch.')


if __name__ == '__main__':
    main()
