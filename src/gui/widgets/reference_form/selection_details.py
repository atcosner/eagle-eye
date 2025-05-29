import logging
from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout

from src.database import DB_ENGINE
from src.database.reference_form import ReferenceForm

from .field_details import FieldDetails
from .region_details import RegionDetails
from .util import SelectionType

logger = logging.getLogger(__name__)


class SelectionDetails(QGroupBox):
    def __init__(self):
        self._base_title = 'Details'
        super().__init__(self._base_title)

        self._current_widget: RegionDetails | FieldDetails | None = None
        self.region_details: dict[int, RegionDetails] = {}
        self.field_details: dict[int, FieldDetails] = {}

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def _update_title(self, suffix: str) -> None:
        prefix = 'Region' if isinstance(self._current_widget, RegionDetails) else 'Field'
        self.setTitle(f'{prefix} {self._base_title}: {suffix}')

    def load_reference_form(self, form: ReferenceForm | int | None) -> None:
        if form is None:
            self.region_details.clear()
            self.field_details.clear()
            self._current_widget = None
            return

        with Session(DB_ENGINE) as session:
            form = session.get(ReferenceForm, form) if isinstance(form, int) else form

            for region in form.regions.values():
                region_details = RegionDetails(self, region)
                region_details.setVisible(False)
                self.region_details[region.id] = region_details
                self.layout.addWidget(region_details)

                for field in region.fields:
                    field_details = FieldDetails(self, field)
                    field_details.setVisible(False)
                    self.field_details[field.id] = field_details
                    self.layout.addWidget(field_details)

    @pyqtSlot(SelectionType, int)
    def load_details(self, selection: SelectionType, db_id: int) -> None:
        match selection:
            case SelectionType.REGION:
                widget = self.region_details[db_id]
            case SelectionType.FIELD:
                widget = self.field_details[db_id]
            case _:
                logger.error(f'Unknown selection type: {selection}')
                return

        if self._current_widget is not widget:
            if self._current_widget:
                self._current_widget.setVisible(False)
            widget.setVisible(True)
            self._current_widget = widget
            self._update_title(self._current_widget.get_name())
