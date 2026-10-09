"""Deliberately strict DXF subset. Reject loss rather than silently discard data."""
import os
import tempfile
from pathlib import Path
from .model import Document, Point, Line, Circle, Layer


def save_dxf(document, path):
    import ezdxf
    path = Path(path)
    if path.suffix.lower() != ".dxf":
        raise ValueError("Sólo exportación DXF; DWG no implementado")
    drawing = ezdxf.new("R2010")
    for name, layer in document.layers.items():
        target = drawing.layers.get(name) if name in drawing.layers else drawing.layers.new(name)
        target.dxf.true_color = int(layer.color.lstrip("#"), 16)
        target.lock() if layer.locked else target.unlock()
        target.on() if layer.visible else target.off()
    space = drawing.modelspace()
    for e in document.entities.values():
        attrs = {"layer": e.layer}
        if isinstance(e, Line):
            space.add_line((e.start.x,e.start.y,e.start.z), (e.end.x,e.end.y,e.end.z), dxfattribs=attrs)
        elif isinstance(e, Circle):
            space.add_circle((e.center.x,e.center.y,e.center.z), e.radius, dxfattribs=attrs)
        else:
            raise ValueError("Entidad no soportada")
    drawing.header["$CLAYER"] = document.current_layer
    drawing.header["$INSUNITS"] = document.units
    fd, temp = tempfile.mkstemp(suffix=".dxf", dir=path.parent)
    os.close(fd)
    try:
        drawing.saveas(temp)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def load_dxf(path):
    import ezdxf
    if Path(path).suffix.lower() != ".dxf":
        raise ValueError("Sólo DXF; DWG no implementado")
    drawing = ezdxf.readfile(path)
    unsupported = sorted({e.dxftype() for e in drawing.modelspace() if e.dxftype() not in ("LINE", "CIRCLE")})
    if unsupported:
        raise ValueError("DXF fuera del subconjunto: " + ", ".join(unsupported))
    if len(list(drawing.layouts)) > 2 or len(drawing.paperspace()) or any(not b.name.startswith("*") for b in drawing.blocks):
        raise ValueError("Bloques/presentaciones con contenido aún no soportados")
    doc = Document()
    doc.units = drawing.header.get("$INSUNITS",0)
    doc.layers = {}
    for layer in drawing.layers:
        if layer.is_frozen() or layer.dxf.linetype != "Continuous" or layer.dxf.lineweight != -3 or layer.has_extension_dict or layer.xdata:
            raise ValueError("Attributs de capa fuera del subconjunto de conservación")
        rgb = layer.rgb or (214, 226, 236)
        doc.layers[layer.dxf.name] = Layer(layer.dxf.name, "#%02x%02x%02x" % tuple(rgb), not layer.is_off(), layer.is_locked())
    for e in drawing.modelspace():
        if e.xdata or e.has_extension_dict or e.dxf.linetype != "BYLAYER" or e.dxf.color != 256 or e.dxf.hasattr("true_color") or e.dxf.lineweight != -1:
            raise ValueError("Atributos de entidad fuera del subconjunto de conservación")
        if e.dxftype() == "CIRCLE" and tuple(e.dxf.extrusion) != (0, 0, 1):
            raise ValueError("Círculo fuera del plano XY")
        if e.dxf.get("thickness", 0) != 0:
            raise ValueError("Espesor no soportado")
        if e.dxf.get("invisible",0) or e.dxf.get("ltscale",1) != 1 or e.dxf.hasattr("transparency"):
            raise ValueError("Visibilidad, escala de línea o transparencia de entidad no soportada")
        doc.current_layer = e.dxf.layer
        if e.dxftype() == "LINE":
            doc.entities[doc.next_id] = Line(doc.next_id, Point(*e.dxf.start), Point(*e.dxf.end), e.dxf.layer)
        else:
            doc.entities[doc.next_id] = Circle(doc.next_id, Point(*e.dxf.center), e.dxf.radius, e.dxf.layer)
        doc.next_id += 1
    doc.current_layer = drawing.header.get("$CLAYER", "0")
    if doc.current_layer not in doc.layers:
        doc.current_layer = "0"
    return doc
