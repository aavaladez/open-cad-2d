from pathlib import Path
import os
root=Path(SPECPATH).resolve().parent
stage=Path(os.environ['OPENCAD_NATIVE_STAGE']).resolve()
a=Analysis([str(root/'launch.py')],pathex=[str(root/'src')],binaries=[],
    datas=[(str(root/'src/opencad/commands.json'),'opencad'),(str(root/'examples'),'examples'),
           (str(root/'tools'),'tools'),(str(stage/'native'),'native'),(str(stage/'licenses'),'licenses'),
           (str(stage/'sources'),'sources'),
           *[(str(p),'native/adapter') for p in (root/'native/adapter').glob('*.*')],
           *[(str(p),'native/patches') for p in (root/'native/patches').glob('*.patch')],
           *[(str(p),'src/opencad') for p in (root/'src/opencad').glob('*.py')],
           (str(stage/'build-identity.json'),'.')],
    hiddenimports=['PySide6.QtTest','unittest.mock','opencad.packaged_checks'],
    hookspath=[],hooksconfig={},runtime_hooks=[],excludes=[],noarchive=False,optimize=0)
a.binaries=[item for item in a.binaries if Path(item[0]).name.lower() not in ('icuuc.dll','icudt78.dll')]
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,[],exclude_binaries=True,name='OPEN-CAD-2D',debug=False,strip=False,upx=False,console=False)
coll=COLLECT(exe,a.binaries,a.datas,strip=False,upx=False,name='OPEN-CAD-2D-Native')
