import logging

from PyQt6.QtCore import pyqtSlot
from sqlalchemy.orm import Session

from PyQt6.QtWidgets import QGroupBox, QVBoxLayout

from src.database import DB_ENGINE
from src.database.fields.form_field import FormField
from src.database.form_region import FormRegion

from .field_details import FieldDetails
from .region_details import RegionDetails
from .util import SelectionType

logger = logging.getLogger(__name__)


class SelectionDetails(QGroupBox):
    def __init__(self):
        super().__init__('Selection Details')

        self.region_details = RegionDetails(self)
        self.field_details = FieldDetails(self)

        self._set_up_layout()
        self._update_visibility(True)

    def _set_up_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.region_details)
        self.setLayout(layout)

    def _update_visibility(self, is_region: bool) -> None:
        self.region_details.setVisible(is_region)
        self.field_details.setVisible(not is_region)

    @pyqtSlot(SelectionType, int)
    def load_details(self, selection: SelectionType, db_id: int) -> None:
        with Session(DB_ENGINE) as session:
            match selection:
                case SelectionType.REGION:
                    logger.info(f'Loading details for region: {db_id}')
                    region = session.get(FormRegion, db_id)
                    self.region_details.load_region(region)
                    self._update_visibility(True)

                case SelectionType.FIELD:
                    logger.info(f'Loading details for field: {db_id}')
                    field = session.get(FormField, db_id)
                    self.field_details.load_field(field)
                    self._update_visibility(False)

                case _:
                    logger.error(f'Unknown selection type: {selection}')
