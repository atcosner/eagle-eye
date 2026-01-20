from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QGridLayout, QVBoxLayout, QWidget

import src.processing.validation as validation
from src.database import DB_ENGINE
from src.database.processed_fields.processed_circled_field import ProcessedCircledField

from .base import BaseField
from .circled_option import CircledOption
from .util import wrap_in_frame


class CircledField(BaseField):
    def __init__(self, field: ProcessedCircledField):
        super().__init__()

        self.container = QWidget()
        self.options: list[CircledOption] = []

        self.load_field(field)

    def load_field(self, field: ProcessedCircledField) -> None:
        super().load_field(field)
        self.update_validation_result(field.validation_result)

        # Create a checkbox for each option
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        for name, option in field.options.items():
            cb = CircledOption(option)
            cb.dataChanged.connect(self.handle_data_changed)
            self.options.append(cb)

            layout.addWidget(cb)

        self.container.setLayout(layout)

    def add_to_grid(self, row_idx: int, grid: QGridLayout) -> None:
        super().add_to_grid(row_idx, grid)
        grid.addWidget(wrap_in_frame(self.container), row_idx, 2)

    @pyqtSlot()
    def handle_data_changed(self) -> None:
        # TODO: If DB access is not incredibly fast this probably updates it too much

        with Session(DB_ENGINE) as session:
            field = session.get(ProcessedCircledField, self._field_db_id)

            prev_data = [option.circled for option in field.options.values()]
            new_data = [option.get_state() for option in self.options]
            super().update_region_verification(field.processed_field, prev_data, new_data)

            for option in self.options:
                option.update_db_state(session)

            field.validation_result = validation.validate_circled_field(
                field.circled_field,
                field.options,
            )
            self.update_validation_result(field.validation_result)
            session.commit()
