import logging
import uuid

from PyQt6.QtCore import pyqtSlot
from sqlalchemy import select
from sqlalchemy.orm import Session

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QHBoxLayout, QLabel, QComboBox, QSizePolicy

from src.database import DB_ENGINE
from src.database.job import Job
from src.database.reference_form import ReferenceForm
from src.util.paths import LocalPaths

from .base import BaseWindow
from .job_selector import JobDetails, JobSelector
from ..widgets.processing_pipeline import ProcessingPipeline

logger = logging.getLogger(__name__)


def create_job(job_name: str) -> int:
    with Session(DB_ENGINE) as session:
        new_job = Job(name=job_name, uuid=uuid.uuid4())
        session.add(new_job)
        session.commit()

        LocalPaths.set_up_job_directory(new_job.uuid)

        logger.info(f'Created new job with ID: {new_job.id}')
        return new_job.id


class MainWindow(BaseWindow):
    def __init__(self):
        super().__init__(None, 'Form Processing')
        self.setMinimumHeight(700)

        self._job_db_id: int | None = None

        self.job_name = QLineEdit(self)
        self.job_name.setDisabled(True)

        self.reference_form_selector = QComboBox(self)
        self.reference_form_selector.setPlaceholderText('< No Reference Form Selected >')
        size_policy = QSizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Policy.MinimumExpanding)
        self.reference_form_selector.setSizePolicy(size_policy)
        self.reference_form_selector.currentIndexChanged.connect(self.handle_reference_form_change)

        self.processing_pipeline = ProcessingPipeline(self)
        self.processing_pipeline.inputFilesConfirmed.connect(self.handle_input_files_confirmed)

        self._set_layout()
        self._toggle_controls(False)

    def _set_layout(self) -> None:
        job_name_layout = QHBoxLayout()
        job_name_layout.addWidget(QLabel('Job Name: '))
        job_name_layout.addWidget(self.job_name)

        job_reference_layout = QHBoxLayout()
        job_reference_layout.addWidget(QLabel('Reference Form: '))
        job_reference_layout.addWidget(self.reference_form_selector)

        layout = QVBoxLayout()
        layout.addLayout(job_name_layout)
        layout.addLayout(job_reference_layout)
        layout.addSpacing(15)
        layout.addWidget(self.processing_pipeline)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def _toggle_controls(self, enabled: bool) -> None:
        self.reference_form_selector.setDisabled(not enabled)
        self.processing_pipeline.setDisabled(not enabled)

    @pyqtSlot()
    def handle_input_files_confirmed(self) -> None:
        self.reference_form_selector.setDisabled(True)

    @pyqtSlot(int)
    def handle_reference_form_change(self, _: int) -> None:
        self.processing_pipeline.change_reference_form(self.reference_form_selector.currentData())

    def load_job(self, job_id: int) -> None:
        self._toggle_controls(True)

        with Session(DB_ENGINE) as session:
            job = session.get(Job, job_id)
            self._job_db_id = job_id

            self.job_name.setText(job.name)
            self.processing_pipeline.load_job(job_id)

    def reload_reference_forms(self) -> None:
        self.reference_form_selector.clear()
        with Session(DB_ENGINE) as session:
            for row in session.execute(select(ReferenceForm)):
                self.reference_form_selector.addItem(row.ReferenceForm.name, row.ReferenceForm.id)

        if self.reference_form_selector.count() > 0:
            self.reference_form_selector.setCurrentIndex(0)

    def start(self, auto_new_job: bool = False) -> None:
        self.reload_reference_forms()
        self.show()

        if auto_new_job:
            details = JobDetails(db_id=None, job_name=str(uuid.uuid4()))
            self._toggle_controls(True)
        else:
            selector = JobSelector(self)
            if not selector.exec():
                return

            details = selector.get_selected_job()

        # Determine if we are creating a new job or loading one
        logger.info(f'Selected job: {details}')
        if details.db_id is None:
            job_id = create_job(details.job_name)
            self.load_job(job_id)
        else:
            self.load_job(details.db_id)
