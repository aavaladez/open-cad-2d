# SPDX-License-Identifier: GPL-3.0-or-later
"""Own synthetic audit cases. Never modifies original project drawings."""
import argparse, hashlib, json, math, os, platform, subprocess, time
from pathlib import Path
import ezdxf

p = argparse.ArgumentParser()
p.add_argument('--root', type=Path, required=True)
p.add_argument('--cli', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args(); a.root=a.root.resolve(); a.cli=a.cli.resolve(); a.out=a.out.resolve()
a.out.mkdir(parents=True, exist_ok=False)
os.environ['CADCRAFT_CONFIG_DIR']=str(a.out/'profile')
os.environ['QT_QPA_PLATFORM']='offscreen'
os.environ['OPENCAD_SCRATCH']=str(a.out)
from opencad.qcad_backend import QcadDocument, QcadCommandBus
from opencad.lisp import LispRuntime
from opencad.model import Point

def dump(name, data):
    (a.out/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

proc=subprocess.Popen([str(a.cli),'mcp'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=(a.out/'mcp.stderr').open('w'),text=True,encoding='utf-8')
transcript=[]; seq=0
def rpc(method, params):
    global seq
    seq+=1; req={'jsonrpc':'2.0','id':seq,'method':method,'params':params}
    proc.stdin.write(json.dumps(req)+'\n'); proc.stdin.flush()
    while True:
        line=proc.stdout.readline()
        if not line: raise RuntimeError('MCP closed')
        res=json.loads(line)
        if res.get('id')==seq: break
    transcript.append({'request':req,'response':res})
    if 'error' in res: raise ValueError(res['error'])
    return res.get('result')
def call(name, args={}):
    r=rpc('tools/call',{'name':name,'arguments':args})
    if r.get('isError'): raise ValueError(r)
    t=next((c['text'] for c in r.get('content',[]) if c['type']=='text'),'null')
    try: return json.loads(t)
    except json.JSONDecodeError: return t
def cc(cmd, params={}): return call('execute',{'command':cmd,'params':params})
rpc('initialize',{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'opencad-audit','version':'1'}})
dump('mcp-tools.json',rpc('tools/list',{}))
dump('runtime-commands.json',call('list_commands'))
doc=QcadDocument(a.root/'build/native/opencad-qcad-engine.exe',a.root/'.cache/upstream/qcad',a.root/'.cache/qt/6.10.3/msvc2022_64')
bus=QcadCommandBus(doc)
results=[]
def check(case, engine, action):
    t=time.perf_counter()
    try:
        detail=action(); passed=detail.pop('passed')
        results.append({'case':case,'engine':engine,'outcome':'passed' if passed else 'failed','seconds':time.perf_counter()-t,'detail':detail})
    except Exception as e:
        results.append({'case':case,'engine':engine,'outcome':'error','seconds':time.perf_counter()-t,'detail':{'error':str(e)}})
def near(x,y): return abs(x-y)<=1e-9
def freshcc(): call('new_drawing')
def savecc(name):
    f=a.out/name; call('save',{'path':str(f)}); return ezdxf.readfile(f)

def draw(engine):
    if engine=='cadcraft':
        freshcc(); cc('line',{'points':[[0,0],[3,4]]}); cc('circle',{'center':[10,10],'radius':2})
        d=savecc('draw-cc.dxf')
    else:
        bus.execute('LINE','0,0','3,4'); bus.execute('CIRCLE','10,10',2); doc.save_dxf(a.out/'draw-qcad.dxf'); d=ezdxf.readfile(a.out/'draw-qcad.dxf')
    line=list(d.modelspace().query('LINE'))[0]; circle=list(d.modelspace().query('CIRCLE'))[0]
    return {'passed':tuple(line.dxf.start)==(0,0,0) and tuple(line.dxf.end)==(3,4,0) and near(circle.dxf.radius,2),'types':[e.dxftype() for e in d.modelspace()]}
for engine in ['qcad','cadcraft']: check('draw-line-circle-xy',engine,lambda engine=engine:draw(engine))

def selectprops(engine):
    if engine=='cadcraft':
        cc('select',{'window':[[-1,-1],[20,20]]}); selected=call('inspect_drawing')
        cc('properties.set',{'handles':None,'layer':'0'})
        cc('move',{'delta':[1,2]}); cc('undo'); cc('redo'); d=savecc('move-cc.dxf')
    else:
        ids=doc.select('window',Point(-1,-1),Point(20,20)); selected=sorted(ids)
        bus.edit_properties(ids,{'layer':'0'}); bus.execute('MOVE',','.join(map(str,ids)),'1,2,0'); bus.execute('UNDO'); bus.execute('REDO')
        doc.save_dxf(a.out/'move-qcad.dxf'); d=ezdxf.readfile(a.out/'move-qcad.dxf')
    line=list(d.modelspace().query('LINE'))[0]
    return {'passed':tuple(line.dxf.start)==(1,2,0) and tuple(line.dxf.end)==(4,6,0),'selected':selected,'start':list(line.dxf.start),'end':list(line.dxf.end)}
for engine in ['qcad','cadcraft']: check('selection-properties-move-undo-redo',engine,lambda engine=engine:selectprops(engine))

def dimensions(engine):
    if engine=='cadcraft':
        cc('dimaligned',{'p1':[0,0],'p2':[30,40],'at':[-20,20]}); cc('dimlinear',{'p1':[0,0],'p2':[30,40],'at':[0,-10]}); cc('dimradius',{'center':[80,20],'point':[90,20]}); d=savecc('dims-cc.dxf')
    else:
        bus.execute('DIMALIGNED','0,0','30,40','-20,20'); bus.execute('DIMLINEAR','0,0','30,40','0,-10'); bus.execute('DIMRADIUS','80,20','90,20'); doc.save_dxf(a.out/'dims-qcad.dxf'); d=ezdxf.readfile(a.out/'dims-qcad.dxf')
    dims=list(d.modelspace().query('DIMENSION'))
    # Independent analytic measures from definition points. ezdxf 1.4.3's
    # get_measurement projects aligned dimensions on its default angle.
    measures=sorted(math.dist(e.dxf.defpoint2,e.dxf.defpoint3) if (e.dxf.dimtype & 15)==1 else float(e.get_measurement()) for e in dims)
    return {'passed':len(dims)==3 and all(near(x,y) for x,y in zip(measures,[10,30,50])),'measurements':measures}
for engine in ['qcad','cadcraft']: check('three-dimensions-analytic',engine,lambda engine=engine:dimensions(engine))

def lisp(engine):
    f=a.out/'audit.lsp'; text='(defun C:AUDITCAD () (command "LINE" \'(100 0 7) \'(103 4 9)))'; f.write_text(text,encoding='utf-8')
    if engine=='cadcraft':
        cc('appload',{'path':str(f)}); call('command_line',{'text':'AUDITCAD'}); d=savecc('lisp-cc.dxf')
    else:
        l=LispRuntime(bus); l.load(f); bus.execute('AUDITCAD'); doc.save_dxf(a.out/'lisp-qcad.dxf'); d=ezdxf.readfile(a.out/'lisp-qcad.dxf')
    line=next(e for e in d.modelspace().query('LINE') if near(e.dxf.start.x,100))
    return {'passed':tuple(line.dxf.start)==(100,0,7) and tuple(line.dxf.end)==(103,4,9),'start':list(line.dxf.start),'end':list(line.dxf.end)}
for engine in ['qcad','cadcraft']: check('appload-custom-command-xyz',engine,lambda engine=engine:lisp(engine))

def fixture(name,complex=False,n=0):
    d=ezdxf.new('R2010'); d.units=4; d.layers.new('Survey',dxfattribs={'color':3,'true_color':0x123456}); d.header['$CLAYER']='Survey'
    m=d.modelspace(); m.add_line((0,0,7),(3,4,9),dxfattribs={'layer':'Survey'}); m.add_circle((10,10,11),2,dxfattribs={'layer':'Survey'})
    if complex:
        d.appids.new('AUDITDATA'); list(m)[0].set_xdata('AUDITDATA',[(1000,'own-audit'),(1040,1.25)])
        b=d.blocks.new('OwnBlock'); b.add_line((0,0,2),(1,0,2)); m.add_blockref('OwnBlock',(20,20,3)); m.add_text('ámbito XYZ',dxfattribs={'insert':(5,5,4)})
        d.layouts.new('OwnSheet'); m.add_lwpolyline([(0,20,0,0,1),(5,20,0,0,0)],format='xyseb',dxfattribs={'elevation':8})
    for i in range(n): m.add_line((i,30,1),(i+1,31,2),dxfattribs={'layer':'Survey'})
    f=a.out/name; d.saveas(f); return f
def inventory(f):
    d=ezdxf.readfile(f); m=d.modelspace(); out={'types':{},'lines':[],'circles':[],'layers':[],'texts':[],'inserts':[],'xdata':[],'units':d.header.get('$INSUNITS'),'clayer':d.header.get('$CLAYER'),'layouts':list(d.layouts.names())}
    for e in m:
        t=e.dxftype(); out['types'][t]=out['types'].get(t,0)+1
        if t=='LINE': out['lines'].append([list(e.dxf.start),list(e.dxf.end),e.dxf.layer.upper()])
        if t=='CIRCLE': out['circles'].append([list(e.dxf.center),e.dxf.radius,e.dxf.layer.upper()])
        if t=='TEXT': out['texts'].append([e.dxf.text,list(e.dxf.insert)])
        if t=='INSERT': out['inserts'].append([e.dxf.name,list(e.dxf.insert)])
        if e.has_xdata('AUDITDATA'): out['xdata'].append([[tag.code,tag.value] for tag in e.get_xdata('AUDITDATA')])
    for l in d.layers:
        if l.dxf.name.upper()=='SURVEY': out['layers'].append([l.dxf.name.upper(),l.dxf.color,l.dxf.get('true_color'),l.dxf.flags])
    out['clayer']=out['clayer'].upper()
    audit=d.audit(); out['audit_errors']=len(audit.errors); out['audit_fixes']=len(audit.fixes)
    return out
basic=fixture('xyz-basic.dxf'); complexfile=fixture('complex.dxf',True)
for fname in [basic,complexfile]:
    baseline=inventory(fname); dump(fname.stem+'-baseline.json',baseline)
    for engine in ['qcad','cadcraft']:
        def cycle(engine=engine,fname=fname,baseline=baseline):
            dest=a.out/(fname.stem+'-'+engine+'.dxf')
            if engine=='cadcraft':
                call('open',{'path':str(fname)}); call('save',{'path':str(dest)}); call('open',{'path':str(dest)})
            else: doc.open_dxf(fname); doc.save_dxf(dest); doc.open_dxf(dest)
            after=inventory(dest); dump(dest.stem+'-inventory.json',after)
            return {'passed':after==baseline,'equal_inventory':after==baseline,'before':baseline,'after':after}
        check('dxf-cycle-'+fname.stem,engine,cycle)

for engine in ['qcad','cadcraft']:
    def zmove(engine=engine):
        if engine=='cadcraft':
            call('open',{'path':str(basic)}); cc('selectall'); cc('move',{'delta':[1,2,3]}); dest=a.out/'zmove-cc.dxf'; call('save',{'path':str(dest)})
        else:
            doc.open_dxf(basic); bus.execute('MOVE',','.join(map(str,doc.entities)),'1,2,3'); dest=a.out/'zmove-qcad.dxf'; doc.save_dxf(dest)
        after=inventory(dest); return {'passed':after['lines'][0][0]==[1,2,10] and after['lines'][0][1]==[4,6,12] and after['circles'][0][0]==[11,12,14],'after':after}
    check('move-xyz-delta',engine,zmove)

bad=a.out/'malformed.dxf'; bad.write_text('0\nSECTION\n2\nENTITIES\n0\nLINE\n10\nnot-a-number\n',encoding='ascii')
for engine in ['qcad','cadcraft']:
    def reject(engine=engine):
        before=call('inspect_drawing',{'entities':True}) if engine=='cadcraft' else doc.entities
        try:
            if engine=='cadcraft': call('open',{'path':str(bad)})
            else: doc.open_dxf(bad)
        except Exception as e:
            after=call('inspect_drawing',{'entities':True}) if engine=='cadcraft' else doc.entities
            return {'passed':before==after,'rejected':str(e),'active_preserved':before==after}
        after=call('inspect_drawing',{'entities':True}) if engine=='cadcraft' else doc.entities
        return {'passed':False,'error':'malformed input accepted','active_preserved':before==after,'before':before,'after':after}
    check('malformed-reject-active-preserved',engine,reject)

large=fixture('large-10000.dxf',n=10000)
for engine in ['qcad','cadcraft']:
    def largecase(engine=engine):
        if engine=='cadcraft':
            call('open',{'path':str(large)}); data=call('query_entities',{'type':'Line','limit':0}); return {'passed':data['count']==10001,'query':data}
        doc.open_dxf(large); return {'passed':len(doc.entities)==10002,'entities':len(doc.entities)}
    check('open-query-10000',engine,largecase)

def dwgcycle():
    call('open',{'path':str(basic)}); f=a.out/'basic.dwg'; call('save',{'path':str(f)}); call('open',{'path':str(f)}); d=a.out/'from-dwg.dxf'; call('save',{'path':str(d)})
    baseline=inventory(basic); after=inventory(d); return {'passed':after==baseline,'before':baseline,'after':after}
check('dwg-synthetic-bridge-cycle','cadcraft',dwgcycle)

# Analytic modification cases use the same line (0,0)-(3,4) in each engine.
for op in ['COPY','ROTATE','SCALE','ERASE','TRIM','EXTEND','OFFSET']:
    for engine in ['qcad','cadcraft']:
        def modification(op=op,engine=engine):
            if engine=='cadcraft':
                freshcc(); h=cc('line',{'points':[[0,0],[3,4]]})['handles'][0]
                if op=='COPY': cc('copy',{'handles':[h],'delta':[1,2]})
                elif op=='ROTATE': cc('rotate',{'handles':[h],'base':[0,0],'angle':90})
                elif op=='SCALE': cc('scale',{'handles':[h],'base':[0,0],'factor':2})
                elif op=='ERASE': cc('erase',{'handles':[h]}); cc('undo')
                elif op in ['TRIM','EXTEND']:
                    edge=cc('line',{'points':[[1.5,-10],[1.5,10]]})['handles'][0] if op=='TRIM' else cc('line',{'points':[[6,-10],[6,10]]})['handles'][0]
                    cc(op.lower(),{'handle':h,'edges':[edge],'pick':[3,4],'mode':'standard'})
                elif op=='OFFSET': cc('offset',{'handle':h,'distance':5,'side':[-4,3]})
                d=savecc('modify-'+op+'-cc.dxf')
            else:
                doc.open_dxf(basic); bus.execute('ERASE',','.join(map(str,doc.entities))); h=bus.execute('LINE','0,0','3,4')[0]
                if op=='COPY': bus.execute('COPY',str(h),'1,2,0')
                elif op=='ROTATE': bus.execute('ROTATE',str(h),'0,0',90)
                elif op=='SCALE': bus.execute('SCALE',str(h),'0,0',2)
                elif op=='ERASE': bus.execute('ERASE',str(h)); bus.execute('UNDO')
                elif op in ['TRIM','EXTEND']:
                    edge=bus.execute('LINE','1.5,-10','1.5,10')[0] if op=='TRIM' else bus.execute('LINE','6,-10','6,10')[0]
                    bus.execute(op,str(edge),str(h),'3,4')
                elif op=='OFFSET': bus.execute('OFFSET',str(h),5,'-4,3')
                f=a.out/('modify-'+op+'-qcad.dxf'); doc.save_dxf(f); d=ezdxf.readfile(f)
            lines=[(list(e.dxf.start),list(e.dxf.end)) for e in d.modelspace().query('LINE')]
            expected={'COPY':([1,2,0],[4,6,0]),'ROTATE':([0,0,0],[-4,3,0]),'SCALE':([0,0,0],[6,8,0]),'ERASE':([0,0,0],[3,4,0]),'TRIM':([0,0,0],[1.5,2,0]),'EXTEND':([0,0,0],[6,8,0]),'OFFSET':([-4,3,0],[-1,7,0])}[op]
            found=any(all(near(v,w) for v,w in zip(s+t,expected[0]+expected[1])) for s,t in lines)
            return {'passed':found,'expected':expected,'lines':lines}
        check('modify-'+op.lower()+'-analytic',engine,modification)

for engine in ['qcad','cadcraft']:
    def curves(engine=engine):
        if engine=='cadcraft':
            freshcc(); cc('arc',{'center':[0,0],'radius':5,'start':0,'end':90}); cc('pline',{'vertices':[[10,0],[15,0],[15,5]],'closed':True}); d=savecc('curves-cc.dxf')
        else:
            doc.open_dxf(basic); bus.execute('ERASE',','.join(map(str,doc.entities))); bus.execute('ARC','CENTER','0,0',5,0,90); bus.execute('PLINE','10,0','15,0','15,5','CLOSE'); f=a.out/'curves-qcad.dxf'; doc.save_dxf(f); d=ezdxf.readfile(f)
        arc=next(iter(d.modelspace().query('ARC'))); pl=next(iter(d.modelspace().query('LWPOLYLINE')))
        return {'passed':near(arc.dxf.radius,5) and near(arc.dxf.start_angle,0) and near(arc.dxf.end_angle,90) and pl.closed and len(pl)==3,'arc':[arc.dxf.radius,arc.dxf.start_angle,arc.dxf.end_angle],'pline':list(pl.get_points('xy'))}
    check('arc-pline-analytic',engine,curves)

for engine in ['qcad','cadcraft']:
    def failedlsp(engine=engine):
        text='(command "LINE" \'(200 0 0) \'(203 4 0)) (missing-function)'
        if engine=='cadcraft':
            freshcc(); before=call('query_entities',{'limit':0})['count']; r=cc('lisp',{'code':text}); after=call('query_entities',{'limit':0})['count']; rejected='error' in r
        else:
            before=len(doc.entities)
            try: LispRuntime(bus).run(text)
            except ValueError: rejected=True
            else: rejected=False
            after=len(doc.entities); r={'before':before,'after':after}
        return {'passed':rejected and before==after,'rejected':rejected,'before_count':before,'after_count':after,'response':r}
    check('failed-lsp-rollback',engine,failedlsp)
doc.close(); proc.stdin.close(); proc.wait(timeout=10)
dump('mcp-transcript.json',transcript)
dump('results.json',{'platform':platform.platform(),'python':platform.python_version(),'ezdxf':ezdxf.__version__,'qcad_binary_sha256':hashlib.sha256((a.root/'build/native/opencad-qcad-engine.exe').read_bytes()).hexdigest(),'cli_sha256':hashlib.sha256(a.cli.read_bytes()).hexdigest(),'tolerance':1e-9,'results':results})
print(json.dumps(results,ensure_ascii=False,indent=2))
