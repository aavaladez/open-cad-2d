"""Bounded DIMENSION data and derived QCAD render caches; no general style support."""
import math
import re
import ezdxf
from ezdxf.lldxf.encoding import decode_dxf_unicode

PRESET=dict(dimscale=1.0,dimlfac=1.0,dimtxt=2.5,dimgap=.625,dimasz=2.5,
    dimexe=1.25,dimexo=.625,dimtad=1,dimtih=0,dimtsz=0.0,dimlunit=2,dimdec=4,dimzin=8)


def require(ok,message):
    if not ok: raise ValueError(message)


def unicode_text(text):
    # QCAD CE writes lowercase hex; ezdxf1.4.3 only decodes uppercase hex.
    # Canonicalize just valid four-digit Unicode escapes, not rich-text codes.
    return decode_dxf_unicode(re.sub(r'\\U\+([0-9a-fA-F]{4})',lambda m:'\\U+'+m.group(1).upper(),text))


def dimension_record(e):
    typ=e.dxf.dimtype & 7
    require(typ in (0,1,4) and e.dxf.dimtype & ~(7|32)==0,'Tipo/cota con posición de texto personalizada pendiente')
    require(e.dxf.dimstyle.upper()=='STANDARD' and e.dxf.get('leader_length',0)==0 and
        e.dxf.get('horizontal_direction',0)==0 and e.dxf.get('oblique_angle',0)==0 and e.dxf.get('text_rotation',0)==0,
        'Estilo/líder/rotación de texto de cota pendientes')
    text=unicode_text(e.dxf.get('text',''))
    require(len(text)<=256 and '\\' not in text and '^' not in text and all(ord(c)>=32 and ord(c)!=127 for c in text),'Texto de cota simple requerido')
    item=dict(dimension_type={0:'DIMLINEAR',1:'DIMALIGNED',4:'DIMRADIUS'}[typ],
        position=list(e.dxf.defpoint),text='' if text=='<>' else text)
    if typ in (0,1):
        item.update(start=list(e.dxf.defpoint2),end=list(e.dxf.defpoint3))
        if typ==0: item['angle']=e.dxf.angle%360
        points=[item['position'],item['start'],item['end']]
        require(math.dist(item['start'][:2],item['end'][:2])>1e-9,'Cota degenerada')
    else:
        item['chord']=list(e.dxf.defpoint4); points=[item['position'],item['chord']]
        require(math.dist(points[0][:2],points[1][:2])>1e-9,'Radio de cota no positivo')
    require(all(math.isfinite(v) for p in points for v in p) and all(abs(p[2]-points[0][2])<=1e-9 for p in points),'Cota finita y planar requerida')
    return item


def prepare_generated_dimensions(d,audit_log):
    # CE has definition data but no mandatory graphics blocks. An in-memory
    # placeholder prevents audit deleting that data before independent reading.
    # It is never saved. Actual final caches come from validated native graphics.
    count=0
    for e in d.modelspace():
        if e.dxftype()=='DIMENSION' and e.dxf.get('geometry','*') not in d.blocks:
            dimension_record(e)
            block=d.blocks.new_anonymous_block('D'); e.dxf.geometry=block.name; count+=1
    if count and audit_log is not None:
        audit_log.append(dict(code='opencad-ce-dimension-cache',message='Native CE missing graphics blocks; definition data retained for inspection',count=count))


def validate_dimension_blocks(d):
    dims=[e for e in d.modelspace() if e.dxftype()=='DIMENSION']
    names={e.dxf.geometry.upper():e.dxf.layer.upper() for e in dims}
    require(len(names)==len(dims),'Bloque gráfico compartido de cota pendiente')
    if dims:
        style=d.dimstyles.get('Standard')
        reference=ezdxf.new('R2010').dimstyles.get('Standard').dxf
        ignored={'handle','owner','name',*PRESET.keys()}
        for key,value in style.dxf.all_existing_dxf_attribs().items():
            if key=='dimtxsty':
                font_style=d.entitydb.get(value)
                require(font_style is not None and font_style.dxftype()=='STYLE' and font_style.dxf.name.upper()=='STANDARD','Fuente de cota fuera del preset')
            elif key not in ignored:
                default=getattr(reference,key)
                require(value==default or value in ('','0') and default in ('','0',None),
                    'Parámetro de estilo fuera del preset: '+key)
        for key,value in PRESET.items():
            require(style.dxf.get(key)==value and d.header.get('$'+key.upper())==value,'Preset de cota pendiente: '+key)
        font=d.styles.get('Standard').dxf
        reference_font=ezdxf.new('R2010').styles.get('Standard').dxf
        for key,value in font.all_existing_dxf_attribs().items():
            if key not in ('name','owner','handle'):
                require(value==getattr(reference_font,key),'Estilo de texto de cota personalizado pendiente: '+key)
    for name in names:
        require(name.startswith('*D') and name in d.blocks,'Bloque gráfico de cota ausente/no admitido')
        block=d.blocks.get(name); require(bool(list(block)),'Bloque gráfico de cota vacío')
        require(tuple(block.block.dxf.base_point)==(0,0,0),'Base de bloque de cota pendiente')
        require(block.block.dxf.flags==1 and block.block.dxf.get('xref_path','')=='','Bloque de cota no anónimo/referencia pendiente')
        for graphic in block:
            require(graphic.dxftype() in ('LINE','SOLID','TEXT') and not graphic.xdata and not graphic.has_extension_dict,
                    'Contenido personalizado de bloque gráfico de cota pendiente')
            require(graphic.dxf.layer.upper()==names[name] and graphic.dxf.color==256 and not graphic.dxf.hasattr('true_color') and
                graphic.dxf.linetype.upper()=='BYLAYER' and graphic.dxf.lineweight==-1 and graphic.dxf.ltscale==1 and
                not graphic.dxf.hasattr('transparency') and graphic.dxf.get('invisible',0)==0,
                'Atributos personalizados de bloque gráfico de cota pendientes')
            require(tuple(graphic.dxf.get('extrusion',(0,0,1)))==(0,0,1) and graphic.dxf.get('thickness',0)==0,'OCS de bloque gráfico pendiente')
            common={'handle','owner','layer','color','linetype','lineweight','ltscale','extrusion','thickness','invisible'}
            allowed={'LINE':{'start','end'},'SOLID':{'vtx0','vtx1','vtx2','vtx3'},'TEXT':{'text','insert','height','style','rotation','halign','valign','align_point'}}[graphic.dxftype()]
            require(set(graphic.dxf.all_existing_dxf_attribs())<=common|allowed,'Propiedades gráficas de cota personalizadas pendientes')
            if graphic.dxftype()=='TEXT':
                require(graphic.dxf.style.upper()=='STANDARD' and graphic.dxf.height==PRESET['dimtxt'],'Texto gráfico fuera del preset')
                require(graphic.dxf.halign==1 and graphic.dxf.valign==2,'Alineación de texto gráfico fuera del preset')
            if graphic.dxftype()=='SOLID': require(graphic.dxf.vtx3==graphic.dxf.vtx2,'SOLID gráfico de cota no triangular pendiente')
    return set(names)


def add_dimension(d,item,render):
    params=dict(dimtype={'DIMLINEAR':0,'DIMALIGNED':1,'DIMRADIUS':4}[item['dimension_type']]|32,
        defpoint=item['position'],dimstyle='Standard',text=item['text'],layer=item['layer'])
    if item['dimension_type']=='DIMRADIUS': params['defpoint4']=item['chord']
    else:
        params.update(defpoint2=item['start'],defpoint3=item['end'])
        if item['dimension_type']=='DIMLINEAR': params['angle']=item['angle']
    block=d.blocks.new_anonymous_block('D')
    params.update(geometry=block.name,text_midpoint=render['text_position'],actual_measurement=render['measurement'],
        attachment_point=8,line_spacing_style=2,line_spacing_factor=1)
    d.modelspace().new_entity('DIMENSION',dxfattribs=params)
    for shape in render['shapes']:
        if shape['type']=='LINE': block.add_line(shape['start'],shape['end'],dxfattribs={'layer':item['layer']})
        elif shape['type']=='SOLID': block.add_solid(shape['vertices'],dxfattribs={'layer':item['layer']})
        else: raise ValueError('Forma de cota sin writer')
    from ezdxf.enums import TextEntityAlignment
    block.add_text(render['label'],dxfattribs=dict(layer=item['layer'],height=render['text_height'],style='Standard',rotation=render['text_angle'])).set_placement(
        render['text_position'],align=TextEntityAlignment.MIDDLE_CENTER)


def apply_preset(d):
    style=d.dimstyles.get('Standard')
    for key,value in PRESET.items(): style.dxf.set(key,value); d.header['$'+key.upper()]=value


def caches_from_file(path):
    d=ezdxf.readfile(path); result=[]
    for e in d.modelspace():
        if e.dxftype()!='DIMENSION': continue
        shapes=[]; labels=[]
        for part in d.blocks.get(e.dxf.geometry):
            if part.dxftype()=='LINE': shapes.append(dict(type='LINE',start=list(part.dxf.start),end=list(part.dxf.end)))
            elif part.dxftype()=='SOLID': shapes.append(dict(type='SOLID',vertices=[list(part.dxf.get('vtx'+str(i))) for i in range(3)]))
            elif part.dxftype()=='TEXT': labels.append(dict(label=unicode_text(part.dxf.text),text_position=list(part.dxf.align_point),text_height=part.dxf.height,text_angle=part.dxf.rotation%360))
        require(len(labels)==1,'Etiqueta gráfica de cota no única')
        result.append(dict(data=dimension_record(e),shapes=shapes,**labels[0]))
    return result


def caches_from_view(view):
    result=[]
    for e in view['entities']:
        if e['type']!='DIMENSION': continue
        data={k:e[k] for k in ('dimension_type','position','text','start','end','chord','angle') if k in e}
        render={k:v for k,v in e['render'].items() if k!='measurement'}
        result.append(dict(data=data,**render))
    return result
