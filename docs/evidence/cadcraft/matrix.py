# SPDX-License-Identifier: GPL-3.0-or-later
"""Conservative, evidence-gated 472-row comparison; registration is not acceptance."""
import argparse,collections,csv,hashlib,json,re
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
p.add_argument('--audit',type=Path,default=Path(__file__).resolve().parent)
p.add_argument('--source',type=Path)
p.add_argument('--output',type=Path)
a=p.parse_args(); root=a.root.resolve(); audit=a.audit.resolve()
source=a.source.resolve() if a.source else audit/'source'
review=a.output.resolve() if a.output else audit/'review'
coverage=json.loads((root/'requirements/coverage.json').read_text(encoding='utf-8'))
registry={}
for path in (source/'crates/engine/src/cmd').rglob('*.rs'):
    if 'test' in path.name: continue
    text=path.read_text(encoding='utf-8'); starts=list(re.finditer(r'CommandSpec::new\(\s*"([^"\n]+)"',text))
    for n,m in enumerate(starts):
        fragment=text[m.start():starts[n+1].start() if n+1<len(starts) else len(text)]
        command=m.group(1).lower(); evidence={'id':command,'path':path.relative_to(source).as_posix(),'line':text[:m.start()].count('\n')+1}
        registry[command]=evidence
        for aliases in re.findall(r'\.alias\(&\[(.*?)\]\)',fragment,re.S):
            for alias in re.findall(r'"([^"\n]+)"',aliases): registry[alias.lower()]=evidence
manual={
    'load':('crates/engine/src/lisp/builtins.rs','LOAD builtin; distinto de APPLOAD y de comando standalone'),
    'commandline':('crates/ui-egui/src/menus.rs','ui.toggle.cmdline'),
    'commandlinehide':('crates/ui-egui/src/menus.rs','ui.toggle.cmdline'),
    'ribbon':('crates/ui-egui/src/toolbar.rs','No Ribbon AutoCAD equivalente; toolbar/toolsets no satisfacen Ribbon'),
}
semantic={
 'chprop':'properties.set','change':'properties.set','laymatch':'laymch',
 'layerstate':'layerstate.list','dimcenter':'centermark','dimreassoc':'dimreassociate',
 'dimupdate':'dimstyle.update','textstyle':'style','annotationscale':'cannoscale',
 'bcount':'count','dxfout/dxfin':'document.bytes','run / script':'script',
}
ui={'quickprop':'properties.rs','blockspalette':'palettes.rs','quit':'menus.rs',
    'cmdline':'menus.rs','textscr':'menus.rs','graphscr':'menus.rs','commands':'menus.rs',
    'help':'menus.rs','about':'menus.rs','info':'menus.rs','menubar':'menus.rs'}
for k,target in semantic.items():
    if target in registry: registry[k]=dict(registry[target],semantic_note=f'Equivalente API {target}; nombre/prompts originales no acreditados')
for k,path in ui.items():
    actual=source/'crates/ui-egui/src'/path
    if actual.exists(): manual[k]=(actual.relative_to(source).as_posix(),'Equivalente de UI por función; nombre/interacción Windows no verificados')
sysfiles=[source/'crates/engine/src/sysvars.rs',*(source/'crates/engine/src/sysvars').glob('*.rs')]
for path in sysfiles:
    text=path.read_text(encoding='utf-8')
    for name in re.findall(r'"([A-Z][A-Z0-9_]+)"',text):
        manual.setdefault(name.lower(),(path.relative_to(source).as_posix(),'Variable declarada por sysvars; almacenamiento no demuestra su efecto funcional'))
tested={
 'pline':('arc-pline-analytic','polilínea recta cerrada de tres vértices; arcos/anchuras/Z/variantes no aceptados'),
 'arc':('arc-pline-analytic','centro/radio/0–90 grados; otras variantes y Z no aceptados'),
 'copy':('modify-copy-analytic','copia por delta XY; Multiple/Array/base/variantes pendientes'),
 'rotate':('modify-rotate-analytic','90 grados sobre origen; Reference/Copy y otras variantes pendientes'),
 'scale':('modify-scale-analytic','factor 2 sobre origen; Reference/Copy y otras variantes pendientes'),
 'erase':('modify-erase-analytic','borrado y undo; selección/capas/variantes pendientes'),
 'trim':('modify-trim-analytic','LINE por LINE finita; otros tipos y opciones pendientes'),
 'extend':('modify-extend-analytic','LINE hasta LINE finita; otros tipos y opciones pendientes'),
 'offset':('modify-offset-analytic','LINE a distancia 5 por lado; Through/Multiple/curvas/variantes pendientes'),
 'line':('draw-line-circle-xy; appload-custom-command-xyz','dos puntos XY; XYZ/variantes/cancelación no aceptados íntegramente'),
 'circle':('draw-line-circle-xy','centro/radio XY; faltan aceptación 2P/3P/TTR/TTT y Z'),
 'move':('selection-properties-move-undo-redo; move-xyz-delta','traslación XY; desplazamiento XYZ bajo evaluación'),
 'undo':('selection-properties-move-undo-redo','una operación; Mark/Back/grupos no verificados'),
 'redo':('selection-properties-move-undo-redo','una operación; variantes no verificadas'),
 'select':('selection-properties-move-undo-redo','ventana JSON; no aceptación completa por consola/UI'),
 'properties':('selection-properties-move-undo-redo','capa mediante properties.set; resto del panel/UI no verificado'),
 'dimlinear':('three-dimensions-analytic','medida horizontal 30; estilo/asociación/variantes no aceptados'),
 'dimaligned':('three-dimensions-analytic','medida 50 por puntos DXF; estilo/asociación/variantes no aceptados'),
 'dimradius':('three-dimensions-analytic','radio 10; estilos/selección/variantes no aceptados'),
 'open':('dxf-cycle-xyz-basic; dxf-cycle-complex; malformed-reject-active-preserved','apertura de fixtures; conservación y errores se evalúan por atributo'),
 'saveas':('dxf-cycle-xyz-basic; dxf-cycle-complex; dwg-synthetic-bridge-cycle','DXF/DWG sintéticos; ausencia de corpus profesional/aceptación de formato completo'),
 'qsave':('dxf-cycle-xyz-basic','guardar DXF; no aceptación general'),
 'appload':('appload-custom-command-xyz','archivo propio y C:AUDITCAD; XYZ y carga completa bajo evaluación'),
}
states=['Implementado y verificado en CADCraft','Parcialmente implementado','Declarado en documentación, sin prueba','No implementado','No aplicable al alcance CAD 2D']
ocstates={'qcad_partial':states[1],'prototype_partial':states[1],'pending':states[3],'excluded':states[4]}
rows=[]
for entry in coverage['rows']:
    command=entry['command'].strip().lower(); found=registry.get(command); spec=root/'requirements/specs'/f"{entry['id']}.json"
    # Combined source cells stay intact. Finding one subcommand never accepts the whole row.
    subcommands=[x.strip() for x in command.split('/')]
    if not found and len(subcommands)>1:
        match=next((registry[x] for x in subcommands if x in registry),None)
        if match: found=dict(match,semantic_note='Fila agrupada: al menos una parte localizada; todas sus partes/variantes requieren aceptación')
    specdata=json.loads(spec.read_text(encoding='utf-8')) if spec.exists() else {}
    evidence=''; variants=''; tests='no verificada'; state=states[3]; reason='No se encontró implementación equivalente integrada en el registro, aliases y rutas revisadas; no deducir ausencia universal.'
    if entry['status']=='excluded': state=states[4]; reason=entry['scope_reason']
    elif found:
        state=states[2]; reason='Registro/API localizado; no se ejecutó aceptación de variantes de esta fila.'
        evidence=f"https://github.com/storytold/cadcraft/blob/e707ab4d7cc10102e550ad4c5bcecef1084a9baa/{found['path']}#L{found['line']}"
        variants=found.get('semantic_note','API/aliases inspeccionados; alcance total del requisito no verificado')
        if found['id'] in tested and 'semantic_note' not in found:
            state=states[1]; tests,variants=tested[found['id']]; reason='Subconjunto funcional probado o brechas observadas; consultar outcome y revisión exacta en results.json. Ninguna fila tiene aceptación íntegra.'
    elif command in manual:
        path,why=manual[command]; evidence=f'https://github.com/storytold/cadcraft/blob/e707ab4d7cc10102e550ad4c5bcecef1084a9baa/{path}'; reason=why
        if command!='ribbon': state=states[2]
    if entry['sheet']!='AutoCAD' and entry['status']!='excluded': reason='Función Civil/Map geoespacial sin equivalente integrado encontrado; conservar fila/ruta UI, incluso sin nombre.'
    pending=specdata.get('pending',[])
    rows.append({
      'requirement_id':entry['id'],'sheet':entry['sheet'],'source_row':entry['row'],'category':entry['category'],'command':entry['command'],'alias':entry['alias'],'ui_path':entry['ui_path'],'description':entry['description'],'scope':entry['scope'],'source_sha256':coverage['source_sha256'],'source_cells':json.dumps(entry['source_cells'],ensure_ascii=False,sort_keys=True),
      'cadcraft_status':state,'cadcraft_reason':reason,'cadcraft_variants':variants,'cadcraft_evidence':evidence,'cadcraft_case_ids':tests,'cadcraft_source_revision':'e707ab4d7cc10102e550ad4c5bcecef1084a9baa',
      'cadcraft_test_revision':'e707ab4d7cc10102e550ad4c5bcecef1084a9baa' if tests!='no verificada' else '',
      'opencad_status':ocstates[entry['status']],'opencad_original_status':entry['status'],'opencad_backend':'qcad' if entry['status']=='qcad_partial' else 'temporary_prototype' if entry['status']=='prototype_partial' else 'none','opencad_variants':entry.get('implemented_variant',''),'opencad_implementation':entry.get('implementation',''),'opencad_tests':entry.get('tests',''),'opencad_issue':entry.get('issue',''),'opencad_revision':'28480345290cd228f65e8339ec8b44a16ecd5882','spec_sha256':hashlib.sha256(spec.read_bytes()).hexdigest() if spec.exists() else '', 'spec_pending':json.dumps(pending,ensure_ascii=False),
    })
(review/'requirements').mkdir(exist_ok=True)
if (review/'requirements/cadcraft_coverage.csv').exists():
    raise FileExistsError('Choose a new output directory; existing coverage is preserved')
with (review/'requirements/cadcraft_coverage.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
assert len(rows)==472 and len({(r['sheet'],r['source_row']) for r in rows})==472
counts={key:dict(collections.Counter(r[key] for r in rows)) for key in ['cadcraft_status','opencad_status']}
(audit/'matrix-summary.json').write_text(json.dumps(counts,ensure_ascii=False,indent=2),encoding='utf-8')
(audit/'source-registry.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')
(audit/'unmapped.txt').write_text('\n'.join(r['requirement_id']+' '+r['command']+' | '+r['description'] for r in rows if r['cadcraft_status']==states[3]),encoding='utf-8')
print(json.dumps(counts,ensure_ascii=False,indent=2))
