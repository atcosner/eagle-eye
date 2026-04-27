from typing import Any

from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QLineEdit

from src.util.types import BoxBounds


class TextItem(QTreeWidgetItem):
    def __init__(self, parent: QTreeWidget | QTreeWidgetItem, name: str):
        super().__init__(parent)
        self.setText(0, name)

    def load(self, value: Any) -> None:
        self.setText(1, str(value))


class BoundsPart(QTreeWidgetItem):
    def __init__(self, parent: QTreeWidgetItem, name: str):
        super().__init__(parent)
        self._is_dirty: bool = False
        self._initial_text: str | None = None

        self.setText(0, name)

        # TODO: integer validator
        self.edit = QLineEdit()
        self.edit.textEdited.connect(self.handle_text_changed)
        self.treeWidget().setItemWidget(self, 1, self.edit)

    def _update_title(self) -> None:
        # Bold the title if the data is dirty
        font = self.font(0)
        font.setBold(self._is_dirty)
        self.setFont(0, font)

        # Add an asterisk if the data is dirty
        new_title = self.text(0)
        if new_title.startswith('*'):
            new_title = new_title[1:] if not self._is_dirty else new_title
        else:
            new_title = f'* {new_title}' if self._is_dirty else new_title
        self.setText(0, new_title)

    def load_data(self, text: str) -> None:
        self._initial_text = text
        self._is_dirty = False

        self.edit.setText(text)
        self._update_title()

    def get_text(self) -> str:
        return self.edit.text()
    
    def update_text(self, new_text: str) -> None:
        self.edit.setText(new_text)
        self.handle_text_changed(new_text)

    def handle_text_changed(self, new_text: str) -> None:
        # Ignore changes if we don't have initial text
        if self._initial_text is None:
            return

        # Update the title and alert our parent of a change
        self._is_dirty = self._initial_text != new_text.strip()
        self._update_title()
        self.parent().handle_child_data_change()  # We can't use a signal so call the parent directly


class BoxBoundsDetails(QTreeWidgetItem):
    def __init__(self, parent: QTreeWidget | QTreeWidgetItem, name: str):
        super().__init__(parent)
        self._is_dirty: bool = False
        self._initial_bounds: BoxBounds | None = None

        self.setText(0, name)

        self.top_left = BoundsPart(self, 'Top Left')
        self.width = BoundsPart(self, 'Width')
        self.height = BoundsPart(self, 'Height')

    def _update_title(self) -> None:
        # Bold the title if the data is dirty
        font = self.font(0)
        font.setBold(self._is_dirty)
        self.setFont(0, font)

        # Add an asterisk if the data is dirty
        new_title = self.text(0)
        if new_title.startswith('*'):
            new_title = new_title[1:] if not self._is_dirty else new_title
        else:
            new_title = f'* {new_title}' if self._is_dirty else new_title
        self.setText(0, new_title)

    def load(self, bounds: BoxBounds) -> None:
        self._initial_bounds = bounds
        self._is_dirty = False

        self.top_left.load_data(f'{bounds.x},{bounds.y}')
        self.width.load_data(f'{bounds.width}')
        self.height.load_data(f'{bounds.height}')

        self._update_title()

    def update_position(self, position: QRect) -> None:
        self.top_left.update_text(f'{position.x()},{position.y()}')
        self.width.update_text(f'{position.width()}')
        self.height.update_text(f'{position.height()}')

        self._update_title()

    def handle_child_data_change(self):
        # Create the box bounds from our children
        new_bounds = BoxBounds.from_db(f'{self.top_left.get_text()},{self.width.get_text()},{self.height.get_text()}')
        self._is_dirty = self._initial_bounds != new_bounds

        self._update_title()
        self.treeWidget().resizeColumnToContents(0)


class BaseFieldDetails(QTreeWidget):
    def __init__(self):
        super().__init__()

        self.name_item = TextItem(self, 'Name')
        self.visual_region_item  = BoxBoundsDetails(self, 'Visual Region')

        self.setColumnCount(2)
        self.setHeaderLabels(['Setting', 'Value'])
    
    def _load(self, name: str, bounds: BoxBounds | None) -> None:
        self.name_item.load(name)
        if bounds is not None:
            self.visual_region_item.load(bounds)
        else:
            self.visual_region_item.setHidden(True)
    
    def update_position(self, position: QRect) -> None:
        self.visual_region_item.update_position(position)
