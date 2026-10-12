"""Crash the owned QCAD child only; verify acknowledged snapshot and private recovery."""
import argparse,hashlib,json,os,platform
from pathlib import Path
from unittest.mock import patch
from cad_workflow import ROOT,write
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtCore import Qt,qVersion
from PySide6.QtGui import QFont,QFontDatabase
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QPushButton,QMessageBox
from opencad.app import MainWindow
from opencad.lisp import LispRuntime
from opencad.model import Point
from opencad.qcad_backend import QcadDocument,QcadCommandBus
from opencad.qcad_interop import equivalent,native_inventory,inspect_dxf
from opencad.recovery import RecoveryStore


def main():
    p=argparse.ArgumentParser()
    for name in ('binary','source','qt','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args(); a.output.mkdir(parents=True,exist_ok=True); os.environ['OPENCAD_SCRATCH']=str(a.output.resolve())
    doc=QcadDocument(a.binary,a.source,a.qt); bus=QcadCommandBus(doc); lsp=LispRuntime(bus); window=None; checks={}
    store=RecoveryStore(a.output/'backups')
    try:
        lsp.load(ROOT/'examples/plan_a1.lsp'); bus.execute('PLANO_A1')
        original=a.output/'original.dxf'; doc.save_dxf(original); source_hash=hashlib.sha256(original.read_bytes()).hexdigest()
        bus.execute('MOVE',','.join(str(i) for i in doc.entities),'3,4,5')
        expected=native_inventory(doc._view); stable=doc.entities; metadata=store.checkpoint(doc)
        drawing,record,observed=store.read(metadata); equivalent(expected,observed)
        checks['acknowledged_private_checkpoint']=record['source']==str(original.resolve()) and record['entities']==7
        checks['checkpoint_original_unchanged']=source_hash==hashlib.sha256(original.read_bytes()).hexdigest()
        try:
            with doc.transaction():
                doc.add_circle(Point(300,0,7),8)
                checks['staging_is_not_confirmed']=len(doc._view['entities'])==8 and len(doc._confirmed_view['entities'])==7 and doc._view['transaction_active']
                checkpoint=store.checkpoint(doc); _,_,inventory=store.read(checkpoint); equivalent(expected,inventory)
                checks['checkpoint_ignores_staging']=True
                doc.process.kill(); doc.process.wait(timeout=5)
        except RuntimeError:checks['owned_child_failure_detected']=True
        checks['failed_staging_hidden_from_ui']=doc.entities==stable
        checks['confirmed_after_child_crash']=native_inventory(doc._confirmed_view)==expected
        store.restore(doc,metadata); equivalent(expected,native_inventory(doc._view))
        checks['recovered_real_qcad_document']=doc.request('hello')['engine']=='qcad' and doc.process.poll() is None
        checks['recovery_history_empty_source_detached']=doc.file_path is None
        before=doc.entities; doc.undo(); checks['recovery_undo_does_not_replay_failed_command']=doc.entities==before
        bus.execute('CIRCLE','250,0,7',6); checks['recover_then_edit']=len(doc.entities)==8
        destination=a.output/'recovered-copy.dxf'; doc.save_dxf(destination); expected2=native_inventory(doc._view)
        equivalent(expected2,inspect_dxf(destination)); doc.open_dxf(destination); equivalent(expected2,native_inventory(doc._view))
        checks['recovered_edit_save_reopen']=True
        good=store.checkpoint(doc); good_data=json.loads(good.read_text(encoding='utf-8'))
        invalid=good.parent/'invalid.json'; invalid.write_text(json.dumps(good_data|{'dxf':'../../original.dxf'}),encoding='utf-8')
        before=doc.entities
        try:store.restore(doc,invalid)
        except ValueError:checks['path_traversal_rejected']=doc.entities==before
        invalid.write_text(json.dumps(good_data|{'sha256':'0'*64}),encoding='utf-8')
        try:store.restore(doc,invalid)
        except ValueError:checks['tampered_hash_rejected']=doc.entities==before
        app=QApplication.instance() or QApplication([])
        font=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/arial.ttf'
        if font.is_file():
            families=QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFont(str(font)))
            if families:app.setFont(QFont(families[0],10))
        window=MainWindow(doc,recovery_root=a.output/'ui-backups'); window.show(); app.processEvents(); window.ribbon.setCurrentIndex(1)
        window.lisp.load(ROOT/'examples/plan_a1.lsp'); window.lisp.globals['OLDID']=123
        window.execute('LINE 300,0,7 320,0,7'); before=doc.entities; expected3=native_inventory(doc._view)
        QTest.qWait(1700); checks['ui_delayed_checkpoint_created']=window.recovery_pending is not None and window.recovery_pending.is_file()
        buttons={b.text():b for b in window.findChildren(QPushButton)}; doc.process.kill(); doc.process.wait(timeout=5)
        with patch('opencad.app.QMessageBox.question',return_value=QMessageBox.StandardButton.No):
            QTest.mouseClick(buttons['Restaurar respaldo'],Qt.MouseButton.LeftButton)
        checks['ui_cancel_does_not_replace_document']=doc.process.poll() is not None and doc.entities==before
        with patch('opencad.app.QMessageBox.question',return_value=QMessageBox.StandardButton.Yes):
            QTest.mouseClick(buttons['Restaurar respaldo'],Qt.MouseButton.LeftButton)
        equivalent(expected3,native_inventory(doc._view)); checks['ui_recover_last_acknowledged_document']=doc.process.poll() is None
        checks['ui_recovery_clears_stale_lisp_selection']=not window.lisp.functions and 'OLDID' not in window.lisp.globals and not window.selected
        checks['ui_recovery_notice']='Documento recuperado en QCAD' in window.history.toPlainText()
        window.execute('CIRCLE 350,0,7 10'); checks['ui_after_recovery_edits_qcad']=len(doc.entities)==len(before)+1
        window.canvas.fit(); app.processEvents()
        if not window.grab().save(str(a.output/'recovery.png')):raise RuntimeError('Capture failed')
        checks['original_still_unchanged']=source_hash==hashlib.sha256(original.read_bytes()).hexdigest()
        report=dict(kind='application_integration_partial',installed=False,platform=platform.platform(),python=platform.python_version(),qt=qVersion(),
            checks=checks,passed=all(v is True for v in checks.values()),identity=doc.request('hello'),engine_sha256=hashlib.sha256(a.binary.read_bytes()).hexdigest(),
            checkpoint=record,original_sha256=source_hash,observed=doc._view,
            limits=['confirmed state only','undo and LSP state reset','app crash may lose last1.5seconds','no hard power-loss guarantee','not installed'])
        write(a.output/'report.json',report); print(json.dumps(dict(passed=report['passed'],checks=checks)))
        return 0 if report['passed'] else 1
    finally:
        if window:window.close()
        else:doc.close()


if __name__=='__main__':raise SystemExit(main())
