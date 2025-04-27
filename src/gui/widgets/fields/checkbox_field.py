from PyQt6.QtWidgets import QGridLayout, QCheckBox

from src.database.processed_fields.processed_checkbox_field import ProcessedCheckboxField

from .base import BaseField
from .util import wrap_in_frame


class CheckboxField(BaseField):
    def __init__(self, field: ProcessedCheckboxField):
        super().__init__()
        self.checkbox = QCheckBox()

        self.load_field(field)

    def load_field(self, field: ProcessedCheckboxField) -> None:
        super().load_field(field)
        # TODO: Validation result
        self.checkbox.setChecked(field.checked)

    def add_to_grid(self, row_idx: int, grid: QGridLayout) -> None:
        super().add_to_grid(row_idx, grid)
        grid.addWidget(wrap_in_frame(self.checkbox), row_idx, 2)
