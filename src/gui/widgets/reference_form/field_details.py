import logging

from PyQt6.QtWidgets import QWidget, QVBoxLayout

from src.database.fields.form_field import FormField

from ..field_details.checkbox_details import CheckboxDetails

logger = logging.getLogger(__name__)


class FieldDetails(QWidget):
    def __init__(self, parent: QWidget, field: FormField):
        super().__init__(parent)

        self.name = None
        self.checkbox_details = CheckboxDetails()

        self._set_up_layout()
        self._load_field(field)

    def _set_up_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.checkbox_details)
        self.setLayout(layout)

    def _hide_all(self) -> None:
        self.checkbox_details.hide()

    def _load_field(self, field: FormField) -> None:
        self._hide_all()

        if field.text_field is not None:
            pass
        elif field.checkbox_field is not None:
            self.name = field.checkbox_field.name
            self.checkbox_details.load_field(field.checkbox_field)
            self.checkbox_details.setVisible(True)
        elif field.multi_checkbox_field is not None:
            pass
        else:
            logger.error(f'Field {field.id} did not have any sub-fields! ')

    def get_name(self) -> str:
        return self.name
