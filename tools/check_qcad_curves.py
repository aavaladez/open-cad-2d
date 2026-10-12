"""Analytic ARC/straight PLINE fixtures through QCAD, Qt workflows and DXF."""
import argparse,hashlib,json,math,os,platform
from pathlib import Path
from cad_workflow import ROOT,write
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import ezdxf
from PySide6.QtCore import Qt,qVersion
from PySide6.QtGui import QFont,QFontDatabase
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QPushButton
from opencad.app import MainWindow
from opencad.model import Point
from opencad.qcad_views import Arc,Polyline
from opencad.qcad_backend import QcadDocument,QcadCommandBus
from opencad.qcad_interop import inspect_dxf,native_inventory,equivalent


def main():
    parser=argparse.ArgumentParser()
    for name in ('binary','source','qt','output'): parser.add_argument('--'+name,type=Path,required=True)
    a=parser.parse_args(); a.output.mkdir(parents=True,exist_ok=True)
    os.environ['OPENCAD_SCRATCH']=str(a.output.resolve())
    doc=QcadDocument(a.binary,a.source,a.qt); bus=QcadCommandBus(doc); window=None; checks={}; fixtures={}
    near=lambda x,y:abs(x-y)<=1e-9
    def xyz(p,v): return all(near(x,y) for x,y in zip((p.x,p.y,p.z),v))
    def reject(name,action):
        before=doc.entities
        try: action()
        except ValueError: checks[name]=doc.entities==before
        else: checks[name]=False
    try:
        arc=bus.execute('A','5,0,7','0,5,7','-5,0,7'); e=doc.entities[arc]
        checks['arc_three_points_analytic']=isinstance(e,Arc) and xyz(e.center,[0,0,7]) and near(e.radius,5) and near(e.start_angle,0) and near(e.end_angle,180)
        clockwise=bus.execute('ARC','5,0,7','0,-5,7','-5,0,7'); e=doc.entities[clockwise]
        checks['arc_clockwise_same_geometric_locus']=near(e.start_angle,180) and near(e.end_angle,0) and near(e.radius,5)
        crossing=bus.execute('ARC','CENTER','20,0,11',4,350,30); e=doc.entities[crossing]
        checks['arc_center_wraparound']=xyz(e.center,[20,0,11]) and near(e.start_angle,350) and near(e.end_angle,30)
        checks['arc_pick_xy_z_preserved']=doc.select('point',Point(0,5),tolerance=.1)=={arc}
        checks['arc_missing_half_not_selected']=doc.select('point',Point(20,4),tolerance=.1)==set()
        checks['arc_crossing_exact']=arc in doc.select('crossing',Point(-.1,4.9),Point(.1,5.1))
        checks['arc_window_exact']=doc.select('window',Point(-6,-.1),Point(6,6))=={arc}
        poly=bus.execute('PL','30,0,13','40,0,13','40,10,13'); original=doc.entities[poly]
        closed=bus.execute('PLINE','50,0,13','60,0,13','60,10,13','CLOSE')
        checks['pline_one_native_entity']=isinstance(original,Polyline) and len(original.vertices)==3 and not original.closed
        checks['pline_closed_flag']=doc.entities[closed].closed
        checks['pline_pick_xy']=doc.select('point',Point(35,0),tolerance=.1)=={poly}
        checks['pline_closing_edge_pick']=doc.select('point',Point(55,5),tolerance=.1)=={closed}
        checks['pline_crossing_segment']=poly in doc.select('crossing',Point(34,-1),Point(36,1))
        checks['pline_window_containment']=doc.select('window',Point(29,-1),Point(41,11))=={poly}
        selection=f'{arc},{poly}'; baseline=doc.entities
        copied=bus.execute('COPY',selection,'3,4,5')
        checks['curve_copy_new_ids']=len(copied)==2 and set(copied).isdisjoint(baseline) and len(doc.entities)==len(baseline)+2
        clones=[doc.entities[i] for i in copied]
        checks['arc_copy_xyz']=any(isinstance(e,Arc) and xyz(e.center,[3,4,12]) and near(e.radius,5) for e in clones)
        checks['pline_copy_xyz']=any(isinstance(e,Polyline) and xyz(e.vertices[-1],[43,14,18]) for e in clones)
        bus.execute('UNDO'); checks['curve_copy_single_undo']=doc.entities==baseline
        bus.execute('ROTATE',selection,'0,0,100',90)
        checks['arc_rotate_angles_z']=near(doc.entities[arc].start_angle,90) and near(doc.entities[arc].end_angle,270) and doc.entities[arc].center.z==7
        checks['pline_rotate_xyz']=xyz(doc.entities[poly].vertices[-1],[-10,40,13])
        bus.execute('UNDO'); checks['curve_rotate_single_undo']=doc.entities==baseline
        bus.execute('SCALE',selection,'0,0,100',2)
        checks['arc_scale_xy_z']=near(doc.entities[arc].radius,10) and doc.entities[arc].center.z==7
        checks['pline_scale_xy_z']=xyz(doc.entities[poly].vertices[-1],[80,20,13])
        scaled=doc.entities; bus.execute('UNDO'); checks['curve_scale_single_undo']=doc.entities==baseline
        for name,args in [('arc_collinear',('ARC','0,0','1,0','2,0')),
                ('arc_nonplanar',('ARC','1,0,0','0,1,1','-1,0,0')),
                ('arc_full_circle',('ARC','CENTER','0,0',5,0,360)),
                ('arc_invalid_radius',('ARC','CENTER','0,0',0,0,90)),
                ('pline_zero_segment',('PLINE','0,0','0,0','1,1')),
                ('pline_nonplanar',('PLINE','0,0,1','1,1,2')),
                ('pline_closed_too_few',('PLINE','0,0','1,1','C'))]:
            reject(name+'_atomic',lambda args=args:bus.execute(*args))
        bus.execute('REDO'); checks['curve_redo_after_errors']=doc.entities==scaled; bus.execute('UNDO')
        bus.edit_properties({arc},{'center':[1,2,9],'radius':6,'start_angle':270,'end_angle':30})
        checks['arc_properties']=xyz(doc.entities[arc].center,[1,2,9]) and near(doc.entities[arc].radius,6) and near(doc.entities[arc].start_angle,270)
        bus.execute('UNDO'); checks['arc_properties_undo']=doc.entities==baseline
        bus.edit_properties({poly},{'elevation':15,'closed':True})
        checks['pline_properties']=doc.entities[poly].closed and all(p.z==15 for p in doc.entities[poly].vertices)
        bus.execute('UNDO'); checks['pline_properties_undo']=doc.entities==baseline
        bus.edit_properties({poly},{'vertices':[[31,0,13],[41,0,13],[41,11,13]],'elevation':16})
        checks['pline_vertices_elevation_order']=xyz(doc.entities[poly].vertices[-1],[41,11,16])
        bus.execute('UNDO'); checks['pline_vertices_undo']=doc.entities==baseline
        reject('pline_invalid_vertices_atomic',lambda:bus.edit_properties({poly},{'vertices':[[0,0,1],[0,0,1]]}))
        reject('arc_invalid_angles_atomic',lambda:bus.edit_properties({arc},{'end_angle':360}))
        reject('mixed_properties_atomic',lambda:bus.edit_properties({poly,arc},{'radius':2}))
        bus.execute('LAYER','LOCK','0')
        reject('arc_locked_atomic',lambda:bus.execute('ARC','CENTER','0,0',3,0,90))
        reject('pline_locked_atomic',lambda:bus.execute('PLINE','0,0','1,1'))
        reject('curve_properties_locked',lambda:bus.edit_properties({poly},{'elevation':5}))
        bus.execute('LAYER','UNLOCK','0')
        for version in ('R2000','R2010'):
            source=a.output/(version+'-curves.dxf'); d=ezdxf.new(version); d.units=4
            d.layers.new('Survey',dxfattribs={'color':3}); d.header['$CLAYER']='Survey'
            attrs={'layer':'Survey'}
            d.modelspace().add_arc((0,0,7),5,0,180,dxfattribs=attrs)
            d.modelspace().add_arc((20,0,11),4,350,30,dxfattribs=attrs)
            d.modelspace().add_lwpolyline([(30,0),(40,0),(40,10)],format='xy',dxfattribs=attrs|{'elevation':13})
            d.modelspace().add_lwpolyline([(50,0),(60,0),(60,10)],format='xy',close=True,dxfattribs=attrs|{'elevation':15})
            d.saveas(source); digest=hashlib.sha256(source.read_bytes()).hexdigest(); fixtures[source.name]=digest
            expected=inspect_dxf(source); doc.open_dxf(source); equivalent(expected,native_inventory(doc._view))
            checks[version+'_native_import_elevation']=True
            ids=','.join(str(i) for i in doc.entities); bus.execute('MOVE',ids,'2,3,5')
            moved=native_inventory(doc._view); bus.execute('UNDO'); equivalent(expected,native_inventory(doc._view))
            bus.execute('REDO'); equivalent(moved,native_inventory(doc._view))
            target=a.output/(version+'-edited.dxf'); doc.save_dxf(target); equivalent(moved,inspect_dxf(target))
            doc.open_dxf(target); equivalent(moved,native_inventory(doc._view)); checks[version+'_edit_save_reopen']=True
            checks[version+'_original_unchanged']=digest==hashlib.sha256(source.read_bytes()).hexdigest()
        for name,attrs,points in [('bulge',{},[(0,0,1),(1,1,0)]),('width',{'const_width':2},[(0,0,0),(1,1,0)]),
                ('plinegen',{'flags':128},[(0,0,0),(1,1,0)])]:
            bad=a.output/(name+'.dxf'); d=ezdxf.new('R2010'); d.modelspace().add_lwpolyline(points,format='xyb',dxfattribs=attrs); d.saveas(bad)
            digest=hashlib.sha256(bad.read_bytes()).hexdigest()
            reject('unsupported_'+name+'_active_unchanged',lambda:doc.open_dxf(bad))
            checks['unsupported_'+name+'_input_unchanged']=digest==hashlib.sha256(bad.read_bytes()).hexdigest()
        app=QApplication.instance() or QApplication([])
        font=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/arial.ttf'
        if font.is_file():
            families=QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFont(str(font)))
            if families: app.setFont(QFont(families[0],10))
        window=MainWindow(doc); window.show(); app.processEvents(); window.ribbon.setCurrentIndex(2)
        buttons={b.text():b for b in window.findChildren(QPushButton)}
        def click(p): QTest.mouseClick(window.canvas,Qt.MouseButton.LeftButton,pos=window.canvas.screen(p).toPoint())
        count=len(doc.entities); QTest.mouseClick(buttons['Arco 3 puntos'],Qt.MouseButton.LeftButton)
        click(Point(5,20)); QTest.keyClick(window.canvas,Qt.Key.Key_Escape)
        checks['ribbon_arc_escape_atomic']=len(doc.entities)==count and window.mode is None
        QTest.mouseClick(buttons['Arco 3 puntos'],Qt.MouseButton.LeftButton)
        for p in (Point(5,20),Point(0,25),Point(-5,20)): click(p)
        checks['ribbon_arc_three_clicks']=len(doc.entities)==count+1 and window.mode is None
        QTest.mouseClick(buttons['Polilínea'],Qt.MouseButton.LeftButton)
        for p in (Point(10,20),Point(20,20),Point(20,30)): click(p)
        checks['pline_preview_not_committed']=len(doc.entities)==count+1
        QTest.keyClick(window.canvas,Qt.Key.Key_Escape); checks['pline_escape_atomic']=len(doc.entities)==count+1 and not window.pending_points
        QTest.mouseClick(buttons['Polilínea'],Qt.MouseButton.LeftButton)
        for p in (Point(10,20),Point(20,20),Point(20,30)): click(p)
        QTest.mouseClick(buttons['Cerrar polilínea'],Qt.MouseButton.LeftButton)
        checks['ribbon_pline_close']=len(doc.entities)==count+2 and window.mode is None
        latest=max(doc.entities); before=doc.entities
        window.execute('UNDO'); checks['ribbon_pline_single_undo']=len(doc.entities)==count+1
        window.execute('REDO'); checks['ribbon_pline_redo']=doc.entities==before
        window.selected={latest}; window.refresh()
        window.properties.fields['elevation'].setText('19'); QTest.mouseClick(window.properties.apply,Qt.MouseButton.LeftButton)
        checks['panel_pline_elevation']=all(p.z==19 for p in doc.entities[latest].vertices)
        window.entry.setText('ARC CENTER 35,25,17 8 20 160'); QTest.keyClick(window.entry,Qt.Key.Key_Return)
        checks['console_arc']=len(doc.entities)==count+3
        latest=max(doc.entities); window.selected={latest}; window.refresh()
        window.properties.fields['radius'].setText('9'); QTest.mouseClick(window.properties.apply,Qt.MouseButton.LeftButton)
        checks['panel_arc_radius']=doc.entities[latest].radius==9
        selected_arc=latest
        QTest.mouseClick(buttons['Polilínea'],Qt.MouseButton.LeftButton)
        for p in (Point(30,20),Point(30,30)): click(p)
        QTest.mouseClick(buttons['Finalizar polilínea'],Qt.MouseButton.LeftButton)
        checks['ribbon_pline_open']=len(doc.entities)==count+4 and not doc.entities[max(doc.entities)].closed
        QTest.mouseClick(buttons['Polilínea'],Qt.MouseButton.LeftButton)
        for p in (Point(40,20),Point(45,20),Point(45,30)): click(p)
        window.entry.setText('C'); QTest.keyClick(window.entry,Qt.Key.Key_Return)
        checks['pline_console_c_closes_not_circle']=len(doc.entities)==count+5 and doc.entities[max(doc.entities)].closed and window.mode is None
        QTest.mouseClick(buttons['Polilínea'],Qt.MouseButton.LeftButton)
        for p in (Point(35,20),Point(35,30)): click(p)
        QTest.keyClick(window.canvas,Qt.Key.Key_Return)
        checks['pline_canvas_enter_finishes']=len(doc.entities)==count+6 and not doc.entities[max(doc.entities)].closed and window.mode is None
        window.selected={selected_arc}; window.refresh()
        window.canvas.fit(); app.processEvents(); screenshot=a.output/'curves.png'
        if not window.grab().save(str(screenshot)): raise RuntimeError('Capture failed')
        target=a.output/'ui-curves.dxf'; expected=native_inventory(doc._view); doc.save_dxf(target)
        equivalent(expected,inspect_dxf(target)); doc.open_dxf(target); equivalent(expected,native_inventory(doc._view))
        checks['ui_curves_persist_reopened']=True
        report=dict(kind='application_integration_partial',installed=False,platform=platform.platform(),
            python=platform.python_version(),qt=qVersion(),ezdxf=ezdxf.__version__,checks=checks,passed=all(v is True for v in checks.values()),
            identity=doc.request('hello'),engine_sha256=hashlib.sha256(a.binary.read_bytes()).hexdigest(),
            native_dependencies={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                [*a.source.joinpath('release').glob('qcad*.dll'),a.source/'plugins/qcaddxf.dll']},
            source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in [ROOT/'native/adapter/session.cpp',ROOT/'tools/check_qcad_curves.py',
                    *ROOT.joinpath('src/opencad').glob('*.py'),*ROOT.joinpath('native/patches').glob('*.patch')]},
            fixtures=fixtures,observed=doc._view,limitations=['straight zero-width PLINE only','other ARC options pending','no AutoCAD execution','not installed'])
        write(a.output/'report.json',report); print(json.dumps(dict(passed=report['passed'],checks=checks)))
        return 0 if report['passed'] else 1
    finally:
        if window: window.close()
        else: doc.close()


if __name__=='__main__': raise SystemExit(main())
