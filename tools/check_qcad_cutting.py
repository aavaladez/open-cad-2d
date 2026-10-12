"""Independent analytic boundaries for native TRIM/EXTEND/OFFSET and Qt/DXF."""
import argparse,hashlib,json,os,platform
from pathlib import Path
from unittest.mock import patch
from cad_workflow import ROOT,write
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtCore import Qt,qVersion
from PySide6.QtGui import QFont,QFontDatabase
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QPushButton
from opencad.app import MainWindow
from opencad.model import Point,Line,Circle
from opencad.qcad_views import Arc
from opencad.qcad_backend import QcadDocument,QcadCommandBus
from opencad.qcad_interop import inspect_dxf,native_inventory,equivalent


def main():
    p=argparse.ArgumentParser()
    for name in ('binary','source','qt','output'): p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args(); a.output.mkdir(parents=True,exist_ok=True); os.environ['OPENCAD_SCRATCH']=str(a.output.resolve())
    doc=QcadDocument(a.binary,a.source,a.qt); bus=QcadCommandBus(doc); checks={}; window=None
    near=lambda x,y:abs(x-y)<=1e-9
    def xyz(p,values): return all(near(x,y) for x,y in zip((p.x,p.y,p.z),values))
    def line(a,b): return bus.execute('LINE',a,b)[0]
    def rejected(name,action):
        before=doc.entities
        try: action()
        except ValueError: checks[name]=doc.entities==before
        else: checks[name]=False
    try:
        target=line('0,0,7','10,0,17'); boundary=line('6,-5,99','6,5,99'); base=doc.entities
        bus.execute('TR',str(boundary),str(target),'9,0')
        checks['trim_endpoint_analytic_z']=xyz(doc.entities[target].start,[0,0,7]) and xyz(doc.entities[target].end,[6,0,13])
        checks['boundary_unmodified']=doc.entities[boundary]==base[boundary]
        trimmed=doc.entities; bus.execute('UNDO'); checks['trim_single_undo']=doc.entities==base
        bus.execute('REDO'); checks['trim_redo']=doc.entities==trimmed; bus.execute('UNDO')
        bus.execute('TRIM',str(boundary),str(target),'1,0')
        checks['trim_start_analytic_z']=xyz(doc.entities[target].start,[6,0,13]) and xyz(doc.entities[target].end,[10,0,17])
        bus.execute('UNDO')
        circle=bus.execute('CIRCLE','5,0,50',2); base=doc.entities
        pieces=bus.execute('TRIM',str(circle),str(target),'5,0')
        checks['trim_circle_middle_split']=len(pieces)==2 and pieces[0]==target and xyz(doc.entities[target].end,[3,0,10]) and xyz(doc.entities[pieces[1]].start,[7,0,14])
        split=doc.entities; bus.execute('UNDO'); checks['trim_split_single_undo']=doc.entities==base
        bus.execute('REDO'); checks['trim_split_redo']=doc.entities==split; bus.execute('UNDO')
        poly=bus.execute('PLINE','2,-3,20','2,3,20','8,3,20','8,-3,20')
        pieces=bus.execute('TRIM',str(poly),str(target),'5,0')
        checks['trim_polyline_finite_edges']=len(pieces)==2 and xyz(doc.entities[target].end,[2,0,9]) and xyz(doc.entities[pieces[1]].start,[8,0,15])
        bus.execute('UNDO')
        arc=bus.execute('ARC','CENTER','5,0,30',2,0,180)
        arc_target=line('0,1,4','10,1,14'); pieces=bus.execute('TRIM',str(arc),str(arc_target),'5,1')
        checks['trim_arc_native_roots']=len(pieces)==2 and near(doc.entities[arc_target].end.x,5-3**.5) and near(doc.entities[pieces[1]].start.x,5+3**.5)
        checks['trim_arc_z_interpolated']=near(doc.entities[arc_target].end.z,9-3**.5)
        bus.execute('UNDO')
        below=line('0,-1,4','10,-1,14'); rejected('arc_support_circle_not_boundary',lambda:bus.execute('TRIM',str(arc),str(below),'5,-1'))
        far=line('6,3','6,5'); rejected('finite_boundary_no_imaginary_trim',lambda:bus.execute('TRIM',str(far),str(target),'9,0'))
        rejected('trim_pick_on_boundary_ambiguous',lambda:bus.execute('TRIM',str(boundary),str(target),'6,0'))
        rejected('trim_off_target_pick',lambda:bus.execute('TRIM',str(boundary),str(target),'9,2'))
        rejected('self_boundary_rejected',lambda:bus.execute('TRIM',str(target),str(target),'9,0'))
        short=line('0,10,7','4,10,11'); end1=line('8,9,80','8,11,80'); end2=line('12,9','12,11')
        base=doc.entities; bus.execute('EX',f'{end2},{end1}',str(short),'3,10')
        checks['extend_nearest_boundary_xyz']=xyz(doc.entities[short].end,[8,10,15])
        extended=doc.entities; bus.execute('UNDO'); checks['extend_single_undo']=doc.entities==base
        bus.execute('REDO'); checks['extend_redo']=doc.entities==extended; bus.execute('UNDO')
        start_edge=line('-3,9','-3,11'); bus.execute('EXTEND',str(start_edge),str(short),'1,10')
        checks['extend_start_xyz']=xyz(doc.entities[short].start,[-3,10,4]); bus.execute('UNDO')
        rejected('extend_midpoint_ambiguous',lambda:bus.execute('EXTEND',str(end1),str(short),'2,10'))
        rejected('extend_wrong_direction',lambda:bus.execute('EXTEND',str(end1),str(short),'1,10'))
        rejected('extend_finite_boundary_no_imaginary_edge',lambda:bus.execute('EXTEND',str(far),str(short),'3,10'))
        circle_edge=bus.execute('CIRCLE','10,10,30',2); bus.execute('EXTEND',str(circle_edge),str(short),'3,10')
        checks['extend_circle_nearest_root']=xyz(doc.entities[short].end,[8,10,15]); bus.execute('UNDO')
        arc_edge=bus.execute('ARC','CENTER','10,10,50',2,0,180)
        upper=line('0,11,7','4,11,11'); bus.execute('EXTEND',str(arc_edge),str(upper),'3,11')
        checks['extend_arc_native_root_z']=near(doc.entities[upper].end.x,10-3**.5) and near(doc.entities[upper].end.z,17-3**.5)
        bus.execute('UNDO')
        poly_edge=bus.execute('PLINE','8,9,50','8,11,50','12,11,50','12,9,50')
        bus.execute('EXTEND',str(poly_edge),str(short),'3,10')
        checks['extend_polyline_nearest_finite_edge']=xyz(doc.entities[short].end,[8,10,15]); bus.execute('UNDO')
        offset_line=line('0,20,7','10,20,17'); base=doc.entities
        copied=bus.execute('O',str(offset_line),2,'5,30,999')
        checks['offset_line_above_xyz']=copied not in base and xyz(doc.entities[copied].start,[0,22,7]) and xyz(doc.entities[copied].end,[10,22,17])
        checks['offset_source_intact']=all(doc.entities[i]==e for i,e in base.items())
        offset_view=doc.entities; bus.execute('UNDO'); checks['offset_single_undo']=doc.entities==base
        bus.execute('REDO'); checks['offset_redo']=doc.entities==offset_view; bus.execute('UNDO')
        copied=bus.execute('OFFSET',str(offset_line),3,'5,10')
        checks['offset_line_below_xyz']=xyz(doc.entities[copied].start,[0,17,7]); bus.execute('UNDO')
        oc=bus.execute('CIRCLE','30,20,9',5); copied=bus.execute('OFFSET',str(oc),2,'30,20,200')
        checks['offset_circle_inside_xy_not_z']=isinstance(doc.entities[copied],Circle) and doc.entities[copied].radius==3 and doc.entities[copied].center.z==9
        bus.execute('UNDO'); copied=bus.execute('OFFSET',str(oc),2,'40,20')
        checks['offset_circle_outside']=doc.entities[copied].radius==7; bus.execute('UNDO')
        oa=bus.execute('ARC','CENTER','50,20,11',5,350,30); copied=bus.execute('OFFSET',str(oa),2,'50,20,300')
        e=doc.entities[copied]; checks['offset_arc_inside_angles_xyz']=isinstance(e,Arc) and e.radius==3 and e.center.z==11 and near(e.start_angle,350) and near(e.end_angle,30)
        bus.execute('UNDO'); copied=bus.execute('OFFSET',str(oa),2,'60,20')
        checks['offset_arc_outside']=doc.entities[copied].radius==7; last_offset=doc.entities; bus.execute('UNDO')
        for name,args in [('offset_radius_zero',('OFFSET',str(oc),5,'30,20')),
                ('offset_radius_negative',('OFFSET',str(oc),6,'30,20')),
                ('offset_side_on_line',('OFFSET',str(offset_line),2,'25,20')),
                ('offset_side_on_arc_support',('OFFSET',str(oa),2,'50,25')),
                ('offset_nonpositive',('OFFSET',str(offset_line),0,'0,30')),
                ('offset_polyline_explicit_pending',('OFFSET',str(poly),2,'0,0')),
                ('trim_arc_target_explicit_pending',('TRIM',str(boundary),str(arc),'3,0'))]:
            rejected(name,lambda args=args:bus.execute(*args))
        bus.execute('REDO'); checks['redo_survives_cutting_errors']=doc.entities==last_offset; bus.execute('UNDO')
        bus.execute('LAYER','NEW','Limits'); bus.edit_properties({boundary},{'layer':'Limits'}); bus.execute('LAYER','LOCK','Limits')
        base=doc.entities; bus.execute('TRIM',str(boundary),str(target),'9,0')
        checks['locked_boundary_read_only']=xyz(doc.entities[target].end,[6,0,13]) and doc.entities[boundary]==base[boundary]
        bus.execute('UNDO'); checks['locked_boundary_target_undo']=doc.entities==base
        bus.execute('LAYER','LOCK','0')
        for name,args in [('trim_locked',('TRIM',str(boundary),str(target),'9,0')),
                ('extend_locked',('EXTEND',str(end1),str(short),'3,10')),
                ('offset_locked',('OFFSET',str(offset_line),2,'0,30'))]: rejected(name,lambda args=args:bus.execute(*args))
        bus.execute('LAYER','UNLOCK','0')
        app=QApplication.instance() or QApplication([])
        font=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/arial.ttf'
        if font.is_file():
            families=QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFont(str(font)))
            if families: app.setFont(QFont(families[0],10))
        window=MainWindow(doc); window.show(); app.processEvents(); window.ribbon.setCurrentIndex(3)
        buttons={b.text():b for b in window.findChildren(QPushButton)}
        def click(point): QTest.mouseClick(window.canvas,Qt.MouseButton.LeftButton,pos=window.canvas.screen(point).toPoint())
        window.selected={boundary}; window.refresh(); base=doc.entities
        QTest.mouseClick(buttons['Recortar'],Qt.MouseButton.LeftButton); QTest.keyClick(window.canvas,Qt.Key.Key_Escape)
        checks['ui_trim_escape_atomic']=doc.entities==base and window.selected=={boundary}
        QTest.mouseClick(buttons['Recortar'],Qt.MouseButton.LeftButton); click(Point(9,0))
        checks['ui_trim_selected_boundary']=xyz(doc.entities[target].end,[6,0,13]); window.cancel(); window.execute('UNDO')
        window.selected={end1}; window.refresh(); QTest.mouseClick(buttons['Alargar'],Qt.MouseButton.LeftButton); click(Point(3,10))
        checks['ui_extend_selected_boundary']=xyz(doc.entities[short].end,[8,10,15]); window.cancel()
        base=doc.entities
        with patch('opencad.app.QInputDialog.getDouble',return_value=(2,True)):
            QTest.mouseClick(buttons['Desfase'],Qt.MouseButton.LeftButton)
        click(Point(5,20)); QTest.keyClick(window.canvas,Qt.Key.Key_Escape)
        checks['ui_offset_escape_atomic']=doc.entities==base
        with patch('opencad.app.QInputDialog.getDouble',return_value=(2,True)):
            QTest.mouseClick(buttons['Desfase'],Qt.MouseButton.LeftButton)
        click(Point(5,20)); click(Point(5,30))
        checks['ui_offset_side']=len(doc.entities)==len(base)+1 and window.mode is None
        window.entry.setText(f'TRIM {boundary} {target} 9,0'); QTest.keyClick(window.entry,Qt.Key.Key_Return)
        checks['console_trim']=xyz(doc.entities[target].end,[6,0,13])
        window.canvas.fit(); app.processEvents()
        if not window.grab().save(str(a.output/'cutting.png')): raise RuntimeError('Capture failed')
        target_dxf=a.output/'modified.dxf'; expected=native_inventory(doc._view); doc.save_dxf(target_dxf)
        equivalent(expected,inspect_dxf(target_dxf)); doc.open_dxf(target_dxf); equivalent(expected,native_inventory(doc._view))
        checks['cutting_dxf_reopened']=True
        report=dict(kind='application_integration_partial',installed=False,platform=platform.platform(),
            python=platform.python_version(),qt=qVersion(),checks=checks,passed=all(v is True for v in checks.values()),
            identity=doc.request('hello'),engine_sha256=hashlib.sha256(a.binary.read_bytes()).hexdigest(),observed=doc._view,
            source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                [*ROOT.joinpath('native/adapter').glob('*.*'),*ROOT.joinpath('src/opencad').glob('*.py'),Path(__file__).resolve()]},
            limitations=['LINE targets for TRIM/EXTEND','OFFSET LINE/CIRCLE/ARC only','no AutoCAD execution','not installed'])
        write(a.output/'report.json',report); print(json.dumps(dict(passed=report['passed'],checks=checks)))
        return 0 if report['passed'] else 1
    finally:
        if window: window.close()
        else: doc.close()


if __name__=='__main__': raise SystemExit(main())
