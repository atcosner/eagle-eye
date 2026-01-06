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
from src.gui.tabs.reference_form_picker import ReferenceFormPicker
from src.gui.tabs.result_export import ResultExport

logger = logging.getLogger(__name__)


class ProcessingPipeline(QTabWidget):
    inputFilesConfirmed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._job_id: int | None = None

        self.reference_form_picker = ReferenceFormPicker()
        self.file_picker = FilePicker()
        self.pre_processing = FilePreProcessing()
        self.processing = FileProcessing()
        self.result_check = OcrResultCheck()
        self.result_export = ResultExport()

        self.addTab(self.reference_form_picker, 'Step 1 - Choose Reference Form')
        self.addTab(self.file_picker, 'Step 2 - Choose Files')
        self.addTab(self.pre_processing, 'Step 3 - Pre-Processing')
        self.addTab(self.processing, 'Step 4 - OCR Processing')
        self.addTab(self.result_check, 'Step 5 - Check Results')
        self.addTab(self.result_export, 'Step 6 - Export')

        self._connect_signals()
        self._initial_state()

    def _connect_signals(self) -> None:
        self.reference_form_picker.continueToNextStep.connect(self.reference_form_picking_done)
        self.file_picker.continueToNextStep.connect(self.file_picking_done)
        self.pre_processing.continueToNextStep.connect(self.pre_processing_done)
        self.processing.continueToNextStep.connect(self.processing_done)
        self.result_check.continueToNextStep.connect(self.result_check_done)

    def _initial_state(self) -> None:
        self.setCurrentIndex(0)

        # Disable all tabs except the first one
        for tab_idx in range(1, self.count()):
            self.setTabEnabled(tab_idx, False)

    def load_job(self, job_id: int) -> None:
        self._initial_state()

        with Session(DB_ENGINE) as session:
            job: Job | None = session.get(Job, job_id)
            self._job_id = job_id

            self.reference_form_picker.load_job(job)
            self.file_picker.load_job(job)
            self.pre_processing.load_job(job)
            self.processing.load_job(job)
            self.result_check.load_job(job)
            self.result_export.load_job(job)

            # Check if the job has a reference form assigned
            if job.reference_form_id is not None:
                self.gui_move_to_file_picking()

            # Check if any of the input files have been pre-processed
            if job.any_pre_processed():
                self.gui_move_to_pre_processing()

            # If all the files have been pre-processed, move to step 3
            if job.all_pre_processed():
                self.gui_move_to_processing()

            # If all the files have been OCR'd, move to step 4
            if job.all_processed():
                self.gui_move_to_result_check()

    def reload_reference_forms(self) -> None:
        self.reference_form_picker.load_reference_forms()

    def gui_move_to_file_picking(self) -> None:
        self.reference_form_picker.set_view_only(True)

        # Set the file picking tab to have focus
        self.setTabEnabled(1, True)
        self.setCurrentIndex(1)

    def gui_move_to_pre_processing(self) -> None:
        self.file_picker.set_view_only(True)

        # Set the pre-processing tab to have focus
        self.setTabEnabled(2, True)
        self.setCurrentIndex(2)

        # Signal out for the main window to update and gui elements
        self.inputFilesConfirmed.emit()

    def gui_move_to_processing(self) -> None:
        self.pre_processing.set_view_only(True)

        # Set the processing tab to have focus
        self.setTabEnabled(3, True)
        self.setCurrentIndex(3)

    def gui_move_to_result_check(self) -> None:
        self.processing.set_view_only(True)

        # Enable the tabs for step 4 and 5
        self.setTabEnabled(4, True)
        self.setTabEnabled(5, True)

        # Set the check results tab to have focus
        self.setCurrentIndex(4)

    @pyqtSlot()
    def reference_form_picking_done(self) -> None:
        # Add the selected reference form to the job
        with Session(DB_ENGINE) as session:
            job = session.get(Job, self._job_id)
            reference_form = session.get(ReferenceForm, self.reference_form_picker.get_reference_form())
            job.reference_form = reference_form
            session.commit()

        self.gui_move_to_file_picking()

    @pyqtSlot()
    def file_picking_done(self) -> None:
        self.pre_processing.load_job(self._job_id, load_all=True)
        self.gui_move_to_pre_processing()

    @pyqtSlot()
    def pre_processing_done(self) -> None:
        self.processing.load_job(self._job_id)
        self.processing.check_api_config()
        self.gui_move_to_processing()

    @pyqtSlot()
    def processing_done(self) -> None:
        self.result_check.load_job(self._job_id)
        self.gui_move_to_result_check()

    @pyqtSlot()
    def result_check_done(self) -> None:
        self.setCurrentIndex(4)
