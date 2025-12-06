from enum import Enum, auto, IntEnum

from PyQt6.QtCore import Qt, QRectF, QPointF, QSizeF
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsItemGroup, QWidget, QStyleOptionGraphicsItem, QStyle


class SelectionType(Enum):
    REGION = auto()
    FIELD_GROUP = auto()
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


class AnchorPoint(Enum):
    TOP_LEFT = object()
    TOP_MIDDLE = object()
    TOP_RIGHT = object()
    LEFT_MIDDLE = object()
    RIGHT_MIDDLE = object()
    BOTTOM_LEFT = object()
    BOTTOM_MIDDLE = object()
    BOTTOM_RIGHT = object()


def get_position_with_anchor(inside_rect: QRectF, anchor: AnchorPoint, width: int) -> QRectF:
    top_left_point = QPointF()
    match anchor:
        case AnchorPoint.TOP_LEFT:
            top_left_point.setX(inside_rect.topLeft().x() - width)
            top_left_point.setY(inside_rect.topLeft().y() - width)
        case AnchorPoint.TOP_MIDDLE:
            top_left_point.setX(inside_rect.topLeft().x() + ((inside_rect.width() - width) // 2))
            top_left_point.setY(inside_rect.topLeft().y() - width)
        case AnchorPoint.TOP_RIGHT:
            top_left_point.setX(inside_rect.bottomRight().x())
            top_left_point.setY(inside_rect.topLeft().y() - width)
        case AnchorPoint.LEFT_MIDDLE:
            top_left_point.setX(inside_rect.topLeft().x() - width)
            top_left_point.setY(inside_rect.topLeft().y() + ((inside_rect.height() - width) // 2))
        case AnchorPoint.RIGHT_MIDDLE:
            top_left_point.setX(inside_rect.bottomRight().x())
            top_left_point.setY(inside_rect.topLeft().y() + ((inside_rect.height() - width) // 2))
        case AnchorPoint.BOTTOM_LEFT:
            top_left_point.setX(inside_rect.topLeft().x() - width)
            top_left_point.setY(inside_rect.bottomRight().y())
        case AnchorPoint.BOTTOM_MIDDLE:
            top_left_point.setX(inside_rect.topLeft().x() + ((inside_rect.width() - width) // 2))
            top_left_point.setY(inside_rect.bottomRight().y())
        case AnchorPoint.BOTTOM_RIGHT:
            top_left_point.setX(inside_rect.bottomRight().x())
            top_left_point.setY(inside_rect.bottomRight().y())

    return QRectF(top_left_point, QSizeF(width, width))


def get_movement_restrictions(anchor: AnchorPoint) -> tuple[bool, bool]:
    x_restricted = False
    y_restricted = False

    if anchor in [AnchorPoint.TOP_MIDDLE, AnchorPoint.BOTTOM_MIDDLE]:
        x_restricted = True
    if anchor in [AnchorPoint.LEFT_MIDDLE, AnchorPoint.RIGHT_MIDDLE]:
        y_restricted = True

    return x_restricted, y_restricted


def get_irregular_change(anchor: AnchorPoint) -> bool:
    return False if anchor in [AnchorPoint.RIGHT_MIDDLE, AnchorPoint.BOTTOM_MIDDLE, AnchorPoint.BOTTOM_RIGHT] else True
