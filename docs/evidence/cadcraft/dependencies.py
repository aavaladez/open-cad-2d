# SPDX-License-Identifier: GPL-3.0-or-later
import argparse,csv,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--metadata',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
d=json.loads(a.metadata.read_text(encoding='utf-8'))
rows=[]
for pkg in d['packages']:
    folder=Path(pkg['manifest_path']).parent
    notices=[]
    for f in sorted(folder.glob('*')):
        if f.is_file() and (f.name.upper().startswith(('LICENSE','COPYING','NOTICE'))):
            notices.append(f.name+':'+hashlib.sha256(f.read_bytes()).hexdigest())
    rows.append({'module':pkg['name'],'version':pkg['version'],'license_expression':pkg['license'],'source':pkg['source'] or 'CADCraft workspace','manifest_sha256':hashlib.sha256(Path(pkg['manifest_path']).read_bytes()).hexdigest(),'notice_hashes':';'.join(notices),'build_script':';'.join(t['src_path'].replace(str(folder),'') for t in pkg['targets'] if t['kind']==['custom-build']),'scope':'workspace metadata; includes dev and non-Windows targets; not a shipped-binary SBOM'})
with a.output.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows),'modules inventoried;',sum(bool(r['build_script']) for r in rows),'build scripts')
