"""Source/frozen entry point, with explicit local development dependency paths."""
import sys
import os
from pathlib import Path

if not getattr(sys, "frozen", False):
    root = Path(__file__).resolve().parent
    sys.path[:0] = [str(root/"src"),os.environ.get("OPENCAD_DEPS_DIR",str(root/".cache/python"))]

if __name__ == "__main__":
    try:
        from opencad.app import main
        raise SystemExit(main())
    except Exception:
        import traceback
        # Preserve startup evidence even in a frozen Windows GUI executable,
        # where stdout/stderr may be absent. Avoid a blocking error dialog.
        log = Path(sys.executable).parent / "startup-error.log" if getattr(sys,"frozen",False) else Path(__file__).with_name("startup-error.log")
        log.write_text(traceback.format_exc(),encoding="utf-8")
        raise SystemExit(1)
