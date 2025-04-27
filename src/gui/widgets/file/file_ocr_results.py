import logging
from sqlalchemy.orm import Session

from PyQt6.QtWidgets import QWidget, QGridLayout, QSizePolicy

from src.database import DB_ENGINE
from src.database.input_file import InputFile
from src.gui.widgets.fields.text_field import TextField

logger = logging.getLogger(__name__)


class FileOcrResults(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.field_grid = QGridLayout()
        self.setLayout(self.field_grid)

        self.field_widgets: dict[int, QWidget] = {}

    def load_input_file(self, input_file: InputFile | int | None) -> None:
        with Session(DB_ENGINE) as session:
            input_file = session.get(InputFile, input_file) if isinstance(input_file, int) else input_file

            for region_id, region in input_file.process_result.regions.items():
                logger.info(f'Region: {region_id} - {region.name}')
                for field in region.fields:
                    if field.text_field is not None:
                        logger.info(f'Adding text field: {field.text_field.name}')
                        row_idx = self.field_grid.rowCount()

                        field_widget = TextField(field.text_field)
                        field_widget.add_to_grid(row_idx, self.field_grid)
                        self.field_widgets[row_idx] = field_widget
