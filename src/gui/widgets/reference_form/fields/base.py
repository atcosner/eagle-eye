from typing import Any

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsSimpleTextItem, QWidget, \
    QStyleOptionGraphicsItem, QStyle, QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent

from src.database.fields.form_field import FormField

from ..util import AnchorPoint, get_position_with_anchor


class FieldLabel(QGraphicsSimpleTextItem):
    def __init__(self, parent: QGraphicsItem, text: str):
        super().__init__(text, parent=parent)


class ResizeBox(QGraphicsItem):
    def __init__(self, parent: QGraphicsItem, color: QColor, anchors: int):
        super().__init__(parent)
        self.color = color

        self.setAcceptHoverEvents(True)
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        # determine our initial position
        parent_rect = parent.boundingRect()
        self.position_rect = get_position_with_anchor(parent_rect, anchors, 10)

    #
    # Qt overrides
    #

    def mousePressEvent(self, event) -> None:
        print('mouse press')

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        print('mouse move')
        x_change = event.scenePos().x() - event.lastScenePos().x()
        y_change = event.scenePos().y() - event.lastScenePos().y()
        self.parentItem().handle_child_resize(x_change, y_change)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            print(f'child selected: {value}')
        return super().itemChange(change, value)

    def boundingRect(self) -> QRectF:
        return self.position_rect

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: QWidget | None = None,
    ) -> None:
        pen = painter.pen()
        pen.setColor(self.color)
        painter.setPen(pen)
        painter.fillRect(self.position_rect, self.color)

        if self.parentItem().isSelected():
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setColor(QColor('black'))
            painter.setPen(pen)
            painter.drawRect(self.position_rect)


class ResizableField(QGraphicsItem):
    def __init__(self, position_rect: QRectF, color: QColor):
        super().__init__()
        self.hovering: bool = False
        self.selected: bool = False
        self.position_rect = position_rect
        self.color = color

        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        # create the child items for our borders
        self.resize_anchors = [
            ResizeBox(self, color, AnchorPoint.TOP | AnchorPoint.LEFT),
            ResizeBox(self, color, AnchorPoint.TOP | AnchorPoint.RIGHT),
            ResizeBox(self, color, AnchorPoint.TOP | AnchorPoint.H_CENTER),
            ResizeBox(self, color, AnchorPoint.BOTTOM | AnchorPoint.LEFT),
            ResizeBox(self, color, AnchorPoint.BOTTOM | AnchorPoint.RIGHT),
            ResizeBox(self, color, AnchorPoint.BOTTOM | AnchorPoint.H_CENTER),
            ResizeBox(self, color, AnchorPoint.V_CENTER | AnchorPoint.LEFT),
            ResizeBox(self, color, AnchorPoint.V_CENTER | AnchorPoint.RIGHT),
        ]
        for anchor in self.resize_anchors:
            anchor.setVisible(False)

    def update_cursor(self) -> None:
        if self.hovering and self.selected:
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def handle_child_resize(self, delta_x: int, delta_y: int) -> None:
        self.prepareGeometryChange()
        self.position_rect.setWidth(self.position_rect.width() + delta_x)
        self.position_rect.setHeight(self.position_rect.height() + delta_y)

    #
    # Qt overrides
    #

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.hovering = True
        self.update_cursor()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.hovering = False
        self.update_cursor()
        super().hoverEnterEvent(event)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            self.selected = value
            self.update_cursor()
            for anchor in self.resize_anchors:
                anchor.setSelected(True)
                anchor.setVisible(value)
        return super().itemChange(change, value)

    def boundingRect(self) -> QRectF:
        return self.position_rect

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: QWidget | None = None,
    ) -> None:
        pen = painter.pen()
        pen.setColor(self.color)
        painter.setPen(pen)
        painter.drawRect(self.position_rect)

        if option.state & QStyle.StateFlag.State_Selected:
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setColor(QColor('black'))
            painter.setPen(pen)
            painter.drawRect(self.position_rect)


class BaseField(ResizableField):
    def __init__(self, field: FormField, color: QColor) -> None:
        self.position_rect = field.get_sub_field().visual_region.to_qt_rect()
        super().__init__(self.position_rect, color)

        self._field_db_id = field.id

        self.label = FieldLabel(self, field.get_sub_field().name)
        self.label.setPos(self.position_rect.topLeft())

    def get_db_id(self) -> int:
        return self._field_db_id
