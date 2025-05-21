import logging

from sqlalchemy.orm import Session

from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal, QTime, QDate
from PyQt6.QtWidgets import (
    QLineEdit, QGridLayout, QWidget, QVBoxLayout, QCheckBox, QHBoxLayout, QTextEdit,
)

import src.processing.validation as validation
from src.database import DB_ENGINE
from src.database.processed_fields.processed_text_field import ProcessedTextField
from src.database.validation.text_validator import TextValidator
from src.util.validation import validation_result_image, TextValidatorDatatype, VALID_DATE_FORMATS, VALID_TIME_FORMATS

from .base import BaseField
from .util import wrap_in_frame
from ..util.search_combo_box import SearchComboBox
from ..util.strong_focus_widgets import StrongFocusDateEdit, StrongFocusTimeEdit

logger = logging.getLogger(__name__)
WidgetTypeHint = QTextEdit | QLineEdit | StrongFocusDateEdit | StrongFocusTimeEdit | SearchComboBox


#
# Abstraction since a text field can be displayed as many different widgets
#
class TextFieldEntryWidget(QWidget):
    dataChanged = pyqtSignal()

    def __init__(self, validator: TextValidator | None, multiline: bool | None):
        super().__init__()
        self.datatype = validator.datatype if validator else TextValidatorDatatype.RAW_TEXT
        self.invalid_data: bool = False

        # Figure out what widget we should be
        self.input_widget: WidgetTypeHint = QTextEdit() if multiline else QLineEdit()
        if isinstance(self.input_widget, QTextEdit):
            self.input_widget.setTabChangesFocus(True)
            self.input_widget.textChanged.connect(self.dataChanged)
        else:
            self.input_widget.textEdited.connect(self.dataChanged)

        match self.datatype:
            case TextValidatorDatatype.DATE:
                self.input_widget = StrongFocusDateEdit()
                self.input_widget.dateChanged.connect(self.dataChanged)
            case TextValidatorDatatype.TIME:
                self.input_widget = StrongFocusTimeEdit()
                self.input_widget.timeChanged.connect(self.dataChanged)
            case TextValidatorDatatype.LIST_CHOICE:
                self.input_widget = SearchComboBox()
                self.input_widget.addItems(sorted([choice.text for choice in validator.text_choices]))
                self.input_widget.currentTextChanged.connect(self.dataChanged)

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.input_widget)
        self.setLayout(layout)

    def set_read_only(self, read_only: bool) -> None:
        if hasattr(self.input_widget, 'setReadOnly'):
            self.input_widget.setReadOnly(read_only)
        else:
            self.input_widget.setDisabled(read_only)

    def set_data(self, data: str) -> None:
        if self.datatype is TextValidatorDatatype.DATE:
            self.invalid_data = True
            logger.debug(f'Checking if "{data}" is a valid date')

            # Try different string formats to see if we get a match
            for str_format in VALID_DATE_FORMATS:
                date = QDate.fromString(data, str_format)
                if date.isValid():
                    self.input_widget.setDate(date)
                    self.invalid_data = False
                    break

        elif self.datatype is TextValidatorDatatype.TIME:
            self.invalid_data = True
            logger.debug(f'Checking if "{data}" is a valid time')

            # Try different string formats to see if we get a match
            for str_format in VALID_TIME_FORMATS:
                time = QTime.fromString(data, str_format)
                if time.isValid():
                    self.input_widget.setTime(time)
                    self.invalid_data = False
                    break

        elif self.datatype is TextValidatorDatatype.LIST_CHOICE:
            # See if the text is already in the list
            match_index = self.input_widget.findText(data.strip(), Qt.MatchFlag.MatchExactly)
            self.input_widget.setCurrentIndex(match_index if match_index != -1 else 0)

        else:
            self.input_widget.setText(data)

    def get_data(self) -> tuple[bool, str]:
        match self.datatype:
            case TextValidatorDatatype.DATE:
                return self.invalid_data, self.input_widget.date().toString('d MMMM yyyy')
            case TextValidatorDatatype.TIME:
                return self.invalid_data, self.input_widget.time().toString('hh:mm')
            case TextValidatorDatatype.LIST_CHOICE:
                return self.invalid_data, self.input_widget.currentText()
            case _:
                if isinstance(self.input_widget, QTextEdit):
                    return self.invalid_data, self.input_widget.toPlainText()
                else:
                    return self.invalid_data, self.input_widget.text()


class TextField(BaseField):
    def __init__(self, field: ProcessedTextField):
        super().__init__()

        # Determine if we are a multiline field
        multiline = False
        if field.text_field.text_regions is not None:
            multiline = len(field.text_field.text_regions) > 1

        self.data_entry = TextFieldEntryWidget(field.text_field.text_validator, multiline)
        self.data_entry.setMinimumWidth(350)

        self.link_checkbox = QCheckBox('Link', self)
        self.link_checkbox.setVisible(False)
        self.link_checkbox.checkStateChanged.connect(self.handle_link_change)

        self.load_field(field)
        self.data_entry.dataChanged.connect(self.handle_data_changed)

    def load_field(self, field: ProcessedTextField) -> None:
        super().load_field(field)

        self.data_entry.set_data(field.text)

        result_pixmap = validation_result_image(field.validation_result.result)
        self.validation_result.setPixmap(result_pixmap)
        self.validation_result.setToolTip(field.validation_result.explanation)

        # Handle if this field can be linked
        self.link_checkbox.setVisible(field.text_field.allow_copy)
        if field.copied_from_linked is not None:
            self.data_entry.set_read_only(field.copied_from_linked)
            self.link_checkbox.setChecked(field.copied_from_linked)

    def add_to_grid(self, row_idx: int, grid: QGridLayout) -> None:
        super().add_to_grid(row_idx, grid)

        layout = QHBoxLayout()
        layout.addWidget(self.link_checkbox)
        layout.addWidget(self.data_entry)
        layout.addStretch()
        grid.addWidget(wrap_in_frame(layout), row_idx, 2)

    def update_link_data(self) -> None:
        linking = self.link_checkbox.isChecked()
        self.data_entry.set_read_only(linking)

        with Session(DB_ENGINE) as session:
            field = session.get(ProcessedTextField, self._field_db_id)
            field.copied_from_linked = linking
            session.commit()

            # TODO: Do not allow linking if we do not have a linked field id

            # If linking was turned on, update our data
            if linking:
                if field.linked_field_id is None:
                    logger.error(f'Field {field.name} does not have a linked field ID')
                    return

                link_field = session.get(ProcessedTextField, field.linked_field_id)
                if link_field is None:
                    logger.error(f'Could not find linked field: {field.linked_field_id}')
                    return

                self.data_entry.set_data(link_field.text)
                self.update_validation_result(link_field.validation_result)

    @pyqtSlot()
    def handle_link_change(self) -> None:
        self.update_link_data()

    @pyqtSlot()
    def handle_data_changed(self) -> None:
        # TODO: If DB access is not incredibly fast this probably updates it too much

        with Session(DB_ENGINE) as session:
            field = session.get(ProcessedTextField, self._field_db_id)

            invalid_data, text = self.data_entry.get_data()
            super().update_region_verification(field.processed_field, field.text, text)
            field.text = text
            field.validation_result = validation.validate_text_field(
                field.text_field,
                text,
                force_fail=invalid_data,
            )
            self.update_validation_result(field.validation_result)

            correction_text = field.validation_result.correction
            if correction_text is not None and correction_text != text:
                logger.info(f'Validation correction: "{text}" -> "{correction_text}"')
                field.text = correction_text
                self.data_entry.set_data(correction_text)

            # TODO: If this field is the identifier, we may need to recheck all fields for linking

            session.commit()
