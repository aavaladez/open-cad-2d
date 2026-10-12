"""Run the existing trusted functional fixtures from the installed package."""
import hashlib,json,os,platform,runpy,sys
from pathlib import Path
from .runtime_paths import backend_paths


def run(output):
    output=Path(output).resolve(); output.mkdir(parents=True,exist_ok=True)
    root=Path(sys._MEIPASS) if getattr(sys,'frozen',False) else Path(__file__).resolve().parents[2]
    os.environ['OPENCAD_RECOVERY_DIR']=str(output/'recovery-private')
    os.environ['OPENCAD_SCRATCH']=str(output)
    os.environ['QT_QPA_PLATFORM']='offscreen'
    binary,source,qt=backend_paths()
    tools=root/'tools'; sys.path.insert(0,str(tools))
    suites=['application','dxf','editing','transforms','curves','cutting','dimensions','lisp_essential','recovery']
    results={}; original=sys.argv[:]
    try:
        for name in suites:
            script=tools/('check_qcad_'+name+'.py')
            sys.argv=[str(script),'--binary',str(binary),'--source',str(source),'--qt',str(qt),'--output',str(output/name)]
            try:runpy.run_path(str(script),run_name='__main__')
            except SystemExit as exit:results[name]=exit.code==0
            else:results[name]=False
            if not results[name]:break
    finally:sys.argv=original
    record={'kind':'packaged_functional_regression','clean_environment_verified':False,
        'platform':platform.platform(),'application_sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
        'engine_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'results':results,
        'passed':len(results)==len(suites) and all(results.values()),'limits':['offscreen with deterministic dialogs','environment independence requires separate verification']}
    (output/'packaged-report.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    return 0 if record['passed'] else 1
