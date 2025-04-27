from PyQt6.QtWidgets import QGridLayout, QTextEdit

from src.database.processed_fields.processed_multiline_text_field import ProcessedMultilineTextField

from .base import BaseField
from .util import wrap_in_frame


class MultilineTextField(BaseField):
    def __init__(self, field: ProcessedMultilineTextField):
        super().__init__()

        self.text_input = QTextEdit()
        self.text_input.setMinimumWidth(350)

        self.load_field(field)

    def load_field(self, field: ProcessedMultilineTextField) -> None:
        super().load_field(field)
        # TODO: Validation result
        self.text_input.setText(field.text)

    def add_to_grid(self, row_idx: int, grid: QGridLayout) -> None:
        super().add_to_grid(row_idx, grid)
        grid.addWidget(wrap_in_frame(self.text_input), row_idx, 2)
