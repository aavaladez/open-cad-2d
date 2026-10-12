"""Conservative native DXF cycle; independent inspection precedes every promotion.

Only declared geometry/layer/unit attributes are conserved. Default tables and
handles are regenerated. Unsupported data is rejected, never edited in place.
"""
import json
import math
import os
import tempfile
from pathlib import Path
import ezdxf
from .qcad_dimensions_io import (dimension_record,prepare_generated_dimensions,validate_dimension_blocks,
    add_dimension,apply_preset,caches_from_file,caches_from_view)


def require(condition,message):
    if not condition:
        raise ValueError(message)


def ordered(entities):
    return sorted(entities,key=lambda item:json.dumps(item,sort_keys=True))


def inspect_dxf(path,generated=False,audit_log=None):
    path=Path(path)
    require(path.suffix.lower()=='.dxf','Sólo DXF; DWG pendiente')
    require(path.is_file() and path.stat().st_size<=20_000_000,'DXF local de hasta 20 MB requerido')
    d=ezdxf.readfile(path)
    if generated: prepare_generated_dimensions(d,audit_log)
    audit=d.audit()
    if audit_log is not None:
        audit_log.extend(dict(code=int(f.code),message=f.message) for f in audit.fixes)
    require(not audit.errors,'DXF corrupto; apertura cancelada')
    allowed=lambda fix: int(fix.code)==202 and (fix.message.startswith('Fixed invalid owner handle') or
                fix.message.startswith('Removed invalid key ColorSettings/BackgroundColor in DICTIONARY'))
    require(not audit.fixes or generated and all(allowed(f) for f in audit.fixes),
            'DXF requiere reparación no admitida; operación cancelada')
    require(d.dxfversion in ('AC1015','AC1024'),'DXF R2000/R2010 requerido en esta etapa')
    require(all(layout.name=='Model' or layout.name in ('Layout1','Layout2') and not list(layout)
                for layout in d.layouts),'Presentaciones personalizadas/con contenido no admitidas')
    dimension_blocks={e.dxf.geometry.upper() for e in d.modelspace() if e.dxftype()=='DIMENSION'} if generated else validate_dimension_blocks(d)
    for b in d.blocks:
        require((b.name.upper()=='*MODEL_SPACE' or b.name.upper().startswith('*PAPER_SPACE')) and
                (b.name.upper()=='*MODEL_SPACE' or not list(b)) or b.name.upper() in dimension_blocks,
                'Bloques fuera del subconjunto')
    for e in d.entitydb.values():
        if e.is_alive and not generated:
            require(not e.xdata and not e.has_extension_dict,'XDATA/diccionarios de extensión fuera del subconjunto')
    if not generated:
        standard_keys={'ACAD_COLOR','ACAD_GROUP','ACAD_LAYOUT','ACAD_MATERIAL','ACAD_MLEADERSTYLE','ACAD_MLINESTYLE',
            'ACAD_PLOTSETTINGS','ACAD_PLOTSTYLENAME','ACAD_SCALELIST','ACAD_TABLESTYLE','ACAD_VISUALSTYLE','EZDXF_META'}
        require(set(d.rootdict.keys())<=standard_keys,'Diccionario raíz personalizado pendiente')
        for key,allowed_names in {'ACAD_COLOR':set(),'ACAD_GROUP':set(),'ACAD_PLOTSETTINGS':set(),
                'ACAD_SCALELIST':set(),'ACAD_TABLESTYLE':set(),'ACAD_VISUALSTYLE':set(),
                'ACAD_MATERIAL':{'BYBLOCK','BYLAYER','GLOBAL'},'ACAD_MLINESTYLE':{'STANDARD'},
                'ACAD_MLEADERSTYLE':{'STANDARD'}}.items():
            table=d.rootdict.get(key)
            require(table is None or {name.upper() for name in table.keys()}<=allowed_names,
                    'Objetos personalizados pendientes: '+key)
        metadata=d.rootdict.get('EZDXF_META')
        metadata_handle=metadata.dxf.handle if metadata is not None else None
        require(metadata is None or set(metadata.keys())<= {'CREATED_BY_EZDXF','WRITTEN_BY_EZDXF'},'Metadatos personalizados pendientes')
        require(all(e.dxftype() in ('DICTIONARY','ACDBDICTIONARYWDFLT','ACDBPLACEHOLDER','LAYOUT','MATERIAL',
            'MLINESTYLE','MLEADERSTYLE','VISUALSTYLE') or e.dxftype()=='DICTIONARYVAR' and e.dxf.owner==metadata_handle
                    for e in d.objects),'Objetos personalizados fuera del subconjunto')
    require(not list(d.views) and not list(d.ucs),'Vistas/UCS personalizados fuera del subconjunto')
    require(all(e.dxf.name.upper()=='STANDARD' for e in d.styles),'Estilos de texto personalizados pendientes')
    require(all(e.dxf.name.upper()=='STANDARD' for e in d.dimstyles),'Estilos de cota personalizados pendientes')
    require(all(e.dxf.name.upper() in ('BYLAYER','BYBLOCK','CONTINUOUS') for e in d.linetypes),'Tipos de línea personalizados pendientes')
    layers={}
    for layer in d.layers:
        name=layer.dxf.name
        require(not layer.xdata and not layer.has_extension_dict,'Metadatos de capa pendientes')
        require(layer.dxf.flags & ~4 == 0,'Capas congeladas/dependientes fuera del subconjunto')
        require(layer.dxf.linetype.upper()=='CONTINUOUS' and layer.dxf.lineweight in
                (-3,0,5,9,13,15,18,20,25,30,35,40,50,53,60,70,80,90,100,106,120,140,158,200,211),
                'Tipo/peso de línea de capa pendiente')
        expected_plot=0 if name.upper()=='DEFPOINTS' else 1
        require(layer.dxf.get('plot',1)==expected_plot and not layer.dxf.hasattr('transparency'),'Plot/transparencia de capa pendiente')
        aci=abs(layer.dxf.color)
        require(1<=aci<=255,'Color ACI de capa inválido')
        rgb=layer.rgb or ezdxf.colors.aci2rgb(aci)
        color_index=aci if tuple(rgb)==tuple(ezdxf.colors.aci2rgb(aci)) else -1
        layers[name.upper()]=dict(name=name.upper(),color='#%02x%02x%02x'%tuple(rgb),
            color_index=color_index,
            visible=not layer.is_off(),locked=layer.is_locked(),frozen=False,
            linetype='CONTINUOUS',lineweight=layer.dxf.lineweight)
    items=[]
    for e in d.modelspace():
        require((not e.xdata or generated and e.dxftype()=='DIMENSION') and not e.has_extension_dict,'Metadatos de entidad pendientes')
        require(e.dxftype() in ('LINE','CIRCLE','ARC','LWPOLYLINE','DIMENSION'),'Entidad DXF fuera del subconjunto: '+e.dxftype())
        require(e.dxf.layer.upper() in layers,'Entidad con capa ausente')
        require(e.dxf.color==256 and not e.dxf.hasattr('true_color') and e.dxf.linetype.upper()=='BYLAYER'
                and e.dxf.lineweight==-1 and e.dxf.ltscale==1,'Atributos de entidad fuera del subconjunto')
        require(tuple(e.dxf.get('extrusion',(0,0,1)))==(0,0,1) and (e.dxftype()=='DIMENSION' or e.dxf.get('thickness',0)==0),
                'OCS/espesor fuera del subconjunto')
        require(e.dxf.get('invisible',0)==0 and not e.dxf.hasattr('transparency'),'Visibilidad/transparencia fuera del subconjunto')
        item=dict(type=e.dxftype(),layer=e.dxf.layer.upper(),color_index=256,linetype='BYLAYER',lineweight=-1,ltscale=1.0)
        if e.dxftype()=='LINE':
            item.update(start=list(e.dxf.start),end=list(e.dxf.end))
            require(e.dxf.start.distance(e.dxf.end)>1e-9,'Línea degenerada fuera del subconjunto')
        elif e.dxftype() in ('CIRCLE','ARC'):
            item.update(center=list(e.dxf.center),radius=e.dxf.radius)
            require(e.dxf.radius>0,'Radio inválido')
            if e.dxftype()=='ARC':
                start,end=e.dxf.start_angle,e.dxf.end_angle
                require(math.isfinite(start) and math.isfinite(end) and abs((end-start)%360)>1e-9,
                        'Arco degenerado/completo fuera del subconjunto')
                item.update(start_angle=start%360,end_angle=end%360)
        elif e.dxftype()=='DIMENSION': item.update(dimension_record(e))
        else:
            vs=list(e.get_points('xyseb'))
            require(e.dxf.flags & ~1==0 and e.dxf.get('const_width',0)==0 and
                    all(s==0 and t==0 and b==0 for x,y,s,t,b in vs),
                    'PLINE con anchura, bulge o PLINEGEN pendiente')
            closed=bool(e.closed); elevation=e.dxf.elevation
            require(len(vs)>=(3 if closed else 2) and math.isfinite(elevation),'PLINE degenerada')
            item.update(vertices=[[x,y,elevation] for x,y,s,t,b in vs],closed=closed)
            require(all(math.isfinite(v) for p in item['vertices'] for v in p),'Vértice no finito')
            pairs=list(zip(vs,vs[1:]))+([(vs[-1],vs[0])] if closed else [])
            require(all(math.hypot(a[0]-b[0],a[1]-b[1])>1e-9 for a,b in pairs),'Segmento PLINE degenerado')
        require(all(math.isfinite(v) for key in ('start','end','center','radius') if key in item
                    for v in (item[key] if isinstance(item[key],list) else [item[key]])),'Geometría no finita')
        items.append(item)
    current=d.header.get('$CLAYER','0').upper()
    require(current in layers,'Capa actual ausente')
    return dict(entities=ordered(items),layers=layers,current_layer=current,units=d.header.get('$INSUNITS',0))


def native_inventory(view):
    items=[]
    for e in view['entities']:
        item={k:v for k,v in e.items() if k not in ('id','render')}
        item['layer']=item['layer'].upper(); item['linetype']=item['linetype'].upper()
        items.append(item)
    layers={}
    for layer in view['layers']:
        item={k:layer[k] for k in ('name','color','color_index','visible','locked','frozen','linetype','lineweight')}
        item['name']=item['name'].upper(); item['linetype']=item['linetype'].upper()
        layers[item['name']]=item
    return dict(entities=ordered(items),layers=layers,current_layer=view['current_layer'].upper(),units=view['units'])


def equivalent(expected,actual):
    differences=[]
    def same(a,b,path='document'):
        if isinstance(a,(float,int)) and not isinstance(a,bool):
            matched=isinstance(b,(float,int)) and not isinstance(b,bool) and math.isfinite(b) and abs(a-b)<=1e-9
        elif isinstance(a,dict):
            matched=isinstance(b,dict) and a.keys()==b.keys()
            if matched:
                return all([same(v,b[k],path+'.'+k) for k,v in a.items()])
        elif isinstance(a,list):
            matched=isinstance(b,list) and len(a)==len(b)
            if matched:
                return all([same(x,y,path+'.'+str(i)) for i,(x,y) in enumerate(zip(a,b))])
        else: matched=type(a) is type(b) and a==b
        if not matched: differences.append(path)
        return matched
    require(same(expected,actual),'DXF cambió atributos; operación cancelada: '+', '.join(differences[:8]))


def validated_export(document,path,expected):
    document.request('save',path=str(path))
    # Native CE/dxflib emits invalid default dictionary owner references. Permit
    # only its identified structural audit repairs on files we just generated.
    # User inputs requiring any repair remain rejected. Verify native geometry
    # before rebuilding default tables with ezdxf; no user geometry is invented.
    native_audit=[]
    equivalent(expected,inspect_dxf(path,generated=True,audit_log=native_audit))
    write_snapshot(document._view,path)
    document.last_dxf_validation=dict(native_audit_repairs=native_audit,
        native_geometry_attributes_verified=True,final_writer='ezdxf R2010',ezdxf_version=ezdxf.__version__)


def write_snapshot(view,path):
    """Serialize an acknowledged native view, never an editable Python model."""
    expected=native_inventory(view)
    drawing=ezdxf.new('R2010'); drawing.units=expected['units']
    apply_preset(drawing)
    for layer in list(drawing.layers):
        if layer.dxf.name.upper() not in expected['layers']: drawing.layers.remove(layer.dxf.name)
    for name,layer in expected['layers'].items():
        target=drawing.layers.get(name) if name in drawing.layers else drawing.layers.new(name)
        target.dxf.color=max(1,layer['color_index']) if layer['color_index']>0 else 7
        target.dxf.true_color=int(layer['color'][1:],16); target.dxf.lineweight=layer['lineweight']
        target.lock() if layer['locked'] else target.unlock()
        target.on() if layer['visible'] else target.off()
    drawing.header['$CLAYER']=expected['current_layer']
    for item in expected['entities']:
        attrs=dict(layer=item['layer'],color=item['color_index'],linetype=item['linetype'],
            lineweight=item['lineweight'],ltscale=item['ltscale'])
        if item['type']=='LINE': drawing.modelspace().add_line(item['start'],item['end'],dxfattribs=attrs)
        elif item['type']=='CIRCLE': drawing.modelspace().add_circle(item['center'],item['radius'],dxfattribs=attrs)
        elif item['type']=='ARC': drawing.modelspace().add_arc(item['center'],item['radius'],
            item['start_angle'],item['end_angle'],dxfattribs=attrs)
        elif item['type']=='LWPOLYLINE': drawing.modelspace().add_lwpolyline(
            [p[:2] for p in item['vertices']],format='xy',close=item['closed'],
            dxfattribs=attrs|{'elevation':item['vertices'][0][2]})
        elif item['type']=='DIMENSION':
            source=next(e for e in view['entities'] if e['type']=='DIMENSION' and
                {k:v for k,v in e.items() if k not in ('id','render','layer','linetype')}=={k:v for k,v in item.items() if k not in ('layer','linetype')})
            add_dimension(drawing,item,source['render'])
        else: raise ValueError('Entidad sin writer validado: '+item['type'])
    drawing.saveas(path)
    equivalent(expected,inspect_dxf(path))
    equivalent(ordered(caches_from_view(view)),ordered(caches_from_file(path)))


def open_document(document,path):
    require(document._depth==0,'No abrir DXF durante un comando/LSP')
    original=inspect_dxf(path)
    from .qcad_backend import QcadDocument
    candidate=QcadDocument(*document.backend_paths)
    try:
        # The Qt6 CE importer treats char* text as UTF8 even for legacy codepages.
        # Transcode the already-preflighted subset to a private R2010 input; verify
        # semantic equivalence first. Original bytes and drawing remain untouched.
        source=ezdxf.readfile(path)
        normalized=source.dxfversion=='AC1015'
        if normalized:
            with tempfile.TemporaryDirectory(prefix='opencad-input-',dir=os.environ.get('OPENCAD_SCRATCH')) as folder:
                native_input=Path(folder)/'utf8.dxf'; source.dxfversion='AC1024'; source.saveas(native_input)
                equivalent(original,inspect_dxf(native_input))
                candidate.request('load',path=str(native_input.resolve()),original_path=str(Path(path).resolve()),current_layer=original['current_layer'])
        else: candidate.request('load',path=str(Path(path).resolve()),current_layer=original['current_layer'])
        equivalent(original,native_inventory(candidate._view))
        equivalent(ordered(caches_from_file(path)),ordered(caches_from_view(candidate._view)))
        with tempfile.TemporaryDirectory(prefix='opencad-dxf-',dir=os.environ.get('OPENCAD_SCRATCH')) as folder:
            output=Path(folder)/'verification.dxf'
            validated_export(candidate,output,original)
        candidate.last_dxf_validation['input_normalization']='ezdxf R2000 codepage to R2010 UTF8' if normalized else 'none'
        # Swap only after import and independently inspected export both agree.
        # The active document object stays stable for UI/bus/LSP references.
        for name in ('process','reader','log','_view','_confirmed_view'):
            previous=getattr(document,name); setattr(document,name,getattr(candidate,name)); setattr(candidate,name,previous)
        document.id_map={}
        document.last_dxf_validation=candidate.last_dxf_validation
    finally:
        candidate.close()


def save_document(document,path):
    require(document._depth==0,'No guardar DXF durante un comando/LSP')
    path=Path(path).resolve()
    require(path.suffix.lower()=='.dxf','Sólo DXF; DWG pendiente')
    require(path.parent.is_dir(),'Directorio de destino ausente')
    expected=native_inventory(document._view)
    # Use a private directory on the same filesystem, so replace is atomic.
    with tempfile.TemporaryDirectory(prefix='.opencad-save-',dir=path.parent) as folder:
        output=Path(folder)/'validated.dxf'
        validated_export(document,output,expected)
        os.replace(output,path)
