import logging
from sqlalchemy.orm import Session

from PyQt6.QtWidgets import QWidget, QGridLayout

from src.database import DB_ENGINE
from src.database.processed_region import ProcessedRegion
from src.gui.widgets.result_fields.base import BaseField
from src.gui.widgets.result_fields.checkbox_field import CheckboxField
from src.gui.widgets.result_fields.multi_checkbox_field import MultiCheckboxField
from src.gui.widgets.result_fields.multiline_text_field import MultilineTextField
from src.gui.widgets.result_fields.text_field import TextField
from src.gui.widgets.util.table_header import TableHeader

logger = logging.getLogger(__name__)


class RegionOcrResults(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.field_grid = QGridLayout()
        self.field_widgets: dict[int, BaseField] = {}

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        self.setLayout(self.field_grid)

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
            logger.info(f'Loading region: {region.id} - {region.name}')

            for field in region.fields:
                row_idx = self.field_grid.rowCount()

                # Create the specific widget to display the field
                if field.text_field is not None:
                    logger.debug(f'Adding text field: {field.text_field.name}')
                    field_widget = TextField(field.text_field)

                elif field.multiline_text_field is not None:
                    logger.debug(f'Adding multi-line text field: {field.multiline_text_field.name}')
                    field_widget = MultilineTextField(field.multiline_text_field)

                elif field.checkbox_field is not None:
                    logger.debug(f'Adding checkbox field: {field.checkbox_field.name}')
                    field_widget = CheckboxField(field.checkbox_field)

                elif field.multi_checkbox_field is not None:
                    logger.debug(f'Adding multi checkbox field: {field.multi_checkbox_field.name}')
                    field_widget = MultiCheckboxField(field.multi_checkbox_field)

                else:
                    logger.error(f'Processed field ({field.id}) did not have a field we could display')
                    continue

                # Add the field into the layout and the dictionary
                field_widget.add_to_grid(row_idx, self.field_grid)
                self.field_widgets[row_idx] = field_widget

    def handle_tab_shown(self) -> None:
        for widget in self.field_widgets.values():
            widget.update_link_data()
