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
        self._base_title = 'Details'
        super().__init__(self._base_title)

        self.region_details = RegionDetails(self)
        self.field_details = FieldDetails(self)

        self._set_up_layout()
        self._update_visibility(True)

    def _set_up_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.region_details)
        layout.addWidget(self.field_details)
        self.setLayout(layout)

    def _update_visibility(self, is_region: bool) -> None:
        self.region_details.setVisible(is_region)
        self.field_details.setVisible(not is_region)

    def _update_title(self, prefix: str, suffix: str) -> None:
        self.setTitle(f'{prefix} {self._base_title}: {suffix}')

    @pyqtSlot(SelectionType, int)
    def load_details(self, selection: SelectionType, db_id: int) -> None:
        with Session(DB_ENGINE) as session:
            match selection:
                case SelectionType.REGION:
                    logger.info(f'Loading details for region: {db_id}')
                    region = session.get(FormRegion, db_id)
                    name = self.region_details.load_region(region)

                    self._update_visibility(True)
                    self._update_title(prefix='Region', suffix=name)

                case SelectionType.FIELD:
                    logger.info(f'Loading details for field: {db_id}')
                    field = session.get(FormField, db_id)
                    name = self.field_details.load_field(field)

                    self._update_visibility(False)
                    self._update_title(prefix='Field', suffix=name)

                case _:
                    logger.error(f'Unknown selection type: {selection}')
