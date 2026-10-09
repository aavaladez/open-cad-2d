import json
import shlex
from math import hypot, sqrt
from pathlib import Path
from .model import Layer, Point


def point(value):
    if isinstance(value, Point):
        return value
    values = list(value) if isinstance(value, (list, tuple)) else str(value).split(",")
    if len(values) not in (2, 3):
        raise ValueError("Punto esperado: X,Y o X,Y,Z")
    return Point(*map(float, values))


class CommandBus:
    def __init__(self, document, aliases=None):
        self.document = document
        self.definitions = json.loads(Path(__file__).with_name("commands.json").read_text(encoding="utf-8"))
        self.aliases = {a: c for c, d in self.definitions.items() for a in d["aliases"]}
        self.lisp = None
        if aliases is not None:
            self.set_aliases(aliases)

    def set_aliases(self, aliases):
        proposed = dict(self.aliases)
        for alias, command in aliases.items():
            alias, command = alias.upper(), command.upper()
            if not alias or any(c.isspace() for c in alias) or alias in self.definitions or command not in self.definitions:
                raise ValueError("Alias inválido o comando desconocido")
            proposed[alias] = command
        self.aliases = proposed

    def execute_text(self, text):
        tokens = shlex.split(text, posix=True)
        if not tokens:
            return None
        return self.execute(tokens[0], *tokens[1:])

    def execute(self, name, *args):
        name = name.upper().removeprefix("_")
        name = self.aliases.get(name, name)
        if name not in self.definitions:
            if self.lisp and "C:" + name in self.lisp.functions:
                return self.lisp.call_command(name)
            raise ValueError(f"Comando no implementado: {name}")
        if name in ("UNDO", "REDO"):
            if args:
                raise ValueError("No se admiten opciones de historial en este prototipo")
            return getattr(self.document, name.lower())()
        with self.document.transaction():
            if name == "LINE":
                if len(args) < 2:
                    raise ValueError("LINE X,Y X,Y [X,Y ...]")
                points = [point(a) for a in args]
                return [self.document.add_line(a, b) for a, b in zip(points, points[1:])]
            if name == "CIRCLE":
                if len(args) != 2:
                    raise ValueError("CIRCLE centro radio")
                return self.document.add_circle(point(args[0]), float(args[1]))
            if name == "MOVE":
                if len(args) != 2:
                    raise ValueError("MOVE id[,id] dx,dy[,dz]")
                return self.document.move(self.ids(args[0]), point(args[1]))
            if name == "ERASE":
                if len(args) != 1:
                    raise ValueError("ERASE id[,id]")
                return self.document.erase(self.ids(args[0]))
            if name == "DIST":
                if len(args) != 2:
                    raise ValueError("DIST punto punto")
                a, b = map(point, args)
                return {"xy": hypot(b.x-a.x, b.y-a.y), "xyz": sqrt((b.x-a.x)**2 + (b.y-a.y)**2 + (b.z-a.z)**2)}
            if name == "LAYER":
                if len(args) != 2:
                    raise ValueError("LAYER NEW|SET|LOCK|UNLOCK|ON|OFF nombre")
                action, layer = str(args[0]).upper(), str(args[1])
                if not layer or any(c in layer for c in '<>/\\":;?*|='):
                    raise ValueError("Nombre de capa inválido")
                if action == "NEW":
                    if layer in self.document.layers:
                        raise ValueError("La capa ya existe")
                    self.document.layers[layer] = Layer(layer)
                elif layer not in self.document.layers:
                    raise ValueError("Capa desconocida")
                elif action == "SET":
                    self.document.current_layer = layer
                elif action in ("LOCK", "UNLOCK"):
                    self.document.layers[layer].locked = action == "LOCK"
                elif action in ("ON", "OFF"):
                    self.document.layers[layer].visible = action == "ON"
                else:
                    raise ValueError("Opción de capa no implementada")

    @staticmethod
    def ids(value):
        return [int(v) for v in str(value).split(",")]
