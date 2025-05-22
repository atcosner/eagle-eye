from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPen, QColor, QPainter
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsSimpleTextItem, QWidget, \
    QStyleOptionGraphicsItem, QStyle

from src.database.fields.form_field import FormField


class FieldLabel(QGraphicsSimpleTextItem):
    def __init__(self, parent: QGraphicsItem, text: str):
        super().__init__(text, parent=parent)


# class BaseField(QGraphicsRectItem):
#     def __init__(self, field: FormField, color: QColor) -> None:
#         super().__init__()
#         self._field_db_id = field.id
#         sub_field = field.get_sub_field()
#
#         location_rect = sub_field.visual_region.to_qt_rect()
#         self.setRect(location_rect)
#         self.setPen(QPen(color))
#         self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
#         self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
#
#         self.label = FieldLabel(self, sub_field.name)
#         self.label.setPos(location_rect.topLeft())
#
#     def get_db_id(self) -> int:
#         return self._field_db_id


class BaseGraphicsItem(QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        # create the child items for our borders
        self.edges = [
            QGraphicsRectItem(QRectF(100, 100, 20, 20), self)
        ]


class BaseField(BaseGraphicsItem):
    def __init__(self, field: FormField, color: QColor) -> None:
        super().__init__()
        self._field_db_id = field.id
        self.position_rect = field.get_sub_field().visual_region.to_qt_rect()
        self.color = color

        self.label = FieldLabel(self, field.get_sub_field().name)
        self.label.setPos(self.position_rect.topLeft())

    def get_db_id(self) -> int:
        return self._field_db_id

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

