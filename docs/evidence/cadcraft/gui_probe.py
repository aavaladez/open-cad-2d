# SPDX-License-Identifier: GPL-3.0-or-later
import argparse,hashlib,json,os,socket,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--audit',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
r=a.audit.resolve(); out=a.output.resolve(); out.mkdir(exist_ok=False)
env=os.environ.copy(); env['CADCRAFT_CONFIG_DIR']=str(out/'profile'); env['WGPU_BACKEND']='dx12'
with socket.socket() as s: s.bind(('127.0.0.1',0)); port=s.getsockname()[1]
startup=subprocess.STARTUPINFO(); startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW; startup.wShowWindow=0
exe=r/'target/debug/cadcraft.exe'
proc=subprocess.Popen([str(exe),'--sample','--control',str(port)],env=env,stdout=(out/'stdout.log').open('w'),stderr=(out/'stderr.log').open('w'),startupinfo=startup)
log=[]; checks={}; seq=0
try:
    start=time.monotonic()
    while True:
        try: sock=socket.create_connection(('127.0.0.1',port),timeout=1); break
        except OSError:
            if proc.poll() is not None: raise RuntimeError('GUI exited '+str(proc.returncode))
            if time.monotonic()-start>30: raise TimeoutError('GUI control startup 30s')
            time.sleep(.25)
    sock.settimeout(15); f=sock.makefile('rw',encoding='utf-8')
    def call(method,params={}):
        global seq
        seq+=1; req={'id':seq,'method':method,'params':params}; f.write(json.dumps(req)+'\n'); f.flush(); res=json.loads(f.readline()); log.append({'request':req,'response':res})
        if not res.get('ok'): raise ValueError(res)
        return res.get('result')
    before=call('drawing.inspect',{'entities':True}); initial=before['counts'] if 'counts' in before else before
    call('engine.execute',{'command':'line','params':{'points':[[200,200],[203,204]]}})
    after=call('drawing.inspect',{'entities':True}); checks['native_gui_document_changed']=before!=after
    call('engine.execute',{'command':'undo','params':{}}); undone=call('drawing.inspect',{'entities':True})
    call('engine.execute',{'command':'redo','params':{}}); redone=call('drawing.inspect',{'entities':True})
    checks['undo_changed_snapshot']=after!=undone; checks['redo_changed_snapshot']=undone!=redone
    call('ui.menu.invoke',{'command':'line'}); active=call('cmdline.state'); call('cmdline.key',{'key':'escape'}); cancelled=call('cmdline.state'); checks['menu_prompt_escape']=active!=cancelled
    call('ui.set',{'layers':True,'properties':True}); state=call('ui.inspect'); (out/'ui-state.json').write_text(json.dumps(state,indent=2),encoding='utf-8')
    try:
        call('ui.screenshot',{'path':str(out/'screenshot.png')}); checks['screenshot']=(out/'screenshot.png').exists()
    except Exception as e: checks['screenshot']=False; checks['screenshot_error']=str(e)
except Exception as e: checks['runtime_error']=str(e)
finally:
    if proc.poll() is None: proc.terminate(); proc.wait(timeout=10)
(out/'transcript.json').write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'results.json').write_text(json.dumps({'checks':checks,'binary_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'startup':'hidden isolated Windows profile; DX12','port':port},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(checks,ensure_ascii=False))
