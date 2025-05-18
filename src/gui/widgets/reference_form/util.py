from enum import Enum, auto

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsItemGroup, QWidget, QStyleOptionGraphicsItem, QStyle


class SelectionType(Enum):
    REGION = auto()
    FIELD = auto()


class RegionGroup(QGraphicsItemGroup):
    def __init__(self, color: QColor, children: list[QGraphicsItem]):
        super().__init__()
        self._color = color

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

        for child in children:
            self.addToGroup(child)

    #
    # Qt function overrides
    #

    def paint(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
            widget: QWidget | None = None,
    ) -> None:
        if option.state & QStyle.StateFlag.State_Selected:
            pen = painter.pen()
            pen.setColor(self._color)
            pen.setWidth(8)
            pen.setStyle(Qt.PenStyle.DashLine)

            painter.setPen(pen)

        super().paint(painter, option, widget)
