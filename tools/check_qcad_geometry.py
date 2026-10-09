"""Run the original C++ fixture with process-local DLL paths and an analytic oracle."""
import argparse
import json
import os
import subprocess
from pathlib import Path
from cad_workflow import ROOT, compare, write


def main():
    parser = argparse.ArgumentParser()
    for name in ('binary','source','qt','report'):
        parser.add_argument('--'+name,required=True,type=Path)
    args = parser.parse_args()
    env = dict(os.environ)
    env['PATH'] = os.pathsep.join([str(args.source.resolve()/'release'),
                                str(args.qt.resolve()/'bin'),env.get('PATH','')])
    run = subprocess.run([str(args.binary.resolve())],env=env,capture_output=True,text=True)
    if run.returncode:
        write(args.report,{'passed':False,'exit_code':run.returncode,'stderr':run.stderr})
        return 1
    actual = json.loads(run.stdout)
    baseline = json.loads((ROOT/'tests/fixtures/qcad-geometry-baseline.json').read_text(encoding='utf-8'))
    comparison = compare(baseline,actual,1e-9)
    write(args.report,{'passed':actual['passed'] and comparison['passed'],
                      'exit_code':run.returncode,'actual':actual,'comparison':comparison})
    return 0 if actual['passed'] and comparison['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
