"""Small transactional 2D reference model. All coordinates retain Z."""
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass, field, replace
from math import isfinite


@dataclass(frozen=True)
class Point:
    x: float
    y: float
    z: float = 0.0

    def __post_init__(self):
        if not all(isfinite(v) for v in (self.x, self.y, self.z)):
            raise ValueError("Las coordenadas deben ser finitas")

    def moved(self, delta):
        return Point(self.x + delta.x, self.y + delta.y, self.z + delta.z)


@dataclass(frozen=True)
class Line:
    id: int
    start: Point
    end: Point
    layer: str = "0"

    def __post_init__(self):
        if self.start == self.end:
            raise ValueError("Línea de longitud cero")


@dataclass(frozen=True)
class Circle:
    id: int
    center: Point
    radius: float
    layer: str = "0"

    def __post_init__(self):
        if not isfinite(self.radius) or self.radius <= 0:
            raise ValueError("Radio positivo y finito requerido")


@dataclass
class Layer:
    name: str
    color: str = "#d6e2ec"
    visible: bool = True
    locked: bool = False


@dataclass
class Document:
    entities: dict = field(default_factory=dict)
    layers: dict = field(default_factory=lambda: {"0": Layer("0")})
    current_layer: str = "0"
    next_id: int = 1
    units: int = 0
    _undo: list = field(default_factory=list, repr=False)
    _redo: list = field(default_factory=list, repr=False)
    _depth: int = field(default=0, repr=False)

    def snapshot(self):
        return deepcopy((self.entities, self.layers, self.current_layer, self.next_id, self.units))

    def restore(self, state):
        self.entities, self.layers, self.current_layer, self.next_id, self.units = deepcopy(state)

    @contextmanager
    def transaction(self):
        state = self.snapshot()
        outer = self._depth == 0
        self._depth += 1
        try:
            yield
        except Exception:
            self.restore(state)
            raise
        else:
            if outer and self.snapshot() != state:
                self._undo.append(state)
                self._redo.clear()
        finally:
            self._depth -= 1

    def writable(self, layer):
        if layer not in self.layers:
            raise ValueError("Capa desconocida")
        if self.layers[layer].locked:
            raise ValueError("Capa bloqueada")

    def add_line(self, start, end):
        self.writable(self.current_layer)
        entity = Line(self.next_id, start, end, self.current_layer)
        self.entities[entity.id] = entity
        self.next_id += 1
        return entity.id

    def add_circle(self, center, radius):
        self.writable(self.current_layer)
        entity = Circle(self.next_id, center, radius, self.current_layer)
        self.entities[entity.id] = entity
        self.next_id += 1
        return entity.id

    def move(self, ids, delta):
        ids = list(dict.fromkeys(ids))
        for i in ids:
            self.writable(self.entities[i].layer)
        for i in ids:
            e = self.entities[i]
            self.entities[i] = (replace(e, start=e.start.moved(delta), end=e.end.moved(delta))
                                if isinstance(e, Line) else replace(e, center=e.center.moved(delta)))

    def erase(self, ids):
        ids = list(dict.fromkeys(ids))
        for i in ids:
            self.writable(self.entities[i].layer)
        for i in ids:
            del self.entities[i]

    def undo(self):
        if self._depth:
            raise ValueError("UNDO no permitido durante una transacción")
        if self._undo:
            self._redo.append(self.snapshot())
            self.restore(self._undo.pop())

    def redo(self):
        if self._depth:
            raise ValueError("REDO no permitido durante una transacción")
        if self._redo:
            self._undo.append(self.snapshot())
            self.restore(self._redo.pop())

