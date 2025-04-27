from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout

from .util import wrap_in_frame


class BaseField(QWidget):
    def __init__(self):
        super().__init__()

        self.field_name = QLabel()
        self.validation_result = QLabel()
        self.roi_image = QLabel()

    def load_field(self, field) -> None:
        self.field_name.setText(field.name)
        self.roi_image.setPixmap(QPixmap(str(field.roi_path)))

    def add_to_grid(self, row_idx: int, grid: QGridLayout) -> None:
        grid.addWidget(wrap_in_frame(self.field_name), row_idx, 0)
        grid.addWidget(wrap_in_frame(self.validation_result), row_idx, 1)
        # Custom entry widget goes in column #2
        grid.addWidget(wrap_in_frame(self.roi_image), row_idx, 3)
