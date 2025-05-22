from enum import Enum, auto, IntEnum

from PyQt6.QtCore import Qt, QRectF, QPointF, QSizeF
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


class AnchorPoint(IntEnum):
    TOP = 0x1
    BOTTOM = 0x2
    V_CENTER = 0x20
    LEFT = 0x4
    RIGHT = 0x8
    H_CENTER = 0x10


def get_position_with_anchor(inside_rect: QRectF, anchors: int, width: int) -> QRectF:
    top_left_point = QPointF()
    if anchors & AnchorPoint.TOP:
        top_left_point.setY(inside_rect.topLeft().y() - width)
    elif anchors & AnchorPoint.BOTTOM:
        top_left_point.setY(inside_rect.bottomRight().y())
    elif anchors & AnchorPoint.V_CENTER:
        offset = (inside_rect.height() - width) // 2
        top_left_point.setY(inside_rect.topLeft().y() + offset)
    else:
        raise RuntimeError('No vertical anchor specified')

    if anchors & AnchorPoint.LEFT:
        top_left_point.setX(inside_rect.topLeft().x() - width)
    elif anchors & AnchorPoint.RIGHT:
        top_left_point.setX(inside_rect.bottomRight().x())
    elif anchors & AnchorPoint.H_CENTER:
        offset = (inside_rect.width() - width) // 2
        top_left_point.setX(inside_rect.topLeft().x() + offset)
    else:
        raise RuntimeError('No vertical anchor specified')

    return QRectF(top_left_point, QSizeF(width, width))
