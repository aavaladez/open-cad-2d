import os
import sys
import unittest
from pathlib import Path
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from PySide6.QtCore import Qt,QPoint
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from opencad.app import MainWindow
from opencad.model import Point


class UI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = MainWindow()
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def test_keyboard_console(self):
        self.window.entry.setFocus()
        QTest.keyClicks(self.window.entry,"LINE 0,0,3 3,4,3")
        QTest.keyClick(self.window.entry,Qt.Key.Key_Return)
        self.assertEqual(len(self.window.doc.entities),1)
        self.assertEqual(self.window.doc.entities[1].end.z,3)

    def test_mouse_line_escape(self):
        self.window.start("LINE")
        QTest.mouseClick(self.window.canvas,Qt.MouseButton.LeftButton,pos=QPoint(100,100))
        self.assertIsNotNone(self.window.anchor)
        QTest.keyClick(self.window.canvas,Qt.Key.Key_Escape)
        self.assertIsNone(self.window.anchor)
        self.assertFalse(self.window.doc.entities)
        self.window.start("LINE")
        QTest.mouseClick(self.window.canvas,Qt.MouseButton.LeftButton,pos=QPoint(100,100))
        QTest.mouseClick(self.window.canvas,Qt.MouseButton.LeftButton,pos=QPoint(180,100))
        self.assertEqual(len(self.window.doc.entities),1)

    def test_selection_properties_error_no_mutation(self):
        self.window.execute("CIRCLE 0,0 10")
        self.window.on_point(Point(10,0))
        self.assertEqual(self.window.selected,{1})
        self.assertIn("Circle",self.window.properties.toPlainText())
        self.assertFalse(self.window.execute("CIRCLE 0,0 -1"))
        self.assertEqual(len(self.window.doc.entities),1)

    def test_screen_world_and_snap(self):
        p = Point(23,41)
        actual = self.window.canvas.world(self.window.canvas.screen(p))
        self.assertAlmostEqual(actual.x,p.x)
        self.assertAlmostEqual(actual.y,p.y)
        self.window.canvas.snap = True
        self.assertEqual(self.window.canvas.world(self.window.canvas.screen(p)),Point(20,40))
