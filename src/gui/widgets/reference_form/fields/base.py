from typing import Any

from PyQt6.QtCore import Qt, QRect, QRectF, pyqtSignal
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsSimpleTextItem, QWidget, \
    QStyleOptionGraphicsItem, QStyle, QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent, QGraphicsObject

from src.database.fields.circled_field import CircledField
from src.database.fields.checkbox_field import CheckboxField
from src.database.fields.form_field import FormField
from src.database.fields.multi_checkbox_field import MultiCheckboxField

from ..util import AnchorPoint, get_position_with_anchor, get_movement_restrictions


class FieldLabel(QGraphicsSimpleTextItem):
    def __init__(self, parent: QGraphicsItem, text: str):
        super().__init__(text, parent=parent)
    
    def set_bold(self, bold: bool) -> None:
        font = self.font()
        font.setBold(bold)
        self.setFont(font)


class ResizeBox(QGraphicsItem):
    def __init__(self, parent: QGraphicsItem, color: QColor, anchor_point: AnchorPoint):
        super().__init__(parent)
        self.setAcceptHoverEvents(True)

        self.position_rect: QRectF = QRectF()
        self.anchor_point = anchor_point
        self.color = color
        self.x_restricted, self.y_restricted = get_movement_restrictions(anchor_point)

        # determine our initial position
        self.update_position()

    def update_position(self) -> None:
        self.prepareGeometryChange()
        self.position_rect = get_position_with_anchor(self.parentItem().boundingRect(), self.anchor_point, 10)

    #
    # Qt overrides
    #
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent | None) -> None:
        # swallow these events to not take focus from parent
        pass

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent | None) -> None:
        if event is not None:
            x_change = 0 if self.x_restricted else event.scenePos().x() - event.lastScenePos().x()
            y_change = 0 if self.y_restricted else event.scenePos().y() - event.lastScenePos().y()
            self.parentItem().handle_child_resize(self.anchor_point, x_change, y_change)

    def boundingRect(self) -> QRectF:
        return self.position_rect

    def paint(
        self,
        painter: QPainter | None,
        option: QStyleOptionGraphicsItem | None,
        widget: QWidget | None = None,
    ) -> None:
        if painter is None:
            return

        pen = painter.pen()
        pen.setColor(self.color)
        painter.setPen(pen)
        painter.fillRect(self.position_rect, self.color)

        if self.parentItem().isSelected():
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setColor(QColor('black'))
            painter.setPen(pen)
            painter.drawRect(self.position_rect)


class ResizableField(QGraphicsObject):
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
            ResizeBox(self, color, AnchorPoint.TOP_LEFT),
            ResizeBox(self, color, AnchorPoint.TOP_RIGHT),
            ResizeBox(self, color, AnchorPoint.TOP_MIDDLE),
            ResizeBox(self, color, AnchorPoint.BOTTOM_LEFT),
            ResizeBox(self, color, AnchorPoint.BOTTOM_RIGHT),
            ResizeBox(self, color, AnchorPoint.BOTTOM_MIDDLE),
            ResizeBox(self, color, AnchorPoint.LEFT_MIDDLE),
            ResizeBox(self, color, AnchorPoint.RIGHT_MIDDLE),
        ]
        for anchor in self.resize_anchors:
            anchor.setVisible(False)

    def update_cursor(self) -> None:
        if self.hovering and self.selected:
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def handle_child_resize(self, point: AnchorPoint, delta_x: int, delta_y: int) -> None:
        if delta_x or delta_y:
            self.prepareGeometryChange()
            if point in [AnchorPoint.TOP_LEFT, AnchorPoint.TOP_MIDDLE, AnchorPoint.LEFT_MIDDLE]:
                # instead of changing the width and height we need to change the top left point
                update_point = self.position_rect.topLeft()
                update_point.setX(update_point.x() + delta_x)
                update_point.setY(update_point.y() + delta_y)
                self.position_rect.setTopLeft(update_point)
            elif point is AnchorPoint.BOTTOM_LEFT:
                update_point = self.position_rect.bottomLeft()
                update_point.setX(update_point.x() + delta_x)
                update_point.setY(update_point.y() + delta_y)
                self.position_rect.setBottomLeft(update_point)
            elif point is AnchorPoint.TOP_RIGHT:
                update_point = self.position_rect.topRight()
                update_point.setX(update_point.x() + delta_x)
                update_point.setY(update_point.y() + delta_y)
                self.position_rect.setTopRight(update_point)
            else:
                # Right middle, bottom middle, bottom right
                if delta_x:
                    self.position_rect.setWidth(self.position_rect.width() + delta_x)
                if delta_y:
                    self.position_rect.setHeight(self.position_rect.height() + delta_y)

        for anchor in self.resize_anchors:
            anchor.update_position()

    #
    # Qt overrides
    #

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent | None) -> None:
        self.hovering = True
        self.update_cursor()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent | None) -> None:
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
        painter: QPainter | None,
        option: QStyleOptionGraphicsItem | None,
        widget: QWidget | None = None,
    ) -> None:
        if painter is None:
            return

        pen = painter.pen()
        pen.setColor(self.color)
        painter.setPen(pen)
        painter.drawRect(self.position_rect)

        if option and option.state & QStyle.StateFlag.State_Selected:
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setColor(QColor('black'))
            painter.setPen(pen)
            painter.drawRect(self.position_rect)


class LabeledField(ResizableField):
    def __init__(self, position_rect: QRectF, color: QColor, label: str) -> None:
        super().__init__(position_rect, color)

        self._label = FieldLabel(self, label)
        self._label.setPos(self.position_rect.topLeft())

    def handle_child_resize(self, point: AnchorPoint, delta_x: int, delta_y: int) -> None:
        super().handle_child_resize(point, delta_x, delta_y)
        self._label.setPos(self.position_rect.topLeft())


class DbSceneField(LabeledField):
    positionUpdate = pyqtSignal(int, QRect)

    def __init__(self, field: FormField, color: QColor) -> None:
        super().__init__(
            field.get_sub_field().visual_region.to_qt_rect(),
            color,
            field.get_sub_field().name,
        )

        self._field_db_id = field.id
        self._child_items: list[LabeledField] = []

        # make the primary label bold
        self._label.set_bold(True)

        # don't draw ourselves if we dont have a visual region
        self.setVisible(not self.position_rect.isEmpty())

        self._add_children(field, color)

    def _add_children(self, field: FormField, color: QColor) -> None:
        sub_field = field.get_sub_field()
        if isinstance(sub_field, CircledField):
            for option in sub_field.options:
                child_item = LabeledField(option.region.to_qt_rect(), color, option.name)
                child_item.setParentItem(self)
                self._child_items.append(child_item)
        elif isinstance(sub_field, CheckboxField):
            child_item = LabeledField(sub_field.checkbox_region.to_qt_rect(), color, '')
            child_item.setParentItem(self)
            self._child_items.append(child_item)
        elif isinstance(sub_field, MultiCheckboxField):
            for checkbox in sub_field.checkboxes:
                child_item = LabeledField(checkbox.region.to_qt_rect(), color, checkbox.name)
                child_item.setParentItem(self)
                self._child_items.append(child_item)

    def get_db_id(self) -> int:
        return self._field_db_id

    def handle_child_resize(self, point: AnchorPoint, delta_x: int, delta_y: int) -> None:
        super().handle_child_resize(point, delta_x, delta_y)
        self.positionUpdate.emit(self._field_db_id, self.position_rect.toRect())
