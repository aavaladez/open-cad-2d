"""Exercise the real source UI, command bus and LSP against the QCAD adapter."""
import argparse
import hashlib
import json
import os
import platform
from pathlib import Path
from unittest.mock import patch
from cad_workflow import ROOT, write
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtCore import Qt,QPoint
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QPushButton
from PySide6.QtGui import QFontDatabase,QFont
from opencad.app import MainWindow
from opencad.qcad_backend import QcadDocument,QcadCommandBus
from opencad.lisp import LispRuntime
from opencad.model import Point


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',type=Path,required=True)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--qt',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    doc=QcadDocument(args.binary,args.source,args.qt)
    window=None
    checks={'lsp_error_rejected':False,'locked_layer_rejected':False,'layer_batch_error_rejected':False}
    try:
        bus=QcadCommandBus(doc); lsp=LispRuntime(bus)
        ids=bus.execute('L','0,0,7','3,4,7','6,4,7')
        checks['native_ids']=all(i>=0 and i in doc.entities for i in ids)
        checks['chain_z']=len(ids)==2 and all(e.end.z==7 for e in doc.entities.values())
        bus.execute('UNDO'); checks['chain_single_undo']=not doc.entities
        lsp.run('(defun C:NEGATIVE () (- 2))')
        checks['custom_numeric_result']=bus.execute('NEGATIVE')==-2
        # One script creates a layer, makes it current, draws and then locks it.
        lsp.run('(command "LAYER" "NEW" "Batch") (command "LAYER" "SET" "Batch") '
                '(command "LINE" \'(0 0 4) \'(3 4 4)) (command "LAYER" "LOCK" "Batch")')
        checks['staged_layer_batch']=len(doc.entities)==1 and doc.current_layer=='Batch' and doc.layers['Batch'].locked
        bus.execute('UNDO')
        checks['layer_batch_single_undo']=not doc.entities and 'Batch' not in doc.layers and doc.current_layer=='0'
        try:
            lsp.run('(command "LAYER" "NEW" "Failed") (command "LAYER" "SET" "Failed") '
                    '(command "CIRCLE" \'(1 2 3) 4) (missing-function)')
        except ValueError:
            checks['layer_batch_error_rejected']=True
        checks['layer_batch_rollback']=not doc.entities and 'Failed' not in doc.layers and doc.current_layer=='0'
        bus.execute('REDO')
        checks['layer_batch_redo_survives_error']=len(doc.entities)==1 and doc.current_layer=='Batch' and doc.layers['Batch'].locked
        bus.execute('UNDO')
        # Restore the original chain's redo branch after exercising layer history.
        bus.execute('L','0,0,7','3,4,7','6,4,7'); bus.execute('UNDO')
        # A failed LSP must preserve even the redo branch, with no failed edits.
        before=doc.entities
        try:
            lsp.run('(command "CIRCLE" \'(10 10 9) 3) (missing-function)')
        except ValueError:
            checks['lsp_error_rejected']=True
        checks['lsp_rollback']=doc.entities==before
        bus.execute('REDO'); checks['redo_survives_failed_lsp']=len(doc.entities)==2
        bus.execute('UNDO')
        lsp.load(ROOT/'examples/rectangle.lsp')
        checks['load_lsp_same_document']=len(doc.entities)==5 and 'C:MARCO' in lsp.functions
        bus.execute('UNDO'); checks['whole_lsp_undo']=not doc.entities
        bus.execute('REDO'); checks['whole_lsp_redo']=len(doc.entities)==5
        before=doc.entities
        bus.execute('LAYER','LOCK','0')
        try:
            bus.execute('MOVE',','.join(str(i) for i in before),'1,0,0')
        except ValueError:
            checks['locked_layer_rejected']=True
        checks['locked_no_geometry_change']=doc.entities==before
        bus.execute('UNDO')
        # Disposable Python projections cannot mutate QCAD.
        view=doc.entities; view.clear(); doc.request('snapshot')
        checks['projection_not_authoritative']=doc.entities==before
        app=QApplication.instance() or QApplication([])
        if not QFontDatabase.families():
            font=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/arial.ttf'
            if font.is_file(): QFontDatabase.addApplicationFont(str(font)); app.setFont(QFont('Arial',10))
        window=MainWindow(doc); window.show(); app.processEvents()
        window.entry.setFocus()
        QTest.keyClicks(window.entry,'CIRCLE 200,40,9 10')
        QTest.keyClick(window.entry,Qt.Key.Key_Return); app.processEvents()
        checks['console_edits_qcad']=len(doc.entities)==6 and any(getattr(e,'center',None)==Point(200,40,9) for e in doc.entities.values())
        buttons={b.text():b for b in window.ribbon.findChildren(QPushButton)}
        checks['pending_dxf_explicit']=not buttons['Abrir DXF · pendiente'].isEnabled() and 'DXF pendiente' in window.history.toPlainText()
        QTest.mouseClick(buttons['Línea'],Qt.MouseButton.LeftButton)
        QTest.mouseClick(window.canvas,Qt.MouseButton.LeftButton,pos=QPoint(100,100))
        QTest.keyClick(window.canvas,Qt.Key.Key_Escape)
        checks['ribbon_escape']=window.mode is None and len(doc.entities)==6
        QTest.mouseClick(buttons['Línea'],Qt.MouseButton.LeftButton)
        QTest.mouseClick(window.canvas,Qt.MouseButton.LeftButton,pos=QPoint(100,100))
        QTest.mouseClick(window.canvas,Qt.MouseButton.LeftButton,pos=QPoint(180,100))
        QTest.keyClick(window.canvas,Qt.Key.Key_Escape); app.processEvents()
        checks['ribbon_mouse_edits_qcad']=len(doc.entities)==7
        window.on_point(Point(210,40,9))
        checks['selection_properties']=bool(window.selected) and 'Circle' in window.properties.toPlainText()
        # Trigger the actual file-loading UI action with a deterministic selected file.
        window.ribbon.setCurrentIndex(1)
        with patch('opencad.app.QFileDialog.getOpenFileName',return_value=(str(ROOT/'examples/rectangle.lsp'),'AutoLISP')):
            QTest.mouseClick(buttons['Cargar LSP'],Qt.MouseButton.LeftButton)
        app.processEvents()
        checks['lsp_file_ui']=len(doc.entities)==12 and 'LSP cargado:' in window.history.toPlainText()
        window.entry.setFocus(); QTest.keyClicks(window.entry,'MARCO'); QTest.keyClick(window.entry,Qt.Key.Key_Return)
        checks['custom_console_command']=len(doc.entities)==17
        window.canvas.fit(); app.processEvents()
        checks['screenshot']=window.grab().save(str(args.output/'qcad-application.png'))
        report={'kind':'application_integration_partial','installed':False,
            'qcad_integrated':True,'platform':platform.platform(),
            'checks':checks,'passed':all(v is True for v in checks.values()),
            'engine_sha256':hashlib.sha256(args.binary.read_bytes()).hexdigest(),
            'qcad_dll_sha256':{name:hashlib.sha256((args.source/'release'/('qcad'+name+'.dll')).read_bytes()).hexdigest()
                               for name in ('core','entity','operations')},
            'dxf_dll_sha256':hashlib.sha256((args.source/'plugins/qcaddxf.dll').read_bytes()).hexdigest(),
            'identity':doc.request('hello'),'observed':doc._view,
            'limits':'LINE/CIRCLE/MOVE/ERASE/layers and bounded LSP; DXF UI and installer pending'}
        write(args.output/'report.json',report)
        print(json.dumps({'passed':report['passed'],'checks':checks}))
        return 0 if report['passed'] else 1
    finally:
        if window is not None: window.close()
        else: doc.close()


if __name__=='__main__':
    raise SystemExit(main())
