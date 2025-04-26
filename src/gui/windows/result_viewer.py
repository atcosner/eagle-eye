import logging

from PyQt6.QtGui import QShowEvent
from sqlalchemy.orm import Session

from PyQt6.QtWidgets import QWidget, QTabWidget, QScrollArea, QSizePolicy

from src.database import DB_ENGINE
from src.database.job import Job
from src.gui.widgets.file_ocr_results import FileOcrResults

from .base import BaseWindow

logger = logging.getLogger(__name__)


class MinimumScrollArea(QScrollArea):
    def showEvent(self, event: QShowEvent) -> None:
        # Match our minimum width to the inner widget
        self.setMinimumWidth(self.widget().sizeHint().width())
        event.accept()


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

                print(file_tab.sizeHint())

                scroll_area = MinimumScrollArea()
                scroll_area.setWidgetResizable(True)
                scroll_area.setWidget(file_tab)
                print(scroll_area.sizeHint())
                self.file_tabs.addTab(scroll_area, file.path.name)
