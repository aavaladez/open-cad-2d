"""Recovery storage boundaries; native functional cases live in check_qcad_recovery."""
import json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from opencad.recovery import RecoveryStore


class RecoveryBoundaries(unittest.TestCase):
    def setUp(self):
        root=Path(__file__).resolve().parents[1]/'build/test-temp'
        root.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=root); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name); self.store=RecoveryStore(self.root/'recovery')
        self.doc=SimpleNamespace(_confirmed_view={'transaction_active':False,'entities':[]},file_path=None)
        writer=patch('opencad.recovery.write_snapshot',side_effect=lambda view,path:Path(path).write_bytes(b'unit-test-snapshot'))
        writer.start(); self.addCleanup(writer.stop)
        reader=patch('opencad.recovery.inspect_dxf',return_value={'entities':[]})
        reader.start(); self.addCleanup(reader.stop)

    def test_retention_only_removes_own_two_generation_overflow(self):
        first=self.store.checkpoint(self.doc)
        unknown=first.parent/'untouched.dxf'; unknown.write_bytes(b'user data')
        prior=RecoveryStore(self.store.root).checkpoint(self.doc)
        second=self.store.checkpoint(self.doc); third=self.store.checkpoint(self.doc)
        self.assertFalse(first.exists()); self.assertTrue(second.exists()); self.assertTrue(third.exists())
        self.assertTrue(prior.exists()); self.assertEqual(unknown.read_bytes(),b'user data')
        self.assertEqual(len(list(third.parent.glob('*.json'))),2)
        self.store.read(third)

    def test_failed_manifest_publication_preserves_previous(self):
        good=self.store.checkpoint(self.doc); before=good.read_bytes()
        with patch('opencad.recovery.os.fsync',side_effect=OSError('disk failed')):
            with self.assertRaises(OSError):self.store.checkpoint(self.doc)
        self.assertEqual(good.read_bytes(),before); self.store.read(good)
        self.assertEqual(len(list(good.parent.glob('*.dxf'))),1)
        self.assertEqual(len(list(good.parent.glob('*.json'))),1)

    def test_absent_or_unconfirmed_view_never_creates_generation(self):
        for view in (None,{'transaction_active':True,'entities':[]}):
            self.doc._confirmed_view=view
            with self.assertRaises(ValueError):self.store.checkpoint(self.doc)
        self.assertFalse(list(self.store.root.glob('*')))

    def test_changed_dxf_and_oversized_or_foreign_manifest_rejected(self):
        good=self.store.checkpoint(self.doc); drawing,_,_=self.store.read(good)
        drawing.write_bytes(b'tampered')
        with self.assertRaises(ValueError):self.store.read(good)
        foreign=self.root/'foreign.json'; foreign.write_bytes(good.read_bytes())
        with self.assertRaises(ValueError):self.store.read(foreign)
        large=good.parent/'large.json'; large.write_bytes(b' '*65537)
        with self.assertRaises(ValueError):self.store.read(large)

    def test_malformed_and_traversing_manifest_rejected(self):
        good=self.store.checkpoint(self.doc); data=json.loads(good.read_text(encoding='utf-8'))
        bad=good.parent/'invalid.json'
        for content in ('[]','not json',json.dumps(data|{'dxf':'../../drawing.dxf'}),json.dumps(data|{'entities':3})):
            bad.write_text(content,encoding='utf-8')
            with self.assertRaises(ValueError):self.store.read(bad)


if __name__=='__main__':unittest.main()
