from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QTabWidget, QWidget

from src.database import DB_ENGINE
from src.database.job import Job
from src.database.reference_form import ReferenceForm

from ..tabs.file_picker import FilePicker
from ..tabs.file_pre_processing import FilePreProcessing
from ..tabs.ocr_processing import OcrProcessing
from ...util.types import FileDetails


class ProcessingPipeline(QTabWidget):
    inputFilesConfirmed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._job_id: int | None = None
        self._reference_form_id: int | None = None

        self.picker = FilePicker()
        self.pre_processing = FilePreProcessing()
        self.processing = OcrProcessing()

        self.addTab(self.picker, 'Step 1 - Choose Files')
        self.addTab(self.pre_processing, 'Step 2 - Pre-Processing')
        self.addTab(self.processing, 'Step 3 - OCR Processing')

        self._connect_signals()

    def _connect_signals(self) -> None:
        self.picker.filesConfirmed.connect(self.confirm_input_files)
        self.pre_processing.continueToOcr.connect(self.pre_processing_done)

    def load_job(self, job_id: int) -> None:
        with Session(DB_ENGINE) as session:
            job = session.get(Job, job_id)
            self._job_id = job_id

            self.picker.load_job(job)
            self.pre_processing.load_job(job)
            self.processing.load_job(job)

    def change_reference_form(self, db_id: int | None) -> None:
        self._reference_form_id = db_id

    @pyqtSlot(list)
    def confirm_input_files(self, files: list[FileDetails]) -> None:
        # Do nothing if we have no reference form selected
        if self._reference_form_id is None:
            return

        # Disable the Step 1 tab and the reference form selector
        self.setTabEnabled(0, False)
        self.inputFilesConfirmed.emit()

        # Add the selected reference form to the job
        with Session(DB_ENGINE) as session:
            job = session.get(Job, self._job_id)
            reference_form = session.get(ReferenceForm, self._reference_form_id)
            job.reference_form = reference_form
            session.commit()

        self.pre_processing.add_files(files)

    @pyqtSlot()
    def pre_processing_done(self) -> None:
        self.setCurrentIndex(2)
        self.processing.load_job(self._job_id)
