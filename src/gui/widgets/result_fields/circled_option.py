from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QCheckBox, QHBoxLayout

from src.database.processed_fields.processed_circled_option import ProcessedCircledOption


class CircledOption(QWidget):
    dataChanged = pyqtSignal()

    def __init__(self, field: ProcessedCircledOption):
        super().__init__()
        self._field_db_id: int | None = None

        self.checkbox = QCheckBox(field.name)
        self.checkbox.checkStateChanged.connect(self.dataChanged)

        self.load(field)
        self._set_up_layout()

    def _set_up_layout(self) -> None:
        self.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.checkbox)

        self.setLayout(layout)

    def get_state(self) -> bool:
        return self.checkbox.isChecked()

    def load(self, field: ProcessedCircledOption) -> None:
        self._field_db_id = field.id
        self.checkbox.setChecked(field.circled)

    def update_db_state(self, session: Session) -> None:
        option = session.get(ProcessedCircledOption, self._field_db_id)
        option.checked = self.checkbox.isChecked()
