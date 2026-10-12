"""Read-only native entity projections. These never edit authoritative geometry."""
from dataclasses import dataclass
from .model import Point


@dataclass(frozen=True)
class Arc:
    id: int
    center: Point
    radius: float
    start_angle: float  # degrees, canonical counterclockwise geometry
    end_angle: float
    layer: str = '0'


@dataclass(frozen=True)
class Polyline:
    id: int
    vertices: tuple[Point, ...]
    closed: bool
    layer: str = '0'


@dataclass(frozen=True)
class Dimension:
    id: int
    kind: str
    position: Point
    text: str
    start: Point | None
    end: Point | None
    chord: Point | None
    angle: float | None
    render: dict
    layer: str = '0'
