import logging
from sqlalchemy.orm import Session

from PyQt6.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from src.database import Job, DB_ENGINE

from ..widgets.file.file_ocr_results import FileOcrResults
from ..widgets.util.sized_scroll_area import SizedScrollArea

logger = logging.getLogger(__name__)


class OcrResultCheck(QWidget):
    def __init__(self):
        super().__init__()

        self.file_tabs = QTabWidget()

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(self.file_tabs)
        self.setLayout(layout)

    def load_job(self, job: Job | int | None) -> None:
        self.file_tabs.clear()
        if job is None:
            return

        with Session(DB_ENGINE) as session:
            job = session.get(Job, job) if isinstance(job, int) else job

            for file in job.input_files:
                file_tab = FileOcrResults()
                file_tab.load_input_file(file)

                scroll_area = SizedScrollArea(file_tab)
                self.file_tabs.addTab(scroll_area, file.path.name)
