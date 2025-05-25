import logging
from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from src.database import Job, DB_ENGINE
from src.util.validation import get_verified_icon

from ..widgets.ocr_results.file_ocr_results import FileOcrResults

logger = logging.getLogger(__name__)


class OcrResultCheck(QWidget):
    continueToNextStep = pyqtSignal()

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
                file_tab.verificationChange.connect(self.handle_verification_change)
                file_tab.load_input_file(file)

                tab_idx = self.file_tabs.addTab(file_tab, file.path.name)

                # Add an icon to reflect the verification status
                if file.process_result is not None:
                    all_verified = all([region.human_verified for region in file.process_result.regions.values()])
                    self.file_tabs.setTabIcon(tab_idx, get_verified_icon(all_verified))

    @pyqtSlot(bool, bool)
    def handle_verification_change(self, new_status: bool, continue_check: bool) -> None:
        current_idx = self.file_tabs.currentIndex()

        # Update the icon for the tab
        self.file_tabs.setTabIcon(current_idx, get_verified_icon(new_status))

        if continue_check:
            if current_idx >= self.file_tabs.count() - 1:
                # Move to result export
                self.continueToNextStep.emit()
            else:
                # Move to the next tab
                self.file_tabs.setCurrentIndex(current_idx + 1)
