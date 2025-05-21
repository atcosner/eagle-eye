from PyQt6.QtCore import Qt
from PyQt6.QtGui import QWheelEvent
from PyQt6.QtWidgets import QTimeEdit, QDateEdit


class StrongFocusTimeEdit(QTimeEdit):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event: QWheelEvent) -> None:
        # only allow navigating via scroll when in focus
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


class StrongFocusDateEdit(QDateEdit):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCalendarPopup(True)

    def wheelEvent(self, event: QWheelEvent) -> None:
        # only allow navigating via scroll when in focus
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()
