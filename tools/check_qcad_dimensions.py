"""Native dimension data, analytic measures, UI, and conservative DXF caches."""
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
from opencad.qcad_views import Dimension
from opencad.qcad_backend import QcadDocument,QcadCommandBus
from opencad.qcad_interop import inspect_dxf,native_inventory,equivalent,ordered
from opencad.qcad_dimensions_io import caches_from_file,caches_from_view


def main():
    p=argparse.ArgumentParser()
    for name in ('binary','source','qt','output'): p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args(); a.output.mkdir(parents=True,exist_ok=True); os.environ['OPENCAD_SCRATCH']=str(a.output.resolve())
    doc=QcadDocument(a.binary,a.source,a.qt); bus=QcadCommandBus(doc); window=None; checks={}; fixtures={}
    near=lambda a,b:abs(a-b)<=1e-9
    def xyz(p,v): return all(near(a,b) for a,b in zip((p.x,p.y,p.z),v))
    def measure(i): return doc.entities[i].render['measurement']
    def rejected(name,action):
        before=doc.entities
        try: action()
        except ValueError: checks[name]=doc.entities==before
        else: checks[name]=False
    try:
        aligned=bus.execute('DAL','0,0,7','30,40,7','-20,20,7')
        horizontal=bus.execute('DLI','0,0,7','30,40,7','0,-10,7')
        vertical=bus.execute('DIMLINEAR','0,0,7','30,40,7','40,0,7',90)
        radial=bus.execute('DRA','80,20,11','90,20,11')
        checks['native_dimension_not_exploded']=all(isinstance(e,Dimension) for e in doc.entities.values()) and len(doc.entities)==4
        projection=doc.entities[aligned]; projection.render['label']='discardable view'
        checks['dimension_view_cannot_edit_document']=doc.entities[aligned].render['label']=='50'
        checks['aligned_3_4_5_measure']=near(measure(aligned),50)
        checks['horizontal_measure']=near(measure(horizontal),30)
        checks['vertical_measure']=near(measure(vertical),40)
        checks['radial_measure_label_z']=near(measure(radial),10) and doc.entities[radial].render['label']=='R10' and doc.entities[radial].position.z==11
        parts=doc.entities[horizontal].render['shapes']; stroke=next(s for s in parts if s['type']=='LINE')
        midpoint=Point(*[(x+y)/2 for x,y in zip(stroke['start'],stroke['end'])])
        checks['dimension_native_pick']=doc.select('point',midpoint,tolerance=.1)=={horizontal}
        checks['dimension_native_window']=doc.select('window',Point(-100,-100),Point(200,200))==set(doc.entities)
        checks['dimension_native_crossing']=horizontal in doc.select('crossing',Point(midpoint.x-.1,midpoint.y-.1),Point(midpoint.x+.1,midpoint.y+.1))
        base=doc.entities
        bus.edit_properties({aligned},{'end':[60,80,7],'text':'Longitud <>'})
        checks['dimension_edit_recomputed_measure']=near(measure(aligned),100) and doc.entities[aligned].render['label']=='Longitud 100'
        edited=doc.entities; bus.execute('UNDO'); checks['dimension_edit_single_undo']=doc.entities==base
        bus.execute('REDO'); checks['dimension_edit_redo']=doc.entities==edited; bus.execute('UNDO')
        bus.edit_properties({horizontal},{'angle':90})
        checks['dimension_angle_property_measure']=near(measure(horizontal),40); bus.execute('UNDO')
        bus.edit_properties({horizontal},{'position':[0,60,7]})
        checks['dimension_position_property_native']=any(s['type']=='LINE' and near(s['start'][1],60) and near(s['end'][1],60) for s in doc.entities[horizontal].render['shapes'])
        bus.execute('UNDO'); checks['dimension_position_angle_undo']=doc.entities==base
        bus.edit_properties({radial},{'chord':[95,20,11],'text':'RADIO <>'})
        checks['radial_edit_recomputed_label']=near(measure(radial),15) and doc.entities[radial].render['label']=='RADIO 15'; bus.execute('UNDO')
        selection=','.join(str(i) for i in doc.entities); copied=bus.execute('COPY',selection,'3,4,5')
        checks['dimension_copy_new_ids']=len(copied)==4 and len(doc.entities)==8 and set(copied).isdisjoint(base)
        checks['dimension_copy_measure_xyz']=any(e.kind=='DIMALIGNED' and xyz(e.start,[3,4,12]) and e.render['measurement']==50 for i in copied for e in [doc.entities[i]])
        bus.execute('UNDO'); checks['dimension_copy_undo']=doc.entities==base
        bus.execute('ROTATE',selection,'0,0,100',90)
        checks['dimension_rotation_updates_direction']=near(doc.entities[horizontal].angle,90) and near(measure(horizontal),30) and xyz(doc.entities[aligned].end,[-40,30,7])
        bus.execute('UNDO'); checks['dimension_rotate_undo']=doc.entities==base
        bus.execute('SCALE',selection,'0,0,100',2)
        checks['dimension_scale_measure_z']=near(measure(aligned),100) and near(measure(radial),20) and doc.entities[aligned].start.z==7
        scaled=doc.entities; bus.execute('UNDO'); checks['dimension_scale_undo']=doc.entities==base
        rejected('dimension_nonplanar_atomic',lambda:bus.execute('DIMALIGNED','0,0,0','3,4,1','0,6,0'))
        rejected('dimension_degenerate_atomic',lambda:bus.execute('DIMLINEAR','0,0','0,4','3,0',0))
        rejected('dimension_invalid_property_atomic',lambda:bus.edit_properties({aligned},{'end':[0,0,7]}))
        rejected('dimension_control_text_atomic',lambda:bus.edit_properties({aligned},{'text':'\\S1^2;'}))
        bus.execute('REDO'); checks['dimension_redo_after_errors']=doc.entities==scaled; bus.execute('UNDO')
        bus.execute('LAYER','LOCK','0')
        rejected('dimension_locked_creation',lambda:bus.execute('DLI','0,0','3,4','0,6'))
        rejected('dimension_locked_edit',lambda:bus.edit_properties({radial},{'text':'blocked'}))
        bus.execute('LAYER','UNLOCK','0')
        circle=bus.execute('CIRCLE','80,20,11',10)
        entity_radial=bus.execute('DIMRADIUS','ENTITY',circle,'90.1,20,0')
        checks['radial_source_native_projection']=near(measure(entity_radial),10) and xyz(doc.entities[entity_radial].chord,[90,20,11])
        bus.edit_properties({aligned},{'text':'Tramo á <>'})
        checks['dimension_utf8_text']=doc.entities[aligned].render['label']=='Tramo á 50'
        bus.execute('LAYER','NEW','Cotas'); bus.edit_properties({radial},{'layer':'Cotas'})
        target=a.output/'dimensions.dxf'; expected=native_inventory(doc._view); doc.save_dxf(target)
        equivalent(expected,inspect_dxf(target)); equivalent(ordered(caches_from_view(doc._view)),ordered(caches_from_file(target)))
        external=ezdxf.readfile(target); checks['dxf_dimension_entities_valid_blocks']=not external.audit().errors and not external.audit().fixes and len(external.modelspace().query('DIMENSION'))==5
        layer_dim=next(e for e in external.modelspace().query('DIMENSION') if e.dxf.layer=='COTAS')
        checks['dimension_cache_layer_attributes']=all(e.dxf.layer=='COTAS' and e.dxf.color==256 for e in external.blocks.get(layer_dim.dxf.geometry))
        checks['native_missing_cache_reported']=any(f['code']=='opencad-ce-dimension-cache' for f in doc.last_dxf_validation['native_audit_repairs'])
        before=doc.entities; doc.undo(); doc.redo(); checks['dimension_save_history_retained']=doc.entities==before
        for version in ('R2000','R2010'):
            source=a.output/(version+'-dimensions.dxf'); original=ezdxf.readfile(target); original.dxfversion=ezdxf.DXF2000 if version=='R2000' else ezdxf.DXF2010
            original.saveas(source); digest=hashlib.sha256(source.read_bytes()).hexdigest(); fixtures[source.name]=digest
            expected=inspect_dxf(source); doc.open_dxf(source); equivalent(expected,native_inventory(doc._view))
            bus.execute('MOVE',','.join(str(i) for i in doc.entities),'2,3,5'); moved=native_inventory(doc._view)
            output=a.output/(version+'-modified.dxf'); doc.save_dxf(output); equivalent(moved,inspect_dxf(output))
            doc.open_dxf(output); equivalent(moved,native_inventory(doc._view)); checks[version+'_dimension_z_edit_save_reopen']=True
            checks[version+'_original_unchanged']=digest==hashlib.sha256(source.read_bytes()).hexdigest()
        for name,mutation in [('custom_style',lambda d:d.dimstyles.get('Standard').dxf.__setattr__('dimtxt',4)),
                ('cache_user_text',lambda d:next(e for e in d.blocks.get(next(iter(d.modelspace().query('DIMENSION'))).dxf.geometry) if e.dxftype()=='TEXT').dxf.__setattr__('text','must not disappear')),
                ('cache_user_entity',lambda d:d.blocks.get(next(iter(d.modelspace().query('DIMENSION'))).dxf.geometry).add_circle((0,0),4)),
                ('cache_rotated_text',lambda d:next(e for e in d.blocks.get(next(iter(d.modelspace().query('DIMENSION'))).dxf.geometry) if e.dxftype()=='TEXT').dxf.__setattr__('rotation',27))]:
            bad=a.output/(name+'.dxf'); drawing=ezdxf.readfile(target); mutation(drawing); drawing.saveas(bad)
            digest=hashlib.sha256(bad.read_bytes()).hexdigest(); rejected(name+'_active_unchanged',lambda:doc.open_dxf(bad))
            checks[name+'_source_unchanged']=digest==hashlib.sha256(bad.read_bytes()).hexdigest()
        app=QApplication.instance() or QApplication([])
        font=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/arial.ttf'
        if font.is_file():
            families=QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFont(str(font)))
            if families: app.setFont(QFont(families[0],10))
        window=MainWindow(doc); window.show(); app.processEvents(); window.ribbon.setCurrentIndex(4)
        buttons={b.text():b for b in window.findChildren(QPushButton)}
        def click(p):QTest.mouseClick(window.canvas,Qt.MouseButton.LeftButton,pos=window.canvas.screen(p).toPoint())
        base=doc.entities; QTest.mouseClick(buttons['Cota alineada'],Qt.MouseButton.LeftButton); click(Point(20,0)); QTest.keyClick(window.canvas,Qt.Key.Key_Escape)
        checks['dimension_ui_escape_atomic']=doc.entities==base and window.mode is None
        window.entry.setText('DAL'); QTest.keyClick(window.entry,Qt.Key.Key_Return)
        checks['bare_dimension_console_starts_tool']=window.mode=='DIMALIGNED' and doc.entities==base
        QTest.keyClick(window.canvas,Qt.Key.Key_Escape)
        QTest.mouseClick(buttons['Cota alineada'],Qt.MouseButton.LeftButton)
        for p in (Point(10,0),Point(40,40),Point(0,30)):click(p)
        latest=max(doc.entities); checks['ribbon_aligned_three_clicks']=len(doc.entities)==len(base)+1 and near(measure(latest),50) and window.mode is None
        window.selected={latest}; window.refresh(); window.properties.fields['text'].setText('Cota propia <>')
        QTest.mouseClick(window.properties.apply,Qt.MouseButton.LeftButton)
        checks['panel_dimension_text']=doc.entities[latest].render['label']=='Cota propia 50'
        before=doc.entities; window.execute('UNDO'); window.execute('REDO'); checks['panel_dimension_undo_redo']=doc.entities==before
        window.entry.setText('DIMLINEAR 0,50 40,80 50,50 90'); QTest.keyClick(window.entry,Qt.Key.Key_Return)
        checks['console_vertical_dimension']=near(measure(max(doc.entities)),30)
        QTest.mouseClick(buttons['Cota horizontal'],Qt.MouseButton.LeftButton)
        for p in (Point(20,10),Point(50,40),Point(20,5)):click(p)
        checks['ribbon_horizontal_dimension']=near(measure(max(doc.entities)),30)
        QTest.mouseClick(buttons['Cota vertical'],Qt.MouseButton.LeftButton)
        for p in (Point(20,10),Point(50,40),Point(55,10)):click(p)
        checks['ribbon_vertical_dimension']=near(measure(max(doc.entities)),30)
        native_circle=next(e for e in doc._view['entities'] if e['type']=='CIRCLE')
        center=native_circle['center']; radius=native_circle['radius']
        count=len(doc.entities); QTest.mouseClick(buttons['Cota radio'],Qt.MouseButton.LeftButton); click(Point(center[0],center[1]+radius))
        checks['ribbon_radius_native_source']=len(doc.entities)==count+1 and near(measure(max(doc.entities)),radius)
        window.canvas.fit(); app.processEvents()
        if not window.grab().save(str(a.output/'dimensions.png')):raise RuntimeError('Capture failed')
        target=a.output/'ui-dimensions.dxf'; expected=native_inventory(doc._view); doc.save_dxf(target); doc.open_dxf(target); equivalent(expected,native_inventory(doc._view))
        checks['ui_dimension_dxf_persisted']=True
        report=dict(kind='application_integration_partial',installed=False,platform=platform.platform(),python=platform.python_version(),
            qt=qVersion(),ezdxf=ezdxf.__version__,checks=checks,passed=all(v is True for v in checks.values()),fixtures=fixtures,
            identity=doc.request('hello'),engine_sha256=hashlib.sha256(a.binary.read_bytes()).hexdigest(),observed=doc._view,
            source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                [*ROOT.joinpath('native/adapter').glob('*.*'),*ROOT.joinpath('src/opencad').glob('*.py'),*ROOT.joinpath('native/patches').glob('*.patch'),Path(__file__).resolve()]},
            limits=['fixed dimension style preset','no automatic reference association with source geometry','other options pending','not installed','no AutoCAD execution'])
        write(a.output/'report.json',report); print(json.dumps(dict(passed=report['passed'],checks=checks)))
        return 0 if report['passed'] else 1
    finally:
        if window:window.close()
        else:doc.close()


if __name__=='__main__':raise SystemExit(main())
