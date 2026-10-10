"""Application DXF acceptance with original fixtures and an independent reader."""
import argparse
import hashlib
import json
import platform
import os
from unittest.mock import patch
from pathlib import Path
from cad_workflow import ROOT,write
import ezdxf
from opencad.qcad_backend import QcadDocument,QcadCommandBus
from opencad.qcad_interop import inspect_dxf,native_inventory,equivalent
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtGui import QFontDatabase,QFont
from PySide6.QtWidgets import QApplication,QPushButton,QMessageBox
from opencad.app import MainWindow


def main():
    p=argparse.ArgumentParser()
    for name in ('binary','source','qt','output'): p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args(); a.output.mkdir(parents=True,exist_ok=True)
    os.environ['OPENCAD_SCRATCH']=str(a.output.resolve())
    doc=QcadDocument(a.binary,a.source,a.qt); bus=QcadCommandBus(doc)
    checks={}; fixtures=[]
    try:
        for version in ('R2000','R2010'):
            source=a.output/(version+'-source.dxf'); output=a.output/(version+'-edited.dxf')
            d=ezdxf.new(version); d.units=4
            d.layers.new('Survey',dxfattribs={'color':3})
            d.header['$CLAYER']='Survey'
            d.modelspace().add_line((0,0,7),(3,4,7),dxfattribs={'layer':'Survey'})
            d.modelspace().add_circle((10,20,9),3,dxfattribs={'layer':'Survey'})
            d.saveas(source); original_hash=hashlib.sha256(source.read_bytes()).hexdigest()
            doc.open_dxf(source)
            equivalent(inspect_dxf(source),native_inventory(doc._view))
            checks[version+'_open']=len(doc.entities)==2 and doc.units==4 and doc.current_layer=='Survey'
            bus.execute('MOVE',','.join(str(i) for i in doc.entities),'10,2,5')
            checks[version+'_edited_z']=any(getattr(e,'center',None) and e.center.z==14 for e in doc.entities.values())
            checks[version+'_analytic_move']=any(getattr(e,'start',None) and
                list((e.start.x,e.start.y,e.start.z))==[10,2,12] and list((e.end.x,e.end.y,e.end.z))==[13,6,12]
                for e in doc.entities.values()) and any(getattr(e,'center',None) and
                list((e.center.x,e.center.y,e.center.z))==[20,22,14] and e.radius==3 for e in doc.entities.values())
            doc.save_dxf(output)
            expected=native_inventory(doc._view); equivalent(expected,inspect_dxf(output))
            checks[version+'_independent_reader']=True
            bus.execute('UNDO'); equivalent(inspect_dxf(source),native_inventory(doc._view))
            bus.execute('REDO'); equivalent(expected,native_inventory(doc._view)); checks[version+'_save_preserves_undo_redo']=True
            doc.open_dxf(output); equivalent(expected,native_inventory(doc._view))
            checks[version+'_reopened']=len(doc.entities)==2
            checks[version+'_source_unchanged']=hashlib.sha256(source.read_bytes()).hexdigest()==original_hash
            fixtures.extend([dict(path=str(source),sha256=original_hash),dict(path=str(output),sha256=hashlib.sha256(output.read_bytes()).hexdigest())])
        # Reject unsupported content before the current QCAD session/history changes.
        before=doc._view.copy(); original_process=doc.process.pid
        unsupported=a.output/'unsupported.dxf'
        d=ezdxf.new('R2000'); d.modelspace().add_text('Must survive outside this subset'); d.saveas(unsupported)
        checks['unsupported_rejected']=False
        try: doc.open_dxf(unsupported)
        except ValueError: checks['unsupported_rejected']=True
        checks['failed_open_preserves_document']=doc._view==before and doc.process.pid==original_process
        # New layer attributes must also survive writing from the native document.
        bus.execute('LAYER','NEW','Ejes Norte'); bus.execute('LAYER','SET','Ejes Norte')
        bus.execute('LINE','20,30,6','25,30,6')
        created=a.output/'new-layer.dxf'; doc.save_dxf(created)
        equivalent(native_inventory(doc._view),inspect_dxf(created)); checks['created_layer_saved']=True
        bus.execute('LAYER','OFF','Ejes Norte'); bus.execute('LAYER','LOCK','Ejes Norte')
        doc.save_dxf(a.output/'locked-off.dxf')
        equivalent(native_inventory(doc._view),inspect_dxf(a.output/'locked-off.dxf')); checks['layer_flags_saved']=True
        expected=native_inventory(doc._view); doc.open_dxf(a.output/'locked-off.dxf')
        equivalent(expected,native_inventory(doc._view)); checks['layer_flags_reopened']=True
        app=QApplication.instance() or QApplication([])
        if not QFontDatabase.families():
            font=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/arial.ttf'
            if font.is_file(): QFontDatabase.addApplicationFont(str(font)); app.setFont(QFont('Arial',10))
        window=MainWindow(doc)
        window.show(); window.ribbon.setCurrentIndex(1); app.processEvents()
        buttons={b.text():b for b in window.ribbon.findChildren(QPushButton)}
        previous=doc._view.copy(); pid=doc.process.pid
        with (patch('opencad.app.QFileDialog.getOpenFileName',return_value=(str(source),'DXF')),
             patch('opencad.app.QMessageBox.question',return_value=QMessageBox.StandardButton.No)):
            QTest.mouseClick(buttons['Abrir DXF'],Qt.MouseButton.LeftButton)
        checks['ui_open_cancel']=doc._view==previous and doc.process.pid==pid
        with (patch('opencad.app.QFileDialog.getOpenFileName',return_value=(str(source),'DXF')),
             patch('opencad.app.QMessageBox.question',return_value=QMessageBox.StandardButton.Yes)):
            QTest.mouseClick(buttons['Abrir DXF'],Qt.MouseButton.LeftButton)
        checks['ui_open']=len(doc.entities)==2 and doc.current_layer.upper()=='SURVEY'
        window.entry.setFocus(); QTest.keyClicks(window.entry,'CIRCLE 40,30,11 5'); QTest.keyClick(window.entry,Qt.Key.Key_Return)
        ui_output=a.output/'ui-edited.dxf'
        with patch('opencad.app.QFileDialog.getSaveFileName',return_value=(str(ui_output),'DXF')):
            QTest.mouseClick(buttons['Guardar DXF'],Qt.MouseButton.LeftButton)
        equivalent(native_inventory(doc._view),inspect_dxf(ui_output)); checks['ui_edit_save']=len(doc.entities)==3
        with (patch('opencad.app.QFileDialog.getOpenFileName',return_value=(str(ui_output),'DXF')),
             patch('opencad.app.QMessageBox.question',return_value=QMessageBox.StandardButton.Yes)):
            QTest.mouseClick(buttons['Abrir DXF'],Qt.MouseButton.LeftButton)
        checks['ui_reopen']=len(doc.entities)==3
        window.canvas.fit(); app.processEvents()
        checks['screenshot']=window.grab().save(str(a.output/'qcad-dxf.png'))
        report=dict(kind='application_integration_partial',installed=False,qcad_integrated=True,
            platform=platform.platform(),identity=doc.request('hello'),checks=checks,passed=all(checks.values()),
            independent_reader='ezdxf',independent_reader_version=ezdxf.__version__,fixtures=fixtures,
            export_pipeline=doc.last_dxf_validation,
            engine_sha256=hashlib.sha256(a.binary.read_bytes()).hexdigest(),observed=doc._view)
        write(a.output/'report.json',report); print(json.dumps(dict(passed=report['passed'],checks=checks)))
        return 0 if report['passed'] else 1
    finally:
        if 'window' in locals(): window.close()
        else: doc.close()


if __name__=='__main__': raise SystemExit(main())
