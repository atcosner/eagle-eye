import logging
from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton, QCheckBox, QHBoxLayout, QVBoxLayout

from src.database import DB_ENGINE
from src.database.processing.processed_region import ProcessedRegion
from src.gui.widgets.result_fields.base import BaseField
from src.gui.widgets.result_fields.checkbox_field import CheckboxField
from src.gui.widgets.result_fields.field_group import FieldGroup
from src.gui.widgets.result_fields.multi_checkbox_field import MultiCheckboxField
from src.gui.widgets.result_fields.text_field import TextField
from src.gui.widgets.util.table_header import TableHeader

logger = logging.getLogger(__name__)


class RegionOcrResults(QWidget):
    verificationChange = pyqtSignal(bool, bool)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._region_db_id: int | None = None

        self.field_grid = QGridLayout()
        self.field_widgets: dict[int, BaseField] = {}

        self.continue_button = QPushButton("Continue")
        self.mark_verified_checkbox = QCheckBox('Mark as verified')

        self.continue_button.pressed.connect(self.handle_continue)
        self.mark_verified_checkbox.setChecked(True)

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.continue_button)
        button_layout.addWidget(self.mark_verified_checkbox)
        button_layout.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(self.field_grid)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Add the headers to our grid
        self.field_grid.addWidget(TableHeader('Field Name'), 0, 0)
        self.field_grid.addWidget(TableHeader('Validation'), 0, 1)
        self.field_grid.addWidget(TableHeader('Value'), 0, 2)
        self.field_grid.addWidget(TableHeader('Field Image'), 0, 3)

        # Only stretch the value column
        self.field_grid.setColumnStretch(2, 1)

    def load_region(self, region: ProcessedRegion | int | None) -> None:
        self.field_widgets.clear()
        if region is None:
            return

        with Session(DB_ENGINE) as session:
            region = session.get(ProcessedRegion, region) if isinstance(region, int) else region
            self._region_db_id = region.id
            logger.info(f'Loading region: {region.id} - {region.name}')

            for group in region.groups:
                logger.info(f'Loading group: {group.name}')
                row_idx = self.field_grid.rowCount()

                if len(group.fields) > 1:
                    logger.debug(f'Adding field group placeholder')
                    field_widget = FieldGroup(group)
                else:
                    field = group.fields[0]

                    # Create the specific widget to display the field
                    if field.text_field is not None:
                        logger.debug(f'Adding text field: {field.text_field.name}')
                        field_widget = TextField(field.text_field)

                    elif field.checkbox_field is not None:
                        logger.debug(f'Adding checkbox field: {field.checkbox_field.name}')
                        field_widget = CheckboxField(field.checkbox_field)

                    elif field.multi_checkbox_field is not None:
                        logger.debug(f'Adding multi checkbox field: {field.multi_checkbox_field.name}')
                        field_widget = MultiCheckboxField(field.multi_checkbox_field)

                    else:
                        logger.error(f'Processed field ({field.id}) did not have a field we could display')
                        continue

                # Propagate verification removal getting set up
                field_widget.flagUnverified.connect(lambda: self.verificationChange.emit(False, False))

                # Add the field into the layout and the dictionary
                field_widget.add_to_grid(row_idx, self.field_grid)
                self.field_widgets[row_idx] = field_widget

    def handle_tab_shown(self) -> None:
        for widget in self.field_widgets.values():
            widget.update_link_data()

    @pyqtSlot()
    def handle_continue(self) -> None:
        # Update the DB if we want to mark verification
        if self.mark_verified_checkbox.isChecked():
            with Session(DB_ENGINE) as session:
                region = session.get(ProcessedRegion, self._region_db_id)
                region.human_verified = True
                session.commit()

        self.verificationChange.emit(self.mark_verified_checkbox.isChecked(), True)
