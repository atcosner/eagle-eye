from enum import Enum
from pathlib import Path
from typing import NamedTuple

from PyQt6.QtCore import QRectF, QPointF


class BoxBounds(NamedTuple):
    x: int
    y: int
    width: int
    height: int

    def to_widget(self) -> str:
        return f'Top Left: ({self.x}, {self.y}) | Width: {self.width} | Height: {self.height}'

    def to_db(self) -> str:
        return f'{self.x},{self.y},{self.width},{self.height}'

    @staticmethod
    def from_db(db_value: str | None) -> 'BoxBounds | None':
        if db_value is None:
            return None

        int_values = [int(part) for part in db_value.split(',')]
        return BoxBounds(*int_values)

    def to_qt_rect(self) -> QRectF:
        return QRectF(self.x, self.y, self.width, self.height)

    def qt_top_left(self) -> QPointF:
        return QPointF(self.x, self.y)


class FileDetails(NamedTuple):
    db_id: int
    path: Path


class FormLinkingMethod(Enum):
    NO_LINKING = 1
    PREVIOUS_IDENTIFIER = 2
    PREVIOUS_REGION = 3
