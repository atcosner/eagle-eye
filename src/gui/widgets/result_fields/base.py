from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout

from src.database.validation.validation_result import ValidationResult
from src.util.validation import validation_result_image

from .util import wrap_in_frame


class BaseField(QWidget):
    def __init__(self):
        super().__init__()
        self._field_db_id: int | None = None

        self.field_name = QLabel()
        self.validation_result = QLabel()
        self.roi_image = QLabel()

    def load_field(self, field) -> None:
        self._field_db_id = field.id

        self.field_name.setText(field.name)
        self.update_validation_result(None)
        self.roi_image.setPixmap(QPixmap(str(field.roi_path)))

    def update_validation_result(self, result: ValidationResult | None) -> None:
        if result is None:
            self.validation_result.setPixmap(validation_result_image(None))
            self.validation_result.setToolTip('No validation performed')
        else:
            self.validation_result.setPixmap(validation_result_image(result.result))
            self.validation_result.setToolTip(result.explanation)

    def add_to_grid(self, row_idx: int, grid: QGridLayout) -> None:
        grid.addWidget(wrap_in_frame(self.field_name), row_idx, 0)
        grid.addWidget(wrap_in_frame(self.validation_result, center_horizontal=True), row_idx, 1)
        # Custom entry widget goes in column #2
        grid.addWidget(wrap_in_frame(self.roi_image), row_idx, 3)

    def update_link_data(self) -> None:
        pass
