import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from opencad.model import Document,Point
from opencad.commands import CommandBus
from opencad.interop import load_dxf,save_dxf
import ezdxf


class Interop(unittest.TestCase):
    def setUp(self):
        self.tmp_root = Path(__file__).resolve().parents[1]/"build/test-temp"
        self.tmp_root.mkdir(parents=True,exist_ok=True)

    def test_geometry_layers_z(self):
        doc = Document()
        doc.units = 4
        bus = CommandBus(doc)
        bus.execute_text('LAYER NEW "Ejes Norte"')
        bus.execute_text('LAYER SET "Ejes Norte"')
        bus.execute_text('LINE 0,0,3 3,4,5')
        bus.execute_text('CIRCLE 12,6,7 4')
        bus.execute_text('LAYER OFF "Ejes Norte"')
        bus.execute_text('LAYER LOCK "Ejes Norte"')
        with tempfile.TemporaryDirectory(dir=self.tmp_root) as tmp:
            p = Path(tmp)/"test.dxf"
            save_dxf(doc,p)
            new = load_dxf(p)
            self.assertEqual(new.units,4)
            self.assertEqual(list(new.entities.values()),list(doc.entities.values()))
            self.assertEqual(new.layers["Ejes Norte"],doc.layers["Ejes Norte"])
            # Direct backend read independently of OPEN CAD's import mapping.
            raw = ezdxf.readfile(p)
            self.assertFalse(raw.audit().errors)
            self.assertEqual(tuple(raw.modelspace().query("LINE")[0].dxf.end),(3,4,5))

    def test_unsupported_entities_no_source_mutation(self):
        with tempfile.TemporaryDirectory(dir=self.tmp_root) as tmp:
            p = Path(tmp)/"unsupported.dxf"
            drawing = ezdxf.new()
            drawing.modelspace().add_text("Must not be discarded")
            drawing.saveas(p)
            before = p.read_bytes()
            with self.assertRaises(ValueError):
                load_dxf(p)
            self.assertEqual(p.read_bytes(),before)

    def test_xdata_and_ocs_rejected(self):
        with tempfile.TemporaryDirectory(dir=self.tmp_root) as tmp:
            p = Path(tmp)/"attrs.dxf"
            drawing = ezdxf.new()
            drawing.appids.new("EXAMPLE")
            e = drawing.modelspace().add_line((0,0),(1,1))
            e.set_xdata("EXAMPLE",[(1000,"retained elsewhere")])
            drawing.saveas(p)
            with self.assertRaises(ValueError):
                load_dxf(p)
            drawing = ezdxf.new()
            drawing.modelspace().add_circle((0,0),2,dxfattribs={"extrusion":(1,0,0)})
            drawing.saveas(p)
            with self.assertRaises(ValueError):
                load_dxf(p)

    def test_corrupt_and_dwg(self):
        with tempfile.TemporaryDirectory(dir=self.tmp_root) as tmp:
            p = Path(tmp)/"bad.dxf"
            p.write_text("corrupted")
            with self.assertRaises(Exception):
                load_dxf(p)
            with self.assertRaises(ValueError):
                save_dxf(Document(),Path(tmp)/"bad.dwg")

