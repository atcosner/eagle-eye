import logging

from PyQt6.QtWidgets import QWidget, QVBoxLayout

from src.database.fields.form_field import FormField

from ..field_details.checkbox_details import CheckboxDetails

logger = logging.getLogger(__name__)


class FieldDetails(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.checkbox_details = CheckboxDetails()

        self._set_up_layout()
        self.hide_all()

    def _set_up_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.checkbox_details)
        self.setLayout(layout)

    def hide_all(self) -> None:
        self.checkbox_details.hide()

    def load_field(self, field: FormField) -> str:
        self.hide_all()

        if field.text_field is not None:
            pass

        elif field.checkbox_field is not None:
            self.checkbox_details.load_field(field.checkbox_field)
            self.checkbox_details.setVisible(True)
            return field.checkbox_field.name

        elif field.multi_checkbox_field is not None:
            pass

        else:
            logger.error(f'Field {field.id} did not have any sub-fields! ')
            return 'None'
