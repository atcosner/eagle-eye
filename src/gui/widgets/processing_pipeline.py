from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QTabWidget, QWidget

from src.database import DB_ENGINE
from src.database.job import Job
from src.database.reference_form import ReferenceForm

from ..tabs.file_picker import FilePicker
from ..tabs.file_pre_processing import FilePreProcessing
from ..tabs.file_processing import FileProcessing
from ...util.types import FileDetails


class ProcessingPipeline(QTabWidget):
    inputFilesConfirmed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._job_id: int | None = None
        self._reference_form_id: int | None = None

        self.picker = FilePicker()
        self.pre_processing = FilePreProcessing()
        self.processing = FileProcessing()

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

            # Check if any of the input files have been pre-processed
            pre_process_results = [(input_file.pre_process_result is not None) for input_file in job.input_files]
            if any(pre_process_results):
                self.gui_move_to_step_2()

            # If all the files have been pre-processed, move to step 3
            if pre_process_results and all(pre_process_results):
                self.gui_move_to_step_3()

    def gui_move_to_step_2(self) -> None:
        # Disable the Step 1 tab
        self.setTabEnabled(0, False)

        # Signal out for the main window to update and gui elements
        self.inputFilesConfirmed.emit()

    def gui_move_to_step_3(self) -> None:
        self.setCurrentIndex(2)

    def change_reference_form(self, db_id: int | None) -> None:
        self._reference_form_id = db_id

    @pyqtSlot(list)
    def confirm_input_files(self, files: list[FileDetails]) -> None:
        # Do nothing if we have no reference form selected
        if self._reference_form_id is None:
            return

        # Add the selected reference form to the job
        with Session(DB_ENGINE) as session:
            job = session.get(Job, self._job_id)
            reference_form = session.get(ReferenceForm, self._reference_form_id)
            job.reference_form = reference_form
            session.commit()

        self.pre_processing.add_files(files)

        # Move to Step 2
        self.gui_move_to_step_2()

    @pyqtSlot()
    def pre_processing_done(self) -> None:
        self.processing.load_job(self._job_id)
        self.gui_move_to_step_3()
