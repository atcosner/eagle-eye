from PyQt6.QtCore import Qt
from PyQt6.QtGui import QWheelEvent
from PyQt6.QtWidgets import QComboBox


class SearchComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.addItem('<NO MATCH>')
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        # Don't allow focus from simply mousing over while scrolling
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event: QWheelEvent) -> None:
        # only allow navigating via scroll when in focus
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()
