import logging

from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from src.database.fields.form_field import FormField

from .checkbox_field_details import CheckboxFieldDetails
from .circled_field_details import CircledFieldDetails
from .multi_checkbox_field_details import MultiCheckboxFieldDetails
from .text_field_details import TextFieldDetails
from ...util.details.base_field_details import BaseFieldDetails

logger = logging.getLogger(__name__)


class FieldDetails(QWidget):
    def __init__(self, parent: QWidget, field: FormField):
        super().__init__(parent)

        self.name = ''
        self.checkbox_details = CheckboxFieldDetails()
        self.circled_details = CircledFieldDetails()
        self.multi_checkbox_details = MultiCheckboxFieldDetails()
        self.text_details = TextFieldDetails()

        self.details: BaseFieldDetails | None = None

        self._set_up_layout()
        self._load_field(field)

    def _set_up_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.checkbox_details)
        layout.addWidget(self.circled_details)
        layout.addWidget(self.multi_checkbox_details)
        layout.addWidget(self.text_details)
        self.setLayout(layout)

    def _hide_all(self) -> None:
        self.checkbox_details.hide()
        self.circled_details.hide()
        self.multi_checkbox_details.hide()
        self.text_details.hide()

    def _load_field(self, field: FormField) -> None:
        self._hide_all()

        if field.text_field is not None:
            self.name = field.text_field.name
            self.text_details.load(field.text_field)
            self.text_details.setVisible(True)
            self.details = self.text_details
        elif field.checkbox_field is not None:
            self.name = field.checkbox_field.name
            self.checkbox_details.load(field.checkbox_field)
            self.checkbox_details.setVisible(True)
            self.details = self.checkbox_details
        elif field.circled_field is not None:
            self.name = field.circled_field.name
            self.circled_details.load(field.circled_field)
            self.circled_details.setVisible(True)
            self.details = self.circled_details
        elif field.multi_checkbox_field is not None:
            self.name = field.multi_checkbox_field.name
            self.multi_checkbox_details.load(field.multi_checkbox_field)
            self.multi_checkbox_details.setVisible(True)
            self.details = self.multi_checkbox_details
        else:
            logger.error(f'Field {field.id} did not have any sub-fields! ')

    def get_name(self) -> str:
        return self.name

    def update_position(self, position: QRect) -> None:
        if self.details is None:
            logger.error('Did not have details to update the position on')
            return

        self.details.update_position(position)
