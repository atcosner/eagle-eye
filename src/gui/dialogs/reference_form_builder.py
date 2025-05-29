from sqlalchemy.orm import Session

from PyQt6.QtWidgets import QDialog, QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QLabel

from src.database import DB_ENGINE
from src.database.reference_form import ReferenceForm

from ..widgets.reference_form_viewer import ReferenceFormViewer


class ReferenceFormBuilder(QDialog):
    def __init__(self, parent: QWidget | None, allow_edit: bool, form_id: int):
        super().__init__(parent)
        self.setWindowTitle(f'Reference Form {"Editor" if allow_edit else "Viewer"}')

        self._allow_edit = allow_edit
        self._form_id = form_id

        self.form_name = QLineEdit()
        self.form_name.setReadOnly(not allow_edit)
        self.form_viewer = ReferenceFormViewer()

        self._set_up_layout()
        self.load_reference_form(self._form_id)

    def _set_up_layout(self) -> None:
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel('Form Name'))
        name_layout.addWidget(self.form_name)

        layout = QVBoxLayout()
        layout.addLayout(name_layout)
        layout.addWidget(self.form_viewer)
        self.setLayout(layout)

    def load_reference_form(self, form_id: int) -> None:
        self._form_id = form_id
        with Session(DB_ENGINE) as session:
            form = session.get(ReferenceForm, form_id)
            self.form_name.setText(form.name)
            self.form_viewer.load_reference_form(form)
