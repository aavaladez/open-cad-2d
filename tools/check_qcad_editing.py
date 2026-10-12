"""Functional property/selection fixture on a real QCAD document and source UI."""
import argparse,hashlib,json,os,platform
from pathlib import Path
from cad_workflow import write
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QPushButton
from PySide6.QtGui import QFontDatabase,QFont
from opencad.app import MainWindow
from opencad.model import Point
from opencad.qcad_backend import QcadDocument,QcadCommandBus
from opencad.qcad_interop import native_inventory,inspect_dxf,equivalent


def main():
    p=argparse.ArgumentParser()
    for key in ('binary','source','qt','output'): p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args(); a.output.mkdir(parents=True,exist_ok=True); os.environ['OPENCAD_SCRATCH']=str(a.output.resolve())
    doc=QcadDocument(a.binary,a.source,a.qt); bus=QcadCommandBus(doc); window=None; checks={}
    def rejected(name,action):
        before=doc.entities
        try: action()
        except ValueError: checks[name]=doc.entities==before
        else: checks[name]=False
    try:
        line=bus.execute('LINE','0,0,7','10,0,9')[0]; circle=bus.execute('CIRCLE','20,0,11',5)
        other=bus.execute('LINE','30,30,4','40,40,4')[0]
        checks['point_projected_xy']=doc.select('point',Point(0,0),tolerance=.1)=={line}
        checks['window_contains']=doc.select('window',Point(-1,-1),Point(11,1))=={line}
        checks['crossing_intersects']=doc.select('crossing',Point(5,-1),Point(6,1))=={line}
        checks['window_excludes_partial']=not doc.select('window',Point(5,-1),Point(6,1))
        checks['circle_interior_not_curve']=not doc.select('crossing',Point(19,-1),Point(21,1))
        original=doc.entities
        bus.edit_properties({line},{'end':[12,4,9]})
        checks['native_endpoint_edited']=doc.entities[line].end==Point(12,4,9)
        edited=doc.entities; bus.execute('UNDO'); checks['property_undo']=doc.entities==original
        rejected('mixed_invalid_atomic',lambda:bus.edit_properties({line,circle},{'radius':4}))
        bus.execute('REDO'); checks['redo_after_rejected_property']=doc.entities==edited
        bus.edit_properties({circle},{'center':[22,2,11],'radius':6})
        checks['circle_properties']=doc.entities[circle].center==Point(22,2,11) and doc.entities[circle].radius==6
        rejected('invalid_radius_atomic',lambda:bus.edit_properties({circle},{'center':[50,50,50],'radius':-1}))
        rejected('zero_line_atomic',lambda:bus.edit_properties({line},{'end':[0,0,7]}))
        bus.execute('LAYER','NEW','Locked'); bus.execute('LAYER','LOCK','Locked')
        rejected('destination_locked',lambda:bus.edit_properties({line,other},{'layer':'Locked'}))
        bus.execute('LAYER','NEW','Edited')
        bus.edit_properties({line,other},{'layer':'Edited'})
        checks['batch_layer']=all(doc.entities[i].layer=='Edited' for i in (line,other))
        bus.execute('UNDO'); checks['batch_layer_single_undo']=all(doc.entities[i].layer=='0' for i in (line,other))
        bus.execute('LAYER','LOCK','0'); rejected('source_locked',lambda:bus.edit_properties({line},{'end':[20,20,9]}))
        bus.execute('LAYER','UNLOCK','0')
        app=QApplication.instance() or QApplication([])
        if not QFontDatabase.families():
            font=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/arial.ttf'
            if font.is_file(): QFontDatabase.addApplicationFont(str(font)); app.setFont(QFont('Arial',10))
        window=MainWindow(doc); window.show(); app.processEvents()
        def click(point,modifiers=Qt.KeyboardModifier.NoModifier):
            QTest.mouseClick(window.canvas,Qt.MouseButton.LeftButton,modifiers,pos=window.canvas.screen(point).toPoint()); app.processEvents()
        click(Point(0,0)); checks['ui_pick']=window.selected=={line}
        field=window.properties.fields['end']; field.setFocus(); field.selectAll(); QTest.keyClicks(field,'14,6,9')
        QTest.mouseClick(window.properties.apply,Qt.MouseButton.LeftButton)
        checks['ui_property_edit']=doc.entities[line].end==Point(14,6,9)
        window.execute('UNDO'); checks['ui_property_undo_sync']=window.properties.fields['end'].text()=='12,4,9'
        window.execute('REDO'); checks['ui_property_redo_sync']=window.properties.fields['end'].text()=='14,6,9'
        click(Point(28,2)); checks['ui_accumulate']=window.selected=={line,circle}
        click(Point(0,0),Qt.KeyboardModifier.ShiftModifier); checks['ui_shift_remove']=window.selected=={circle}
        QTest.keyClick(window.canvas,Qt.Key.Key_Escape); checks['ui_escape_clears']=not window.selected
        start=window.canvas.screen(Point(-1,-1)).toPoint(); end=window.canvas.screen(Point(15,7)).toPoint()
        QTest.mousePress(window.canvas,Qt.MouseButton.LeftButton,pos=start); QTest.mouseMove(window.canvas,end); QTest.mouseRelease(window.canvas,Qt.MouseButton.LeftButton,pos=end)
        checks['ui_window_drag']=window.selected=={line}
        move=next(b for b in window.ribbon.findChildren(QPushButton) if b.text()=='Mover selección')
        before=doc.entities[line]; QTest.mouseClick(move,Qt.MouseButton.LeftButton); click(Point(0,0)); click(Point(5,2))
        checks['ui_move_selection']=doc.entities[line].start==Point(5,2,7) and doc.entities[line].end==Point(19,8,9)
        window.execute('UNDO'); checks['move_selection_undo']=doc.entities[line]==before
        QTest.mouseClick(move,Qt.MouseButton.LeftButton); click(Point(0,0)); QTest.keyClick(window.canvas,Qt.Key.Key_Escape)
        checks['move_cancel_no_edit']=doc.entities[line]==before and window.mode is None
        QTest.keyClick(window.canvas,Qt.Key.Key_Escape)
        start=window.canvas.screen(Point(17,3)).toPoint(); end=window.canvas.screen(Point(15,1)).toPoint()
        QTest.mousePress(window.canvas,Qt.MouseButton.LeftButton,pos=start); QTest.mouseMove(window.canvas,end); QTest.mouseRelease(window.canvas,Qt.MouseButton.LeftButton,pos=end)
        checks['ui_crossing_drag']=window.selected=={circle}
        saved=a.output/'properties-edited.dxf'; doc.save_dxf(saved); expected=native_inventory(doc._view)
        equivalent(expected,inspect_dxf(saved)); doc.open_dxf(saved); equivalent(expected,native_inventory(doc._view))
        checks['properties_dxf_reopened']=True
        window.selected.clear(); window.refresh(); window.canvas.fit(); window.on_point(Point(28,2)); app.processEvents()
        checks['screenshot']=window.grab().save(str(a.output/'qcad-editing.png'))
        report=dict(kind='application_integration_partial',installed=False,platform=platform.platform(),checks=checks,
            passed=all(v is True for v in checks.values()),identity=doc.request('hello'),
            engine_sha256=hashlib.sha256(a.binary.read_bytes()).hexdigest(),observed=doc._view)
        write(a.output/'report.json',report); print(json.dumps(dict(passed=report['passed'],checks=checks)))
        return 0 if report['passed'] else 1
    finally:
        if window: window.close()
        else: doc.close()


if __name__=='__main__': raise SystemExit(main())
