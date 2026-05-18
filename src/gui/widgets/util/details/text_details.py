from typing import Any

from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem


class TextDetails(QTreeWidgetItem):
    def __init__(self, parent: QTreeWidget | QTreeWidgetItem, name: str):
        super().__init__(parent)
        self.setText(0, name)

    def load(self, value: Any) -> None:
        self.setText(1, str(value))
