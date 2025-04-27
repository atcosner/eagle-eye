from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import QScrollArea, QWidget


class SizedScrollArea(QScrollArea):
    def __init__(self, widget: QWidget):
        super().__init__()
        self.setWidgetResizable(True)
        self.setWidget(widget)

    def showEvent(self, event: QShowEvent) -> None:
        # Match our minimum width to the size hint of the inner widget
        self.setMinimumWidth(self.widget().sizeHint().width())
        event.accept()
