import logging
from sqlalchemy.orm import Session

from PyQt6.QtWidgets import QWidget, QVBoxLayout

from src.database import DB_ENGINE
from src.database.input_file import InputFile
from src.gui.widgets.util.sized_scroll_area import SizedScrollArea
from src.gui.widgets.util.vertical_tabs import VerticalTabs

from .region_ocr_results import RegionOcrResults

logger = logging.getLogger(__name__)


class FileOcrResults(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.tabs = VerticalTabs()
        self.region_widgets: dict[str, RegionOcrResults] = {}

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def load_input_file(self, input_file: InputFile | int | None) -> None:
        self.tabs.clear()
        self.region_widgets.clear()
        if input_file is None:
            return

        with Session(DB_ENGINE) as session:
            input_file = session.get(InputFile, input_file) if isinstance(input_file, int) else input_file
            if input_file.process_result is None:
                return

            for region in input_file.process_result.regions.values():
                region_results = RegionOcrResults()
                region_results.load_region(region)

                scroll_area = SizedScrollArea(region_results)
                self.tabs.addTab(scroll_area, region.name)
                self.region_widgets[region.name] = region_results
