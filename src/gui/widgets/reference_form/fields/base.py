from PyQt6.QtGui import QPen, QColor
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsSimpleTextItem

from src.database.fields.form_field import FormField


class FieldLabel(QGraphicsSimpleTextItem):
    def __init__(self, parent: QGraphicsItem, text: str):
        super().__init__(text, parent=parent)
        # self.setParentItem(parent)
        # self.setPos(0, 0)
        # print(self.parentItem())
        # print(self.pos())
        # print(self.mapToParent(0, 0))
        # print(self.parentItem().pos())


class BaseField(QGraphicsRectItem):
    def __init__(self, field: FormField, color: QColor) -> None:
        super().__init__()
        self._field_db_id = field.id
        sub_field = field.get_sub_field()

        self.setRect(sub_field.visual_region.to_qt_rect())
        self.setPen(QPen(color))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        # # print(self.pos())
        # self.label = FieldLabel(self, sub_field.name)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        val = super().itemChange(change, value)
        if change == QGraphicsItem.GraphicsItemChange.ItemSceneChange:
            print(self.scenePos())

        return val
