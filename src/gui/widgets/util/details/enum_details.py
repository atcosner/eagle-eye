from enum import Enum

from PyQt6.QtWidgets import QTreeWidgetItem, QComboBox


class EnumDetails(QTreeWidgetItem):
    def __init__(self, parent: QTreeWidgetItem, name: str, value_enum: Enum):
        super().__init__(parent)
        self._is_dirty: bool = False
        self._initial_value: int | None = None
        self._enum: Enum = value_enum

        self.setText(0, name)

        self._combo_box = QComboBox()
        self._combo_box.currentIndexChanged.connect(self.handle_current_index_changed)
        self.treeWidget().setItemWidget(self, 1, self._combo_box)

        # add all the enum values to the combo box
        for value in self._enum:
            value_name = value.name.replace('_', ' ').capitalize()
            self._combo_box.addItem(value_name, value.value)

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
    
    def load_data(self, value: Enum) -> None:
        self._initial_value = value.value
        self._is_dirty = False

        index = self._combo_box.findData(value.value)
        if index != -1:
            self._combo_box.setCurrentIndex(index)
        self._update_title()

    def handle_current_index_changed(self, current_index: int) -> None:
        if current_index == -1:
            return
        
        value = self._combo_box.itemData(current_index)
        self._is_dirty = value != self._initial_value
        self._update_title()
