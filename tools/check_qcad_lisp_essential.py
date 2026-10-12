"""Custom LSP loading and essential-command batches over the real QCAD document."""
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
from opencad.qcad_backend import QcadDocument,QcadCommandBus
from opencad.qcad_interop import native_inventory,inspect_dxf,equivalent
from opencad.lisp import LispRuntime


def main():
    p=argparse.ArgumentParser()
    for name in ('binary','source','qt','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args(); a.output.mkdir(parents=True,exist_ok=True); os.environ['OPENCAD_SCRATCH']=str(a.output.resolve())
    doc=QcadDocument(a.binary,a.source,a.qt); bus=QcadCommandBus(doc); lsp=LispRuntime(bus); window=None; checks={}
    fixture=ROOT/'examples/plan_a1.lsp'; digest=hashlib.sha256(fixture.read_bytes()).hexdigest()
    def same_xyz(p,values):return all(abs(a-b)<=1e-9 for a,b in zip((p.x,p.y,p.z),values))
    try:
        before=doc.entities; lsp.load(fixture)
        checks['lsp_definitions_load_without_drawing']=doc.entities==before and 'C:PLANO_A1' in lsp.functions and 'CAD_AJUSTAR' in lsp.functions
        result=bus.execute('PLANO_A1'); inventory=native_inventory(doc._view)
        checks['custom_command_result']=result=='Plano LSP creado'
        counts={t:sum(e['type']==t for e in inventory['entities']) for t in ('LINE','CIRCLE','ARC','LWPOLYLINE','DIMENSION')}
        checks['lsp_native_entity_types']=counts==dict(LINE=1,CIRCLE=1,ARC=1,LWPOLYLINE=1,DIMENSION=3)
        checks['lsp_polyline_native_vertices']=any(e['type']=='LWPOLYLINE' and e['closed'] and e['vertices']==[[0,0,7],[40,0,7],[40,30,7],[0,30,7]] for e in inventory['entities'])
        checks['lsp_arc_analytic']=any(e['type']=='ARC' and all(abs(x-y)<=1e-9 for x,y in zip(e['center'],[60,0,7])) and
            abs(e['radius']-10)<=1e-9 and abs(e['start_angle'])<=1e-9 and abs(e['end_angle']-180)<=1e-9 for e in inventory['entities'])
        checks['lsp_dimensions_analytic']=sorted(e.render['measurement'] for e in doc.entities.values() if hasattr(e,'render'))==[10,40,50]
        base=doc.entities; layers=dict(doc.layers)
        lsp.run('(command "LAYER" "NEW" "LSP-Cotas") (command "LAYER" "SET" "LSP-Cotas") '
                '(command "DIMALIGNED" \'(0 0 7) \'(3 4 7) \'(0 6 7)) (command "LAYER" "LOCK" "LSP-Cotas")')
        checks['lsp_layer_dimension_lock_batch']=len(doc.entities)==len(base)+1 and doc.current_layer=='LSP-Cotas' and doc.layers['LSP-Cotas'].locked
        bus.execute('UNDO'); checks['lsp_layer_dimension_batch_undo']=doc.entities==base and doc.layers==layers
        drawn=doc.entities; bus.execute('UNDO'); checks['lsp_drawing_batch_single_undo']=not doc.entities
        bus.execute('REDO'); checks['lsp_drawing_batch_redo']=doc.entities==drawn
        target=a.output/'lsp-plan.dxf'; expected=native_inventory(doc._view); doc.save_dxf(target); equivalent(expected,inspect_dxf(target))
        doc.open_dxf(target); equivalent(expected,native_inventory(doc._view)); checks['lsp_geometry_dimensions_dxf']=True
        # Work on separate existing LINE geometry. IDs are bridge IDs, not ENAMEs.
        target_id=bus.execute('LINE','0,0,7','10,0,17')[0]
        cut=bus.execute('LINE','6,-5,99','6,5,99')[0]; limit=bus.execute('LINE','10,-5,99','10,5,99')[0]
        base=doc.entities; result=lsp.run(f'(cad_ajustar {target_id} {cut} {limit})')
        checks['lsp_modify_result']=result=='Ajuste LSP creado'
        checks['lsp_trim_extend_rotate_scale_xyz']=same_xyz(doc.entities[target_id].start,[0,0,7]) and same_xyz(doc.entities[target_id].end,[0,20,17])
        copies=[e for i,e in doc.entities.items() if i not in base]
        checks['lsp_offset_xyz']=any(hasattr(e,'start') and same_xyz(e.start,[0,2,7]) and same_xyz(e.end,[10,2,17]) for e in copies)
        checks['lsp_copy_xyz']=any(hasattr(e,'start') and same_xyz(e.start,[0,5,10]) and same_xyz(e.end,[10,5,20]) for e in copies)
        checks['lsp_modify_boundaries_unchanged']=doc.entities[cut]==base[cut] and doc.entities[limit]==base[limit]
        modified=doc.entities; bus.execute('UNDO'); checks['lsp_modify_single_undo']=doc.entities==base
        # Errors revert geometry, layers, variables, functions and output, preserving redo.
        state=(dict(lsp.globals),dict(lsp.functions),list(lsp.output))
        try:lsp.run('(setq partial 1) (defun failed () 3) (command "ARC" "CENTER" \'(0 0 7) 5 0 90) (princ "partial") (missing-function)')
        except ValueError:checks['lsp_partial_error_rejected']=True
        checks['lsp_partial_full_rollback']=doc.entities==base and state==(lsp.globals,lsp.functions,lsp.output)
        bus.execute('REDO'); checks['lsp_redo_after_failed_batch']=doc.entities==modified
        aliases=dict(bus.aliases)
        try:bus.set_aliases({'NOFILE':'OPEN'})
        except ValueError:checks['undefined_file_alias_config_blocked']=bus.aliases==aliases
        bus.set_aliases({'BACK':'UNDO','ARCO':'ARC'})
        for name,code in [('alias_file_blocked','(command "NOFILE" "x.dxf")'),('alias_history_blocked','(command "BACK")'),
                ('process_blocked','(startapp "cmd")'),('network_com_blocked','(vlax-create-object "X")')]:
            before=doc.entities
            try:lsp.run(code)
            except ValueError:checks[name]=doc.entities==before
            else:checks[name]=False
        before=doc.entities; result=lsp.run('(command "ARCO" "CENTER" \'(200 0 7) 10 0 90)')
        checks['lsp_allowed_alias_nil']=result is None and len(doc.entities)==len(before)+1
        bus.execute('UNDO'); checks['lsp_allowed_alias_undo']=doc.entities==before
        bus.execute('LAYER','LOCK','0'); before=doc.entities
        try:bus.execute('PLANO_A1')
        except ValueError:checks['lsp_locked_batch_atomic']=doc.entities==before
        bus.execute('LAYER','UNLOCK','0')
        app=QApplication.instance() or QApplication([])
        font=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/arial.ttf'
        if font.is_file():
            families=QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFont(str(font)))
            if families:app.setFont(QFont(families[0],10))
        window=MainWindow(doc); window.show(); app.processEvents(); window.ribbon.setCurrentIndex(1)
        buttons={b.text():b for b in window.findChildren(QPushButton)}; before=doc.entities
        with patch('opencad.app.QFileDialog.getOpenFileName',return_value=(str(fixture),'AutoLISP')):
            QTest.mouseClick(buttons['Cargar LSP'],Qt.MouseButton.LeftButton)
        checks['ui_custom_file_loaded']=doc.entities==before and 'C:PLANO_A1' in window.lisp.functions and 'LSP cargado:' in window.history.toPlainText()
        window.entry.setText('PLANO_A1'); QTest.keyClick(window.entry,Qt.Key.Key_Return)
        checks['ui_custom_command_creates_all_types']=len(doc.entities)==len(before)+7
        after=doc.entities; window.execute('UNDO'); checks['ui_lsp_single_undo']=doc.entities==before
        window.execute('REDO'); checks['ui_lsp_redo']=doc.entities==after
        window.canvas.fit(); app.processEvents()
        if not window.grab().save(str(a.output/'lisp-essential.png')):raise RuntimeError('Capture failed')
        expected=native_inventory(doc._view); target=a.output/'lsp-ui.dxf'; doc.save_dxf(target); doc.open_dxf(target); equivalent(expected,native_inventory(doc._view))
        checks['ui_lsp_dxf_reopened']=True; checks['lsp_source_unchanged']=digest==hashlib.sha256(fixture.read_bytes()).hexdigest()
        report=dict(kind='application_integration_partial',installed=False,platform=platform.platform(),python=platform.python_version(),qt=qVersion(),
            checks=checks,passed=all(v is True for v in checks.values()),identity=doc.request('hello'),engine_sha256=hashlib.sha256(a.binary.read_bytes()).hexdigest(),
            lsp_sha256=digest,observed=doc._view,commands=sorted(lsp.allowed_commands),
            source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                [ROOT/'src/opencad/lisp.py',ROOT/'src/opencad/commands.py',ROOT/'src/opencad/qcad_backend.py',Path(__file__).resolve()]},
            limits=['complete arguments only','bridge IDs not ENAMEs','no ssget/entget','no AutoCAD comparison','not installed'])
        write(a.output/'report.json',report); print(json.dumps(dict(passed=report['passed'],checks=checks)))
        return 0 if report['passed'] else 1
    finally:
        if window:window.close()
        else:doc.close()


if __name__=='__main__':raise SystemExit(main())
