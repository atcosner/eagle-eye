from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox,
)

from src.database import DB_ENGINE

from ..widgets.reference_form.form_details_tree import FormDetailsTree


class ReferenceFormSelector(QDialog):
    def __init__(self, parent: QWidget | None):
        super().__init__(parent)
        self.setWindowTitle('Reference Form Selector')
        self.setMinimumWidth(600)

        self.form_tree = FormDetailsTree()

        self.view_button = QPushButton('View')
        self.view_button.pressed.connect(self.handle_open_form)

        self._set_up_layout()
        self._load_reference_forms()

    def _set_up_layout(self) -> None:
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.view_button)

        layout = QVBoxLayout()
        layout.addWidget(self.form_tree)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _load_reference_forms(self) -> None:
        with Session(DB_ENGINE) as session:
            self.form_tree.load_reference_forms(session)

    def get_selected_form(self) -> int:
        selected_item = self.form_tree.selectedItems()[0]
        return selected_item.data(0, Qt.ItemDataRole.UserRole)

    @pyqtSlot()
    def handle_open_form(self) -> None:
        # ensure we have a form selected
        if not self.form_tree.selectedItems():
            QMessageBox.critical(self, 'Error', 'Please select a reference form.')
            return

        self.accept()
