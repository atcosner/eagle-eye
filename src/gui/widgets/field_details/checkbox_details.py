from PyQt6.QtWidgets import QWidget, QLabel, QTreeWidgetItem

from src.database.fields.checkbox_field import CheckboxField
from src.util.types import BoxBounds

from ..util.bounds_widget import BoundsWidget
from ..util.details_table import DetailsTable
from ..util.details_tree import DetailsTree


class TextItem(QTreeWidgetItem):
    def __init__(self, parent: DetailsTree, name: str):
        super().__init__(parent)
        self.setText(0, name)

    def load(self, value: str):
        self.setText(1, value)


class BoundsPart(QTreeWidgetItem):
    def __init__(self, parent: QTreeWidgetItem, name: str):
        super().__init__(parent)
        self.setText(0, name)

    def set_text(self, text: str) -> None:
        self.setText(1, text)


class BoundsItem(QTreeWidgetItem):
    def __init__(self, parent: DetailsTree, name: str):
        super().__init__(parent)
        self.setText(0, name)

        self.top_left = BoundsPart(self, 'Top Left')
        self.width = BoundsPart(self, 'Width')
        self.height = BoundsPart(self, 'Height')

    def load_bounds(self, bounds: BoxBounds):
        self.setText(1, bounds.to_widget())
        self.top_left.set_text(f'{bounds.x},{bounds.y}')
        self.width.set_text(f'{bounds.width}')
        self.height.set_text(f'{bounds.height}')


class CheckboxDetails(DetailsTree):
    def __init__(self):
        super().__init__()

        self.name = TextItem(self, 'Name')
        self.visual_region = BoundsItem(self, 'Visual Region')
        self.checkbox_region = BoundsItem(self, 'Checkbox Region')

        self._load_rows()

    def _load_rows(self) -> None:
        self.addTopLevelItem(self.name)
        # self.add_row('Name', self.name)
        # self.add_row('Visual Region', self.visual_region)
        # self.add_row('Checkbox Region', self.checkbox_region)

    def load_field(self, field: CheckboxField) -> None:
        self.name.load(field.name)
        self.visual_region.load_bounds(field.visual_region)
        self.checkbox_region.load_bounds(field.checkbox_region)
