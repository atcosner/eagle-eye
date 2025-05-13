from PyQt6.QtCore import QMargins
from PyQt6.QtWidgets import QLabel


class TableLabel(QLabel):
    def __init__(self, text: str, margins: QMargins):
        super().__init__(text)
        self.setContentsMargins(margins)
