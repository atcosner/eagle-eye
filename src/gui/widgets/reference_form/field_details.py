from PyQt6.QtWidgets import QWidget

from src.database.fields.form_field import FormField


class FieldDetails(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

    def load_field(self, field: FormField) -> None:
        pass
