from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QGridLayout, QCheckBox

from src.database import DB_ENGINE
from src.database.processed_fields.processed_field_group import ProcessedFieldGroup

from .base import BaseField
from .util import wrap_in_frame


class FieldGroup(BaseField):
    def __init__(self, group: ProcessedFieldGroup):
        super().__init__()

        self.load_field(group)

    def load_field(self, group: ProcessedFieldGroup) -> None:
        super().load_field(group)

    def add_to_grid(self, row_idx: int, grid: QGridLayout) -> None:
        super().add_to_grid(row_idx, grid)
        # grid.addWidget(wrap_in_frame(self.checkbox), row_idx, 2)
