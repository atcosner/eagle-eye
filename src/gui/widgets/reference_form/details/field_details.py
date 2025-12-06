import logging

from PyQt6.QtWidgets import QWidget, QVBoxLayout

from src.database.fields.form_field import FormField

from ...field_details.checkbox_details import CheckboxDetails
from ...field_details.circled_details import CircledDetails
from ...field_details.multi_checkbox_details import MultiCheckboxDetails
from ...field_details.text_details import TextDetails

logger = logging.getLogger(__name__)


class FieldDetails(QWidget):
    def __init__(self, parent: QWidget, field: FormField):
        super().__init__(parent)

        self.name = None
        self.checkbox_details = CheckboxDetails()
        self.circled_details = CircledDetails()
        self.multi_checkbox_details = MultiCheckboxDetails()
        self.text_details = TextDetails()

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
            self.text_details.load_field(field.text_field)
            self.text_details.setVisible(True)
        elif field.checkbox_field is not None:
            self.name = field.checkbox_field.name
            self.checkbox_details.load_field(field.checkbox_field)
            self.checkbox_details.setVisible(True)
        elif field.circled_field is not None:
            self.name = field.circled_field.name
            self.circled_details.load_field(field.circled_field)
            self.circled_details.setVisible(True)
        elif field.multi_checkbox_field is not None:
            self.name = field.multi_checkbox_field.name
            self.multi_checkbox_details.load_field(field.multi_checkbox_field)
            self.multi_checkbox_details.setVisible(True)
        else:
            logger.error(f'Field {field.id} did not have any sub-fields! ')

    def get_name(self) -> str:
        return self.name
