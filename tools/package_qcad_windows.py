"""Stage the existing QCAD build and freeze it; never rebuild/modify the SDK."""
import argparse,hashlib,json,os,shutil,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,os.environ.get('OPENCAD_DEPS_DIR',str(ROOT/'.cache/python312')))
import pefile


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--qt',type=Path,default=ROOT/'.cache/qt/6.10.3/msvc2022_64')
    parser.add_argument('--source',type=Path,default=ROOT/'.cache/upstream/qcad')
    parser.add_argument('--engine',type=Path,default=ROOT/'build/native/opencad-qcad-engine.exe')
    parser.add_argument('--crt',type=Path,required=True); parser.add_argument('--output',type=Path,default=ROOT/'build/windows-package')
    args=parser.parse_args(); stage=args.output.resolve()
    if stage.exists():raise ValueError('Use an absent staging directory; never overwrite an existing package')
    stage.mkdir(parents=True); native=stage/'native'; native.mkdir()
    source=args.source.resolve(); qt=args.qt.resolve(); crt=args.crt.resolve()
    actual=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    if actual!='4c830eb4d80285ca64b1f2c2dc0987f729344126':raise ValueError('QCAD source pin mismatch')
    search=[source/'release',source/'plugins',qt/'bin',crt]
    index={p.name.lower():p for folder in reversed(search) for p in folder.glob('*.dll')}
    seeds=[args.engine.resolve(),qt/'plugins/platforms/qoffscreen.dll']
    queue=seeds[:]; seen=set(); dependencies=[]
    while queue:
        path=queue.pop(0)
        if path.name.lower() in seen:continue
        seen.add(path.name.lower())
        if path.name=='qoffscreen.dll':dest=native/'qt/plugins/platforms'/path.name
        elif path.suffix.lower()=='.exe':dest=native/path.name
        elif path.name.lower().startswith('qt6'):dest=native/'qt/bin'/path.name
        elif path.parent==source/'plugins':dest=native/'plugins'/path.name
        else:dest=native/'release'/path.name
        dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(path,dest)
        pe=pefile.PE(str(path)); imports=[]
        for attribute in ('DIRECTORY_ENTRY_IMPORT','DIRECTORY_ENTRY_DELAY_IMPORT'):
            imports.extend(item.dll.decode('ascii') for item in getattr(pe,attribute,[]))
        pe.close()
        for name in imports:
            key=name.lower()
            if key in index:queue.append(index[key])
            elif key.startswith(('api-ms-','ext-ms-')) or (Path(os.environ['WINDIR'])/'System32'/name).is_file():pass
            else:raise ValueError('Unresolved native dependency: '+name)
        dependencies.append({'path':str(dest.relative_to(stage)),'sha256':sha(dest),'imports':imports})
    (native/'qt.conf').write_text('[Paths]\nPrefix=qt\nPlugins=plugins\n',encoding='utf-8')
    licenses=stage/'licenses'; shutil.copytree(ROOT/'packaging/licenses',licenses)
    shutil.copyfile(ROOT/'LICENSE',licenses/'OPEN-CAD-GPL-3.0.txt')
    for name,path in {'QCAD-LICENSE.txt':source/'LICENSE.txt','opennurbs.txt':source/'src/3rdparty/opennurbs/LICENSE',
        'spatialindex.txt':source/'src/3rdparty/spatialindexnavel/COPYING',
        'stemmer.txt':source/'src/3rdparty/stemmer/bsd-2.txt'}.items():shutil.copyfile(path,licenses/name)
    shutil.copytree(qt/'sbom',licenses/'qt-sdk-sbom')
    sources=stage/'sources'; sources.mkdir()
    for name,folder in [('qcad-reviewed',source),('open-cad-base',ROOT)]:
        subprocess.run(['git','-C',str(folder),'archive','--format=zip','--output',str(sources/(name+'.zip')),'HEAD'],check=True,timeout=90)
    (sources/'QCAD-local-changes.patch').write_bytes(subprocess.check_output(['git','-C',str(source),'diff']))
    (sources/'OPEN-CAD-local-changes.patch').write_bytes(subprocess.check_output(['git','diff','--binary']))
    # Task-local additions are absent from HEAD until committed. Include them
    # explicitly without scanning caches, SDKs, user folders or ignored files.
    with zipfile.ZipFile(sources/'OPEN-CAD-additions.zip','w',compression=zipfile.ZIP_DEFLATED) as archive:
        for relative in ['src/opencad/runtime_paths.py','src/opencad/packaged_checks.py',
            'tools/package_qcad_windows.py','tools/prepare_inno.ps1','tools/verify_windows_install.ps1',
            'packaging/opencad-native.spec','packaging/windows/opencad-native.iss','docs/WINDOWS_A1_INSTALLATION.md']:
            archive.write(ROOT/relative,relative)
    (sources/'SOURCES.md').write_text('Development package, no public release. QCAD includes audited local modifications; OPEN CAD source snapshot includes current working tree. Qt6/PySide/Python and all binary dependency corresponding-source/license review remains required before public redistribution. See bundled Qt SDK SBOM and repository docs/THIRD_PARTY_NOTICES.md.\n',encoding='utf-8')
    record={'kind':'development_package','release':False,'revision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'qcad_revision':actual,'engine_sha256':sha(args.engine),'native_dependencies':dependencies,
        'licensing':'open distribution path; full corresponding-source bundle and binary license audit pending',
        'clean_windows_verified':False,'working_tree_changes':bool(subprocess.check_output(['git','status','--porcelain'],text=True).strip())}
    (stage/'build-identity.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    env=dict(os.environ); env['OPENCAD_NATIVE_STAGE']=str(stage)
    subprocess.run([sys.executable,'-m','PyInstaller','--noconfirm','--workpath',str(stage/'pyinstaller'),
        '--distpath',str(stage/'dist'),str(ROOT/'packaging/opencad-native.spec')],env=env,check=True)
    print(json.dumps({'stage':str(stage),'native_dependencies':len(dependencies)}))


if __name__=='__main__':main()
