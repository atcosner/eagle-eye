from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QGridLayout

from src.database.processed_fields.processed_multiline_text_field import ProcessedMultilineTextField
from src.database.processed_fields.processed_text_field import ProcessedTextField

from .util import wrap_in_frame


class TextField(QWidget):
    def __init__(self, field: ProcessedTextField | ProcessedMultilineTextField):
        super().__init__(None)

        self.field_name = QLabel()
        self.roi_image = QLabel()
        self.validation_result = QLabel()
        self.text_input = QLineEdit()

        self.load_field(field)

    def load_field(self, field: ProcessedTextField | ProcessedMultilineTextField) -> None:
        self.field_name.setText(field.name)
        roi_pixmap = QPixmap(str(field.roi_path))
        self.roi_image.setPixmap(roi_pixmap)
        self.text_input.setText(field.text)

        # TODO: Validation result

    def add_to_grid(self, row_idx: int, grid: QGridLayout) -> None:
        grid.addWidget(wrap_in_frame(self.field_name), row_idx, 0)
        grid.addWidget(wrap_in_frame(self.roi_image), row_idx, 1)
        grid.addWidget(wrap_in_frame(self.validation_result), row_idx, 2)
        grid.addWidget(wrap_in_frame(self.text_input), row_idx, 3)
