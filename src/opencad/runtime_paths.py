"""Explicit development or bundled native paths; no SDK discovery fallback."""
import sys
from pathlib import Path


def backend_paths():
    if getattr(sys,'frozen',False):
        native=Path(sys._MEIPASS)/'native'
        return native/'opencad-qcad-engine.exe',native,native/'qt'
    root=Path(__file__).resolve().parents[2]
    return root/'build/native/opencad-qcad-engine.exe',root/'.cache/upstream/qcad',root/'.cache/qt/6.10.3/msvc2022_64'
