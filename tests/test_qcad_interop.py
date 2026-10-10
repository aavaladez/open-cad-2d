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
