from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QGridLayout, QCheckBox

from src.database import DB_ENGINE
from src.database.processed_fields.processed_checkbox_field import ProcessedCheckboxField

from .base import BaseField
from .util import wrap_in_frame


class CheckboxField(BaseField):
    def __init__(self, field: ProcessedCheckboxField):
        super().__init__()

        self.checkbox = QCheckBox()

        self.load_field(field)
        self.checkbox.checkStateChanged.connect(self.handle_data_changed)

    def load_field(self, field: ProcessedCheckboxField) -> None:
        super().load_field(field)
        self.checkbox.setChecked(field.checked)

    def add_to_grid(self, row_idx: int, grid: QGridLayout) -> None:
        super().add_to_grid(row_idx, grid)
        grid.addWidget(wrap_in_frame(self.checkbox), row_idx, 2)

    @pyqtSlot()
    def handle_data_changed(self) -> None:
        # TODO: If DB access is not incredibly fast this probably updates it too much

        with Session(DB_ENGINE) as session:
            field = session.get(ProcessedCheckboxField, self._field_db_id)
            super().update_region_verification(field.processed_field, field.checked, self.checkbox.isChecked())
            field.checked = self.checkbox.isChecked()
