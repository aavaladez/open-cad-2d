"""Conservation boundaries and failure atomicity independent of a native build."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import ezdxf
from opencad.qcad_interop import inspect_dxf,equivalent,save_document


class NativeInteropBoundaries(unittest.TestCase):
    def setUp(self):
        root=Path(__file__).resolve().parents[1]/'build/test-temp'; root.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=root); self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'source.dxf'

    def drawing(self):
        d=ezdxf.new('R2010'); d.modelspace().add_line((0,0,7),(3,4,9)); return d

    def test_xyz_indexed_color_and_case_semantics(self):
        d=self.drawing(); d.layers.new('Survey',dxfattribs={'color':3})
        d.modelspace().add_circle((10,20,9),3,dxfattribs={'layer':'Survey'})
        d.saveas(self.path); result=inspect_dxf(self.path)
        self.assertEqual(result['layers']['SURVEY']['color_index'],3)
        self.assertEqual(result['layers']['SURVEY']['color'],'#00ff00')
        self.assertTrue(any(e.get('end')==[3,4,9] for e in result['entities']))

    def test_unsupported_metadata_never_changes_input(self):
        mutations=[lambda d:d.modelspace().add_text('Required text'),
            lambda d:d.rootdict.add_xrecord('Custom').reset([(1000,'Must not disappear')]),
            lambda d:d.groups.new('Assembly'),
            lambda d:d.layers.get('0').freeze(),
            lambda d:d.modelspace().query('LINE')[0].dxf.__setattr__('extrusion',(1,0,0)),
            lambda d:d.modelspace().query('LINE')[0].dxf.__setattr__('color',3),
            lambda d:d.styles.new('CustomFont')]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                d=self.drawing(); mutation(d); d.saveas(self.path); before=self.path.read_bytes()
                with self.assertRaises(ValueError): inspect_dxf(self.path)
                self.assertEqual(before,self.path.read_bytes())

    def test_comparison_rejects_lost_z_and_entity_count(self):
        baseline={'entities':[{'start':[0,0,7],'end':[3,4,9]}]}
        with self.assertRaises(ValueError): equivalent(baseline,{'entities':[{'start':[0,0,0],'end':[3,4,0]}]})
        with self.assertRaises(ValueError): equivalent(baseline,{'entities':[]})

    def test_arc_and_straight_polyline_inventory_and_rejection(self):
        d=self.drawing(); d.modelspace().add_arc((0,0,7),5,350,30)
        pl=d.modelspace().add_lwpolyline([(0,0),(3,0),(3,4)],format='xy',close=True,dxfattribs={'elevation':9})
        d.saveas(self.path); inventory=inspect_dxf(self.path)
        arc=next(e for e in inventory['entities'] if e['type']=='ARC')
        self.assertEqual((arc['center'],arc['start_angle'],arc['end_angle']),([0,0,7],350,30))
        poly=next(e for e in inventory['entities'] if e['type']=='LWPOLYLINE')
        self.assertEqual(poly['vertices'],[[0,0,9],[3,0,9],[3,4,9]])
        self.assertTrue(poly['closed'])
        for key,value in [('const_width',2),('flags',129)]:
            pl.dxf.set(key,value); d.saveas(self.path); before=self.path.read_bytes()
            with self.assertRaises(ValueError): inspect_dxf(self.path)
            self.assertEqual(before,self.path.read_bytes()); pl.dxf.discard(key)
        pl.set_points([(0,0,1),(3,0,0),(3,4,0)],format='xyb'); d.saveas(self.path)
        with self.assertRaises(ValueError): inspect_dxf(self.path)

    def test_degenerate_arc_and_polyline_rejected(self):
        for create in [lambda m:m.add_arc((0,0,0),5,0,360),
                lambda m:m.add_lwpolyline([(0,0),(0,0),(1,1)],format='xy'),
                lambda m:m.add_lwpolyline([(0,0),(1,1)],format='xy',close=True)]:
            d=ezdxf.new('R2010'); create(d.modelspace()); d.saveas(self.path)
            with self.assertRaises(ValueError): inspect_dxf(self.path)

    def test_dimension_graphics_and_styles_are_not_silently_accepted(self):
        from opencad.qcad_dimensions_io import add_dimension,apply_preset,dimension_record
        item=dict(type='DIMENSION',dimension_type='DIMALIGNED',position=[0,5,7],start=[0,0,7],end=[3,4,7],text='',layer='0')
        render=dict(shapes=[dict(type='LINE',start=[0,5,0],end=[3,9,0])],label='5',text_position=[1,7,7],text_height=2.5,text_angle=53.13010235415598,measurement=5)
        d=ezdxf.new('R2010'); apply_preset(d); add_dimension(d,item,render); d.saveas(self.path)
        observed=inspect_dxf(self.path)['entities'][0]
        self.assertEqual(observed['start'],[0,0,7]); self.assertEqual(observed['end'],[3,4,7])
        dim=next(iter(d.modelspace()))
        dim.dxf.dimtype|=128
        with self.assertRaises(ValueError): dimension_record(dim)
        dim.dxf.dimtype&=~128
        d.dimstyles.get('Standard').dxf.dimtxt=4; d.saveas(self.path)
        with self.assertRaises(ValueError): inspect_dxf(self.path)

    def test_dimension_render_cache_tampering_is_observable(self):
        from opencad.qcad_dimensions_io import add_dimension,apply_preset,caches_from_file
        item=dict(dimension_type='DIMRADIUS',position=[0,0,7],chord=[3,0,7],text='',layer='0')
        render=dict(shapes=[dict(type='LINE',start=[0,0,0],end=[3,0,0])],label='R3',text_position=[4,1,7],text_height=2.5,text_angle=0,measurement=3)
        d=ezdxf.new('R2010'); apply_preset(d); add_dimension(d,item,render); d.saveas(self.path)
        baseline=caches_from_file(self.path); block=d.blocks.get(next(iter(d.modelspace())).dxf.geometry)
        next(e for e in block if e.dxftype()=='TEXT').dxf.text='User annotation'; d.saveas(self.path)
        with self.assertRaises(ValueError): equivalent(baseline,caches_from_file(self.path))

    def test_dimension_unicode_hex_case_without_accepting_rich_text(self):
        from opencad.qcad_dimensions_io import unicode_text,dimension_record
        self.assertEqual(unicode_text(r'Tramo \U+00e1'), 'Tramo á')
        self.assertEqual(unicode_text(r'Tramo \U+00E1'), 'Tramo á')
        d=ezdxf.new('R2010'); dim=d.modelspace().new_entity('DIMENSION',dxfattribs=dict(
            dimtype=1,defpoint=(0,6,7),defpoint2=(0,0,7),defpoint3=(3,4,7),text=r'\S1^2;'))
        with self.assertRaises(ValueError): dimension_record(dim)

    def test_failed_native_export_preserves_existing_destination(self):
        self.path.write_bytes(b'original destination')
        class Document:
            _depth=0
            _view={'entities':[],'layers':[],'current_layer':'0','units':0}
            def request(self,*args,**kwargs): raise ValueError('Export failure')
        with self.assertRaises(ValueError): save_document(Document(),self.path)
        self.assertEqual(self.path.read_bytes(),b'original destination')
        self.assertEqual(list(Path(self.temp.name).iterdir()),[self.path])

    def test_mismatch_before_replace_preserves_existing_destination(self):
        self.path.write_bytes(b'original destination')
        class Document:
            _depth=0
            _view={'entities':[],'layers':[],'current_layer':'0','units':0}
        with patch('opencad.qcad_interop.validated_export',side_effect=ValueError('Unexpected attributes')):
            with self.assertRaises(ValueError): save_document(Document(),self.path)
        self.assertEqual(self.path.read_bytes(),b'original destination')


if __name__=='__main__': unittest.main()
