from pathlib import Path
import sys

root = Path(SPECPATH).resolve().parent
a = Analysis(
    [str(root / 'launch.py')], pathex=[str(root / 'src')],
    binaries=[], datas=[(str(root / 'src/opencad/commands.json'), 'opencad'),
                        (str(root / 'examples'), 'examples')],
    hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=[], noarchive=False, optimize=0,
)
if sys.platform == 'win32':
    # Qt 6.10.3 uses Windows' ICU API. An unrelated Poppler ICU on PATH
    # shadows that system DLL and lacks its exports. Do not redistribute it.
    a.binaries = [item for item in a.binaries
                  if Path(item[0]).name.lower() not in ('icuuc.dll', 'icudt78.dll')]
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='OPEN-CAD-2D',
          debug=False, strip=False, upx=False, console=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='OPEN-CAD-2D')
