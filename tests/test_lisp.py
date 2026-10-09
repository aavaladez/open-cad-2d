import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from opencad.model import Document
from opencad.commands import CommandBus
from opencad.lisp import LispRuntime,parse


class Lisp(unittest.TestCase):
    def setUp(self):
        self.doc = Document()
        self.bus = CommandBus(self.doc)
        self.lisp = LispRuntime(self.bus)

    def test_original_rectangle_and_c_command(self):
        self.lisp.load(Path(__file__).resolve().parents[1]/"examples/rectangle.lsp")
        self.assertEqual(len(self.doc.entities),5)
        self.assertEqual(self.doc.entities[5].radius,18)
        self.assertEqual(self.doc.entities[5].center.z,2)
        self.bus.execute("UNDO")
        self.assertFalse(self.doc.entities)
        self.bus.execute("MARCO")
        self.assertEqual(len(self.doc.entities),5)

    def test_arithmetic_lists_and_condition(self):
        self.assertEqual(self.lisp.run("(setq n (+ 1 2 3)) (if (= n 6) (car '(10 20)) 99)"),10)
        self.assertEqual(self.lisp.run("(length (cons 3 '(4 5)))"),3)
        self.assertEqual(self.lisp.run("(* 2 (- 7 3) (/ 12 3))"),32)
        self.assertEqual(self.lisp.run("(if 0 1 2)"),1)
        self.assertEqual(self.lisp.run("(quote 0)"),0)
        self.assertEqual(self.lisp.run("(if '() 1 2)"),2)

    def test_rollback_model_and_runtime(self):
        with self.assertRaises(ValueError):
            self.lisp.run('(setq new 10) (command "LINE" \'(0 0) \'(1 1)) (vlax-create-object "X")')
        self.assertFalse(self.doc.entities)
        self.assertNotIn("NEW",self.lisp.globals)

    def test_blocked_capabilities(self):
        for code in ('(command "APPLOAD" "x")','(command "UNDO")','(startapp "cmd")','(open "x" "w")'):
            with self.assertRaises(ValueError):
                self.lisp.run(code)

    def test_malformed_depth_and_recursion(self):
        for code in ("(list 1", ")", "("*100 + "0" + ")"*100):
            with self.assertRaises(ValueError):
                parse(code)
        with self.assertRaises(ValueError):
            self.lisp.run("(defun recur () (recur)) (recur)")

    def test_size_limit(self):
        with self.assertRaises(ValueError):
            parse(" "*100001)

