# SPDX-License-Identifier: GPL-3.0-or-later
import argparse,hashlib,json,os,platform,statistics,subprocess,time
from pathlib import Path
import ezdxf
from opencad.qcad_backend import QcadDocument
p=argparse.ArgumentParser(); p.add_argument('--root',type=Path,required=True); p.add_argument('--audit',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
r=a.audit.resolve(); root=a.root.resolve(); out=a.output.resolve(); out.mkdir(exist_ok=False)
os.environ['OPENCAD_SCRATCH']=str(out); os.environ['QT_QPA_PLATFORM']='offscreen'
results=[]
for n in [1000,10000,100000]:
    d=ezdxf.new('R2010'); m=d.modelspace()
    for i in range(n): m.add_line((i,0,7),(i+1,1,9))
    f=out/f'{n}.dxf'; d.saveas(f)
    for engine in ['cadcraft','qcad']:
        trials=[]
        for trial in range(3):
            doc=None; t=time.perf_counter()
            try:
                if engine=='cadcraft':
                    p=subprocess.run([str(r/'target/debug/cadcraft-cli.exe'),'info',str(f)],capture_output=True,text=True,encoding='utf-8',timeout=30)
                    data=json.loads(p.stdout); count=data['counts']['Line']; assert p.returncode==0
                else:
                    doc=QcadDocument(root/'build/native/opencad-qcad-engine.exe',root/'.cache/upstream/qcad',root/'.cache/qt/6.10.3/msvc2022_64'); doc.open_dxf(f); count=len(doc.entities)
                trials.append({'seconds':time.perf_counter()-t,'outcome':'passed' if count==n else 'failed','count':count})
            except Exception as e: trials.append({'seconds':time.perf_counter()-t,'outcome':'error','error':str(e)})
            finally:
                if doc: doc.close()
        results.append({'n':n,'engine':engine,'bytes':f.stat().st_size,'fixture_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'trials':trials,'median_seconds':statistics.median(x['seconds'] for x in trials)})
        print(n,engine,[(round(x['seconds'],3),x['outcome']) for x in trials],flush=True)
(out/'results.json').write_text(json.dumps({'platform':platform.platform(),'method':'fresh CLI info or QcadDocument constructor/open/entities; different validation costs; three trials; no peak memory or rendering','results':results},ensure_ascii=False,indent=2),encoding='utf-8')
