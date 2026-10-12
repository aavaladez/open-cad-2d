"""Analytic transform fixtures with actual QCAD transactions, console and DXF."""
import argparse,hashlib,json,os,platform,math
from pathlib import Path
from cad_workflow import write
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from opencad.app import MainWindow
from opencad.qcad_backend import QcadDocument,QcadCommandBus
from opencad.qcad_interop import inspect_dxf,native_inventory,equivalent


def main():
    p=argparse.ArgumentParser()
    for name in ('binary','source','qt','output'): p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args(); a.output.mkdir(parents=True,exist_ok=True); os.environ['OPENCAD_SCRATCH']=str(a.output.resolve())
    doc=QcadDocument(a.binary,a.source,a.qt); bus=QcadCommandBus(doc); window=None; checks={}
    def xyz(point,expected): return all(abs(x-y)<=1e-9 for x,y in zip((point.x,point.y,point.z),expected))
    def rejection(name,action):
        before=doc.entities
        try: action()
        except ValueError: checks[name]=doc.entities==before
        else: checks[name]=False
    try:
        line=bus.execute('LINE','0,0,7','3,4,9')[0]; circle=bus.execute('CIRCLE','10,20,9',3)
        original=doc.entities; selection=f'{line},{circle}'
        copied=bus.execute('CO',selection,'10,2,5')
        checks['copy_new_ids']=len(copied)==2 and len(doc.entities)==4 and set(copied).isdisjoint(original)
        clones=[doc.entities[i] for i in copied]
        checks['copy_line_xyz']=any(hasattr(e,'start') and xyz(e.start,[10,2,12]) and xyz(e.end,[13,6,14]) for e in clones)
        checks['copy_circle_xyz']=any(hasattr(e,'center') and xyz(e.center,[20,22,14]) and e.radius==3 for e in clones)
        checks['copy_original_untouched']=all(doc.entities[i]==e for i,e in original.items())
        copied_view=doc.entities; bus.execute('UNDO'); checks['copy_single_undo']=doc.entities==original
        bus.execute('REDO'); checks['copy_redo']=doc.entities==copied_view; bus.execute('UNDO')
        bus.execute('RO',selection,'0,0,100',90)
        checks['rotate_line_xy_z']=xyz(doc.entities[line].start,[0,0,7]) and xyz(doc.entities[line].end,[-4,3,9])
        checks['rotate_circle_xy_z']=xyz(doc.entities[circle].center,[-20,10,9]) and doc.entities[circle].radius==3
        rotated=doc.entities; bus.execute('UNDO'); checks['rotate_single_undo']=doc.entities==original
        bus.execute('REDO'); checks['rotate_redo']=doc.entities==rotated; bus.execute('UNDO')
        bus.execute('SC',selection,'1,2,100',2)
        checks['scale_line_xy_z']=xyz(doc.entities[line].start,[-1,-2,7]) and xyz(doc.entities[line].end,[5,6,9])
        checks['scale_circle_xy_z']=xyz(doc.entities[circle].center,[19,38,9]) and doc.entities[circle].radius==6
        scaled=doc.entities; bus.execute('UNDO'); checks['scale_single_undo']=doc.entities==original
        rejection('scale_zero_atomic',lambda:bus.execute('SCALE',selection,'0,0',0))
        rejection('unknown_id_atomic',lambda:bus.execute('COPY',str(line)+',9999999','1,2,3'))
        rejection('scale_overflow_atomic',lambda:bus.execute('SCALE',selection,'0,0',1e308))
        bus.execute('REDO'); checks['redo_after_errors']=doc.entities==scaled
        bus.execute('LAYER','LOCK','0')
        for name,args in [('COPY',('1,2,3',)),('ROTATE',('0,0',90)),('SCALE',('0,0',2))]:
            rejection(name+'_locked',lambda name=name,args=args:bus.execute(name,selection,*args))
        bus.execute('LAYER','UNLOCK','0')
        app=QApplication.instance() or QApplication([]); window=MainWindow(doc); window.show(); app.processEvents()
        window.entry.setFocus(); QTest.keyClicks(window.entry,f'COPY {line} 5,0,0'); QTest.keyClick(window.entry,Qt.Key.Key_Return)
        checks['console_copy']=len(doc.entities)==3
        window.execute('UNDO'); checks['console_copy_undo']=len(doc.entities)==2
        target=a.output/'transformed.dxf'; expected=native_inventory(doc._view); doc.save_dxf(target)
        equivalent(expected,inspect_dxf(target)); doc.open_dxf(target); equivalent(expected,native_inventory(doc._view))
        checks['transforms_dxf_reopened']=True
        report=dict(kind='application_integration_partial',installed=False,platform=platform.platform(),checks=checks,
            passed=all(v is True for v in checks.values()),engine_sha256=hashlib.sha256(a.binary.read_bytes()).hexdigest(),
            identity=doc.request('hello'),observed=doc._view)
        write(a.output/'report.json',report); print(json.dumps(dict(passed=report['passed'],checks=checks)))
        return 0 if report['passed'] else 1
    finally:
        if window: window.close()
        else: doc.close()


if __name__=='__main__': raise SystemExit(main())
