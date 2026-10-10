"""Apply only reviewed patches to the pinned GPL QCAD source; never reset changes."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN = '4c830eb4d80285ca64b1f2c2dc0987f729344126'


def main():
    source = Path(sys.argv[1]).resolve()
    actual = subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    if actual != PIN:
        raise SystemExit('Re-auditar upstream antes de cambiar el pin.')
    command = ['git','-C',str(source),'apply']
    for name in ('qcad-msvc-link-paths.patch','qcad-dxf-z.patch','qcad-dxf-clayer.patch',
                 'qcad-dxf-layer-off.patch','qcad-dxf-off-import.patch'):
        patch = ROOT / 'native/patches' / name
        if subprocess.run(command+['--reverse','--check',str(patch)],capture_output=True).returncode == 0:
            print('Reviewed QCAD patch already applied: '+name)
            continue
        subprocess.run(command+['--check',str(patch)],check=True)
        subprocess.run(command+[str(patch)],check=True)
        print('Applied reviewed QCAD patch: '+name)


if __name__ == '__main__':
    main()
