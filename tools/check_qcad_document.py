"""Original DXF/transaction fixture; independent ezdxf reader, no A1 application claim."""
import argparse
import hashlib
import json
import os
import platform
import subprocess
import tempfile
from pathlib import Path
from cad_workflow import ROOT, compare, write
import ezdxf

PIN = '4c830eb4d80285ca64b1f2c2dc0987f729344126'


def ordered(items):
    return sorted(items, key=lambda x: json.dumps(x, sort_keys=True))


def expected():
    return [dict(type='LINE',layer='Survey',start=[0,0,7],end=[3,4,7]),
            dict(type='CIRCLE',layer='Survey',center=[10,20,9],radius=3)]


def main():
    parser = argparse.ArgumentParser()
    for name in ('binary','source','qt','output'):
        parser.add_argument('--'+name,required=True,type=Path)
    args = parser.parse_args()
    actual_pin = subprocess.check_output(['git','-C',str(args.source),'rev-parse','HEAD'],text=True).strip()
    if actual_pin != PIN:
        raise ValueError('Re-auditar QCAD antes de cambiar el commit de la prueba.')
    args.output.mkdir(parents=True,exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix='run-',dir=args.output))
    source, saved = folder/'original.dxf', folder/'edited.dxf'
    doc = ezdxf.new('R2000'); doc.units = 4
    doc.layers.new('Survey',dxfattribs={'color':3})
    space = doc.modelspace()
    space.add_line((0,0,7),(3,4,7),dxfattribs={'layer':'Survey'})
    space.add_circle((10,20,9),3,dxfattribs={'layer':'Survey'})
    doc.saveas(source)
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    input_hash = digest(source)
    env = dict(os.environ)
    env['PATH'] = os.pathsep.join([str(args.source.resolve()/'release'),
        str(args.source.resolve()/'plugins'),str(args.qt.resolve()/'bin'),env.get('PATH','')])
    env['QT_QPA_PLATFORM'] = 'offscreen'
    # Explicit CE factories only: never load a directory of third-party plugins.
    command = [str(args.binary.resolve()),str(source.resolve()),str(saved.resolve())]
    run = subprocess.run(command,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60)
    (folder/'stderr.txt').write_text(run.stderr,encoding='utf-8')
    (folder/'stdout.json').write_text(run.stdout,encoding='utf-8')
    report = {'kind':'dependency_functional','application_integrated':False,
        'platform':platform.platform(),'qcad_revision':PIN,'ezdxf_version':ezdxf.__version__,
        'command':command,'exit_code':run.returncode,'binary_sha256':digest(args.binary),
        'input_sha256':input_hash,'fixture_directory':str(folder), 'passed':False}
    if run.stdout.strip():
        native = json.loads(run.stdout)
        edited = expected()+[dict(type='LINE',layer='Survey',start=[10,2,5],end=[13,6,5])]
        def check(reference,actual,engine='qcad',version=PIN):
            return compare({'origin':'analytic','version':'fixture-1','evidence':'Original coordinates and prescribed translation',
                            'result':ordered(reference)},
                           {'origin':engine,'version':version,'result':ordered(actual)},1e-9)
        comparisons = {'import':check(expected(),native['before']),
                       'edited':check(edited,native['after']), 'reopened':check(edited,native['reopened'])}
        external = ezdxf.readfile(saved)
        entities = []
        attributes = []
        for entity in external.modelspace():
            item = dict(type=entity.dxftype(),layer=entity.dxf.layer)
            # DXF table names are case-insensitive; compare semantic identity.
            attributes.append(entity.dxf.color == 256 and entity.dxf.linetype.upper() == 'BYLAYER')
            if entity.dxftype() == 'LINE':
                item.update(start=list(entity.dxf.start),end=list(entity.dxf.end))
            elif entity.dxftype() == 'CIRCLE':
                item.update(center=list(entity.dxf.center),radius=entity.dxf.radius)
            entities.append(item)
        comparisons['independent_reader'] = check(edited,entities,'ezdxf',ezdxf.__version__)
        checks = dict(native['checks'], input_unchanged=digest(source)==input_hash,
            units=external.units==4,layer_color=external.layers.get('Survey').dxf.color==3,
            entity_attributes=all(attributes))
        report.update(checks=checks,comparisons=comparisons,native=native,
            patch_sha256=digest(ROOT/'native/patches/qcad-dxf-z.patch'),
            qcad_dll_sha256={name:digest(args.source/'release'/('qcad'+name+'.dll'))
                            for name in ('core','entity','operations')},
            dxf_dll_sha256=digest(args.source/'plugins/qcaddxf.dll'),
            independent_inventory=entities,output_sha256=digest(saved))
        report['passed'] = run.returncode == 0 and all(v is True for v in checks.values()) and all(v['passed'] for v in comparisons.values())
    write(folder/'report.json',report)
    print(json.dumps({'passed':report['passed'],'report':str(folder/'report.json')}))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
