from sqlalchemy.orm import Session

from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QWidget, QCheckBox, QLineEdit, QHBoxLayout

from src.database.processed_fields.processed_multi_checkbox_option import ProcessedMultiCheckboxOption


class MultiCheckboxOption(QWidget):
    dataChanged = pyqtSignal()

    def __init__(self, field: ProcessedMultiCheckboxOption):
        super().__init__()
        self._field_db_id: int | None = None

        self.checkbox = QCheckBox(field.name)
        self.checkbox.checkStateChanged.connect(self.handle_checkbox_state_changed)
        self.checkbox.checkStateChanged.connect(self.dataChanged)

        self.text_entry = QLineEdit()
        self.text_entry.textChanged.connect(self.dataChanged)

        self._set_up_layout()
        self.load(field)

    def _set_up_layout(self) -> None:
        self.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.text_entry)

        self.setLayout(layout)

    def to_tuple(self) -> tuple[bool, str]:
        return self.checkbox.isChecked(), self.text_entry.text()

    @pyqtSlot(Qt.CheckState)
    def handle_checkbox_state_changed(self, state: Qt.CheckState) -> None:
        if state == Qt.CheckState.Checked:
            self.text_entry.setEnabled(True)
        else:
            self.text_entry.setEnabled(False)

    def load(self, field: ProcessedMultiCheckboxOption) -> None:
        self._field_db_id = field.id

        self.checkbox.setChecked(field.checked)

        self.text_entry.setEnabled(field.checked)
        self.text_entry.setText(field.text)
        self.text_entry.setVisible(field.ocr_text is not None)

    def update_db_state(self, session: Session) -> None:
        option = session.get(ProcessedMultiCheckboxOption, self._field_db_id)
        option.checked = self.checkbox.isChecked()

        if option.ocr_text is not None or self.text_entry.text():
            option.text = self.text_entry.text()
