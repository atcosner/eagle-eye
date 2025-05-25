import logging
from sqlalchemy.orm import Session

from PyQt6.QtCore import pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QTabWidget, QWidget

from src.database import DB_ENGINE
from src.database.job import Job
from src.database.reference_form import ReferenceForm
from src.gui.tabs.file_picker import FilePicker
from src.gui.tabs.file_pre_processing import FilePreProcessing
from src.gui.tabs.file_processing import FileProcessing
from src.gui.tabs.ocr_result_check import OcrResultCheck
from src.gui.tabs.result_export import ResultExport
from src.util.types import FileDetails

logger = logging.getLogger(__name__)


class ProcessingPipeline(QTabWidget):
    inputFilesConfirmed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._job_id: int | None = None
        self._reference_form_id: int | None = None

        self.picker = FilePicker()
        self.pre_processing = FilePreProcessing()
        self.processing = FileProcessing()
        self.result_check = OcrResultCheck()
        self.result_export = ResultExport()

        self.addTab(self.picker, 'Step 1 - Choose Files')
        self.addTab(self.pre_processing, 'Step 2 - Pre-Processing')
        self.addTab(self.processing, 'Step 3 - OCR Processing')
        self.addTab(self.result_check, 'Step 4 - Check Results')
        self.addTab(self.result_export, 'Step 5 - Export')

        self._connect_signals()
        self._initial_state()

    def _connect_signals(self) -> None:
        self.picker.continueToNextStep.connect(self.file_picking_done)
        self.pre_processing.continueToNextStep.connect(self.pre_processing_done)
        self.processing.continueToNextStep.connect(self.processing_done)
        self.result_check.continueToNextStep.connect(self.result_check_done)

    def _initial_state(self) -> None:
        self.setCurrentIndex(0)

        # Disable steps 4 and 5 until we have completed OCR processing
        self.setTabEnabled(3, False)
        self.setTabEnabled(4, False)

    def load_job(self, job_id: int) -> None:
        self._initial_state()

        with Session(DB_ENGINE) as session:
            job: Job | None = session.get(Job, job_id)
            self._job_id = job_id

            self.picker.load_job(job)
            self.pre_processing.load_job(job)
            self.processing.load_job(job)
            self.result_check.load_job(job)
            self.result_export.load_job(job)

            # Check if any of the input files have been pre-processed
            if job.any_pre_processed():
                self.gui_move_to_pre_processing()

            # If all the files have been pre-processed, move to step 3
            if job.all_pre_processed():
                self.gui_move_to_processing()

            # If all the files have been OCR'd, move to step 4
            if job.all_processed():
                self.gui_move_to_result_check()

    def gui_move_to_pre_processing(self) -> None:
        self.picker.set_view_only(True)

        # Set the pre-processing tab to have focus
        self.setCurrentIndex(1)

        # Signal out for the main window to update and gui elements
        self.inputFilesConfirmed.emit()

    def gui_move_to_processing(self) -> None:
        self.pre_processing.set_view_only(True)

        # Set the processing tab to have focus
        self.setCurrentIndex(2)

    def gui_move_to_result_check(self) -> None:
        self.processing.set_view_only(True)

        # Enable the tabs for step 4 and 5
        self.setTabEnabled(3, True)
        self.setTabEnabled(4, True)

        # Set the check results tab to have focus
        self.setCurrentIndex(3)

    def change_reference_form(self, db_id: int | None) -> None:
        self._reference_form_id = db_id

    @pyqtSlot()
    def file_picking_done(self) -> None:
        # Do nothing if we have no reference form selected
        if self._reference_form_id is None:
            # TODO: warn user
            logger.error('No reference form selected')
            return

        # Add the selected reference form to the job
        with Session(DB_ENGINE) as session:
            job = session.get(Job, self._job_id)
            reference_form = session.get(ReferenceForm, self._reference_form_id)
            job.reference_form = reference_form
            session.commit()

        self.pre_processing.load_job(self._job_id, load_all=True)
        self.gui_move_to_pre_processing()

    @pyqtSlot()
    def pre_processing_done(self) -> None:
        self.processing.load_job(self._job_id)
        self.gui_move_to_processing()

    @pyqtSlot()
    def processing_done(self) -> None:
        self.result_check.load_job(self._job_id)
        self.gui_move_to_result_check()

    @pyqtSlot()
    def result_check_done(self) -> None:
        self.setCurrentIndex(4)
