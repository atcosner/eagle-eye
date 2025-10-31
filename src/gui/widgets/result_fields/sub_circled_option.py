from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QCheckBox, QHBoxLayout

from src.database.processed_fields.processed_sub_circled_option import ProcessedSubCircledOption


class SubCircledOption(QWidget):
    dataChanged = pyqtSignal()

    def __init__(self, field: ProcessedSubCircledOption):
        super().__init__()
        self._field_db_id: int | None = None

        self.checkbox = QCheckBox(field.name)
        self.checkbox.checkStateChanged.connect(self.dataChanged)

        self._set_up_layout()
        self.load(field)

    def _set_up_layout(self) -> None:
        self.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.checkbox)

        self.setLayout(layout)

    def load(self, field: ProcessedSubCircledOption) -> None:
        self._field_db_id = field.id
        self.checkbox.setChecked(field.circled)

    def update_db_state(self, session: Session) -> None:
        option = session.get(ProcessedSubCircledOption, self._field_db_id)
        option.circled = self.checkbox.isChecked()
