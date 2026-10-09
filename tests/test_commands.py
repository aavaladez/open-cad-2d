import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from opencad.model import Document,Point
from opencad.commands import CommandBus


class Commands(unittest.TestCase):
    def setUp(self):
        self.doc = Document()
        self.bus = CommandBus(self.doc)

    def test_line_alias_chain_z_undo(self):
        self.bus.execute_text("L 0,0,7 3,4,7 8,4,9")
        self.assertEqual(len(self.doc.entities),2)
        self.assertEqual(self.doc.entities[2].end,Point(8,4,9))
        self.bus.execute("UNDO")
        self.assertFalse(self.doc.entities)
        self.bus.execute("REDO")
        self.assertEqual(len(self.doc.entities),2)

    def test_invalid_chain_atomic(self):
        with self.assertRaises(ValueError):
            self.bus.execute_text("LINE 0,0 3,4 3,4")
        self.assertFalse(self.doc.entities)
        self.assertEqual(self.doc.next_id,1)
        self.assertFalse(self.doc._undo)

    def test_circle_invalid_and_valid(self):
        for radius in (0,-1,float("nan"),float("inf")):
            with self.assertRaises(ValueError):
                self.bus.execute("CIRCLE","0,0",radius)
        self.bus.execute_text("C 1,2,8 5")
        self.assertEqual(self.doc.entities[1].center,Point(1,2,8))
        self.assertEqual(self.doc.entities[1].radius,5)

    def test_move_erase_layer_lock(self):
        self.bus.execute_text("LAYER NEW Ejes")
        self.bus.execute_text("LAYER SET Ejes")
        self.bus.execute_text("LINE 0,0,2 3,4,2")
        self.bus.execute_text("MOVE 1,1 10,20,3")
        self.assertEqual(self.doc.entities[1].start,Point(10,20,5))
        self.bus.execute_text("LAYER LOCK Ejes")
        before = self.doc.snapshot()
        for command in ("ERASE 1","MOVE 1 1,1","LINE 0,0 2,2"):
            with self.assertRaises(ValueError):
                self.bus.execute_text(command)
        self.assertEqual(before,self.doc.snapshot())
        self.bus.execute_text("LAYER UNLOCK Ejes")
        self.bus.execute_text("ERASE 1")
        self.bus.execute_text("UNDO")
        self.assertIn(1,self.doc.entities)

    def test_layer_visibility_undo(self):
        self.bus.execute_text("LAYER OFF 0")
        self.assertFalse(self.doc.layers["0"].visible)
        self.bus.execute_text("UNDO")
        self.assertTrue(self.doc.layers["0"].visible)

    def test_dist_analytic(self):
        self.assertEqual(self.bus.execute("DIST","0,0,0","3,4,12"),{"xy":5,"xyz":13})

    def test_alias_atomic_config(self):
        with self.assertRaises(ValueError):
            self.bus.set_aliases({"LIN":"LINE","LINE":"CIRCLE"})
        self.assertNotIn("LIN",self.bus.aliases)
        self.bus.set_aliases({"LIN":"LINE"})
        self.bus.execute_text("LIN 0,0 1,1")
        self.assertEqual(len(self.doc.entities),1)

    def test_nonfinite_and_unknown(self):
        for text in ("LINE nan,0 1,1","CIRCLE 0,inf 4","BOX 10","MOVE 99 2,2"):
            with self.assertRaises((ValueError,KeyError)):
                self.bus.execute_text(text)
        self.assertFalse(self.doc.entities)
