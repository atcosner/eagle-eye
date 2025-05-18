from PyQt6.QtGui import QPen, QColor
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsSimpleTextItem

from src.database.fields.form_field import FormField


class FieldLabel(QGraphicsSimpleTextItem):
    def __init__(self, parent: QGraphicsItem, text: str):
        super().__init__(text, parent=parent)


class BaseField(QGraphicsRectItem):
    def __init__(self, field: FormField, color: QColor) -> None:
        super().__init__()
        self._field_db_id = field.id
        sub_field = field.get_sub_field()

        location_rect = sub_field.visual_region.to_qt_rect()
        self.setRect(location_rect)
        self.setPen(QPen(color))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        self.label = FieldLabel(self, sub_field.name)
        self.label.setPos(location_rect.topLeft())

    def get_db_id(self) -> int:
        return self._field_db_id

    # def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
    #     val = super().itemChange(change, value)
    #     if change == QGraphicsItem.GraphicsItemChange.ItemSceneChange:
    #         print(self.scenePos())
    #
    #     return val
