import logging
from sqlalchemy.orm import Session

from PyQt6.QtWidgets import QWidget, QTabWidget

from src.database import DB_ENGINE
from src.database.job import Job
from src.gui.widgets.file_ocr_results import FileOcrResults

from .base import BaseWindow

logger = logging.getLogger(__name__)


class ResultViewer(BaseWindow):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent, 'Result Viewer')

        self.file_tabs = QTabWidget()

        self._set_up_layout()

    def _set_up_layout(self) -> None:
        self.setCentralWidget(self.file_tabs)

    def load_job(self, job: Job | int) -> None:
        with Session(DB_ENGINE) as session:
            job = session.get(Job, job) if isinstance(job, int) else job
            self.update_title(suffix=f' | {job.name}', append=True)

            for file in job.input_files:
                file_tab = FileOcrResults()
                file_tab.load_input_file(file)
                self.file_tabs.addTab(file_tab, file.path.name)
