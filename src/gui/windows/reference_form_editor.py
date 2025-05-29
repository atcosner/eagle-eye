from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot, QSize
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from src.database import DB_ENGINE
from src.database.reference_form import ReferenceForm
from src.util.resources import get_lock_icon

from .base import BaseWindow
from ..widgets.reference_form_viewer import ReferenceFormViewer


class ReferenceFormEditor(BaseWindow):
    def __init__(self, parent: QWidget | None, allow_edit: bool, form_id: int):
        super().__init__(parent, f'Reference Form {"Editor" if allow_edit else "Viewer"}')
        self.setMinimumHeight(900)

        self._allow_edit = allow_edit
        self._form_id = form_id

        self.lock_button = QPushButton()
        self.form_name = QLineEdit()
        self.form_viewer = ReferenceFormViewer()

        self.lock_button.setIconSize(QSize(32, 32))
        self.lock_button.pressed.connect(self.handle_edit_mode_change)

        self._set_up_layout()
        self.load_reference_form(self._form_id)
        self.set_edit_mode(self._allow_edit)

    def _set_up_layout(self) -> None:
        name_layout = QHBoxLayout()
        name_layout.addWidget(self.lock_button)
        name_layout.addWidget(QLabel('Form Name'))
        name_layout.addWidget(self.form_name)

        layout = QVBoxLayout()
        layout.addLayout(name_layout)
        layout.addWidget(self.form_viewer)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def load_reference_form(self, form_id: int) -> None:
        self._form_id = form_id
        with Session(DB_ENGINE) as session:
            form = session.get(ReferenceForm, form_id)
            self.form_name.setText(form.name)
            self.form_viewer.load_reference_form(form)

    def set_edit_mode(self, allow_edits: bool) -> None:
        self.form_viewer.set_edit_mode(allow_edits)
        self.form_name.setReadOnly(not allow_edits)

        # update the button
        self.lock_button.setText('Lock' if allow_edits else 'Unlock')
        self.lock_button.setIcon(get_lock_icon(not allow_edits))

    @pyqtSlot()
    def handle_edit_mode_change(self) -> None:
        self._allow_edit = not self._allow_edit
        self.set_edit_mode(self._allow_edit)

    #
    # Qt overrides
    #

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)

        # fit the reference form to our size
        self.form_viewer.fit_form()
