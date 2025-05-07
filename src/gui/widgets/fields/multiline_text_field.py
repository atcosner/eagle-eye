from PyQt6.QtWidgets import QGridLayout, QTextEdit

from src.database.processed_fields.processed_multiline_text_field import ProcessedMultilineTextField
from src.util.validation import validation_result_image

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
        self.text_input.setText(field.text)

        result_pixmap = validation_result_image(field.validation_result.result)
        self.validation_result.setPixmap(result_pixmap)
        self.validation_result.setToolTip(field.validation_result.explanation)

    def add_to_grid(self, row_idx: int, grid: QGridLayout) -> None:
        super().add_to_grid(row_idx, grid)
        grid.addWidget(wrap_in_frame(self.text_input), row_idx, 2)
