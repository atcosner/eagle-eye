from PyQt6.QtWidgets import QWidget, QCheckBox, QLineEdit, QHBoxLayout

from src.database.processed_fields.processed_multi_checkbox_option import ProcessedMultiCheckboxOption


class MultiCheckboxOption(QWidget):
    def __init__(self, field: ProcessedMultiCheckboxOption):
        super().__init__()

        self.checkbox = QCheckBox(field.name)
        self.text_entry = QLineEdit()

        self._set_up_layout()
        self.load(field)

    def _set_up_layout(self) -> None:
        layout = QHBoxLayout()
        layout.addWidget(self.checkbox)
        layout.addWidget(self.text_entry)

        self.setLayout(layout)

    def load(self, field: ProcessedMultiCheckboxOption) -> None:
        self.checkbox.setChecked(field.checked)
        self.text_entry.setText(field.text)
        self.text_entry.setVisible(field.ocr_text is not None)
