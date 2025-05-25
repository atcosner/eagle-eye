from PyQt6.QtWidgets import QDialog, QWidget


class ReferenceFormSelector(QDialog):
    def __init__(self, parent: QWidget | None):
        super().__init__(parent)
        self.setWindowTitle('Reference Form Selector')
        self.setMinimumWidth(400)
