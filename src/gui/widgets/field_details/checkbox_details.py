from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtWidgets import QWidget, QLabel, QTreeWidgetItem, QLineEdit

from src.database.fields.checkbox_field import CheckboxField
from src.util.types import BoxBounds

from ..util.bounds_widget import BoundsWidget
from ..util.details_tree import DetailsTree, BoxBoundsDetails


class TextItem(QTreeWidgetItem):
    def __init__(self, parent: DetailsTree, name: str):
        super().__init__(parent)
        self.setText(0, name)

    def load(self, value: str):
        self.setText(1, value)


class CheckboxDetails(DetailsTree):
    def __init__(self):
        super().__init__()

        self.name = TextItem(self, 'Name')
        self.visual_region = BoxBoundsDetails(self, 'Visual Region')
        self.checkbox_region = BoxBoundsDetails(self, 'Checkbox Region')

        self.resizeColumnToContents(0)

    def load_field(self, field: CheckboxField) -> None:
        self.name.load(field.name)
        self.visual_region.load_bounds(field.visual_region)
        self.checkbox_region.load_bounds(field.checkbox_region)
