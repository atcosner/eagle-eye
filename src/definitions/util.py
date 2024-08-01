from typing import NamedTuple


class BoxBounds(NamedTuple):
    # Top Left Coordinate
    x: int
    y: int
    width: int
    height: int


class OcrField(NamedTuple):
    name: str
    region: BoxBounds
    segment: str
