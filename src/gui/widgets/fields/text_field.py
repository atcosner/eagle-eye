from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QGridLayout

from src.database.processed_fields.processed_multiline_text_field import ProcessedMultilineTextField
from src.database.processed_fields.processed_text_field import ProcessedTextField


class TextField(QWidget):
    def __init__(self, field: ProcessedTextField | ProcessedMultilineTextField):
        super().__init__(None)

        self.roi_image = QLabel()
        self.validation_result = QLabel()
        self.text_input = QLineEdit()

        self.load_field(field)

    def load_field(self, field: ProcessedTextField | ProcessedMultilineTextField) -> None:
        roi_pixmap = QPixmap(str(field.roi_path))
        self.roi_image.setPixmap(roi_pixmap)
        self.text_input.setText(field.text)

    def add_to_grid(self, grid: QGridLayout) -> None:
        row_idx = grid.rowCount()
        grid.addWidget(self.roi_image, row_idx, 0)
        grid.addWidget(self.validation_result, row_idx, 1)
        grid.addWidget(self.text_input, row_idx, 2)
