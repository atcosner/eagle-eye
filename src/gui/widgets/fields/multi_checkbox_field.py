from PyQt6.QtWidgets import QGridLayout, QCheckBox, QVBoxLayout, QWidget

from src.database.processed_fields.processed_multi_checkbox_field import ProcessedMultiCheckboxField

from .base import BaseField
from .multi_checkbox_option import MultiCheckboxOption
from .util import wrap_in_frame


class MultiCheckboxField(BaseField):
    def __init__(self, field: ProcessedMultiCheckboxField):
        super().__init__()

        self.container = QWidget()
        self.options: list[MultiCheckboxOption] = []

        self.load_field(field)

    def load_field(self, field: ProcessedMultiCheckboxField) -> None:
        super().load_field(field)
        # TODO: Validation result

        # Create a checkbox for each option
        layout = QVBoxLayout()
        for name, option in field.checkboxes.items():
            cb = MultiCheckboxOption(option)
            self.options.append(cb)

            layout.addWidget(cb)

        self.container.setLayout(layout)

    def add_to_grid(self, row_idx: int, grid: QGridLayout) -> None:
        super().add_to_grid(row_idx, grid)
        grid.addWidget(wrap_in_frame(self.container), row_idx, 2)
